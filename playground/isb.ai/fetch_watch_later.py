#!/usr/bin/env python3
import os
import yt_dlp

PLAYLIST_FILE = "playground/isb.ai/playlist_later.txt"
PLAYLIST2_FILE = "playground/isb.ai/playlist2.txt"

def main():
    print("Extracting Watch Later playlist URLs using Chrome cookies...")
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        # The Watch Later playlist ("WL") is private to the user's Google account
        # and strictly requires authentication cookies.
        "cookiesfrombrowser": ("chrome",),
    }
    
    url = "https://www.youtube.com/playlist?list=WL"
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            playlist_info = ydl.extract_info(url, download=False)
            if not playlist_info:
                print("Failed to retrieve playlist info.")
                return
            
            entries = [e for e in playlist_info.get("entries", []) if e]
            print(f"Found {len(entries)} videos in Watch Later.")
            
            urls_to_append = []
            seen_channels = set()
            channel_first_videos = []
            
            for entry in entries:
                v_id = entry.get("id")
                if not v_id:
                    continue
                
                video_url = f"https://www.youtube.com/watch?v={v_id}"
                urls_to_append.append(video_url)
                
                # Channel classification & deduplication
                chan_name = entry.get("uploader") or entry.get("channel") or "Unknown Channel"
                chan_key = (entry.get("uploader_id") or entry.get("channel_id") or chan_name).lower()
                
                if chan_key not in seen_channels:
                    seen_channels.add(chan_key)
                    channel_first_videos.append((chan_name, video_url))
            
            # Save all URLs to playlist_later.txt
            if urls_to_append:
                os.makedirs(os.path.dirname(PLAYLIST_FILE), exist_ok=True)
                file_exists = os.path.exists(PLAYLIST_FILE)
                with open(PLAYLIST_FILE, "a", encoding="utf-8") as f:
                    if file_exists:
                        f.write("\n")
                    f.write("# Watch Later Sync\n")
                    for item_url in urls_to_append:
                        f.write(f"{item_url}\n")
                print(f"Successfully appended {len(urls_to_append)} URLs to {PLAYLIST_FILE}")
            
            # Save first video per channel to playlist2.txt
            if channel_first_videos:
                os.makedirs(os.path.dirname(PLAYLIST2_FILE), exist_ok=True)
                with open(PLAYLIST2_FILE, "w", encoding="utf-8") as f2:
                    for chan_name, item_url in channel_first_videos:
                        f2.write(f"# {chan_name}\n")
                        f2.write(f"{item_url}\n\n")
                print(f"Successfully wrote first video of each channel to {PLAYLIST2_FILE}")
            else:
                print("No videos found to append.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
