#!/usr/bin/env python3
"""ISB.AI GOD Monolith Entrypoint.

Provides unified interface for both ingestion/syncing (first-pass) and Gemini Web
curadoria (second-pass) pipelines in a flat, KISS architecture.
"""

import argparse
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# Local flat imports
import sync_channels
from gemini_web import (
    NEWS_SYSTEM_PROMPT,
    TECHNICAL_SYSTEM_PROMPT,
    GeminiWebProcessor,
    load_processed_log,
    save_processed_log,
)
from helper import parse_merged_transcriptions, read_playlist_urls

# --- Path Configurations ---
ISB_ROOT = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR = ISB_ROOT / "raw"
DEFAULT_WIKI_DIR = ISB_ROOT / "wiki"
DEFAULT_CHROME_PROFILE = Path.home() / ".isb-ai-chrome-profile"
PROCESSED_LOG_FILE = ISB_ROOT / "processed_gemini.json"


# ==================== FIRST-PASS INGESTION ROUTER ====================

def run_sync_subcommand(args: argparse.Namespace) -> None:
    """Invokes sync_channels to crawl/download transcripts."""
    playlist_path = Path(args.playlist)
    csv_path = Path(args.csv)
    output_dir = Path(args.output_dir)

    playlist_urls = []
    if playlist_path.exists():
        playlist_urls = read_playlist_urls(playlist_path)

    if playlist_urls:
        print(f"Starting channel sync for {len(playlist_urls)} seed URL(s)...")
        sync_channels.sync_channels_and_seeds(
            days=args.days,
            output_dir=output_dir,
            model_name=args.model,
            keep_audio=args.keep_audio,
            playlist_urls=playlist_urls,
            csv_path=csv_path,
        )
    else:
        print("No seed URLs found in playlist.txt.")


# ==================== SECOND-PASS CURADORIA ====================

def classify_channel(channel_name: str) -> str:
    """Classifies source channel deterministically.

    Required by Section 2.1: Content classification happens by rules in Python code.
    """
    news_channels = {
        "andré marsiglia", "andre marsiglia", "deltan dallagnol", "nando moura",
        "leandro ruschel", "ancapsu", "hoje no mundo militar", "felipe moura brasil",
        "inteligência mil grau", "inteligencia mil grau"
    }
    name_clean = channel_name.lower().strip()
    if name_clean in news_channels:
        return "news"
    return "technical"


def scan_mocs(wiki_dir: Path) -> list[str]:
    """Scans wiki/MOCs/ directory to build a list of existing maps of content.

    Required by Section 3.1: Sweep Obsidian Map of Content folder.
    """
    mocs_dir = wiki_dir / "MOCs"
    if not mocs_dir.exists():
        return []
    # Find all Markdown files in the MOCs folder and return their stems/names
    mocs = [f.stem for f in mocs_dir.glob("*.md")]
    return sorted(mocs)


def parse_gemini_response(text: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Extracts bounded file blocks and MOC associations from Gemini response."""
    files = {}
    moc_associations = []

    # 1. Parse file blocks bounded by <<<< FILE: filename >>>> and <<<< END FILE >>>>
    file_pattern = re.compile(
        r'<<<<\s*FILE:\s*([^\n>]+)\s*>>>>(.*?)<<<<\s*END FILE\s*>>>>',
        re.DOTALL
    )
    for match in file_pattern.finditer(text):
        filename = match.group(1).strip()
        content = match.group(2).strip()
        files[filename] = content

    # 2. Parse MOC associations block
    moc_pattern = re.compile(
        r'<<<<\s*MOC_ASSOCIATIONS\s*>>>>(.*?)<<<<\s*END MOC_ASSOCIATIONS\s*>>>>',
        re.DOTALL
    )
    moc_match = moc_pattern.search(text)
    if moc_match:
        assoc_block = moc_match.group(1)
        for line in assoc_block.splitlines():
            line = line.strip()
            if "->" in line:
                parts = line.split("->")
                if len(parts) == 2:
                    file_ref = parts[0].strip()
                    moc_name = parts[1].strip()
                    moc_associations.append((file_ref, moc_name))

    return files, moc_associations


def update_or_create_moc(wiki_dir: Path, note_filename: str, moc_name: str) -> None:
    """Links note to target MOC file, generating it autonomously if not active.

    Required by Section 3.2: MOC Resolution & Autonomous Creation.
    """
    mocs_dir = wiki_dir / "MOCs"
    mocs_dir.mkdir(parents=True, exist_ok=True)

    # Clean MOC name format
    clean_moc = moc_name.replace(".md", "").strip()
    if not clean_moc.startswith("MOC_"):
        clean_moc = f"MOC_{clean_moc}"

    moc_file = mocs_dir / f"{clean_moc}.md"
    note_stem = note_filename.replace(".md", "").strip()
    link_line = f"- [[{note_stem}]]"

    if moc_file.exists():
        with open(moc_file, "r", encoding="utf-8") as f:
            content = f.read()

        if f"[[{note_stem}]]" not in content:
            updated_content = content.rstrip() + f"\n{link_line}\n"
            with open(moc_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"  ✓ Linked [[{note_stem}]] in existing {moc_file.name}")
    else:
        title = clean_moc.replace("MOC_", "")
        content = f"# MOC {title}\n\n{link_line}\n"
        with open(moc_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ★ Created new MOC: {moc_file.name} linking [[{note_stem}]]")


def run_process_subcommand(args: argparse.Namespace) -> None:
    """Executes the Second-Pass Gemini Web Curadoria loop."""
    raw_dir = Path(args.raw_dir)
    wiki_dir = Path(args.output_dir)
    chrome_profile = Path(args.chrome_profile)

    if not raw_dir.exists():
        print(f"Error: Raw transcriptions directory not found at {raw_dir}")
        return

    # 1. Discover all blocks in raw/ files
    all_blocks = []
    txt_files = sorted(raw_dir.rglob("*.txt"))
    print(f"Scanning raw transcription files...")
    for txt_file in txt_files:
        blocks = parse_merged_transcriptions(txt_file)
        for b in blocks:
            b["source_file"] = txt_file
            all_blocks.append(b)

    print(f"Discovered {len(all_blocks)} blocks in total.")

    # 2. Filter using idempotency log
    processed_log = load_processed_log(PROCESSED_LOG_FILE)
    pending_blocks = []
    for b in all_blocks:
        video_id = b.get("metadata", {}).get("video_id")
        if video_id and video_id not in processed_log:
            pending_blocks.append(b)

    print(f"Already processed: {len(all_blocks) - len(pending_blocks)}")
    print(f"Pending processing: {len(pending_blocks)}")

    if args.limit:
        pending_blocks = pending_blocks[:args.limit]
        print(f"Limiting to first {args.limit} pending block(s).")

    if not pending_blocks:
        print("Nothing to process.")
        return

    # 3. Dry-run details
    if args.dry_run:
        print("\n--- DRY RUN: Pending Blocks Details ---")
        for i, b in enumerate(pending_blocks, 1):
            meta = b.get("metadata", {})
            channel = meta.get("channel_name", "Unknown Channel")
            classification = classify_channel(channel)
            print(
                f"  {i:2d}. [{meta.get('video_id')}] Date: {meta.get('video_date')} | "
                f"Class: {classification.upper()} | {meta.get('video_title')[:50]}"
            )
        return

    # 4. Process live using Playwright & Gemini Web
    processed_count = 0
    error_count = 0

    # Read current MOC names
    active_mocs = scan_mocs(wiki_dir)
    mocs_str = ", ".join(active_mocs) if active_mocs else "Nenhum MOC ativo"
    print(f"Active MOCs in vault: {mocs_str}")

    with GeminiWebProcessor(user_data_dir=chrome_profile) as processor:
        for i, b in enumerate(pending_blocks, 1):
            meta = b.get("metadata", {})
            video_id = meta.get("video_id", "unknown")
            channel = meta.get("channel_name", "Unknown Channel")
            date_yaml = meta.get("video_date", "Sem data")
            transcription = b.get("text", "")

            classification = classify_channel(channel)

            print(f"\n{'='*60}")
            print(f"[{i}/{len(pending_blocks)}] Processing: {meta.get('video_title')[:60]}")
            print(f"  Channel: {channel} | Classification: {classification.upper()}")
            print(f"  YAML Date (Temporal Anchor): {date_yaml}")

            if not transcription.strip():
                print("  ⚠️ Empty transcript. Skipping.")
                continue

            # Select prompt template & inject context
            if classification == "news":
                system_prompt = NEWS_SYSTEM_PROMPT.format(
                    data_yaml=date_yaml,
                    mocs_list=mocs_str,
                    transcription=transcription,
                )
            else:
                system_prompt = TECHNICAL_SYSTEM_PROMPT.format(
                    data_yaml=date_yaml,
                    mocs_list=mocs_str,
                    transcription=transcription,
                )

            try:
                start_time = time.time()
                response = processor.send_prompt(system_prompt)
                duration = time.time() - start_time
                print(f"  Gemini responded in {duration:.1f}s. Parsing...")

                # Parse response files and MOC links
                generated_files, mocs_mapping = parse_gemini_response(response)

                if not generated_files:
                    print("  ⚠️ Warning: No file outputs parsed from Gemini response.")
                    print("--- Raw Response for debugging ---")
                    print(response[:800] + "\n...")

                # Save generated notes
                for filename, content in generated_files.items():
                    target_file = wiki_dir / filename
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  ✓ Created note: {filename}")

                # Update MOC files
                for file_ref, moc_name in mocs_mapping:
                    if file_ref in generated_files:
                        update_or_create_moc(wiki_dir, file_ref, moc_name)

                # Update idempotency tracking
                processed_log[video_id] = datetime.now(UTC).isoformat()
                save_processed_log(PROCESSED_LOG_FILE, processed_log)
                processed_count += 1

                # Update MOC list for subsequent iterations
                active_mocs = scan_mocs(wiki_dir)
                mocs_str = ", ".join(active_mocs) if active_mocs else "Nenhum MOC ativo"

            except Exception as e:
                print(f"  ✗ Error: {e}")
                error_count += 1

    print(f"\n{'='*60}")
    print(f"Curadoria processing finished. Success: {processed_count}, Errors: {error_count}")


# ==================== CLI PARSER ====================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ISB.AI GOD Monolith - Ingestion and AI Curadoria Tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: sync
    sync_parser = subparsers.add_parser("sync", help="Sync latest videos from playlist channels.")
    sync_parser.add_argument(
        "--days",
        type=int,
        default=180,
        help="Sync uploads in range of last N days (default: 180)."
    )
    sync_parser.add_argument(
        "--model",
        type=str,
        default="base",
        help="Whisper fallback model: tiny, base, small (default: base)."
    )
    sync_parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Retain downloaded OGG audio file."
    )
    sync_parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_RAW_DIR),
        help=f"Ingested files output directory (default: {DEFAULT_RAW_DIR})."
    )
    sync_parser.add_argument(
        "--playlist",
        type=str,
        default=str(ISB_ROOT / "playlist.txt"),
        help="Playlist seeds file path."
    )
    sync_parser.add_argument(
        "--csv",
        type=str,
        default=str(DEFAULT_WIKI_DIR / "log.md"),
        help="Markdown log file path."
    )

    # Subcommand: process
    process_parser = subparsers.add_parser("process", help="Process raw transcripts with Gemini Web.")
    process_parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(DEFAULT_RAW_DIR),
        help=f"Raw transcripts directory (default: {DEFAULT_RAW_DIR})."
    )
    process_parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_WIKI_DIR),
        help=f"Obsidian wiki output directory (default: {DEFAULT_WIKI_DIR})."
    )
    process_parser.add_argument(
        "--chrome-profile",
        type=str,
        default=str(DEFAULT_CHROME_PROFILE),
        help=f"Chrome profile for session cookie (default: {DEFAULT_CHROME_PROFILE})."
    )
    process_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and list pending blocks without executing browser."
    )
    process_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit execution to first N blocks."
    )

    args = parser.parse_args()

    if args.command == "sync":
        run_sync_subcommand(args)
    elif args.command == "process":
        run_process_subcommand(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
