"""
Utility script to incrementally batch git stage and commit raw transcriptions
without freezing IDE UI or hitting HTTP 500 push body limits.
"""
import subprocess
import sys
from pathlib import Path

ISB_ROOT = Path(__file__).parent.resolve()
RAW_DIR = ISB_ROOT / "raw"
REPO_ROOT = ISB_ROOT.parent.parent


def sync_raw_in_batches(batch_size: int = 10, push: bool = True) -> None:
    """Stages and commits raw transcriptions channel by channel."""
    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR} does not exist.")
        return

    subdirs = sorted([d for d in RAW_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(subdirs)} channel directories in raw.")

    committed_count = 0
    batch_count = 0

    for idx, channel_dir in enumerate(subdirs, 1):
        rel_path = channel_dir.relative_to(REPO_ROOT)
        print(f"[{idx}/{len(subdirs)}] {rel_path}")
        # Stage directory
        res = subprocess.run(
            ["git", "add", str(rel_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            print(f"  Warning: git add failed for {channel_dir.name}: {res.stderr}")
            continue

        # Check if anything is staged for this path
        diff_res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", str(rel_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        staged_files = [f for f in diff_res.stdout.splitlines() if f.strip()]

        if staged_files:
            msg = f"sync(raw): add {len(staged_files)} transcriptions for '{channel_dir.name}'"
            commit_res = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )
            if commit_res.returncode == 0:
                print(f"  Committed {len(staged_files)} files for '{channel_dir.name}'")
                committed_count += 1
                batch_count += 1
            else:
                print(f"  Commit error for {channel_dir.name}: {commit_res.stderr.strip()}")

        if push and batch_count >= batch_size:
            print("--> Pushing batch to remote...")
            push_res = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )
            if push_res.returncode == 0:
                print("--> Batch push successful!")
                batch_count = 0
            else:
                print(f"--> Push warning/error: {push_res.stderr.strip()}")

    if push and batch_count > 0:
        print("--> Final push to remote...")
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT)

    print(f"Done! Processed {len(subdirs)} channels. Created {committed_count} new commits.")


if __name__ == "__main__":
    push_flag = "--push" in sys.argv
    sync_raw_in_batches(batch_size=10)
