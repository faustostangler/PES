"""
Utility script to incrementally batch git stage and commit raw transcriptions
without freezing IDE UI, hitting HTTP 500 push body limits or GitHub 100MB file limit.
Fast Python globbing for .txt and .md text files.
"""
import subprocess
import sys
import time
from pathlib import Path

ISB_ROOT = Path(__file__).parent.resolve()
CRESMO_ROOT = ISB_ROOT.parent / "cresmo"
RAW_DIR = CRESMO_ROOT / "raw"
REPO_ROOT = ISB_ROOT.parent.parent
LOCK_FILE = REPO_ROOT / ".git" / "index.lock"


def clear_stale_lock() -> None:
    """Remove index.lock if it exists."""
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass


def run_git_command(args: list[str], max_retries: int = 5) -> subprocess.CompletedProcess:
    """Executes a git command with lock retry logic."""
    for attempt in range(max_retries):
        res = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)
        if "index.lock" in res.stderr and attempt < max_retries - 1:
            time.sleep(0.3)
            clear_stale_lock()
            continue
        return res
    return res


def sync_raw_in_batches(batch_size: int = 10, push: bool = False) -> None:
    """Stages and commits raw transcriptions channel by channel."""
    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR} does not exist.")
        return

    subdirs = sorted([d for d in RAW_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(subdirs)} channel directories in raw.")

    committed_count = 0
    batch_count = 0

    for idx, channel_dir in enumerate(subdirs, 1):
        clear_stale_lock()

        # Find all .txt and .md transcript files under this channel
        txt_files = list(channel_dir.rglob("*.txt")) + list(channel_dir.rglob("*.md"))
        if not txt_files:
            continue

        rel_files = [str(f.relative_to(REPO_ROOT)) for f in txt_files]

        # Stage files in chunks of 500 to avoid OS CLI argument limits
        chunk_size = 500
        for i in range(0, len(rel_files), chunk_size):
            file_chunk = rel_files[i:i + chunk_size]
            run_git_command(["git", "add"] + file_chunk)

        # Check if anything is staged for this channel
        rel_channel = str(channel_dir.relative_to(REPO_ROOT))
        diff_res = run_git_command(["git", "diff", "--cached", "--name-only", "--", rel_channel])
        staged_files = [f for f in diff_res.stdout.splitlines() if f.strip()]

        if staged_files:
            msg = f"sync(raw): add {len(staged_files)} transcriptions for '{channel_dir.name}'"
            commit_res = run_git_command(["git", "commit", "-m", msg])
            if commit_res.returncode == 0:
                print(f"[{idx}/{len(subdirs)}] Committed {len(staged_files)} files for '{channel_dir.name}'")
                committed_count += 1
                batch_count += 1
            else:
                print(f"  [{idx}/{len(subdirs)}] Commit error for '{channel_dir.name}': {commit_res.stderr.strip()}")

        if push and batch_count >= batch_size:
            print("--> Pushing batch to remote...")
            push_res = run_git_command(["git", "push", "origin", "main"])
            if push_res.returncode == 0:
                print("--> Batch push successful!")
                batch_count = 0
            else:
                print(f"--> Push warning/error: {push_res.stderr.strip()}")

    if push and batch_count > 0:
        print("--> Final push to remote...")
        run_git_command(["git", "push", "origin", "main"])

    print(f"\nDone! Processed {len(subdirs)} channels. Created {committed_count} new commits.")


if __name__ == "__main__":
    push_flag = "--push" in sys.argv
    sync_raw_in_batches(batch_size=10, push=push_flag)
