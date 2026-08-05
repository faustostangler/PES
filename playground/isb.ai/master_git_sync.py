"""
Master Git Sync Script
Handles end-to-end local staging, per-channel committing, and chunked pushing to GitHub.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ISB_ROOT = Path(__file__).parent.resolve()
REPO_ROOT = ISB_ROOT.parent.parent
RAW_DIR = ISB_ROOT / "raw"
LOCK_FILE = REPO_ROOT / ".git" / "index.lock"


def clear_lock() -> None:
    """Removes stale index.lock file if present."""
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass


def run_git(args: list[str], max_retries: int = 5) -> subprocess.CompletedProcess:
    """Executes a git command with lock retry logic."""
    for attempt in range(max_retries):
        clear_lock()
        res = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)
        if "index.lock" in res.stderr and attempt < max_retries - 1:
            time.sleep(0.5)
            continue
        return res
    return res


def get_chunk_size_str(chunk_commits: list[str]) -> str:
    """Calculates human-readable total size of changed objects in commit chunk."""
    try:
        parent = f"{chunk_commits[0]}^"
        target = chunk_commits[-1]
        diff_res = run_git(["git", "diff-tree", "-r", "--no-commit-id", parent, target])
        if diff_res.returncode != 0:
            diff_res = run_git(["git", "diff-tree", "-r", "--no-commit-id", "--root", target])

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


def step1_commit_raw_channels() -> None:
    """Finds and commits all channel text transcripts (.txt and .md) per channel."""
    print("\n--- STEP 1: Staging & Committing Raw Channels ---")
    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR} does not exist.")
        return

    subdirs = sorted([d for d in RAW_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(subdirs)} channel directories in raw.")

    committed = 0
    for idx, channel_dir in enumerate(subdirs, 1):
        clear_lock()

        txt_files = list(channel_dir.rglob("*.txt")) + list(channel_dir.rglob("*.md"))
        if not txt_files:
            continue

        rel_files = [str(f.relative_to(REPO_ROOT)) for f in txt_files]

        chunk_size = 500
        for i in range(0, len(rel_files), chunk_size):
            file_chunk = rel_files[i:i + chunk_size]
            run_git(["git", "add"] + file_chunk)

        rel_channel = str(channel_dir.relative_to(REPO_ROOT))
        diff_res = run_git(["git", "diff", "--cached", "--name-only", "--", rel_channel])
        staged = [f for f in diff_res.stdout.splitlines() if f.strip()]

        if staged:
            msg = f"sync(raw): add {len(staged)} transcriptions for '{channel_dir.name}'"
            res = run_git(["git", "commit", "-m", msg])
            if res.returncode == 0:
                print(f"  [{idx}/{len(subdirs)}] Committed {len(staged)} files for '{channel_dir.name}'")
                committed += 1
            else:
                print(f"  [{idx}/{len(subdirs)}] Commit error for '{channel_dir.name}': {res.stderr.strip()}")

    print(f"Step 1 Complete: Created {committed} channel commits.")


def step2_commit_code_and_skills() -> None:
    """Stages and commits any remaining project files, agent skills, cresmo, enriched, and code."""
    print("\n--- STEP 2: Staging Remaining Code, Skills & Enriched ---")
    clear_lock()

    targets = [
        ".agents/",
        "playground/cresmo/",
        "playground/isb.ai/enriched/",
        "playground/isb.ai/wiki/",
        "playground/isb.ai/*.py",
        ".gitignore",
        "pyproject.toml",
        "uv.lock",
        "projects.md",
    ]

    for t in targets:
        run_git(["git", "add", t])

    diff_res = run_git(["git", "diff", "--cached", "--name-only"])
    staged = [f for f in diff_res.stdout.splitlines() if f.strip()]
    if staged:
        msg = f"feat: sync project code, cresmo pipeline, skills and enriched data ({len(staged)} files)"
        res = run_git(["git", "commit", "-m", msg])
        if res.returncode == 0:
            print(f"  Committed {len(staged)} project and enriched files.")
        else:
            print(f"  Commit error in step 2: {res.stderr.strip()}")
    else:
        print("  No unstaged code/skills/enriched files found.")

    print("Step 2 Complete.")


def step3_push_to_remote(batch_size: int = 1) -> None:
    """Pushes unpushed local commits to GitHub in small chunks."""
    print("\n--- STEP 3: Pushing Commits to GitHub Remote ---")
    clear_lock()

    res = run_git(["git", "log", "--reverse", "--format=%H", "origin/main..HEAD"])
    commits = [c.strip() for c in res.stdout.splitlines() if c.strip()]

    if not commits:
        print("🎉 Everything is already up to date on origin/main!")
        return

    print(f"Total commits to push: {len(commits)}")
    total_batches = (len(commits) + batch_size - 1) // batch_size

    for i in range(0, len(commits), batch_size):
        chunk = commits[i:i + batch_size]
        target = chunk[-1]
        batch_num = (i // batch_size) + 1
        size_str = get_chunk_size_str(chunk)

        pushed_ok = False
        for attempt in range(1, 4):
            clear_lock()
            push_res = run_git(["git", "push", "origin", f"{target}:refs/heads/main"])
            if push_res.returncode == 0:
                print(f"  ✓ [{batch_num}/{total_batches}] Pushed commit {target[:7]} ({size_str})")
                pushed_ok = True
                break
            else:
                print(f"  Warning (attempt {attempt}/3): {push_res.stderr.strip()}")
                time.sleep(2)

        if not pushed_ok:
            print(f"  ✗ Failed pushing batch {batch_num}. Stopping.")
            break

    print("Step 3 Complete.")


def step4_verify() -> None:
    """Verifies final sync state between local and remote."""
    print("\n--- STEP 4: Verification ---")
    res = run_git(["git", "rev-list", "--count", "origin/main..HEAD"])
    count = res.stdout.strip()
    print(f"Commits ahead of origin/main: {count}")
    if count == "0":
        print("✅ SUCCESS: Local and Remote repositories are 100% synchronized!")
    else:
        print(f"⚠️ Notice: {count} local commits remain unpushed.")


if __name__ == "__main__":
    clear_lock()
    step1_commit_raw_channels()
    step2_commit_code_and_skills()
    step3_push_to_remote(batch_size=1)
    step4_verify()
