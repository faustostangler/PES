#!/usr/bin/env python3
"""
Temporary migration script:
Merge all individual heatmap clips into a single video per (channel, video_title),
re-compiled at 50% speed (2x duration) with the format:
    channel_dir / f"{video_title}_{resolution}.mp4"
Removes individual source clips upon successful merge and updates SQLite database.
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "heatmap_pipeline.sqlite"
SMB_TARGET = Path(
    f"/run/user/{os.getuid()}/gvfs/smb-share:server=files.local,share=public/Fausto Stangler/Documentos/Videos/yt-heatmap/clips_harvested"
)
LOCAL_TARGET = BASE_DIR / "clips_harvested"


def resolve_temp_dir(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve scratch temporary directory prioritizing custom parameter, environment variable, or /mnt/gamer_d."""
    if custom_path:
        p = Path(custom_path)
    elif "HEATMAP_TEMP_DIR" in os.environ and os.environ["HEATMAP_TEMP_DIR"].strip():
        p = Path(os.environ["HEATMAP_TEMP_DIR"].strip())
    elif Path("/mnt/gamer_d/tmp/yt-heatmap").exists() or Path("/mnt/gamer_d").exists():
        p = Path("/mnt/gamer_d/tmp/yt-heatmap")
    else:
        p = Path(tempfile.gettempdir()) / "yt-heatmap"
    p.mkdir(parents=True, exist_ok=True)
    return p


DEFAULT_TEMP_DIR = resolve_temp_dir()


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


def format_time(sec: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    s = max(0, int(sec))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_video_duration(file_path: Path) -> float:
    """Quickly probe video container duration in seconds."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(file_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def run_ffmpeg_with_progress(
    cmd: List[str],
    expected_duration_sec: float = 0.0,
    label: str = "NVENC",
    timeout: int = 1800,
) -> Tuple[int, str]:
    """
    Execute ffmpeg command with real-time ETA, speed, and percentage progress bar.
    Reads progress events via '-progress pipe:1 -nostats'.
    """
    # Build command with progress options
    full_cmd = [cmd[0], "-y", "-progress", "pipe:1", "-nostats"] + [a for a in cmd[1:] if a != "-y"]

    t0 = time.time()
    stderr_lines: List[str] = []
    curr_sec = 0.0
    speed_val = 0.0
    fps_val = 0.0

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
    except Exception as e:
        return -1, str(e)

    def read_stderr():
        if proc.stderr:
            for line in proc.stderr:
                stderr_lines.append(line.strip())

    t_err = threading.Thread(target=read_stderr, daemon=True)
    t_err.start()

    try:
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k == "out_time_us" and v.isdigit():
                    curr_sec = int(v) / 1_000_000.0
                elif k == "speed":
                    s_str = v.rstrip("x").strip()
                    try:
                        speed_val = float(s_str)
                    except ValueError:
                        pass
                elif k == "fps":
                    try:
                        fps_val = float(v)
                    except ValueError:
                        pass
                elif k == "progress" and v in ("continue", "end"):
                    pct = min(99.9, (curr_sec / expected_duration_sec) * 100.0) if expected_duration_sec > 0 else 0.0
                    rem_sec = max(0.0, expected_duration_sec - curr_sec)
                    eta_sec = (rem_sec / speed_val) if speed_val > 0 else 0.0
                    filled = int(pct / 5)
                    bar = "█" * filled + "░" * (20 - filled)
                    speed_display = f"{speed_val:.1f}x" if speed_val > 0 else "..."
                    fps_display = f" ({int(fps_val)} fps)" if fps_val > 0 else ""
                    dur_display = (
                        f"{format_time(curr_sec)}/{format_time(expected_duration_sec)}"
                        if expected_duration_sec > 0
                        else format_time(curr_sec)
                    )
                    eta_display = (
                        f" | ETA: {format_time(eta_sec)}"
                        if (expected_duration_sec > 0 and speed_val > 0)
                        else ""
                    )

                    sys.stdout.write(
                        f"\r        [{label}] [{bar}] {pct:5.1f}% | {dur_display} | {speed_display}{fps_display}{eta_display}   "
                    )
                    sys.stdout.flush()

        proc.wait(timeout=timeout)
        t_err.join(timeout=2.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        sys.stdout.write("\n")
        return -1, "Timed out"
    except Exception as e:
        proc.kill()
        sys.stdout.write("\n")
        return -1, str(e)

    elapsed = time.time() - t0
    avg_speed = (expected_duration_sec / elapsed) if (expected_duration_sec > 0 and elapsed > 0) else speed_val

    if proc.returncode == 0:
        bar = "█" * 20
        dur_display = format_time(expected_duration_sec) if expected_duration_sec > 0 else format_time(curr_sec)
        sys.stdout.write(
            f"\r        [{label}] [{bar}] 100.0% | {dur_display} finished in {elapsed:.1f}s ({avg_speed:.1f}x avg)       \n"
        )
        sys.stdout.flush()
    else:
        sys.stdout.write("\n")

    return proc.returncode, "\n".join(stderr_lines[-10:])


def merge_and_slowdown_clips(
    clip_paths: List[Path],
    output_path: Path,
    speed_factor: float = 0.5,
    temp_dir: Optional[Path] = None,
    expected_duration: Optional[float] = None,
) -> bool:
    """Concatenate video clips and re-compile at 50% speed (2x duration) with real-time ETA progress."""
    if not clip_paths:
        return False

    valid_clips = [c for c in clip_paths if c.exists() and c.stat().st_size > 0]
    if not valid_clips:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pts_factor = round(1.0 / speed_factor, 4)
    atempo = round(speed_factor, 4)
    has_audio = has_audio_stream(valid_clips[0])

    scratch = temp_dir or DEFAULT_TEMP_DIR
    scratch.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=scratch) as f:
        for c in valid_clips:
            esc = str(c.resolve()).replace("'", "'\\''")
            f.write(f"file '{esc}'\n")
        concat_file = Path(f.name)

    # Encode to local scratch temp file first to maximize throughput and avoid network latency
    local_temp = scratch / f"merged_{output_path.name}"
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

    success = False
    try:
        ret, err = run_ffmpeg_with_progress(
            cmd_nvenc,
            expected_duration_sec=expected_duration or 0.0,
            label="NVENC",
            timeout=1800,
        )
        if ret == 0 and local_temp.exists() and local_temp.stat().st_size > 0:
            success = True
        else:
            print(f"        [!] NVENC not available or failed (exit {ret}), falling back to CPU (libx264 veryfast)...")
            ret2, err2 = run_ffmpeg_with_progress(
                cmd_cpu,
                expected_duration_sec=expected_duration or 0.0,
                label="CPU",
                timeout=3600,
            )
            if ret2 == 0 and local_temp.exists() and local_temp.stat().st_size > 0:
                success = True
            else:
                print(f"        [!] CPU ffmpeg failed: {err2}")
    except Exception as e:
        print(f" [!] Error running ffmpeg: {e}")
    finally:
        concat_file.unlink(missing_ok=True)

    if success and local_temp.exists() and is_clip_intact(local_temp):
        try:
            shutil.copyfile(str(local_temp), str(output_path))
            local_temp.unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f" [!] Error copying {local_temp} -> {output_path}: {e}")
            return False
    else:
        if local_temp.exists():
            local_temp.unlink(missing_ok=True)
        return False


def update_clip_paths(db_path: Path, target_path: Path, clip_paths: List[Path]) -> None:
    """Safely update SQLite database file paths with retry logic."""
    for attempt in range(1, 4):
        try:
            with sqlite3.connect(f"file:{db_path.resolve()}?nolock=1", uri=True, timeout=30.0) as c:
                for cp in clip_paths:
                    c.execute(
                        "UPDATE clips SET file_path = ? WHERE file_path = ? OR file_path LIKE ?",
                        (str(target_path), str(cp), f"%/{cp.name}"),
                    )
            return
        except Exception as e:
            if attempt == 3:
                print(f"    [!] Warning: Failed to update SQLite for {target_path.name}: {e}")
            else:
                time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(description="Merge individual clips per video into 50% speed video.")
    parser.add_argument("--temp-dir", default=str(DEFAULT_TEMP_DIR), help=f"Scratch temporary directory (default: {DEFAULT_TEMP_DIR})")
    args = parser.parse_args()
    temp_dir = resolve_temp_dir(args.temp_dir)

    root_dir = SMB_TARGET if SMB_TARGET.exists() else LOCAL_TARGET
    print(f"[*] Starting migration on root directory: {root_dir}")
    print(f"[*] Scratch Temp Directory: {temp_dir}")

    # Read clip start times and durations from SQLite safely
    clip_start_times: Dict[str, float] = {}
    clip_durations: Dict[str, float] = {}
    if DB_PATH.exists():
        try:
            with sqlite3.connect(f"file:{DB_PATH.resolve()}?nolock=1", uri=True, timeout=30.0) as db_conn:
                cursor = db_conn.execute("SELECT file_path, start_time, clip_duration, end_time FROM clips WHERE file_path IS NOT NULL")
                for fp, st, dur, et in cursor.fetchall():
                    if fp:
                        if st is not None:
                            clip_start_times[str(Path(fp))] = float(st)
                            clip_start_times[Path(fp).name] = float(st)
                        d = float(dur) if dur else (float(et) - float(st) if et and st else 0.0)
                        if d > 0:
                            clip_durations[str(Path(fp))] = d
                            clip_durations[Path(fp).name] = d
        except Exception as e:
            print(f" [!] Warning: Could not read clip metadata from SQLite: {e}")

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
            # Estimate expected output duration (at 50% speed, duration is 2x input)
            total_in_sec = sum(
                clip_durations.get(cp.name, 0.0) or clip_durations.get(str(cp), 0.0)
                for cp in clip_paths
            )
            if total_in_sec <= 0:
                total_in_sec = sum(get_video_duration(cp) for cp in clip_paths)
            expected_output_sec = (total_in_sec / 0.5) if total_in_sec > 0 else 0.0

            t0 = time.time()
            ok = merge_and_slowdown_clips(
                clip_paths,
                target_path,
                speed_factor=0.5,
                temp_dir=temp_dir,
                expected_duration=expected_output_sec,
            )
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
            update_clip_paths(DB_PATH, target_path, [cp for _, cp in sorted_clips])
            for _, cp in sorted_clips:
                try:
                    cp.unlink(missing_ok=True)
                    clips_deleted += 1
                except Exception as e:
                    print(f"    [!] Could not delete source clip {cp.name}: {e}")

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
