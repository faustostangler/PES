#!/usr/bin/env python3
"""Cresmo Stage 1: Raw Transcript Ingestion CLI Script.

Crawls and downloads YouTube transcripts, producing raw transcript files with standard
YAML metadata headers in playground/cresmo/raw/[Channel_Name]/[Video_ID].txt.
"""

import argparse
import sys
from pathlib import Path

# Ensure script directory is in sys.path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))
# Add parent directory if sync_channels is located in playground/isb.ai
ISB_DIR = SCRIPT_DIR.parent / "isb.ai"
if ISB_DIR.exists():
    sys.path.insert(0, str(ISB_DIR))

import sync_channels
from cresmo_shared import (
    CRESMO_ROOT,
    DEFAULT_RAW_DIR,
    read_playlist_urls,
)


def run_cresmo_ingestion(
    playlist_path: Path = CRESMO_ROOT / "playlist.txt",
    csv_path: Path = CRESMO_ROOT / "brain.csv",
    output_dir: Path = DEFAULT_RAW_DIR,
    days: int = 30,
    model_name: str = "base",
    keep_audio: bool = False,
    max_workers: int = 1,
) -> None:
    """Execute Stage 1 raw ingestion pipeline."""
    playlist_urls = []
    if playlist_path.exists():
        playlist_urls = read_playlist_urls(playlist_path)

    if not playlist_urls:
        print(f"[Stage 1 Ingestion] No seed URLs found in {playlist_path}. Exiting.")
        return

    print(f"==================================================")
    print(f"🚀 Cresmo Stage 1: Ingesting Raw Transcripts")
    print(f"   Target Channels: {len(playlist_urls)}")
    print(f"   Output Directory: {output_dir}")
    print(f"   Days Limit: {days}")
    print(f"==================================================")

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
    parser.add_argument("--playlist", default=str(CRESMO_ROOT / "playlist.txt"), help="Path to playlist seed text file")
    parser.add_argument("--csv", default=str(CRESMO_ROOT / "brain.csv"), help="Path to brain metadata CSV")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw output directory")
    parser.add_argument("--days", type=int, default=30, help="Number of days to search back for uploads")
    parser.add_argument("--model", default="base", help="Whisper fallback model size")
    parser.add_argument("--keep-audio", action="store_true", help="Keep downloaded audio files")
    parser.add_argument("--max-workers", type=int, default=1, help="Max parallel worker threads")

    args = parser.parse_args()

    run_cresmo_ingestion(
        playlist_path=Path(args.playlist),
        csv_path=Path(args.csv),
        output_dir=Path(args.raw_dir),
        days=args.days,
        model_name=args.model,
        keep_audio=args.keep_audio,
        max_workers=args.max_workers,
    )
