#!/usr/bin/env python3
"""Multi-threaded script to fetch synopses for all channels in playlist2.txt and save to playlist2_content.txt."""

import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

PLAYLIST2_FILE = Path("playground/isb.ai/playlist2.txt")
OUTPUT_FILE = Path("playground/isb.ai/playlist2_content.txt")
MAX_WORKERS = 12

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
            "description": (channel_info.get("description") or "No description provided.").strip(),
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

    total = len(channels)
    print(f"Starting fetch for {total} channels using {MAX_WORKERS} workers...")

    results = [None] * total  # Keep ordering same as playlist2.txt
    
    def worker(index, name, url):
        try:
            info = get_channel_description(url)
            return index, info, None
        except Exception as e:
            return index, None, str(e)

    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(worker, idx, name, url): idx for idx, (name, url) in enumerate(channels)}
        for fut in as_completed(futures):
            idx, info, err = fut.result()
            results[idx] = (channels[idx][0], channels[idx][1], info, err)
            completed += 1
            if completed % 10 == 0 or completed == total:
                print(f"Progress: {completed}/{total} channels fetched...")

    # Write to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for idx, (name, url, info, err) in enumerate(results):
            f_out.write(f"# {name}\n")
            f_out.write(f"URL: {url}\n")
            if err:
                f_out.write(f"Status: ERROR ({err})\n")
            elif info:
                f_out.write(f"Channel Name: {info['channel_name']}\n")
                f_out.write(f"Channel ID:   {info['channel_id']}\n")
                if info['subscribers']:
                    try:
                        subs_val = int(info['subscribers'])
                        f_out.write(f"Subscribers:  {subs_val:,}\n")
                    except Exception:
                        f_out.write(f"Subscribers:  {info['subscribers']}\n")
                f_out.write("Synopsis:\n")
                # Format description with indentation
                for line in info["description"].splitlines():
                    f_out.write(f"  {line}\n")
            f_out.write("\n" + "="*80 + "\n\n")

    print(f"\nDone! Successfully saved all synopses to {OUTPUT_FILE.name}")

if __name__ == "__main__":
    main()
