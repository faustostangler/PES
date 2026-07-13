#!/usr/bin/env python3
"""YouTube Channel Video Syncer script.

Downloads new videos uploaded within the last X days from channels listed in playlist.txt.
Maintains idempotency via a Markdown log file.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yt_dlp

from downloader import extract_video_metadata, get_youtube_audio_or_transcript
from helper import get_full_upload_date, is_within_range, read_playlist_urls, sanitize_for_path, format_date_for_path, parse_yaml_header, clean_filename, parse_merged_transcriptions, extract_youtube_video_id
from ollama_processor import process_transcript_to_obsidian
from transcriber import transcribe_audio_to_text

# --- Configs ---
PLAYLIST_FILE = Path(__file__).parent / "playlist.txt"
CSV_FILE = Path(__file__).parent / "wiki" / "log.md"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "raw"

def load_historical_metadata(output_dir: Path) -> tuple[set[str], set[str]]:
    """Load previously synced video IDs and channel IDs by recursively scanning all
    *.txt files in the output directory and reading their YAML headers.

    Returns:
        tuple[set[str], set[str]]: A tuple containing (synced_ids, synced_channels)
    """
    synced_ids = set()
    synced_channels = set()
    if output_dir.exists():
        try:
            for txt_file in output_dir.rglob("*.txt"):
                blocks = parse_merged_transcriptions(txt_file)
                for block in blocks:
                    meta = block.get("metadata", {})
                    v_id = meta.get("video_id")
                    c_id = meta.get("channel_id")
                    if v_id:
                        synced_ids.add(v_id)
                    if c_id:
                        synced_channels.add(c_id)
        except Exception as e:
            print(f"Warning: Failed to load historical metadata from {output_dir.name}: {e}")
    return synced_ids, synced_channels

def record_synced_video(log_path: Path, channel_id: str, video_id: str, upload_date: str, title: str = "Unknown Title") -> None:
    """Record a successfully synced video in the Markdown log table."""
    file_exists = log_path.exists()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("# Ingestion Log\n\n")
                f.write("| Channel ID | Video ID | Upload Date | Title |\n")
                f.write("| --- | --- | --- | --- |\n")
            clean_title = title.replace("|", "\\|")
            f.write(f"| {channel_id} | {video_id} | {upload_date} | {clean_title} |\n")
        # print(f"Recorded video {video_id} in {log_path.name}")
    except Exception as e:
        print(f"Error saving to Markdown log: {e}")

def fetch_channel_recent_videos(channel_id: str, limit: int = 50) -> list[dict]:
    """Query recent videos from a channel using its uploads playlist ID."""
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
        "playlistend": limit,
        "extract_flat": True,
        "extractor_args": {"youtubetab": {"approximate_date": [""]}},
        "ignoreerrors": True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            playlist_info = ydl.extract_info(url, download=False)
            if playlist_info:
                # Filter out None values from failed extractions
                entries = [e for e in playlist_info.get("entries", []) if e]
                return entries
        except Exception as e:
            print(f"Error fetching channel playlist: {e}")
    return []

def sync_single_video(url: str, output_dir: Path, model_name: str, keep_audio: bool, info: dict | None = None) -> dict:
    """Process a single video using the 3-tier fallback model (JSON3 -> SRV1 -> Whisper OGG).

    Returns a dict containing:
        - text: the transcript text
        - title: the video title
        - video_id: the video ID
        - upload_date: the upload date (ISO or YYYYMMDD)
        - channel: the channel name
        - channel_id: the channel ID
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch metadata first
    if not info:
        info = extract_video_metadata(url)
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
    year_month = date_str[:7] if len(date_str) >= 7 and date_str[4] == "-" else "unknown_month"
    txt_path = target_dir / f"{channel} - {year_month}.txt"

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
        print(f"Transcribing audio file with Whisper (model: {model_name})...")
        result = transcribe_audio_to_text(ogg_path, model_name=model_name)
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

    file_exists = txt_path.exists() and txt_path.stat().st_size > 0
    mode = "a" if file_exists else "w"

    with open(txt_path, mode, encoding="utf-8") as f:
        if file_exists:
            f.write("\n\n" + yaml_header + "\n" + text)
        else:
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
    info: dict | None = None
) -> dict:
    """Download, transcribe, log, and compile a YouTube video to Obsidian."""
    res = sync_single_video(url, output_dir, model_name, keep_audio, info=info)
    actual_channel_id = channel_id or res["channel_id"]

    # Record to ingestion log
    record_synced_video(csv_path, actual_channel_id, res["video_id"], res["upload_date"], title=res["video_title"])
    synced_ids.add(res["video_id"])

    res["channel_id"] = actual_channel_id

    print(f"{res['upload_date']} | {actual_channel_id} {res['video_id']} | {res['video_title'][:40]}...")

    # # Compile to Obsidian Note inside wiki/
    # process_transcript_to_obsidian(
    #     res,
    #     model=llm_model,
    #     ollama_url=ollama_url,
    #     output_dir=output_dir.parent / "wiki"
    # )
    return res

def sync_channels_and_seeds(
    days: int,
    output_dir: Path,
    model_name: str,
    keep_audio: bool,
    playlist_urls: list[str],
    csv_path: Path,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434"
) -> None:
    """Core synchronization execution flow."""
    # 1. Load synced video IDs and historical channels
    synced_ids, synced_channels = load_historical_metadata(output_dir)
    # print(f"Loaded {len(synced_ids)} synced video IDs and {len(synced_channels)} synced channel IDs.")

    channels_to_scan = set(synced_channels)

    # 2. Process seed URLs and add their channels to our list
    for url in playlist_urls:
        url_id = extract_youtube_video_id(url)
        if not url_id:
            continue
        if url_id in synced_ids:
            continue

        try:
            info = extract_video_metadata(url)
        except Exception as e:
            print(f"Error fetching metadata for seed URL {url}: {e}")
            continue

        channel_id = info.get("channel_id")
        upload_date = get_full_upload_date(info)
        print(f"{upload_date} | {channel_id} {url_id} | {info.get('title')}")

        if channel_id:
            channels_to_scan.add(channel_id)

        # Process the seed video itself if it is not yet synced
        video_id = info.get("id")
        if not video_id:
            continue
        if video_id in synced_ids:
            continue
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
                info=info
            )
        except Exception as e:
            print(f"Error syncing seed video {video_id}: {e}")

    # 4. Scan all unique channels (both seed channels and historical ones)
    # print(f"\nScanning total of {len(channels_to_scan)} channels for new uploads...")
    safe_limit = max(50, days * 30)
    for chan_id in channels_to_scan:
        recent_entries = fetch_channel_recent_videos(chan_id, limit=safe_limit)
        found = False

        for entry in recent_entries:
            entry_date = get_full_upload_date(entry)
            entry_id = entry.get("id")

            if not entry_id:
                continue
            if not is_within_range(entry_date, days):
                continue
            if entry_id in synced_ids:
                continue

            entry_url = entry.get("url")
            # if not found:
            #     print(f"Found new videos on the channel {chan_id}.")
            found = True
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
                    synced_ids=synced_ids
                )
            except Exception as e:
                print(f"  Error syncing video {entry_id}: {e}")

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
