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
from helper import fetch_url_content


def find_subtitle_url(info: dict, preferred_ext: str) -> tuple[str, str] | None:
    """Search for a suitable subtitle or automatic caption URL matching the preferred extension.

    Prioritizes:
    1. pt-BR, pt-orig, pt, pt-PT, en, en-US in manual subtitles
    2. pt-BR, pt-orig, pt, pt-PT, en, en-US in automatic captions
    3. Any language code starting with 'pt' or 'en'
    4. Any language code at all that has the preferred format
    """
    subtitles = info.get("subtitles") or {}
    auto_caps = info.get("automatic_captions") or {}

    preferred_languages = ["pt-BR", "pt-orig", "pt", "pt-PT", "en", "en-US"]

    for source in (subtitles, auto_caps):
        # 1. Search in exact preference order
        for lang in preferred_languages:
            if lang in source:
                for fmt in source[lang]:
                    if fmt.get("ext") == preferred_ext:
                        return lang, fmt.get("url")

        # 2. Search for any key starting with 'pt' or 'en'
        for lang in source:
            if lang.startswith("pt") or lang.startswith("en"):
                for fmt in source[lang]:
                    if fmt.get("ext") == preferred_ext:
                        return lang, fmt.get("url")

        # 3. Search for any key at all that has the preferred format
        for lang in source:
            for fmt in source[lang]:
                if fmt.get("ext") == preferred_ext:
                    return lang, fmt.get("url")

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

def extract_video_metadata(url: str, use_cookies: bool = True) -> dict:
    """Extract and return video metadata using yt-dlp."""
    ydl_opts_meta = {
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    if use_cookies:
        ydl_opts_meta["cookiesfrombrowser"] = ("chrome",)
    try:
        with yt_dlp.YoutubeDL(ydl_opts_meta.copy()) as ydl:
            res = ydl.extract_info(url, download=False)
            return res or {}
    except Exception as e:
        if not use_cookies:
            ydl_opts_meta["cookiesfrombrowser"] = ("chrome",)
            try:
                with yt_dlp.YoutubeDL(ydl_opts_meta.copy()) as ydl:
                    res = ydl.extract_info(url, download=False)
                    return res or {}
            except Exception as inner_e:
                print(f"  Warning: Failed to fetch metadata for {url}: {inner_e}")
                return {}
        else:
            print(f"  Warning: Failed to fetch metadata for {url}: {e}")
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
    if use_cookies:
        ydl_opts_download["cookiesfrombrowser"] = ("chrome",)
    try:
        with yt_dlp.YoutubeDL(ydl_opts_download.copy()) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        if not use_cookies:
            ydl_opts_download["cookiesfrombrowser"] = ("chrome",)
            with yt_dlp.YoutubeDL(ydl_opts_download.copy()) as ydl:
                ydl.extract_info(url, download=True)
        else:
            raise e
    ogg_file = output_dir / f"{video_id}.ogg"
    return ogg_file.resolve()

import yt_dlp
from helper import fetch_url_content

RATE_LIMIT_LOG_FILE = Path(__file__).parent / "rate_limit_log.json"
_GLOBAL_429_ATTEMPT = 0
_ACCUMULATED_BLOCKED_TIME = 0.0


def reset_429_state() -> None:
    """Reset the accumulated 429 rate-limit attempt counter and blocked time to 0."""
    global _GLOBAL_429_ATTEMPT, _ACCUMULATED_BLOCKED_TIME
    _GLOBAL_429_ATTEMPT = 0
    _ACCUMULATED_BLOCKED_TIME = 0.0


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


def get_youtube_audio_or_transcript(url: str, output_dir: str = ".", force_audio: bool = False, info: dict | None = None) -> tuple[str | None, str | None, str]:
    """Retrieve the transcript directly from YouTube subtitles if available (json3 paragraphs -> srv1 raw text).
    Otherwise, download the audio and convert it to OGG format for Whisper.

    Args:
        url: The YouTube video URL.
        output_dir: The directory where output files will be saved.
        force_audio: If True, skips subtitle checks and forces audio downloading.
        info: Optional pre-extracted yt-dlp metadata dictionary.

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
        status_str = "ao vivo" if is_live_now else "agendada (upcoming)"
        print(f"  ⚠️ Pulando '{title[:30]}...': Transmissão {status_str} (não finalizada).")
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

        # Adaptive initial delay: start at half the estimated timeout if known, or 10s default
        est_timeout = get_estimated_timeout_seconds()
        if _GLOBAL_429_ATTEMPT == 0 and est_timeout and est_timeout > 20.0:
            initial_delay = max(10.0, est_timeout / 2.0)
        else:
            initial_delay = 10.0

        max_accumulated_attempts = 5
        attempts_for_this_video = (
            1 if _GLOBAL_429_ATTEMPT >= max_accumulated_attempts else (max_accumulated_attempts - _GLOBAL_429_ATTEMPT)
        )

        sub_success = False
        transcript_text = None

        for _ in range(attempts_for_this_video):
            is_429 = False
            for fmt_name, lang, sub_url, parse_fn in candidates:
                try:
                    transcript = parse_fn(sub_url)
                    if transcript and transcript.strip():
                        sub_success = True
                        transcript_text = transcript
                        break
                except Exception as e:
                    if (isinstance(e, urllib.error.HTTPError) and e.code == 429) or ("429" in str(e) or "Too Many Requests" in str(e)):
                        is_429 = True
                        break
                    else:
                        print(f"Warning: Failed to parse {fmt_name} subtitles ({e}).")

            if sub_success:
                # ACCESS PERMITTED: Log telemetry and reset global state!
                log_rate_limit_telemetry(
                    video_id=video_id,
                    streak=_GLOBAL_429_ATTEMPT,
                    delay_sec=0.0,
                    status="SUCCESS",
                    total_blocked_sec=_ACCUMULATED_BLOCKED_TIME
                )
                reset_429_state()
                return transcript_text, None, video_id

            if is_429:
                delay = initial_delay * (2 ** min(_GLOBAL_429_ATTEMPT, 5))
                _ACCUMULATED_BLOCKED_TIME += delay
                log_rate_limit_telemetry(
                    video_id=video_id,
                    streak=_GLOBAL_429_ATTEMPT + 1,
                    delay_sec=delay,
                    status="RATE_LIMITED_429",
                    total_blocked_sec=_ACCUMULATED_BLOCKED_TIME
                )
                print(
                    f"  ⚠️ Rate limit (HTTP 429) hit fetching subtitles for '{title[:30]}...'. "
                    f"Waiting {delay:.1f}s for reset (global 429 streak: {_GLOBAL_429_ATTEMPT + 1}, total blocked time: {_ACCUMULATED_BLOCKED_TIME:.1f}s)..."
                )
                time.sleep(delay)
                _GLOBAL_429_ATTEMPT += 1
            else:
                break

        print(f"  ⚠️ Subtitle rate-limit persisted for '{title[:30]}...'. Falling back to Whisper audio processing...")

    # Tier 3: Download audio and convert to OGG for Whisper
    print(f"Downloading audio stream (Whisper fallback) for '{title[:30]}...'...")
    try:
        ogg_file = download_audio_as_ogg(url, out_path, video_id)
        print(f"Successfully downloaded and processed '{title}' as: {ogg_file}")
        return None, str(ogg_file), video_id
    except Exception as e:
        print(f"Error downloading/processing audio: {e}")
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
