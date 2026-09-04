#!/usr/bin/env python3
"""YouTube downloader script using yt-dlp to extract audio as OGG or fetch structured subtitles directly."""

from datetime import UTC, datetime
import html
import json
import re
import sys
import time
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

import yt_dlp
from helper import apply_cookies_to_ydl_opts, fetch_url_content


def _is_native_sub_url(url: str | None) -> bool:
    """Validate that subtitle URL is native and not an on-the-fly machine translation."""
    if not url:
        return False
    # Strictly reject on-the-fly machine-translated subtitles that cause HTTP 429
    if "tlang=" in url:
        return False
    return True


def find_subtitle_url(info: dict, preferred_ext: str) -> tuple[str, str] | None:
    """Search for a suitable subtitle or automatic caption URL matching the preferred extension.

    Strictly prioritizes the native spoken audio language (*-orig, video audio language)
    and completely filters out on-the-fly machine translations (tlang=) which cause HTTP 429.
    """
    subtitles = info.get("subtitles") or {}
    auto_caps = info.get("automatic_captions") or {}

    video_lang = (info.get("language") or "").lower()
    is_pt_video = video_lang.startswith("pt")

    if is_pt_video:
        ordered_langs = ["pt-orig", "pt-BR", "pt", "pt-PT", "en-orig", "en", "en-US"]
    else:
        ordered_langs = ["en-orig", "en", "en-US", "pt-orig", "pt-BR", "pt", "pt-PT"]

    # 1. Search in manual subtitles in preferred language order (never tlang)
    for lang in ordered_langs:
        if lang in subtitles:
            for fmt in subtitles[lang]:
                url = fmt.get("url")
                if fmt.get("ext") == preferred_ext and _is_native_sub_url(url):
                    return lang, url

    # 2. Search manual subtitles in any language
    for lang, formats in subtitles.items():
        for fmt in formats:
            url = fmt.get("url")
            if fmt.get("ext") == preferred_ext and _is_native_sub_url(url):
                return lang, url

    # 3. Automatic captions: Prioritize explicit original tracks (*-orig)
    orig_keys = [k for k in auto_caps.keys() if k.endswith("-orig") or k == "orig"]
    # Sort so video language's orig comes first
    orig_keys.sort(key=lambda k: 0 if (is_pt_video and "pt" in k) or (not is_pt_video and "en" in k) else 1)
    for lang in orig_keys:
        for fmt in auto_caps[lang]:
            url = fmt.get("url")
            if fmt.get("ext") == preferred_ext and _is_native_sub_url(url):
                return lang, url

    # 4. Automatic captions matching preferred language order without tlang
    for lang in ordered_langs:
        if lang in auto_caps:
            for fmt in auto_caps[lang]:
                url = fmt.get("url")
                if fmt.get("ext") == preferred_ext and _is_native_sub_url(url):
                    return lang, url

    # 5. Any automatic caption track without tlang
    for lang, formats in auto_caps.items():
        for fmt in formats:
            url = fmt.get("url")
            if fmt.get("ext") == preferred_ext and _is_native_sub_url(url):
                return lang, url

    return None

def fetch_json_from_url(url: str) -> dict:
    """Fetch and decode JSON from the given URL."""
    content = fetch_url_content(url)
    return json.loads(content)

def reconstruct_json3_paragraphs(data: dict, silence_threshold_ms: int = 2000, punctuation_limit: int = 5) -> str:
    """Reconstruct JSON3 format subtitles into clean paragraphs using time-gaps and punctuation counts."""
    events = data.get("events", [])

    # Filter out layout/header events and append events
    text_events = []
    for event in events:
        if "segs" in event and not event.get("aAppend"):
            # Combine segment texts
            seg_text = "".join(seg.get("utf8", "") for seg in event["segs"]).strip()
            if seg_text:
                text_events.append({
                    "start": event["tStartMs"],
                    "duration": event["dDurationMs"],
                    "end": event["tStartMs"] + event["dDurationMs"],
                    "text": seg_text
                })

    if not text_events:
        return ""

    paragraphs = []
    current_paragraph_texts = []
    punc_count = 0

    max_end_so_far = text_events[0]["end"]
    current_paragraph_texts.append(text_events[0]["text"])

    # Count punctuation in the first chunk
    punc_count += len(re.findall(r'[.!?]', text_events[0]["text"]))

    for i in range(1, len(text_events)):
        curr = text_events[i]

        # Calculate silence gap
        gap = curr["start"] - max_end_so_far

        # Count punctuation in the current event text
        curr_punc = len(re.findall(r'[.!?]', curr["text"]))

        # Split paragraph if:
        # 1. Silence gap is >= silence_threshold_ms
        # 2. Accumulated punctuation in the current paragraph meets or exceeds the limit
        if gap >= silence_threshold_ms or punc_count >= punctuation_limit:
            paragraphs.append(" ".join(current_paragraph_texts))
            current_paragraph_texts = [curr["text"]]
            punc_count = curr_punc
        else:
            current_paragraph_texts.append(curr["text"])
            punc_count += curr_punc

        max_end_so_far = max(max_end_so_far, curr["end"])

    if current_paragraph_texts:
        paragraphs.append(" ".join(current_paragraph_texts))

    # Clean up multiple spaces and join paragraphs
    cleaned_paragraphs = []
    for p in paragraphs:
        p_clean = re.sub(r'\s+', ' ', p).strip()
        if p_clean:
            cleaned_paragraphs.append(p_clean)

    return "\n\n".join(cleaned_paragraphs)

def parse_json3_to_paragraphs(json3_url: str, silence_threshold_ms: int = 2000, punctuation_limit: int = 5) -> str:
    """Fetch JSON3 format subtitles and reconstruct them into clean paragraphs."""
    data = fetch_json_from_url(json3_url)
    return reconstruct_json3_paragraphs(data, silence_threshold_ms, punctuation_limit)

def reconstruct_srv1_paragraphs(xml_data: str, punctuation_limit: int = 5) -> str:
    """Extract text from XML subtitle in srv1 format and split into paragraphs based on punctuation count."""
    root = ET.fromstring(xml_data)
    texts = []
    for child in root.findall('text'):
        t = child.text
        if t:
            # HTML entities like &quot; and &#39; need to be unescaped
            texts.append(html.unescape(t.strip()))

    raw_text = " ".join(texts)

    # Split raw_text into paragraphs of at most punctuation_limit punctuation marks
    words = raw_text.split()
    paragraphs = []
    current_paragraph = []
    punc_count = 0

    for word in words:
        current_paragraph.append(word)
        punc_count += len(re.findall(r'[.!?]', word))
        if punc_count >= punctuation_limit:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []
            punc_count = 0

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    return "\n\n".join(p for p in paragraphs if p.strip())

def fetch_and_parse_srv1(url: str, punctuation_limit: int = 5) -> str:
    """Fetch the XML subtitle in srv1 format and extract text split into paragraphs."""
    xml_data = fetch_url_content(url)
    return reconstruct_srv1_paragraphs(xml_data, punctuation_limit)

class QuietLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def extract_video_metadata(url: str, use_cookies: bool = False) -> dict:
    """Extract and return video metadata using yt-dlp.

    Why use_cookies defaults to False:
    Querying video metadata/subtitles without account cookies avoids binding large batches
    of requests to a single logged-in Google session. Authenticated sessions face aggressive
    global rate-limiting (HTTP 429) across YouTube's timedtext/player endpoints.
    If bot protection is detected, cookies can be applied on retry.
    """
    ydl_opts_meta = {
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'logger': QuietLogger(),
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    apply_cookies_to_ydl_opts(ydl_opts_meta, use_cookies=use_cookies)
    try:
        with yt_dlp.YoutubeDL(ydl_opts_meta.copy()) as ydl:
            res = ydl.extract_info(url, download=False)
            return res or {}
    except Exception as e:
        err_msg = str(e).lower()
        if any(pattern in err_msg for pattern in ("sign in to confirm", "bot", "cookie", "login")):
            # Attempt auto-refreshing cookies from browser if blocked anonymously
            print(f"[COOKIE EXPIRED] Auto-refreshing cookies for {url}...")
            apply_cookies_to_ydl_opts(ydl_opts_meta, use_cookies=True, force_refresh=True)
            try:
                with yt_dlp.YoutubeDL(ydl_opts_meta.copy()) as ydl:
                    res = ydl.extract_info(url, download=False)
                    return res or {}
            except Exception as retry_err:
                print(f"[COOKIE ERROR] Retry failed for {url}: {retry_err}")
        return {}


def download_audio_as_ogg(url: str, output_dir: Path, video_id: str, use_cookies: bool = True) -> Path:
    """Download audio stream using yt-dlp and convert to OGG format for Whisper fallback."""
    ydl_opts_download = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'vorbis',
            'preferredquality': '192',
        }],
        'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'postprocessor_args': {
            'FFmpegExtractAudio': ['-loglevel', 'error'],
        },
        'external_downloader_args': {
            'ffmpeg': ['-loglevel', 'error'],
        },
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    apply_cookies_to_ydl_opts(ydl_opts_download, use_cookies=use_cookies)
    try:
        with yt_dlp.YoutubeDL(ydl_opts_download.copy()) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        err_msg = str(e).lower()
        if use_cookies and any(pattern in err_msg for pattern in ("sign in to confirm", "bot", "cookie", "login")):
            print(f"[BOT DETECTED] Refreshing cookies for audio download ({video_id})...")
            apply_cookies_to_ydl_opts(ydl_opts_download, use_cookies=True, force_refresh=True)
            with yt_dlp.YoutubeDL(ydl_opts_download.copy()) as ydl:
                ydl.extract_info(url, download=True)
        else:
            raise e
    ogg_file = output_dir / f"{video_id}.ogg"
    return ogg_file.resolve()

import os
import random
import yt_dlp
from helper import fetch_url_content

_CRESMO_DIR = Path(__file__).resolve().parent.parent / "cresmo"
_ENV_RATE_LIMIT_LOG = os.environ.get("YOUTUBE_RATE_LIMIT_LOG_FILE")
if _ENV_RATE_LIMIT_LOG:
    RATE_LIMIT_LOG_FILE = Path(_ENV_RATE_LIMIT_LOG).resolve()
elif _CRESMO_DIR.exists():
    RATE_LIMIT_LOG_FILE = (_CRESMO_DIR / "rate_limit_log.json").resolve()
else:
    RATE_LIMIT_LOG_FILE = (Path(__file__).resolve().parent / "rate_limit_log.json").resolve()

_GLOBAL_429_ATTEMPT = 0
_ACCUMULATED_BLOCKED_TIME = 0.0

# TCP Retransmission Timer (RFC 6298 / EWMA) state parameters
_BASE_BACKOFF_QUANTUM = 1.0  # B_0: initial base quantum (seconds)
_EWMA_ALPHA = 0.5            # alpha: historical memory decay factor in [0, 1)
_T_MAX_DELAY = 60.0          # t_max: maximum backoff upper bound (seconds)


def reset_429_state(reset_quantum: bool = False, default_quantum: float = 1.0) -> None:
    """Reset the accumulated 429 rate-limit attempt counter and blocked time to 0.

    Optionally resets the EWMA base quantum B_k to default_quantum.
    """
    global _GLOBAL_429_ATTEMPT, _ACCUMULATED_BLOCKED_TIME, _BASE_BACKOFF_QUANTUM
    _GLOBAL_429_ATTEMPT = 0
    _ACCUMULATED_BLOCKED_TIME = 0.0
    if reset_quantum:
        _BASE_BACKOFF_QUANTUM = default_quantum


def update_base_quantum(latency: float, alpha: float = _EWMA_ALPHA) -> float:
    """Update smoothed base quantum B_k using EWMA on successful response latency X_k.

    Formula: B_k = alpha * B_{k-1} + (1 - alpha) * X_k
    """
    global _BASE_BACKOFF_QUANTUM
    _BASE_BACKOFF_QUANTUM = (alpha * _BASE_BACKOFF_QUANTUM) + ((1.0 - alpha) * latency)
    return _BASE_BACKOFF_QUANTUM


def get_base_backoff_quantum() -> float:
    """Return the current EWMA smoothed base quantum B_k."""
    return _BASE_BACKOFF_QUANTUM


def set_base_backoff_quantum(quantum: float) -> None:
    """Set the EWMA base quantum B_k."""
    global _BASE_BACKOFF_QUANTUM
    _BASE_BACKOFF_QUANTUM = max(0.001, float(quantum))


def apply_preventative_pacing(min_delay: float = 1.0, max_delay: float = 2.5) -> float:
    """Apply polite stochastic delay with uniform jitter to prevent CDN IP burst rate-limiting."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    return delay


def calculate_backoff_delay(
    n: int,
    base_quantum: float | None = None,
    t_max: float = _T_MAX_DELAY,
    jitter: bool = False
) -> float:
    """Calculate exponential backoff delay based on RFC 6298 TCP Retransmission Timer logic.

    Formulas:
        t(n) = min(t_max, B_k * (2 ** n))
        t_jitter(n) = Uniform(0, min(t_max, B_k * (2 ** n)))
    """
    if base_quantum is None:
        base_quantum = _BASE_BACKOFF_QUANTUM

    delay = min(t_max, base_quantum * (2 ** n))
    if jitter:
        return random.uniform(0.0, delay)
    return delay


def get_429_attempt_count() -> int:
    """Return the current accumulated 429 rate-limit attempt count."""
    return _GLOBAL_429_ATTEMPT


def log_rate_limit_telemetry(
    video_id: str,
    streak: int,
    delay_sec: float,
    status: str,
    total_blocked_sec: float,
    log_file: Path | None = None
) -> None:
    """Record rate limit telemetry event to JSON log file for empirical analysis."""
    if log_file is None:
        log_file = RATE_LIMIT_LOG_FILE

    log_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "video_id": video_id,
        "streak": streak,
        "delay_seconds": round(delay_sec, 2),
        "status": status,
        "total_blocked_seconds": round(total_blocked_sec, 2)
    }

    data = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    data.append(entry)
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save rate limit telemetry: {e}")


def get_estimated_timeout_seconds(log_file: Path | None = None) -> float | None:
    """Calculate estimated YouTube 429 timeout duration based on historical successful recovery events."""
    if log_file is None:
        log_file = RATE_LIMIT_LOG_FILE

    if not log_file.exists():
        return None

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        recovery_times = [
            item["total_blocked_seconds"]
            for item in data
            if item.get("status") == "SUCCESS" and item.get("total_blocked_seconds", 0) > 0
        ]
        if not recovery_times:
            return None

        recovery_times.sort()
        mid = len(recovery_times) // 2
        return float(recovery_times[mid])
    except Exception:
        return None


def get_youtube_audio_or_transcript(
    url: str,
    output_dir: str = ".",
    force_audio: bool = False,
    info: dict | None = None,
    download_audio_if_missing: bool = True,
    jitter: bool = False
) -> tuple[str | None, str | None, str]:
    """Retrieve the transcript directly from YouTube subtitles if available (json3 paragraphs -> srv1 raw text).
    Otherwise, download the audio and convert it to OGG format for Whisper.

    Args:
        url: The YouTube video URL.
        output_dir: The directory where output files will be saved.
        force_audio: If True, skips subtitle checks and forces audio downloading.
        info: Optional pre-extracted yt-dlp metadata dictionary.
        download_audio_if_missing: If False, returns (None, None, video_id) when subtitles are absent.
        jitter: If True, applies uniform stochastic jitter in [0, t(n)] to backoff delay.

    Returns:
        A tuple of (transcript_text, ogg_file_path, video_id).
        One of transcript_text or ogg_file_path will be None.
    """
    global _GLOBAL_429_ATTEMPT, _ACCUMULATED_BLOCKED_TIME

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not info:
        info = extract_video_metadata(url)
    video_id = info.get("id", "unknown_video")
    title = info.get("title", "Unknown Title")

    is_live_now = info.get("is_live") is True or info.get("live_status") == "is_live"
    is_upcoming = info.get("live_status") == "is_upcoming"
    if is_live_now or is_upcoming:
        status_str = "live" if is_live_now else "upcoming"
        print(f"[SKIPPED] {video_id} | Live stream {status_str} (in progress).")
        return None, None, video_id

    subtitles = info.get("subtitles") or {}
    auto_caps = info.get("automatic_captions") or {}
    has_subtitles = bool(subtitles or auto_caps)

    if not force_audio and has_subtitles:
        sub_json3 = find_subtitle_url(info, "json3")
        sub_srv1 = find_subtitle_url(info, "srv1")

        candidates = []
        if sub_json3:
            candidates.append(("JSON3", sub_json3[0], sub_json3[1], parse_json3_to_paragraphs))
        if sub_srv1:
            candidates.append(("SRV1", sub_srv1[0], sub_srv1[1], fetch_and_parse_srv1))

        max_accumulated_attempts = 5
        attempts_for_this_video = (
            1 if _GLOBAL_429_ATTEMPT >= max_accumulated_attempts else (max_accumulated_attempts - _GLOBAL_429_ATTEMPT)
        )

        sub_success = False
        transcript_text = None
        observed_latency = 0.0

        for _ in range(attempts_for_this_video):
            has_429 = False
            for fmt_name, lang, sub_url, parse_fn in candidates:
                try:
                    start_time = time.perf_counter()
                    transcript = parse_fn(sub_url)
                    observed_latency = time.perf_counter() - start_time
                    if transcript and transcript.strip():
                        sub_success = True
                        transcript_text = transcript
                        break
                except Exception as e:
                    status_code = getattr(e, "status", getattr(e, "code", None))
                    if status_code == 429 or "429" in str(e) or "Too Many Requests" in str(e):
                        has_429 = True
                        print(f"[429 RETRY] {video_id} ({fmt_name}-{lang}) | Trying next candidate...")
                        continue
                    else:
                        print(f"[PARSE ERROR] {video_id} ({fmt_name}): {e}")

            if sub_success:
                # ACCESS PERMITTED: Update EWMA base quantum, log telemetry, and reset global streak!
                update_base_quantum(observed_latency)
                log_rate_limit_telemetry(
                    video_id=video_id,
                    streak=_GLOBAL_429_ATTEMPT,
                    delay_sec=0.0,
                    status="SUCCESS",
                    total_blocked_sec=_ACCUMULATED_BLOCKED_TIME
                )
                reset_429_state()
                return transcript_text, None, video_id

            if has_429:
                delay = calculate_backoff_delay(
                    n=_GLOBAL_429_ATTEMPT,
                    base_quantum=_BASE_BACKOFF_QUANTUM,
                    t_max=_T_MAX_DELAY,
                    jitter=jitter
                )
                _ACCUMULATED_BLOCKED_TIME += delay
                log_rate_limit_telemetry(
                    video_id=video_id,
                    streak=_GLOBAL_429_ATTEMPT + 1,
                    delay_sec=delay,
                    status="RATE_LIMITED_429",
                    total_blocked_sec=_ACCUMULATED_BLOCKED_TIME
                )
                print(f"[429 BACKOFF] {video_id} | Waiting {delay:.1f}s (streak: {_GLOBAL_429_ATTEMPT + 1})")
                time.sleep(delay)
                _GLOBAL_429_ATTEMPT += 1
            else:
                break

        print(f"[SUBTITLE 429] {video_id} | Falling back to audio Whisper...")

    if not download_audio_if_missing and not force_audio:
        return None, None, video_id

    # Tier 3: Download audio and convert to OGG for Whisper
    try:
        ogg_file = download_audio_as_ogg(url, out_path, video_id)
        return None, str(ogg_file), video_id
    except Exception as e:
        print(f"[AUDIO ERROR] {video_id}: {e}")
        raise e

if __name__ == "__main__":
    # Quick CLI invocation test if run directly
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("No YouTube URL provided via command line.")
        try:
            url = input("Enter YouTube URL (or press Enter to run test video): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
        if not url:
            url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
            print(f"Using default test URL: {url}")

    txt, ogg, vid = get_youtube_audio_or_transcript(url, output_dir="./downloads")
    if txt:
        print(f"\n--- SUBTITLES RETRIEVED (Video ID: {vid}) ---")
        print(txt[:500] + "\n...")
    else:
        print(f"\n--- AUDIO DOWNLOADED (Video ID: {vid}) ---")
        print(f"File path: {ogg}")
