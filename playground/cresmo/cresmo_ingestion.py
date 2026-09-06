#!/usr/bin/env python3
"""Cresmo Stage 1: Raw Transcript Ingestion CLI Script.

Crawls and downloads YouTube transcripts, producing raw transcript files with standard
YAML metadata headers in playground/cresmo/raw/[Channel_Name]/[Video_ID].txt.
"""

import argparse
from pathlib import Path
import sys

# Ensure script directory is in sys.path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))
# Add parent directory if sync_channels is located in playground/isb.ai
ISB_DIR = SCRIPT_DIR.parent / "isb.ai"
if ISB_DIR.exists():
    sys.path.insert(0, str(ISB_DIR))

import downloader
import sync_channels
from cresmo_shared import (
    DEFAULT_BRAIN_CSV,
    DEFAULT_PLAYLIST_FILE,
    DEFAULT_PLAYLIST_PRIORITY_FILE,
    DEFAULT_RATE_LIMIT_LOG_FILE,
    DEFAULT_RAW_DIR,
    read_playlist_urls,
    read_priority_entries,
)

# --- Ingestion Defaults ---
DEFAULT_DAYS: int = 365 * 2
DEFAULT_WHISPER_MODEL: str = "base"
DEFAULT_KEEP_AUDIO: bool = False
DEFAULT_MAX_WORKERS: int = 1


def run_cresmo_ingestion(
    playlist_path: Path = DEFAULT_PLAYLIST_FILE,
    csv_path: Path = DEFAULT_BRAIN_CSV,
    output_dir: Path = DEFAULT_RAW_DIR,
    days: int = DEFAULT_DAYS,
    model_name: str = DEFAULT_WHISPER_MODEL,
    keep_audio: bool = DEFAULT_KEEP_AUDIO,
    max_workers: int = DEFAULT_MAX_WORKERS,
    rate_limit_log_file: Path = DEFAULT_RATE_LIMIT_LOG_FILE,
    priority_playlist: Path | None = DEFAULT_PLAYLIST_PRIORITY_FILE,
) -> None:
    """Execute Stage 1 raw ingestion pipeline."""
    downloader.RATE_LIMIT_LOG_FILE = rate_limit_log_file
    playlist_urls = []
    if playlist_path.exists():
        playlist_urls = read_playlist_urls(playlist_path)

    priority_entries = []
    if priority_playlist:
        priority_entries = read_priority_entries(Path(priority_playlist))

    if not playlist_urls and not priority_entries:
        print(f"[Stage 1 Ingestion] No seed URLs found in {playlist_path} or {priority_playlist}. Exiting.")
        return

    print("==================================================")
    print("🚀 Cresmo Stage 1: Ingesting Raw Transcripts")
    print(f"   Target Channels:    {len(playlist_urls)}")
    if priority_entries:
        playlist_name = Path(priority_playlist).name if priority_playlist else "none"
        print(f"   Priority Videos:    {len(priority_entries)} from {playlist_name}")
    print(f"   Output Directory:   {output_dir}")
    print(f"   Days Limit:         {days}")
    print("==================================================")

    # Ingest standalone priority videos first
    if priority_entries:
        print(f"\n⚡ Ingesting {len(priority_entries)} priority video(s)...")
        for entry in priority_entries:
            vid = entry["video_id"]
            url = entry["url"]
            existing = list(output_dir.glob(f"**/*{vid}*.txt"))
            if existing:
                print(f"  ✓ [Priority Ingestion] Already exists: {vid} -> {existing[0].name}")
                continue
            try:
                print(f"  ⬇️ [Priority Ingestion] Downloading {vid} ({url})...")
                sync_channels.sync_single_video(
                    url=url,
                    output_dir=output_dir,
                    model_name=model_name,
                    keep_audio=keep_audio,
                )
            except Exception as e:
                print(f"  ❌ [Priority Ingestion Error] {vid}: {e}")

    if playlist_urls:
        sync_channels.sync_channels_and_seeds(
            days=days,
            output_dir=output_dir,
            model_name=model_name,
            keep_audio=keep_audio,
            playlist_urls=playlist_urls,
            csv_path=csv_path,
            max_workers=max_workers,
        )
    print("\n✓ Stage 1 Raw Ingestion Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cresmo Stage 1 Ingestion CLI")
    parser.add_argument("--playlist", default=str(DEFAULT_PLAYLIST_FILE), help="Path to playlist seed text file")
    parser.add_argument("--csv", default=str(DEFAULT_BRAIN_CSV), help="Path to brain metadata CSV")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw output directory")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Number of days to search back for uploads")
    parser.add_argument("--model", default=DEFAULT_WHISPER_MODEL, help="Whisper fallback model size")
    parser.add_argument("--keep-audio", action="store_true", default=DEFAULT_KEEP_AUDIO, help="Keep downloaded audio files")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help="Max parallel worker threads")
    parser.add_argument(
        "--priority-playlist",
        default=str(DEFAULT_PLAYLIST_PRIORITY_FILE),
        help="Path to priority playlist text file (default: playground/cresmo/playlist-priority.txt)",
    )

    args = parser.parse_args()

    run_cresmo_ingestion(
        playlist_path=Path(args.playlist),
        csv_path=Path(args.csv),
        output_dir=Path(args.raw_dir),
        days=args.days,
        model_name=args.model,
        keep_audio=args.keep_audio,
        max_workers=args.max_workers,
        priority_playlist=Path(args.priority_playlist) if args.priority_playlist else None,
    )
