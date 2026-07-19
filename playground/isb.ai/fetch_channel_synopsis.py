#!/usr/bin/env python3
"""Fetch and print channel descriptions (synopses) from playlist2.txt."""

import re
from pathlib import Path
import yt_dlp

PLAYLIST2_FILE = Path("playground/isb.ai/playlist2.txt")
LIMIT = 5

def get_channel_description(video_url: str) -> dict:
    """Fetch channel ID and metadata (synopsis/description) using yt-dlp."""
    ydl_opts_flat = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
        video_info = ydl.extract_info(video_url, download=False)
        channel_id = video_info.get("channel_id") or video_info.get("uploader_id")
        channel_name = video_info.get("channel") or video_info.get("uploader")
        
    if not channel_id:
        raise ValueError("Could not extract channel ID from video URL.")
        
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    ydl_opts_chan = {
        "quiet": True,
        "no_warnings": True,
        "playlistend": 0,
    }
    with yt_dlp.YoutubeDL(ydl_opts_chan) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False, process=False)
        return {
            "channel_name": channel_name,
            "channel_id": channel_id,
            "subscribers": channel_info.get("channel_follower_count"),
            "description": channel_info.get("description") or "No description provided.",
        }

def main():
    if not PLAYLIST2_FILE.exists():
        print(f"Error: {PLAYLIST2_FILE} not found.")
        return

    with open(PLAYLIST2_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    block_pattern = re.compile(r'#\s*([^\n]+)\n([^\n]+)')
    channels = []
    for match in block_pattern.finditer(content):
        channels.append((match.group(1).strip(), match.group(2).strip()))

    print(f"Loaded {len(channels)} channels from {PLAYLIST2_FILE.name}")
    print(f"Retrieving synopsis for first {LIMIT} channels...\n")

    for i, (name, url) in enumerate(channels[:LIMIT], start=1):
        print(f"[{i}/{LIMIT}] Querying Channel: '{name}'")
        try:
            info = get_channel_description(url)
            print(f"  Channel:     {info['channel_name']} ({info['channel_id']})")
            if info['subscribers']:
                try:
                    subs_formatted = f"{int(info['subscribers']):,}"
                    print(f"  Subscribers: {subs_formatted}")
                except Exception:
                    print(f"  Subscribers: {info['subscribers']}")
            print("  Synopsis:")
            desc_lines = info["description"].strip().split("\n")
            for line in desc_lines[:10]:
                print(f"    {line}")
            if len(desc_lines) > 10:
                print("    ...")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        print("-" * 60)

if __name__ == "__main__":
    main()
