#!/usr/bin/env python3
"""YouTube Channel Video Syncer script.

Downloads new videos uploaded within the last X days from channels listed in playlist.txt.
Maintains idempotency via a Markdown log file.
"""

import json
import os
import queue
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import yt_dlp

from downloader import extract_video_metadata, get_youtube_audio_or_transcript
from export_cookies import ensure_cookies
from helper import (
    apply_cookies_to_ydl_opts,
    clean_filename,
    extract_youtube_video_id,
    format_date_for_path,
    get_full_upload_date,
    is_within_range,
    parse_merged_transcriptions,
    parse_yaml_header,
    read_playlist_urls,
    sanitize_for_path,
)
from ollama_processor import process_transcript_to_obsidian
from transcriber import transcribe_audio_to_text

# --- Configs ---
PLAYLIST_FILE = Path(__file__).parent / "playlist.txt"
CSV_FILE = Path(__file__).parent / "wiki" / "log.md"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "raw"

def load_historical_metadata(output_dir: Path, csv_path: Path | None = None, max_workers: int = 32) -> tuple[set[str], set[str]]:
    """Load previously synced video IDs and channel IDs.
    
    Combines fast parsing of the Markdown ingestion log table with a multi-threaded header-only
    scan of text files in the output directory, avoiding expensive full-file transcript parsing.

    Returns:
        tuple[set[str], set[str]]: A tuple containing (synced_ids, synced_channels)
    """
    synced_ids: set[str] = set()
    synced_channels: set[str] = set()

    # 1. Fast loading from the log file (O(1) pass, ~0.1s for 40k+ entries)
    if csv_path and csv_path.exists():
        try:
            with open(csv_path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("|") and "---" not in line and "Channel ID" not in line:
                        parts = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts) >= 2:
                            synced_channels.add(parts[0])
                            synced_ids.add(parts[1])
        except Exception as e:
            print(f"Warning: Failed to load metadata from log file {csv_path.name}: {e}")

    # 2. Fast scan of files in output_dir for any unlogged files
    if output_dir.exists():
        try:
            yt_id_pattern = re.compile(r"^.*-([a-zA-Z0-9_-]{11})$")
            unparsed_files: list[Path] = []

            for txt_file in output_dir.rglob("*.txt"):
                m = yt_id_pattern.match(txt_file.stem)
                if m:
                    synced_ids.add(m.group(1))
                else:
                    unparsed_files.append(txt_file)

            # For files that do not follow standard filename convention, perform parallel header-only parsing
            if unparsed_files:
                def _scan_header(p: Path) -> tuple[str | None, str | None]:
                    v_id, c_id = None, None
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("video_id:"):
                                    v_id = line.split(":", 1)[1].strip(" \"'\t\r\n")
                                elif line.startswith("channel_id:"):
                                    c_id = line.split(":", 1)[1].strip(" \"'\t\r\n")
                                elif line.strip() == "---" and (v_id or c_id):
                                    break
                    except Exception:
                        pass
                    return v_id, c_id

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for v_id, c_id in executor.map(_scan_header, unparsed_files):
                        if v_id:
                            synced_ids.add(v_id)
                        if c_id:
                            synced_channels.add(c_id)

        except Exception as e:
            print(f"Warning: Failed to load historical metadata from {output_dir.name}: {e}")

    return synced_ids, synced_channels

CACHE_LOCK = threading.Lock()
RECORD_LOG_LOCK = threading.Lock()
SYNCED_IDS_LOCK = threading.RLock()
CHANNELS_TO_SCAN_LOCK = threading.Lock()
QUEUED_IDS = set()
QUEUED_IDS_LOCK = threading.Lock()


class QuietLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def load_channel_cache(cache_path: Path) -> dict[str, list[dict]]:
    """Load previously fetched channel entries from disk cache."""
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("channels", {})
    except Exception as e:
        print(f"Warning: Failed to load channel cache {cache_path.name}: {e}")
        return {}


def update_channel_cache(cache_path: Path, channel_id: str, entries: list[dict]) -> None:
    """Save channel playlist entries incrementally to disk cache using atomic file replacement."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_LOCK:
        data = {"channels": {}}
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {"channels": {}}
        if "channels" not in data:
            data["channels"] = {}
        data["channels"][channel_id] = entries

        tmp_path = cache_path.with_name(f"{cache_path.stem}_{threading.get_ident()}.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            tmp_path.replace(cache_path)
        except Exception as e:
            print(f"Warning: Failed to save channel cache: {e}")
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

def record_synced_video(log_path: Path, channel_id: str, video_id: str, upload_date: str, title: str = "Unknown Title") -> None:
    """Record a successfully synced video in the Markdown log table (thread-safe)."""
    file_exists = log_path.exists()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with RECORD_LOG_LOCK:
            with open(log_path, "a", encoding="utf-8") as f:
                if not file_exists:
                    f.write("# Ingestion Log\n\n")
                    f.write("| Channel ID | Video ID | Upload Date | Title |\n")
                    f.write("| --- | --- | --- | --- |\n")
                clean_title = title.replace("|", "\\|")
                f.write(f"| {channel_id} | {video_id} | {upload_date} | {clean_title} |\n")
    except Exception as e:
        print(f"Error saving to Markdown log: {e}")

def fetch_channel_recent_videos(channel_id: str, limit: int = 50, use_cookies: bool = False) -> list[dict]:
    """Query recent videos from a channel using its uploads playlist ID.

    Why use_cookies defaults to False:
    Querying public channel playlists without user session cookies prevents YouTube from
    accumulating quota usage or flagging the user account with 429 rate limits across
    the multi-channel crawler pipeline.
    """
    if not channel_id.startswith("UC"):
        print(f"Warning: Channel ID '{channel_id}' does not match standard UC prefix. Fetching videos page directly.")
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
    else:
        # Swap UC to UU to target the channel's uploads playlist directly
        uploads_playlist_id = "UU" + channel_id[2:]
        url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

    # print(f"Querying channel uploads for ID: {url}")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": QuietLogger(),
        "playlistend": limit,
        "extract_flat": True,
        "extractor_args": {"youtubetab": {"approximate_date": [""]}},
        "ignoreerrors": True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    apply_cookies_to_ydl_opts(ydl_opts, use_cookies=use_cookies)

    def extract_with_opts(opts):
        with yt_dlp.YoutubeDL(opts.copy()) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            if playlist_info:
                return [e for e in playlist_info.get("entries", []) if e]
            return []

    try:
        return extract_with_opts(ydl_opts)
    except Exception as e:
        if not use_cookies:
            # Fallback to try with cookies if anonymous scraping encounters bot defense
            ydl_opts_with_cookies = ydl_opts.copy()
            apply_cookies_to_ydl_opts(ydl_opts_with_cookies, use_cookies=True)
            try:
                return extract_with_opts(ydl_opts_with_cookies)
            except Exception:
                pass
        print(f"Error fetching channel playlist {channel_id}: {e}")
    return []

def sync_single_video(url: str, output_dir: Path, model_name: str, keep_audio: bool, info: dict | None = None) -> dict:
    """Process a single video using the 3-tier fallback model (JSON3 -> SRV1 -> Whisper OGG)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch metadata first
    if not info:
        info = extract_video_metadata(url)
    if not info or not info.get("id"):
        print(f"  Warning: Skipping video {url} due to unresolvable metadata/bot protection.")
        return {}
    video_id = info.get("id", "unknown_video")

    # 2. Extract and sanitize path components
    categories = info.get("categories")
    category = categories[0] if categories else "uncategorized"
    cat_dir = sanitize_for_path(category)

    channel = info.get("channel") or info.get("uploader") or "unknown_channel"
    chan_dir = sanitize_for_path(channel)

    upload_date = get_full_upload_date(info)
    date_str = format_date_for_path(upload_date)

    target_dir = output_dir / channel
    target_dir.mkdir(parents=True, exist_ok=True)
    txt_path = target_dir / f"{date_str}-{video_id}.txt"

    # Check 3-tier downloader
    transcript_text, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(target_dir), info=info)

    if transcript_text:
        text = transcript_text.strip()
    else:
        # Fallback to Whisper
        if not ogg_path:
            # Re-fetch forcing download
            _, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(target_dir), force_audio=True, info=info)

        assert ogg_path and os.path.exists(ogg_path), f"Audio file not found: {ogg_path}"

        detected_lang = None
        if info:
            lang_code = info.get("language")
            if lang_code and isinstance(lang_code, str):
                detected_lang = lang_code.split("-")[0].lower()
            if not detected_lang:
                for source in (info.get("subtitles") or {}, info.get("automatic_captions") or {}):
                    for code in source.keys():
                        code_short = code.split("-")[0].lower()
                        if code_short in ("pt", "en"):
                            detected_lang = code_short
                            break
                    if detected_lang:
                        break

        print(f"Transcribing audio file with Whisper (model: {model_name}, language: {detected_lang or 'auto'})...")
        result = transcribe_audio_to_text(ogg_path, model_name=model_name, language=detected_lang)
        text = result.get("text", "").strip()

        # Clean up
        if not keep_audio:
            try:
                os.remove(ogg_path)
                print("Cleaned up OGG file.")
            except Exception as e:
                print(f"Warning: Failed to delete OGG file: {e}")

    # Save the text
    assert len(text) > 0, "No text extracted."
    desc = info.get("description") or ""
    desc_indented = "\n".join("  " + l for l in desc.splitlines())
    
    yaml_header = f"""---
video_title: "{info.get('title', 'Unknown Title').replace('"', '\\"')}"
video_id: {video_id}
channel_name: "{info.get('channel', 'Unknown Channel').replace('"', '\\"')}"
channel_id: {info.get('channel_id', 'unknown_channel')}
channel_category: "{category.replace('"', '\\"')}"
url: {url}
video_date: {upload_date}
video_description: |
{desc_indented}
---"""

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(yaml_header + "\n" + text)
    # print(f"Saved text to: {txt_path}")

    return {
        "text": text,
        "video_title": info.get("title", "Unknown Title"),
        "video_id": video_id,
        "channel_name": info.get("channel", "Unknown Channel"),
        "channel_category": category,
        "channel_id": info.get("channel_id", "unknown_channel"),
        "url": url,
        "video_description": desc,
        "upload_date": upload_date,
    }

def audio_worker(audio_q: queue.Queue) -> None:
    """Worker thread processing audio downloads and Whisper transcriptions in parallel."""
    while True:
        item = audio_q.get()
        if item is None:
            audio_q.task_done()
            break

        (
            url,
            output_dir,
            model_name,
            keep_audio,
            info,
            csv_path,
            actual_channel_id,
        ) = item

        video_id = info.get("id", "unknown_video") if info else "unknown_video"
        title = info.get("title", "Unknown Title") if info else "Unknown Title"
        categories = info.get("categories") if info else None
        category = categories[0] if categories else "uncategorized"
        channel = info.get("channel") or info.get("uploader") or "unknown_channel" if info else "unknown_channel"
        upload_date = get_full_upload_date(info) if info else ""
        date_str = format_date_for_path(upload_date)

        target_dir = output_dir / channel
        target_dir.mkdir(parents=True, exist_ok=True)
        txt_path = target_dir / f"{date_str}-{video_id}.txt"

        print(f"  [AUDIO WORKER START] Downloading & transcribing '{title[:30]}...' ({video_id})...")
        try:
            _, ogg_path, _ = get_youtube_audio_or_transcript(
                url, output_dir=str(target_dir), force_audio=True, info=info
            )
            if not ogg_path or not os.path.exists(ogg_path):
                print(f"  [AUDIO WORKER ERROR] Audio file not created for {video_id}")
                continue

            detected_lang = None
            if info:
                lang_code = info.get("language")
                if lang_code and isinstance(lang_code, str):
                    detected_lang = lang_code.split("-")[0].lower()
                if not detected_lang:
                    for source in (info.get("subtitles") or {}, info.get("automatic_captions") or {}):
                        for code in source.keys():
                            code_short = code.split("-")[0].lower()
                            if code_short in ("pt", "en"):
                                detected_lang = code_short
                                break
                        if detected_lang:
                            break

            result = transcribe_audio_to_text(ogg_path, model_name=model_name, language=detected_lang)
            text = result.get("text", "").strip()

            if not keep_audio:
                try:
                    os.remove(ogg_path)
                except Exception as e:
                    print(f"  [AUDIO WORKER WARNING] Failed to delete OGG file: {e}")

            if text:
                desc = info.get("description") or "" if info else ""
                desc_indented = "\n".join("  " + l for l in desc.splitlines())

                yaml_header = f"""---
video_title: "{title.replace('"', '\\"')}"
video_id: {video_id}
channel_name: "{channel.replace('"', '\\"')}"
channel_id: {actual_channel_id}
channel_category: "{category.replace('"', '\\"')}"
url: {url}
video_date: {upload_date}
video_description: |
{desc_indented}
---"""
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(yaml_header + "\n" + text)

                record_synced_video(csv_path, actual_channel_id, video_id, upload_date, title=title)
                print(f"  ✓ [AUDIO WORKER SUCCESS] {upload_date} | {actual_channel_id} {video_id} | {title[:40]}...")
            else:
                print(f"  [AUDIO WORKER ERROR] Empty transcription for {video_id}")
        except Exception as e:
            print(f"  [AUDIO WORKER ERROR] Failed processing {video_id}: {e}")
        finally:
            audio_q.task_done()


def process_and_compile_video(
    url: str,
    output_dir: Path,
    csv_path: Path,
    model_name: str,
    keep_audio: bool,
    llm_model: str,
    ollama_url: str,
    channel_id: str | None,
    synced_ids: set[str],
    info: dict | None = None,
    audio_queue: queue.Queue | None = None
) -> dict:
    """Process video: download JSON subtitle immediately; if unavailable, push to audio queue for parallel processing."""
    if not info:
        info = extract_video_metadata(url, use_cookies=False)
    if not info or not info.get("id"):
        return {}
    video_id = info.get("id", "unknown_video")
    actual_channel_id = channel_id or info.get("channel_id", "unknown_channel")

    categories = info.get("categories")
    category = categories[0] if categories else "uncategorized"
    channel = info.get("channel") or info.get("uploader") or "unknown_channel"
    upload_date = get_full_upload_date(info)
    date_str = format_date_for_path(upload_date)

    target_dir = output_dir / channel
    target_dir.mkdir(parents=True, exist_ok=True)
    txt_path = target_dir / f"{date_str}-{video_id}.txt"

    # Fast path: Try JSON subtitles without blocking for audio
    transcript_text, _, _ = get_youtube_audio_or_transcript(
        url, output_dir=str(target_dir), info=info, download_audio_if_missing=False
    )

    if transcript_text:
        text = transcript_text.strip()
        desc = info.get("description") or ""
        desc_indented = "\n".join("  " + l for l in desc.splitlines())

        yaml_header = f"""---
video_title: "{info.get('title', 'Unknown Title').replace('"', '\\"')}"
video_id: {video_id}
channel_name: "{channel.replace('"', '\\"')}"
channel_id: {actual_channel_id}
channel_category: "{category.replace('"', '\\"')}"
url: {url}
video_date: {upload_date}
video_description: |
{desc_indented}
---"""
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(yaml_header + "\n" + text)

        record_synced_video(csv_path, actual_channel_id, video_id, upload_date, title=info.get("title", "Unknown Title"))
        with SYNCED_IDS_LOCK:
            synced_ids.add(video_id)
        print(f"  ✓ [JSON FETCHED] {upload_date} | {actual_channel_id} {video_id} | {info.get('title', 'Unknown Title')[:40]}...")
        return {"video_id": video_id, "status": "json_fetched"}

    # Fallback path: Enqueue to Audio Queue if audio_queue is active
    with SYNCED_IDS_LOCK:
        synced_ids.add(video_id)
    if audio_queue is not None:
        print(f"  ➔ [ENQUEUED FOR AUDIO] {video_id} ('{info.get('title', 'Unknown Title')[:30]}...')")
        audio_queue.put((
            url,
            output_dir,
            model_name,
            keep_audio,
            info,
            csv_path,
            actual_channel_id,
        ))
        return {"video_id": video_id, "status": "enqueued_for_audio"}
    else:
        # Fallback inline processing if audio_queue is None
        res = sync_single_video(url, output_dir, model_name, keep_audio, info=info)
        if res and "video_id" in res:
            record_synced_video(csv_path, actual_channel_id, res["video_id"], res["upload_date"], title=res["video_title"])
            print(f"{res['upload_date']} | {actual_channel_id} {res['video_id']} | {res['video_title'][:40]}...")
        return res


def sync_channels_and_seeds(
    days: int,
    output_dir: Path,
    model_name: str,
    keep_audio: bool,
    playlist_urls: list[str],
    csv_path: Path,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434",
    max_workers: int = 32
) -> None:
    """Core synchronization execution flow with parallel channel scanning, streaming video processing, and incremental caching."""
    # Ensure fresh, authenticated cookies exist before dispatching parallel jobs
    ensure_cookies(max_age_hours=12, verbose=True)

    synced_ids, synced_channels = load_historical_metadata(output_dir, csv_path=csv_path, max_workers=max_workers)
    with QUEUED_IDS_LOCK:
        QUEUED_IDS.clear()
    channels_to_scan = set(synced_channels)
    cache_path = Path(__file__).parent / "channel_cache.json"
    cached_channels = load_channel_cache(cache_path)
    if cached_channels:
        print(f"Loaded {len(cached_channels)} channel(s) from disk cache ({cache_path.name}).")

    # Start background audio queue worker
    audio_queue = queue.Queue()
    worker_thread = threading.Thread(target=audio_worker, args=(audio_queue,), daemon=True)
    worker_thread.start()

    # Shared thread pool for streaming video processing
    video_executor = ThreadPoolExecutor(max_workers=max_workers)

    def _submit_candidate_video(chan_id: str, entry: dict) -> None:
        entry_id = entry.get("id")
        if not entry_id:
            return

        with SYNCED_IDS_LOCK:
            if entry_id in synced_ids:
                return

        with QUEUED_IDS_LOCK:
            if entry_id in QUEUED_IDS:
                return
            QUEUED_IDS.add(entry_id)

        def _process_task():
            entry_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry_id}"
            if not entry_url.startswith("http"):
                entry_url = f"https://www.youtube.com/watch?v={entry_id}"
            entry_date = get_full_upload_date(entry)

            info = None
            if not entry_date:
                try:
                    info = extract_video_metadata(entry_url)
                    entry_date = get_full_upload_date(info)
                except Exception as e:
                    print(f"  Warning: Failed to fetch metadata to resolve date for {entry_id}: {e}")
                    return

            if info and (info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming")):
                return

            if not is_within_range(entry_date, days):
                return

            try:
                process_and_compile_video(
                    url=entry_url,
                    output_dir=output_dir,
                    csv_path=csv_path,
                    model_name=model_name,
                    keep_audio=keep_audio,
                    llm_model=llm_model,
                    ollama_url=ollama_url,
                    channel_id=chan_id,
                    synced_ids=synced_ids,
                    info=info,
                    audio_queue=audio_queue,
                )
            except Exception as e:
                print(f"  Error syncing video {entry_id}: {e}")

        video_executor.submit(_process_task)

    try:
        # 1. Process seed URLs in parallel
        def _process_seed_url(url: str) -> None:
            url_id = extract_youtube_video_id(url)
            with SYNCED_IDS_LOCK:
                if url_id and url_id in synced_ids:
                    return
            try:
                info = extract_video_metadata(url)
            except Exception as e:
                print(f"Error fetching metadata for seed URL {url}: {e}")
                return

            channel_id = info.get("channel_id")
            if channel_id:
                with CHANNELS_TO_SCAN_LOCK:
                    channels_to_scan.add(channel_id)

            video_id = info.get("id")
            with SYNCED_IDS_LOCK:
                if not video_id or video_id in synced_ids:
                    return

            if info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming"):
                print(f"Skipping seed video {video_id}: live stream in progress or upcoming.")
                return

            try:
                process_and_compile_video(
                    url=url,
                    output_dir=output_dir,
                    csv_path=csv_path,
                    model_name=model_name,
                    keep_audio=keep_audio,
                    llm_model=llm_model,
                    ollama_url=ollama_url,
                    channel_id=channel_id,
                    synced_ids=synced_ids,
                    info=info,
                    audio_queue=audio_queue,
                )
            except Exception as e:
                print(f"Error syncing seed video {video_id}: {e}")

        if playlist_urls:
            max_seed_workers = min(max_workers, max(1, len(playlist_urls)))
            with ThreadPoolExecutor(max_workers=max_seed_workers) as seed_executor:
                list(seed_executor.map(_process_seed_url, playlist_urls))

        # 2. Immediately stream cached candidate videos into video_executor
        cached_dispatched = 0
        for cid, entries in cached_channels.items():
            for entry in entries:
                entry_id = entry.get("id")
                if entry_id and entry_id not in synced_ids:
                    _submit_candidate_video(cid, entry)
                    cached_dispatched += 1
        if cached_dispatched > 0:
            print(f"Dispatched {cached_dispatched} candidate video(s) from disk cache for immediate processing.")

        # 3. Scan all unique channels in parallel, streaming entries & saving cache incrementally
        safe_limit = max(50, days * 30)
        chan_list = sorted(channels_to_scan)
        total_channels = len(chan_list)
        print(f"Syncing {total_channels} channels concurrently (max_workers={max_workers})...")

        completed_channels = 0
        count_lock = threading.Lock()

        def _fetch_channel(chan_id: str) -> tuple[str, list[dict]]:
            nonlocal completed_channels
            try:
                entries = fetch_channel_recent_videos(chan_id, limit=safe_limit)
                with count_lock:
                    completed_channels += 1
                    print(f"  [{completed_channels}/{total_channels}] Channel {chan_id}: {len(entries)} video(s) found")
                return chan_id, entries
            except Exception as e:
                with count_lock:
                    completed_channels += 1
                    print(f"  [{completed_channels}/{total_channels}] Error fetching channel {chan_id}: {e}")
                return chan_id, []

        with ThreadPoolExecutor(max_workers=max_workers) as chan_executor:
            print('skip syncing channel videos')
            # future_to_cid = {chan_executor.submit(_fetch_channel, cid): cid for cid in chan_list}
            # for future in as_completed(future_to_cid):
            #     cid, entries = future.result()
            #     if entries:
            #         update_channel_cache(cache_path, cid, entries)
            #         for entry in entries:
            #             _submit_candidate_video(cid, entry)

        # 4. Wait for all submitted video processing tasks to complete
        video_executor.shutdown(wait=True)

    finally:
        if not audio_queue.empty():
            print(f"\n[QUEUE] Waiting for {audio_queue.qsize()} background audio download/transcription task(s) to finish...")
        audio_queue.join()
        audio_queue.put(None)
        worker_thread.join()
        print("[QUEUE] Parallel JSON download & Audio transcription queue finished.")

def bulk_compile_historical_transcripts(
    csv_path: Path,
    output_dir: Path,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434"
) -> None:
    """Scan the Markdown log file and compile any unprocessed video transcripts into Obsidian notes."""
    if not csv_path.exists():
        print(f"No historical sync log found at {csv_path}. Nothing to compile.")
        return

    print(f"Scanning {csv_path.name} for transcripts to compile...")

    wiki_dir = output_dir.parent / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    sources_dir = wiki_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    try:
        with open(csv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                if "---" in line:
                    continue
                if "Channel ID" in line:
                    continue
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 3:
                    title = parts[3] if len(parts) >= 4 else "Unknown Title"
                    rows.append((parts[0], parts[1], parts[2], title))
    except Exception as e:
        print(f"Error reading log table: {e}")
        return

    print(f"Found {len(rows)} entries in sync log.")
    compiled_count = 0

    for channel_id, video_id, upload_date, title in rows:
        source_note_path = sources_dir / f"{video_id}.md"
        if source_note_path.exists():
            continue

        # Look for the video_id in the monthly merged files
        txt_path = None
        target_block = None

        # Check output_dir first (which now has monthly files)
        for txt_file in output_dir.rglob("*.txt"):
            blocks = parse_merged_transcriptions(txt_file)
            for block in blocks:
                if block.get("metadata", {}).get("video_id") == video_id:
                    txt_path = txt_file
                    target_block = block
                    break
            if txt_path:
                break

        if not txt_path:
            # Check old single-video download files as fallback
            txt_path_alt = output_dir.parent.parent / "downloads" / f"{video_id}.txt"
            if txt_path_alt.exists():
                txt_path = txt_path_alt
                single_blocks = parse_merged_transcriptions(txt_path_alt)
                if single_blocks:
                    target_block = single_blocks[0]

        if not txt_path or not target_block:
            print(f"Warning: Transcript text file for {video_id} not found in {output_dir.name}. Skipping.")
            continue

        meta = target_block.get("metadata", {})
        text_only = target_block.get("text", "")

        if not text_only:
            print(f"Warning: Transcript {txt_path} is empty. Skipping.")
            continue

        if title == "Unknown Title" or not title:
            print(f"Fetching title for video {video_id} to compile note...")
            channel = "Unknown Channel"
            try:
                info = extract_video_metadata(f"https://www.youtube.com/watch?v={video_id}")
                title = info.get("title", "Unknown Title")
                channel = info.get("channel", "Unknown Channel")
            except Exception as e:
                print(f"Warning: Could not fetch metadata for {video_id}: {e}. Using placeholders.")
        else:
            channel = meta.get("channel_name") or "Unknown Channel"

        res = {
            "text": text_only,
            "video_title": meta.get("video_title") or title or "Unknown Title",
            "video_id": meta.get("video_id") or video_id,
            "channel_name": meta.get("channel_name") or channel or "Unknown Channel",
            "channel_id": meta.get("channel_id") or channel_id or "unknown_channel",
            "upload_date": meta.get("upload_date") or upload_date or "",
        }

        success = process_transcript_to_obsidian(
            res,
            model=llm_model,
            ollama_url=ollama_url,
            output_dir=wiki_dir
        )
        if success:
            compiled_count += 1

    print(f"\nBulk compilation finished. Successfully compiled {compiled_count} new notes.")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="YouTube Channel Video Syncer - Sync videos in a date range."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days range of videos to sync (default: 7)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to save output files (default: './downloads')."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="Whisper model name to use for fallback: tiny, base, etc. (default: 'tiny')."
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded OGG audio file if Whisper runs."
    )
    parser.add_argument(
        "--playlist",
        type=str,
        default=str(PLAYLIST_FILE),
        help="Path to playlist seed URLs text file."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(CSV_FILE),
        help="Path to CSV persistence log."
    )
    parser.add_argument(
        "--ollama-model",
        type=str,
        default="gemma4:e2b",
        help="Ollama model to use for Obsidian note generation (default: 'gemma4:e2b')."
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL (default: 'http://localhost:11434')."
    )
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Run bulk compilation on all historical synced transcripts without downloading new videos."
    )

    args = parser.parse_args()
    output_path = Path(args.output_dir)

    if args.compile_only:
        bulk_compile_historical_transcripts(
            csv_path=Path(args.csv),
            output_dir=output_path,
            llm_model=args.ollama_model,
            ollama_url=args.ollama_url
        )
    else:
        playlist_path = Path(args.playlist)
        playlist_urls = read_playlist_urls(playlist_path)
        sync_channels_and_seeds(
            days=args.days,
            output_dir=output_path,
            model_name=args.model,
            keep_audio=args.keep_audio,
            playlist_urls=playlist_urls,
            csv_path=Path(args.csv),
            llm_model=args.ollama_model,
            ollama_url=args.ollama_url
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSync process aborted by user.")
        sys.exit(1)
