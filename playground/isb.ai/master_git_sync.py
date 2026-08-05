"""
Master Git Sync Script
Handles end-to-end local staging, per-channel chunked committing, and incremental pushing to GitHub.
Ensures large sets of files (e.g. ~10,000 files in /raw and /enriched) are committed in safe, small chunks
(e.g., maximum 100 files per commit) to prevent Git lockup, UI freeze, or push body payload timeouts.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ISB_ROOT = Path(__file__).parent.resolve()
REPO_ROOT = ISB_ROOT.parent.parent
RAW_DIR = ISB_ROOT / "raw"
ENRICHED_DIR = ISB_ROOT / "enriched"
LOCK_FILE = REPO_ROOT / ".git" / "index.lock"

MAX_FILES_PER_COMMIT = 100
STAGE_CHUNK_SIZE = 500


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


def stage_and_commit_file_list(
    file_paths: list[Path],
    commit_prefix: str,
    max_per_commit: int = MAX_FILES_PER_COMMIT,
) -> int:
    """Helper to stage and commit a list of files in chunked commits."""
    if not file_paths:
        return 0

    rel_files = [str(f.relative_to(REPO_ROOT)) for f in file_paths]
    total_files = len(rel_files)
    total_parts = (total_files + max_per_commit - 1) // max_per_commit
    commits_created = 0

    for idx, i in enumerate(range(0, total_files, max_per_commit), 1):
        file_chunk = rel_files[i : i + max_per_commit]
        clear_lock()

        # Stage files in sub-chunks for CLI argument length safety
        for j in range(0, len(file_chunk), STAGE_CHUNK_SIZE):
            stage_subchunk = file_chunk[j : j + STAGE_CHUNK_SIZE]
            run_git(["git", "add"] + stage_subchunk)

        diff_res = run_git(["git", "diff", "--cached", "--name-only"])
        staged = [f for f in diff_res.stdout.splitlines() if f.strip()]

        if staged:
            part_suffix = f" (part {idx}/{total_parts})" if total_parts > 1 else ""
            msg = f"{commit_prefix}: add {len(staged)} files{part_suffix}"
            res = run_git(["git", "commit", "-m", msg])
            if res.returncode == 0:
                commits_created += 1
            else:
                print(f"    Commit error: {res.stderr.strip()}")

    return commits_created


def step1_commit_raw_channels() -> None:
    """Finds and commits all channel text transcripts (.txt and .md) per channel in chunks."""
    print("\n--- STEP 1: Staging & Committing Raw Channels ---")
    if not RAW_DIR.exists():
        print(f"Directory {RAW_DIR} does not exist.")
        return

    subdirs = sorted([d for d in RAW_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(subdirs)} channel directories in raw.")

    total_commits = 0
    for idx, channel_dir in enumerate(subdirs, 1):
        clear_lock()
        txt_files = sorted(list(channel_dir.rglob("*.txt")) + list(channel_dir.rglob("*.md")))
        if not txt_files:
            continue

        prefix = f"sync(raw): '{channel_dir.name}'"
        c_count = stage_and_commit_file_list(txt_files, commit_prefix=prefix)
        if c_count > 0:
            print(f"  [{idx}/{len(subdirs)}] Channel '{channel_dir.name}': {len(txt_files)} files -> {c_count} commits.")
            total_commits += c_count

    print(f"Step 1 Complete: Created {total_commits} raw channel commits.")


def step2_commit_enriched_channels() -> None:
    """Finds and commits all enriched channel files in chunks per channel."""
    print("\n--- STEP 2: Staging & Committing Enriched Data ---")
    if not ENRICHED_DIR.exists():
        print(f"Directory {ENRICHED_DIR} does not exist.")
        return

    subdirs = sorted([d for d in ENRICHED_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(subdirs)} channel directories in enriched.")

    total_commits = 0
    for idx, channel_dir in enumerate(subdirs, 1):
        clear_lock()
        enriched_files = sorted([f for f in channel_dir.rglob("*") if f.is_file()])
        if not enriched_files:
            continue

        prefix = f"sync(enriched): '{channel_dir.name}'"
        c_count = stage_and_commit_file_list(enriched_files, commit_prefix=prefix)
        if c_count > 0:
            print(f"  [{idx}/{len(subdirs)}] Channel '{channel_dir.name}': {len(enriched_files)} files -> {c_count} commits.")
            total_commits += c_count

    # Also handle root files in ENRICHED_DIR if any
    root_files = sorted([f for f in ENRICHED_DIR.glob("*") if f.is_file()])
    if root_files:
        c_count = stage_and_commit_file_list(root_files, commit_prefix="sync(enriched): root files")
        total_commits += c_count

    print(f"Step 2 Complete: Created {total_commits} enriched commits.")


def step3_commit_code_and_skills() -> None:
    """Stages and commits any remaining project code, agent skills, cresmo, and configs."""
    print("\n--- STEP 3: Staging Remaining Code & Skills ---")
    clear_lock()

    targets = [
        ".agents/",
        "playground/cresmo/",
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
        msg = f"feat: sync project code, cresmo pipeline, skills ({len(staged)} files)"
        res = run_git(["git", "commit", "-m", msg])
        if res.returncode == 0:
            print(f"  Committed {len(staged)} project code and skills files.")
        else:
            print(f"  Commit error in step 3: {res.stderr.strip()}")
    else:
        print("  No unstaged code/skills files found.")

    print("Step 3 Complete.")


def step4_push_to_remote(batch_size: int = 1) -> None:
    """Pushes unpushed local commits to GitHub in small chunks."""
    print("\n--- STEP 4: Pushing Commits to GitHub Remote ---")
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

    print("Step 4 Complete.")


def step5_verify() -> None:
    """Verifies final sync state between local and remote."""
    print("\n--- STEP 5: Verification ---")
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
    step2_commit_enriched_channels()
    step3_commit_code_and_skills()
    step4_push_to_remote(batch_size=1)
    step5_verify()
