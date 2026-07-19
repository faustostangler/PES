#!/usr/bin/env python3
"""Fetch channel metadata from video URLs in playlist2.txt using yt-dlp."""

import re
from pathlib import Path
import yt_dlp

PLAYLIST2_FILE = Path("playground/isb.ai/playlist2.txt")
LIMIT = 5  # Limit to first 5 channels for quick demonstration

def extract_channel_info(video_url: str) -> dict:
    """Extract channel info from a video URL using yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        # yt-dlp extracts uploader info from the video metadata
        return {
            "channel_name": info.get("channel") or info.get("uploader"),
            "channel_id": info.get("channel_id") or info.get("uploader_id"),
            "channel_url": info.get("channel_url") or info.get("uploader_url"),
        }

def main():
    if not PLAYLIST2_FILE.exists():
        print(f"Error: {PLAYLIST2_FILE} not found.")
        return

    with open(PLAYLIST2_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse channel blocks from playlist2.txt
    block_pattern = re.compile(r'#\s*([^\n]+)\n([^\n]+)')
    channels = []
    for match in block_pattern.finditer(content):
        channels.append((match.group(1).strip(), match.group(2).strip()))

    print(f"Loaded {len(channels)} channels from {PLAYLIST2_FILE.name}")
    print(f"Querying first {LIMIT} channels...\n")

    for i, (name, url) in enumerate(channels[:LIMIT], start=1):
        print(f"[{i}/{LIMIT}] Querying video: {url} (Channel name in file: '{name}')")
        try:
            info = extract_channel_info(url)
            print(f"  ✓ Real Channel Name: {info['channel_name']}")
            print(f"  ✓ Channel ID:        {info['channel_id']}")
            print(f"  ✓ Channel URL:       {info['channel_url']}")
        except Exception as e:
            print(f"  ✗ Failed to extract info: {e}")
        print()

if __name__ == "__main__":
    main()
