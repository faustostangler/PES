#!/usr/bin/env python3
"""Comprehensive Disk Space Diagnosis Tool.

Audits root partition, swapfile allocation, temporary media artifacts,
snap revisions, system journals, apt caches, and user profile caches.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

HOME = Path.home()
EXCLUDE_DIR = HOME / "gamer_d"
REPORT_PATH = Path(__file__).parent / "diagnosis_report.md"


def get_dir_size(path: Path) -> int:
    """Recursively calculate directory size in bytes, skipping symlinks and exclusions.

    Args:
        path: Path to target directory.

    Returns:
        Total size in bytes.
    """
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            entry_path = Path(entry.path)
            if entry_path == EXCLUDE_DIR:
                continue
            if entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry_path)
            else:
                total += entry.stat().st_size
    except (PermissionError, FileNotFoundError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format.

    Args:
        size_bytes: Raw size in bytes.

    Returns:
        Human-readable formatted string (e.g. 1.25 GB).
    """
    val = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024.0:
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} PB"


def audit_system_partitions() -> str:
    """Query partition usage for root and user partitions."""
    try:
        res = subprocess.run(["df", "-h", "/", "/home"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return f"Error executing df: {e}"


def audit_swap() -> Tuple[str, int]:
    """Inspect swap allocation and identify swapfile size."""
    swap_file = Path("/swap.img")
    size_bytes = 0
    status_lines = []
    if swap_file.exists():
        try:
            size_bytes = swap_file.stat().st_size
            status_lines.append(f"- `/swap.img` file size: **{format_size(size_bytes)}**")
        except Exception as e:
            status_lines.append(f"- `/swap.img` stat error: {e}")
    try:
        res = subprocess.run(["swapon", "--show"], capture_output=True, text=True)
        if res.stdout.strip():
            status_lines.append("```text\n" + res.stdout.strip() + "\n```")
    except Exception:
        pass
    return "\n".join(status_lines), size_bytes


def audit_tmp_media() -> Tuple[List[str], int]:
    """Scan /tmp for orphaned large video files and directories."""
    tmp_path = Path("/tmp")
    items: List[str] = []
    total_bytes = 0

    if not tmp_path.exists():
        return items, total_bytes

    try:
        for entry in os.scandir(tmp_path):
            p = Path(entry.path)
            if p.is_file() and p.suffix.lower() in [".mp4", ".mkv", ".ts", ".webm"]:
                size = p.stat().st_size
                if size > 10 * 1024 * 1024:  # > 10MB
                    total_bytes += size
                    items.append(f"- `{p.name}`: **{format_size(size)}**")
            elif p.is_dir() and (p.name.startswith("harvest_") or p.name.startswith("tmp")):
                size = get_dir_size(p)
                if size > 10 * 1024 * 1024:
                    total_bytes += size
                    items.append(f"- Directory `{p.name}`: **{format_size(size)}**")
    except Exception as e:
        items.append(f"Error auditing /tmp: {e}")

    return items, total_bytes


def audit_snap_revisions() -> Tuple[List[str], int]:
    """Identify disabled/old snap packages consuming space."""
    lines: List[str] = []
    total_bytes = 0
    try:
        res = subprocess.run(["snap", "list", "--all"], capture_output=True, text=True)
        disabled_snaps = []
        for line in res.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6 and "disabled" in parts[-1]:
                disabled_snaps.append((parts[0], parts[2]))  # name, rev

        snaps_dir = Path("/var/lib/snapd/snaps")
        if snaps_dir.exists():
            for name, rev in disabled_snaps:
                snap_file = snaps_dir / f"{name}_{rev}.snap"
                if snap_file.exists():
                    size = snap_file.stat().st_size
                    total_bytes += size
                    lines.append(f"- `{snap_file.name}` (disabled): **{format_size(size)}**")
                else:
                    lines.append(f"- Snap `{name}` rev `{rev}` (disabled)")
    except Exception as e:
        lines.append(f"Could not audit snap packages: {e}")
    return lines, total_bytes


def audit_system_caches() -> Dict[str, str]:
    """Inspect systemd journals, apt archives, and flatpak."""
    results = {}

    # 1. Systemd Journal
    journal_path = Path("/var/log/journal")
    if journal_path.exists():
        results["Systemd Journal (`/var/log/journal`)"] = format_size(get_dir_size(journal_path))
    else:
        results["Systemd Journal (`/var/log/journal`)"] = "Not Found"

    # 2. APT Cache
    apt_cache = Path("/var/cache/apt/archives")
    if apt_cache.exists():
        results["APT Package Cache (`/var/cache/apt/archives`)"] = format_size(get_dir_size(apt_cache))
    else:
        results["APT Package Cache"] = "Not Found"

    # 3. Flatpak system runtimes
    flatpak_dir = Path("/var/lib/flatpak")
    if flatpak_dir.exists():
        results["Flatpak Runtimes (`/var/lib/flatpak`)"] = format_size(get_dir_size(flatpak_dir))

    return results


def run_diagnosis() -> None:
    """Execute complete system and home directory audit and save report."""
    print("Starting comprehensive disk space diagnosis...")
    report = []
    report.append("# Comprehensive Disk Space Diagnosis Report")
    report.append(f"Generated on: {os.popen('date').read().strip()}")
    report.append(f"Target: System `/` and `{HOME}` (Excluding: `{EXCLUDE_DIR}`)\n")

    # 1. Partition usage
    report.append("## 1. Partition Disk Usage")
    report.append(f"```text\n{audit_system_partitions()}\n```\n")

    # 2. Swapfile
    swap_info, swap_bytes = audit_swap()
    report.append("## 2. Swapfile Memory Allocation")
    report.append(swap_info)
    if swap_bytes > 16 * 1024 * 1024 * 1024:
        report.append(
            "> [!WARNING]\n"
            f"> `/swap.img` is currently allocating **{format_size(swap_bytes)}** on the root SSD.\n"
            "> For a 116 GB root drive, this consumes ~28% of total storage. Reducing or moving swap can free 16-24 GB.\n"
        )
    report.append("")

    # 3. Temporary Media Leftovers in /tmp
    tmp_items, tmp_bytes = audit_tmp_media()
    report.append("## 3. Temporary Media Artifacts in `/tmp`")
    report.append(f"**Total space trapped in `/tmp`:** **{format_size(tmp_bytes)}**\n")
    if tmp_items:
        report.extend(tmp_items[:20])
    else:
        report.append("_No large temporary media files found in `/tmp`._")
    report.append("")

    # 4. Snap Disabled Revisions
    snap_items, snap_bytes = audit_snap_revisions()
    report.append("## 4. Inactive Snap Package Revisions (`/var/lib/snapd/snaps`)")
    report.append(f"**Reclaimable space from disabled snap revisions:** **{format_size(snap_bytes)}**\n")
    if snap_items:
        report.extend(snap_items)
    else:
        report.append("_No disabled snap revisions found._")
    report.append("")

    # 5. System Caches (Journal, APT)
    report.append("## 5. System Level Caches")
    sys_caches = audit_system_caches()
    for name, size_str in sys_caches.items():
        report.append(f"- **{name}**: **{size_str}**")
    report.append("")

    # 6. User Profile Caches
    report.append("## 6. User Profile & Development Caches")
    user_caches = {
        "Google Chrome Cache": HOME / ".cache/google-chrome",
        "Antigravity IDE Conversations": HOME / ".gemini/antigravity-ide/conversations",
        "Antigravity IDE Browser Recordings": HOME / ".gemini/antigravity-ide/browser_recordings",
        "Antigravity Browser Profile": HOME / ".gemini/antigravity-browser-profile",
        "NPM Cache": HOME / ".npm",
        "UV Cache": HOME / ".local/share/uv",
        "Hugging Face Cache": HOME / ".cache/huggingface",
        "Whisper Cache": HOME / ".cache/whisper",
        "Steam Data & Shaders": HOME / ".local/share/Steam",
        "Standard ~/.cache Folder": HOME / ".cache",
    }
    for name, path in user_caches.items():
        if path.exists():
            report.append(f"- **{name}** (`{path}`): **{format_size(get_dir_size(path))}**")
        else:
            report.append(f"- **{name}** (`{path}`): _Not Found_")
    report.append("")

    # 7. Top Subdirectories in Home
    report.append("## 7. Top 12 Largest Home Subdirectories (excluding gamer_d)")
    dir_sizes = []
    try:
        for entry in os.scandir(HOME):
            entry_path = Path(entry.path)
            if entry_path == EXCLUDE_DIR or entry_path.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                size = get_dir_size(entry_path)
                dir_sizes.append((entry_path, size))
    except Exception as e:
        report.append(f"Error listing subdirectories: {e}")

    dir_sizes.sort(key=lambda x: x[1], reverse=True)
    for path, size in dir_sizes[:12]:
        report.append(f"- `{path.relative_to(HOME)}`: **{format_size(size)}**")
    report.append("")

    # Write report
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        print(f"\nDiagnosis complete. Report saved to: {REPORT_PATH}")
    except Exception as e:
        print(f"Error saving report: {e}")


if __name__ == "__main__":
    run_diagnosis()
