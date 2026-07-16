#!/usr/bin/env python3
"""Personalized Disk Cleanup Tool - Custom tailored based on diagnosis_report.md findings."""

import os
import sys
from pathlib import Path

REPORT_PATH = Path(__file__).parent / "diagnosis_report.md"
HOME = Path.home()

def print_header(title: str):
    print("\n" + "=" * 55)
    print(f" {title.center(53)} ")
    print("=" * 55)

def execute_command(cmd: str):
    """Safely run shell command and print outcome."""
    print(f"\nExecuting: {cmd}")
    res = os.system(cmd)
    if res == 0:
        print(">>> Success!")
    else:
        print(f">>> Failed (Exit code: {res})")

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

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def clean_config_caches():
    import shutil
    print("\n--- Scanning and Cleaning Caches in ~/.config ---")
    config_dir = HOME / ".config"
    if not config_dir.exists():
        return
    
    cache_names = {"Cache", "Code Cache", "GPUCache", "CacheStorage", "ScriptCache"}
    total_freed = 0
    
    # Also explicitly target the large OptGuide models in Chrome
    chrome_opt_guide = config_dir / "google-chrome/OptGuideOnDeviceModel"
    if chrome_opt_guide.exists():
        size = get_dir_size(chrome_opt_guide)
        print(f"Deleting Chrome Optimization Guide Models: {chrome_opt_guide.relative_to(HOME)} ({format_size(size)})")
        try:
            shutil.rmtree(chrome_opt_guide)
            total_freed += size
        except Exception as e:
            print(f"Failed to delete {chrome_opt_guide}: {e}")
            
    chrome_classifier = config_dir / "google-chrome/OptGuideOnDeviceClassifierModel"
    if chrome_classifier.exists():
        size = get_dir_size(chrome_classifier)
        print(f"Deleting Chrome Classifier Models: {chrome_classifier.relative_to(HOME)} ({format_size(size)})")
        try:
            shutil.rmtree(chrome_classifier)
            total_freed += size
        except Exception as e:
            print(f"Failed to delete {chrome_classifier}: {e}")

    for root, dirs, files in os.walk(config_dir):
        for d in list(dirs):
            if d in cache_names:
                path = Path(root) / d
                size = get_dir_size(path)
                if size > 10 * 1024 * 1024:  # > 10MB
                    print(f"Deleting cache directory: {path.relative_to(HOME)} ({format_size(size)})")
                    try:
                        shutil.rmtree(path)
                        total_freed += size
                    except Exception as e:
                        print(f"Failed to delete {path}: {e}")
                        
    print(f"Total space freed in .config: {format_size(total_freed)}")

def run_cleanup():
    import shutil
    if not REPORT_PATH.exists():
        print("Error: diagnosis_report.md not found. Please run diagnose.py first.")
        sys.exit(1)

    print_header("STARTING NON-INTERACTIVE CLEANUP")

    # Action 1: Docker (More aggressive - system prune)
    print("\n--- Cleaning Docker Containers, Images, and Volumes ---")
    execute_command("docker system prune -a -f --volumes")

    # Action 2: Whisper Cache
    whisper_dir = HOME / ".cache/whisper"
    if whisper_dir.exists():
        print("\n--- Cleaning Whisper Models Cache ---")
        try:
            size = get_dir_size(whisper_dir)
            shutil.rmtree(whisper_dir)
            print(f"Deleted Whisper cache ({format_size(size)})")
        except Exception as e:
            print(f"Failed to delete Whisper cache: {e}")

    # Action 3: Hugging Face cache
    hf_dir = HOME / ".cache/huggingface"
    if hf_dir.exists():
        print("\n--- Cleaning Hugging Face Cache ---")
        try:
            size = get_dir_size(hf_dir)
            shutil.rmtree(hf_dir)
            print(f"Deleted Hugging Face cache ({format_size(size)})")
        except Exception as e:
            print(f"Failed to delete HF cache: {e}")

    # Action 4: Playwright & Electron caches
    print("\n--- Cleaning Playwright & Electron caches ---")
    electron_cache = HOME / ".cache/electron"
    if electron_cache.exists():
        try:
            shutil.rmtree(electron_cache)
            print("Deleted Electron download cache.")
        except Exception as e:
            print(f"Failed: {e}")
            
    playwright_cache = HOME / ".cache/ms-playwright"
    if playwright_cache.exists():
        try:
            shutil.rmtree(playwright_cache)
            print("Deleted Playwright browsers cache.")
        except Exception as e:
            print(f"Failed: {e}")
            
    playwright_go_cache = HOME / ".cache/ms-playwright-go"
    if playwright_go_cache.exists():
        try:
            shutil.rmtree(playwright_go_cache)
            print("Deleted Playwright Go cache.")
        except Exception as e:
            print(f"Failed: {e}")

    # Action 5: NPM cache (Aggressive - delete directory)
    npm_dir = HOME / ".npm"
    if npm_dir.exists():
        print("\n--- Cleaning NPM Cache ---")
        try:
            size = get_dir_size(npm_dir)
            shutil.rmtree(npm_dir)
            print(f"Deleted NPM directory ({format_size(size)})")
        except Exception as e:
            print(f"Failed to delete NPM directory: {e}")
            execute_command("npm cache clean --force")

    # Action 6: Antigravity IDE optimization models (4 GB!)
    gemini_opt_guide = HOME / ".gemini/antigravity-browser-profile/OptGuideOnDeviceModel"
    if gemini_opt_guide.exists():
        print("\n--- Cleaning Antigravity IDE Browser On-Device Models ---")
        try:
            size = get_dir_size(gemini_opt_guide)
            shutil.rmtree(gemini_opt_guide)
            print(f"Deleted Antigravity browser on-device models ({format_size(size)})")
        except Exception as e:
            print(f"Failed to delete Antigravity browser models: {e}")

    # Action 7: .config Caches (Chrome, Electron apps)
    clean_config_caches()

    # Action 8: Sudo journal logs vacuuming
    print("\n--- Vacuuming Journalctl Logs ---")
    execute_command("sudo journalctl --vacuum-time=2d")

    print_header("CLEANUP COMPLETE")
    print("Cleanup run finished. You can run python3 diagnose.py again to check your freed space.")

if __name__ == "__main__":
    try:
        run_cleanup()
    except KeyboardInterrupt:
        print("\nCleanup aborted.")
        sys.exit(0)
