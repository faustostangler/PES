#!/usr/bin/env python3
"""Comprehensive System & User Disk Cleanup Tool.

Targets:
1. Orphaned temporary media files and directories in /tmp (harvest/merge leftovers).
2. Disabled legacy Snap package revisions in /var/lib/snapd/snaps.
3. Systemd journal log vacuuming.
4. APT archive and dependency cleanup.
5. User profile caches (Chrome, Antigravity IDE recordings, NPM, Whisper).
6. Docker build and image pruning.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Set

HOME = Path.home()
REPORT_PATH = Path(__file__).parent / "diagnosis_report.md"


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string (e.g. 1.25 GB).
    """
    val = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024.0:
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} PB"


def get_dir_size(path: Path) -> int:
    """Recursively calculate directory size in bytes."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                total += get_dir_size(Path(entry.path))
            else:
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def get_open_files_in_tmp() -> Set[str]:
    """Find all open file descriptors targeting /tmp using /proc.

    Returns:
        Set of resolved paths currently held open by active processes.
    """
    open_paths: Set[str] = set()
    proc = Path("/proc")
    try:
        for pid_dir in proc.iterdir():
            if not pid_dir.is_dir() or not pid_dir.name.isdigit():
                continue
            fd_dir = pid_dir / "fd"
            if not fd_dir.exists():
                continue
            try:
                for fd in fd_dir.iterdir():
                    try:
                        target = os.readlink(fd)
                        if target.startswith("/tmp"):
                            open_paths.add(target)
                    except (OSError, FileNotFoundError):
                        pass
            except (PermissionError, FileNotFoundError):
                pass
    except Exception:
        pass
    return open_paths


def clean_tmp_orphans(dry_run: bool = False) -> int:
    """Safely remove orphaned media artifacts and harvest dirs from /tmp.

    Args:
        dry_run: If True, only simulate actions.

    Returns:
        Total bytes freed or reclaimable.
    """
    print("\n--- Scanning and Cleaning Orphaned Media Leftovers in /tmp ---")
    tmp_path = Path("/tmp")
    if not tmp_path.exists():
        return 0

    open_files = get_open_files_in_tmp()
    total_freed = 0

    for entry in os.scandir(tmp_path):
        p = Path(entry.path)
        # Check files
        if p.is_file() and p.suffix.lower() in [".mp4", ".mkv", ".ts", ".webm"]:
            if str(p.resolve()) in open_files:
                print(f"[SKIP - IN USE] {p.name}")
                continue
            size = p.stat().st_size
            total_freed += size
            if dry_run:
                print(f"[WOULD REMOVE] {p.name} ({format_size(size)})")
            else:
                try:
                    p.unlink()
                    print(f"[REMOVED] {p.name} ({format_size(size)})")
                except Exception as e:
                    print(f"[ERROR] Failed removing {p.name}: {e}")

        # Check directories
        elif p.is_dir() and (p.name.startswith("harvest_") or p.name.startswith("tmp")):
            # Check if any file inside directory is open
            is_active = any(str(f.resolve()) in open_files for f in p.glob("**/*") if f.is_file())
            if is_active:
                print(f"[SKIP - DIR IN USE] {p.name}")
                continue
            size = get_dir_size(p)
            if size > 1024 * 1024:  # > 1MB
                total_freed += size
                if dry_run:
                    print(f"[WOULD REMOVE DIR] {p.name} ({format_size(size)})")
                else:
                    try:
                        shutil.rmtree(p)
                        print(f"[REMOVED DIR] {p.name} ({format_size(size)})")
                    except Exception as e:
                        print(f"[ERROR] Failed removing dir {p.name}: {e}")

    print(f"Total /tmp space {'reclaimable' if dry_run else 'freed'}: {format_size(total_freed)}")
    return total_freed


def clean_snap_revisions(dry_run: bool = False) -> None:
    """Remove disabled snap package revisions to reclaim /var/lib/snapd space."""
    print("\n--- Removing Disabled Snap Package Revisions ---")
    try:
        res = subprocess.run(["snap", "list", "--all"], capture_output=True, text=True, check=True)
    except Exception as e:
        print(f"Failed to query snaps: {e}")
        return

    disabled_snaps = []
    for line in res.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 6 and "disabled" in parts[-1]:
            disabled_snaps.append((parts[0], parts[2]))  # name, rev

    if not disabled_snaps:
        print("No disabled snap revisions found.")
        return

    for name, rev in disabled_snaps:
        if dry_run:
            print(f"[WOULD EXECUTE] sudo snap remove '{name}' --revision='{rev}'")
        else:
            print(f"Removing snap revision: {name} (rev {rev})...")
            cmd = f"sudo snap remove '{name}' --revision='{rev}'"
            subprocess.run(cmd, shell=True)


def clean_systemd_journal(dry_run: bool = False) -> None:
    """Vacuum systemd journal logs to retain up to 100MB."""
    print("\n--- Vacuuming Systemd Journal Logs ---")
    if dry_run:
        print("[WOULD EXECUTE] sudo journalctl --vacuum-size=100M")
    else:
        subprocess.run("sudo journalctl --vacuum-size=100M", shell=True)


def clean_apt_cache(dry_run: bool = False) -> None:
    """Clean APT package archives and unused dependencies."""
    print("\n--- Cleaning APT Archives and Autoremoving Unused Packages ---")
    if dry_run:
        print("[WOULD EXECUTE] sudo apt clean && sudo apt autoremove --purge -y")
    else:
        subprocess.run("sudo apt clean && sudo apt autoremove --purge -y", shell=True)


def clean_user_caches(dry_run: bool = False) -> int:
    """Clean Google Chrome, NPM, Whisper, and Antigravity IDE browser recordings."""
    print("\n--- Cleaning User Profile Caches ---")
    total_freed = 0

    # 1. Chrome Cache
    chrome_cache = HOME / ".cache/google-chrome"
    if chrome_cache.exists():
        size = get_dir_size(chrome_cache)
        total_freed += size
        if dry_run:
            print(f"[WOULD REMOVE] Google Chrome Cache: {chrome_cache} ({format_size(size)})")
        else:
            try:
                shutil.rmtree(chrome_cache)
                print(f"[REMOVED] Google Chrome Cache ({format_size(size)})")
            except Exception as e:
                print(f"[ERROR] Failed removing Chrome cache: {e}")

    # 2. Antigravity IDE Browser Recordings
    recordings_dir = HOME / ".gemini/antigravity-ide/browser_recordings"
    if recordings_dir.exists():
        size = get_dir_size(recordings_dir)
        total_freed += size
        if dry_run:
            print(f"[WOULD REMOVE] Browser Recordings: {recordings_dir} ({format_size(size)})")
        else:
            try:
                shutil.rmtree(recordings_dir)
                recordings_dir.mkdir(parents=True, exist_ok=True)
                print(f"[REMOVED] Browser Recordings ({format_size(size)})")
            except Exception as e:
                print(f"[ERROR] Failed removing recordings: {e}")

    # 3. NPM Cache
    npm_dir = HOME / ".npm"
    if npm_dir.exists():
        size = get_dir_size(npm_dir)
        total_freed += size
        if dry_run:
            print(f"[WOULD REMOVE] NPM Cache: {npm_dir} ({format_size(size)})")
        else:
            try:
                shutil.rmtree(npm_dir)
                print(f"[REMOVED] NPM Cache ({format_size(size)})")
            except Exception as e:
                print(f"[ERROR] Failed removing NPM cache: {e}")

    # 4. Whisper Cache
    whisper_dir = HOME / ".cache/whisper"
    if whisper_dir.exists():
        size = get_dir_size(whisper_dir)
        total_freed += size
        if dry_run:
            print(f"[WOULD REMOVE] Whisper Cache: {whisper_dir} ({format_size(size)})")
        else:
            try:
                shutil.rmtree(whisper_dir)
                print(f"[REMOVED] Whisper Cache ({format_size(size)})")
            except Exception as e:
                print(f"[ERROR] Failed removing Whisper cache: {e}")

    print(f"Total user caches {'reclaimable' if dry_run else 'freed'}: {format_size(total_freed)}")
    return total_freed


def main() -> None:
    """Parse CLI options and execute targeted cleanup."""
    parser = argparse.ArgumentParser(description="Comprehensive Disk Cleanup Tool.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate cleanup without deleting files.")
    parser.add_argument("--all", action="store_true", help="Perform all cleanups (tmp, user, system, snaps).")
    parser.add_argument("--tmp", action="store_true", help="Clean orphaned /tmp video files and harvest directories.")
    parser.add_argument("--user", action="store_true", help="Clean user caches (Chrome, NPM, IDE recordings, Whisper).")
    parser.add_argument("--system", action="store_true", help="Vacuum journal logs and clean APT cache (requires sudo).")
    parser.add_argument("--snaps", action="store_true", help="Remove disabled snap package revisions (requires sudo).")

    args = parser.parse_args()

    # If no specific flags, default to showing dry-run plan
    if not (args.all or args.tmp or args.user or args.system or args.snaps):
        print("No target specified. Running dry-run simulation of safe user targets (--tmp, --user)...")
        clean_tmp_orphans(dry_run=True)
        clean_user_caches(dry_run=True)
        print("\nTo execute actual cleanup, specify flags:")
        print("  python3 clean.py --tmp      (Clean orphaned videos in /tmp without sudo)")
        print("  python3 clean.py --user     (Clean Chrome/NPM/IDE caches without sudo)")
        print("  python3 clean.py --system   (Vacuum journal & clean APT archives with sudo)")
        print("  python3 clean.py --snaps    (Remove disabled snap revisions with sudo)")
        print("  python3 clean.py --all      (Execute all cleanup phases)")
        return

    if args.all or args.tmp:
        clean_tmp_orphans(dry_run=args.dry_run)

    if args.all or args.user:
        clean_user_caches(dry_run=args.dry_run)

    if args.all or args.system:
        clean_systemd_journal(dry_run=args.dry_run)
        clean_apt_cache(dry_run=args.dry_run)

    if args.all or args.snaps:
        clean_snap_revisions(dry_run=args.dry_run)

    print("\nCleanup cycle completed. Run python3 diagnose.py to verify updated disk space.")


if __name__ == "__main__":
    main()
