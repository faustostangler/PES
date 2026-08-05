"""
Pushes commits to origin main in small batches of N commits
to avoid payload limits and VS Code execution crashes.
Includes network retry logic and commit size calculation.
"""
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def get_commit_size(chunk_commits: list[str]) -> str:
    """Calculates human-readable total size of changed objects in chunk."""
    try:
        parent = f"{chunk_commits[0]}^"
        target = chunk_commits[-1]

        diff_res = subprocess.run(
            ["git", "diff-tree", "-r", "--no-commit-id", parent, target],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        if diff_res.returncode != 0:
            diff_res = subprocess.run(
                ["git", "diff-tree", "-r", "--no-commit-id", "--root", target],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )

        shas = [
            line.split()[3]
            for line in diff_res.stdout.splitlines()
            if len(line.split()) >= 4 and line.split()[3] != "0" * 40
        ]
        if not shas:
            return "0 B"

        cat_res = subprocess.run(
            ["git", "cat-file", "--batch-check=%(objectsize)"],
            cwd=REPO_ROOT,
            input="\n".join(shas),
            capture_output=True,
            text=True
        )
        total_bytes = sum(int(s) for s in cat_res.stdout.splitlines() if s.strip().isdigit())

        size = float(total_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    except Exception:
        return "N/A"


def push_commits_in_batches(batch_size: int = 1) -> None:
    res = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "origin/main..HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        print(f"Error getting git log: {res.stderr}")
        return

    commits = [c.strip() for c in res.stdout.splitlines() if c.strip()]
    if not commits:
        print("Everything is up to date! Nothing to push.")
        return

    print(f"Total commits ahead of origin/main: {len(commits)}")
    total_batches = (len(commits) + batch_size - 1) // batch_size

    for i in range(0, len(commits), batch_size):
        chunk = commits[i:i + batch_size]
        target_commit = chunk[-1]
        batch_num = (i // batch_size) + 1
        size_str = get_commit_size(chunk)

        pushed_ok = False
        for attempt in range(1, 4):
            push_res = subprocess.run(
                ["git", "push", "origin", f"{target_commit}:refs/heads/main"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )
            if push_res.returncode == 0:
                print(f"[{batch_num}/{total_batches}] committed {target_commit} ({size_str})")
                pushed_ok = True
                break
            else:
                print(f"  Warning (attempt {attempt}/3): {push_res.stderr.strip()}")
                time.sleep(2)

        if not pushed_ok:
            print(f"  ✗ Failed pushing batch {batch_num}. Stopping.")
            break

    print("Done batch pushing!")


if __name__ == "__main__":
    b_size = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    push_commits_in_batches(b_size)
