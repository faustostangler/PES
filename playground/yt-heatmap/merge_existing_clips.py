#!/usr/bin/env python3
"""
Temporary migration script:
Merge all individual heatmap clips into a single video per (channel, video_title),
re-compiled at 50% speed (2x duration) with the format:
    channel_dir / f"{video_title}_{resolution}.mp4"
Removes individual source clips upon successful merge and updates SQLite database.
"""

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "heatmap_pipeline.sqlite"
SMB_TARGET = Path(
    f"/run/user/{os.getuid()}/gvfs/smb-share:server=files.local,share=public/Fausto Stangler/Documentos/Videos/yt-heatmap/clips_harvested"
)
LOCAL_TARGET = BASE_DIR / "clips_harvested"


def is_clip_intact(file_path: Path, max_desync_sec: float = 3.0) -> bool:
    """Validate that media file exists, has valid video stream, and is not truncated."""
    if not file_path.exists() or file_path.stat().st_size < 1024:
        return False
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,duration",
            "-of", "json",
            str(file_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return False
        data = json.loads(res.stdout)
        streams = data.get("streams", [])
        v_dur = next(
            (float(s["duration"]) for s in streams if s.get("codec_type") == "video" and "duration" in s),
            None,
        )
        a_dur = next(
            (float(s["duration"]) for s in streams if s.get("codec_type") == "audio" and "duration" in s),
            None,
        )
        if v_dur is None:
            return False
        if a_dur is not None and (a_dur - v_dur) > max_desync_sec:
            return False
        return True
    except Exception:
        return False


def has_audio_stream(video_path: Path) -> bool:
    """Check if the media file contains an audio stream."""
    try:
        res = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return "audio" in res.stdout
    except Exception:
        return True


def merge_and_slowdown_clips(
    clip_paths: List[Path],
    output_path: Path,
    speed_factor: float = 0.5,
) -> bool:
    """Concatenate video clips and re-compile at 50% speed (2x duration)."""
    if not clip_paths:
        return False

    valid_clips = [c for c in clip_paths if c.exists() and c.stat().st_size > 0]
    if not valid_clips:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pts_factor = round(1.0 / speed_factor, 4)
    atempo = round(speed_factor, 4)
    has_audio = has_audio_stream(valid_clips[0])

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for c in valid_clips:
            esc = str(c.resolve()).replace("'", "'\\''")
            f.write(f"file '{esc}'\n")
        concat_file = Path(f.name)

    # Encode to local /tmp file first to maximize throughput and avoid network latency
    local_temp = Path(tempfile.gettempdir()) / f"merged_{output_path.name}"
    if local_temp.exists():
        try:
            local_temp.unlink()
        except Exception:
            pass

    if has_audio:
        filter_complex = f"[0:v]setpts={pts_factor}*PTS[v];[0:a]atempo={atempo}[a]"
        map_args = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_complex = f"[0:v]setpts={pts_factor}*PTS[v]"
        map_args = ["-map", "[v]"]

    # Attempt 1: NVIDIA NVENC Hardware Accelerated (CUDA)
    cmd_nvenc = [
        "ffmpeg", "-y",
        "-hwaccel", "cuda",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-filter_complex", filter_complex,
        *map_args,
        "-c:v", "h264_nvenc", "-preset", "p1", "-cq", "21", "-pix_fmt", "yuv420p",
    ]
    if has_audio:
        cmd_nvenc.extend(["-c:a", "aac", "-b:a", "192k"])
    cmd_nvenc.append(str(local_temp))

    success = False
    try:
        r = subprocess.run(cmd_nvenc, capture_output=True, text=True, timeout=1800)
        if r.returncode == 0 and local_temp.exists() and local_temp.stat().st_size > 0:
            success = True
        else:
            # Fallback Attempt 2: CPU libx264
            cmd_cpu = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_file),
                "-filter_complex", filter_complex,
                *map_args,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
            ]
            if has_audio:
                cmd_cpu.extend(["-c:a", "aac", "-b:a", "192k"])
            cmd_cpu.append(str(local_temp))
            r2 = subprocess.run(cmd_cpu, capture_output=True, text=True, timeout=3600)
            if r2.returncode == 0 and local_temp.exists() and local_temp.stat().st_size > 0:
                success = True
    except Exception as e:
        print(f" [!] Error running ffmpeg: {e}")
    finally:
        concat_file.unlink(missing_ok=True)

    if success and local_temp.exists() and is_clip_intact(local_temp):
        try:
            shutil.move(str(local_temp), str(output_path))
            return True
        except Exception as e:
            print(f" [!] Error moving {local_temp} -> {output_path}: {e}")
            return False
    else:
        if local_temp.exists():
            local_temp.unlink(missing_ok=True)
        return False


def main():
    root_dir = SMB_TARGET if SMB_TARGET.exists() else LOCAL_TARGET
    print(f"[*] Starting migration on root directory: {root_dir}")

    # Connect to SQLite
    conn = None
    clip_start_times: Dict[str, float] = {}
    if DB_PATH.exists():
        conn = sqlite3.connect(f"file:{DB_PATH.resolve()}?nolock=1", uri=True)
        with conn:
            cursor = conn.execute("SELECT file_path, start_time FROM clips WHERE file_path IS NOT NULL")
            for fp, st in cursor.fetchall():
                if fp and st is not None:
                    clip_start_times[str(Path(fp))] = float(st)
                    clip_start_times[Path(fp).name] = float(st)

    # Clean up leftover .part files
    for part in root_dir.glob("*/*.part"):
        try:
            part.unlink(missing_ok=True)
            print(f" [i] Cleaned up partial download artifact: {part.name}")
        except Exception:
            pass

    # Pattern: <video_title>_clip_<rank>_<res>.mp4
    pat = re.compile(r"^(.*)_clip_(\d+)_(\d+p)\.mp4$")

    all_clip_files = list(root_dir.glob("*/*_clip_*.mp4"))
    print(f"[*] Found {len(all_clip_files)} total clip(s) to process.")

    groups: Dict[Tuple[Path, str, str], List[Tuple[int, Path]]] = defaultdict(list)
    for c in all_clip_files:
        m = pat.match(c.name)
        if m:
            v_title, rank_str, res = m.group(1), m.group(2), m.group(3)
            groups[(c.parent, v_title, res)].append((int(rank_str), c))
        else:
            print(f" [!] Unrecognized clip naming pattern: {c.name}")

    total_groups = len(groups)
    print(f"[*] Grouped into {total_groups} unique video(s) to merge.\n")

    videos_merged = 0
    clips_deleted = 0
    errors_encountered = 0
    start_time_all = time.time()

    for idx, ((channel_dir, v_title, res), clip_items) in enumerate(groups.items(), start=1):
        target_path = channel_dir / f"{v_title}_{res}.mp4"
        print(f"[{idx}/{total_groups}] {channel_dir.name} / {v_title[:60]} ({len(clip_items)} clips, {res}):")

        # Sort clips chronologically by start_time (fallback to rank)
        def get_sort_key(item: Tuple[int, Path]) -> float:
            rank, path = item
            if str(path) in clip_start_times:
                return clip_start_times[str(path)]
            if path.name in clip_start_times:
                return clip_start_times[path.name]
            return float(rank)

        sorted_clips = sorted(clip_items, key=get_sort_key)
        clip_paths = [c for _, c in sorted_clips]

        # Check if merged video already exists and is intact
        if target_path.exists() and is_clip_intact(target_path):
            print(f"    [i] Merged video already exists and intact: {target_path.name}")
            ok = True
        else:
            t0 = time.time()
            ok = merge_and_slowdown_clips(clip_paths, target_path, speed_factor=0.5)
            elapsed = time.time() - t0
            if ok:
                print(f"    [✓] Merged & slowed down to 50% speed in {elapsed:.1f}s -> {target_path.name}")
            else:
                print(f"    [!] Failed to merge clips for: {v_title}")
                errors_encountered += 1
                continue

        # If successfully merged, update SQLite and delete source clips
        if ok and target_path.exists() and is_clip_intact(target_path):
            videos_merged += 1
            if conn:
                with conn:
                    for _, cp in sorted_clips:
                        conn.execute(
                            "UPDATE clips SET file_path = ? WHERE file_path = ? OR file_path LIKE ?",
                            (str(target_path), str(cp), f"%/{cp.name}"),
                        )
            for _, cp in sorted_clips:
                try:
                    cp.unlink(missing_ok=True)
                    clips_deleted += 1
                except Exception as e:
                    print(f"    [!] Could not delete source clip {cp.name}: {e}")

    if conn:
        conn.commit()
        conn.close()

    total_elapsed = time.time() - start_time_all
    print("\n" + "=" * 70)
    print(" MIGRATION AND MERGE COMPLETE")
    print("=" * 70)
    print(f" Total Videos Merged:    {videos_merged}/{total_groups}")
    print(f" Source Clips Deleted:   {clips_deleted}/{len(all_clip_files)}")
    print(f" Errors Encountered:     {errors_encountered}")
    print(f" Total Elapsed Time:     {total_elapsed/60:.1f} minutes")
    print("=" * 70)


if __name__ == "__main__":
    main()
