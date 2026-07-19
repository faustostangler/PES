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
from time_logger import log_time_data, plot_time_log

# --- Path Configurations ---
ISB_ROOT = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR = ISB_ROOT / "raw"
DEFAULT_ENRICHED_DIR = ISB_ROOT / "enriched"
DEFAULT_WIKI_DIR = ISB_ROOT / "wiki"
DEFAULT_CHROME_PROFILE = Path.home() / ".isb-ai-chrome-profile"
PROCESSED_LOG_FILE = ISB_ROOT / "processed_gemini.json"


# ==================== FIRST-PASS INGESTION ROUTER ====================

def run_sync_subcommand(args: argparse.Namespace) -> None:
    """Invokes sync_channels to crawl/download transcripts."""
    playlist_path = Path(args.playlist)
    csv_path = Path(args.csv)
    output_dir = Path(args.raw_dir)

    playlist_urls = []
    if playlist_path.exists():
        playlist_urls = read_playlist_urls(playlist_path)

    if playlist_urls:
        print(f"Sync {len(playlist_urls)} channels...")
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

def classify_channel(channel_name: str) -> tuple[str, str]:
    """Classifies source channel deterministically into (domain, category_type).

    Required by Section 2.1: Content classification happens by rules in Python code.
    """
    name_clean = channel_name.lower().strip()

    # Perennial channels
    perennial_tech = {
        "fabio akita", "lucas montano", "mano deyvin",
        "matheus battisti - hora de codar", "chrome for developers",
        "augusto galego", "onde eu clico"
    }
    perennial_ai = {
        "sandeco channel - decomplicated ia", "inteligência mil grau",
        "inteligencia mil grau"
    }

    # Volatile channels
    volatile_politics = {
        "ancapsu", "andré marsiglia", "andre marsiglia", "deltan dallagnol",
        "nando moura", "felipe moura brasil", "renato augusto",
        "jeffrey chiquini", "leandro ruschel", "full texts"
    }
    volatile_geo = {
        "hoje no mundo militar", "ronnald hawk"
    }
    volatile_finance = {
        "investidor sardinha l raul sena", "investidor sardinha",
        "rafael quintanilha – quantbrasil", "rafael quintanilha - quantbrasil",
        "world revolving"
    }

    if name_clean in perennial_tech:
        return "technology", "perennial"
    elif name_clean in perennial_ai:
        return "ai_data_science", "perennial"
    elif name_clean in volatile_politics:
        return "politics_law", "volatile"
    elif name_clean in volatile_geo:
        return "geopolitics_military", "volatile"
    elif name_clean in volatile_finance:
        return "finance_economics", "volatile"

    return "uncategorized", "volatile"


def resolve_note_path(wiki_dir: Path, filename: str) -> Path:
    """Resolves target note path based on file prefix or MOC type under wiki/."""
    clean_fn = filename.replace("[", "").replace("]", "").strip()

    # Handle files with explicit folder prefix like "MOCs/MOC_Name.md"
    if clean_fn.startswith("MOCs/"):
        return wiki_dir / "MOCs" / clean_fn.replace("MOCs/", "")

    # Map of Content files
    if clean_fn.startswith("MOC_"):
        return wiki_dir / "MOCs" / clean_fn

    # Perennial Reference Notes
    if clean_fn.startswith("R_"):
        return wiki_dir / "concepts" / clean_fn

    # Perennial Action Notes
    if clean_fn.startswith("A_"):
        return wiki_dir / "procedures" / clean_fn

    # Volatile Chronicles
    return wiki_dir / "chronicles" / clean_fn


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

    # Clean MOC name format (handles [[MOCs/MOC_Name]], [[MOC_Name]], etc.)
    clean_moc = moc_name.replace("[", "").replace("]", "").strip()
    if "/" in clean_moc:
        clean_moc = clean_moc.split("/")[-1].strip()
    clean_moc = clean_moc.replace(".md", "").strip()
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
            # print(f"  ✓ Linked [[{note_stem}]] in existing {moc_file.name}")
    else:
        title = clean_moc.replace("MOC_", "")
        content = f"# MOC {title}\n\n{link_line}\n"
        with open(moc_file, "w", encoding="utf-8") as f:
            f.write(content)
        # print(f"  ★ Created new MOC: {moc_file.name} linking [[{note_stem}]]")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to xxhxxmxxs (e.g. 02h14m45s)."""
    secs = int(seconds)
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    remaining_secs = secs % 60
    return f"{hours:02d}h{minutes:02d}m{remaining_secs:02d}s"


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
    print(f"Videos to process")
    for txt_file in txt_files:
        blocks = parse_merged_transcriptions(txt_file)
        for b in blocks:
            b["source_file"] = txt_file
            all_blocks.append(b)

    # print(f"Discovered {len(all_blocks)} videos in total.")

    # 2. Filter using idempotency log
    processed_log = load_processed_log(PROCESSED_LOG_FILE)
    pending_blocks = []
    
    # Track counts for breakdown
    channel_total = {}
    channel_pending = {}
    category_total = {}
    category_pending = {}

    for b in all_blocks:
        meta = b.get("metadata", {})
        video_id = meta.get("video_id")
        channel = meta.get("channel_name", "Unknown Channel")
        category = meta.get("channel_category", "uncategorized")

        # Increment totals
        channel_total[channel] = channel_total.get(channel, 0) + 1
        category_total[category] = category_total.get(category, 0) + 1

        if not video_id:
            continue
        if video_id in processed_log:
            continue

        pending_blocks.append(b)
        # Increment pendings
        channel_pending[channel] = channel_pending.get(channel, 0) + 1
        category_pending[category] = category_pending.get(category, 0) + 1

    # print("\n--- Breakdown by Channel (Pending / Total) ---")
    # for chan in sorted(channel_total.keys()):
    #     total = channel_total[chan]
    #     pending = channel_pending.get(chan, 0)
    #     print(f"  - {chan}: {pending} pending / {total} total")

    # print("\n--- Breakdown by Category (Pending / Total) ---")
    for cat in sorted(category_total.keys()):
        total = category_total[cat]
        pending = category_pending.get(cat, 0)
        print(f"{cat}: {pending}/{total}")

    # print(f"Already processed: {len(all_blocks) - len(pending_blocks)}")
    # print(f"Pending processing: {len(pending_blocks)}")

    if args.limit:
        pending_blocks = pending_blocks[:args.limit]
        print(f"Limiting to first {args.limit} pending block(s).")

    if not pending_blocks:
        print("Nothing to process.")
        return

    # 3. Dry-run details
    if args.dry_run:
        print("\n--- DRY RUN: Pending Blocks Details (Sample of up to 10) ---")
        sample_limit = 10
        for i, b in enumerate(pending_blocks[:sample_limit], 1):
            meta = b.get("metadata", {})
            channel = meta.get("channel_name", "Unknown Channel")
            domain, category_type = classify_channel(channel)
            print(
                f"  {i:2d}. [{meta.get('video_id')}] Date: {meta.get('video_date')} | "
                f"Domain/Class: {domain.upper()}/{category_type.upper()} | {meta.get('video_title')[:50]}"
            )
        if len(pending_blocks) > sample_limit:
            print(f"  ... and {len(pending_blocks) - sample_limit} more pending video(s).")
        return

    # 4. Process live using Playwright & Gemini Web
    processed_count = 0
    error_count = 0
    total_active_runs_session = 0
    set_start_time = time.time()
    run_id = f"curadoria_{time.strftime('%Y%m%d_%H%M%S')}"

    # Read current MOC names
    active_mocs = scan_mocs(wiki_dir)
    mocs_str = ", ".join(active_mocs) if active_mocs else "Nenhum MOC ativo"
    # print(f"Active MOCs in vault: {mocs_str}")

    with GeminiWebProcessor(user_data_dir=chrome_profile) as processor:
        for i, b in enumerate(pending_blocks, 1):
            meta = b.get("metadata", {})
            video_id = meta.get("video_id", "unknown")
            channel_id = meta.get("channel_id", "unknown")
            channel = meta.get("channel_name", "Unknown Channel")
            date_yaml = meta.get("video_date", "Sem data")
            transcription = b.get("text", "")

            domain, category_type = classify_channel(channel)

            remaining = len(pending_blocks) - i
            percent = (i / len(pending_blocks)) * 100
            total = len(pending_blocks)

            elapsed = time.time() - set_start_time
            if total_active_runs_session > 0 and elapsed > 0:
                rate = total_active_runs_session / elapsed
                eta_sec = remaining / rate
                elapsed_str = format_duration(elapsed)
                eta_str = format_duration(eta_sec)
                total_time_str = format_duration(elapsed + eta_sec)
                time_block = f"{elapsed_str}+{eta_str} = {total_time_str}"
                rate_block = f"{rate:.3f}"
            else:
                elapsed_str = format_duration(elapsed)
                time_block = f"{elapsed_str}+--h--m--s = --h--m--s"
                rate_block = ""

            print(f"[{i}+{remaining}={total}] [{rate_block} {percent:.2f}%] [{time_block}] {domain.upper()}/{category_type.upper()} {channel_id} {video_id} | {meta.get('video_title')[:20]}...")

            if not transcription.strip():
                print("  ⚠️ Empty transcript. Skipping.")
                continue

            # Select prompt template & inject context
            if category_type == "volatile":
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
                # print(f"  Gemini responded in {duration:.1f}s. Parsing...")

                # Parse response files and MOC links
                generated_files, mocs_mapping = parse_gemini_response(response)

                if not generated_files:
                    print("--- Raw Response for debugging ---")
                    print(response[:800] + "\n...")
                    raise RuntimeError("No file outputs parsed from Gemini response.")

                # Save generated notes
                for filename, content in generated_files.items():
                    target_file = resolve_note_path(wiki_dir, filename)
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    # print(f"  ✓ Created note: {filename}")

                # Update MOC files
                for file_ref, moc_name in mocs_mapping:
                    if file_ref in generated_files:
                        update_or_create_moc(wiki_dir, file_ref, moc_name)

                # Update idempotency tracking
                processed_log[video_id] = datetime.now(UTC).isoformat()
                save_processed_log(PROCESSED_LOG_FILE, processed_log)
                processed_count += 1
                total_active_runs_session += 1

                # Update MOC list for subsequent iterations
                active_mocs = scan_mocs(wiki_dir)
                mocs_str = ", ".join(active_mocs) if active_mocs else "Nenhum MOC ativo"

            except Exception as e:
                print(f"  ✗ Error: {e}")
                error_count += 1
                total_active_runs_session += 1

            # Log progress metrics to CSV and update plot
            elapsed_after = time.time() - set_start_time
            if total_active_runs_session > 1 and elapsed_after > 0:
                rate_after = (total_active_runs_session - 1) / elapsed_after
                eta_val = remaining / rate_after
            else:
                eta_val = None

            log_time_data(run_id, i, len(pending_blocks), percent, elapsed_after, eta_val)
            try:
                plot_time_log()
            except Exception as e_plot:
                print(f"  ⚠️ Warning: Failed to update time chart: {e_plot}", file=sys.stderr)

    print(f"\n{'='*60}")
    print(f"Curadoria processing finished. Success: {processed_count}, Errors: {error_count}")


# ==================== STAGE 2 AI ENRICHMENT ====================

def run_stage2_subcommand(args: argparse.Namespace) -> None:
    """Executes Stage 2 AI Enrichment on raw files."""
    import stage2
    raw_path = Path(args.raw_dir).resolve()
    enriched_path = Path(args.enriched_dir).resolve()
    chrome_profile = Path(args.chrome_profile).resolve()

    unprocessed = stage2.discover_unprocessed_files(raw_path, enriched_path)
    print(f"Stage 2: Discovered {len(unprocessed)} unprocessed raw files.")

    if args.limit:
        unprocessed = unprocessed[:args.limit]
        print(f"Limiting execution to first {args.limit} files.")

    if not unprocessed:
        print("Nothing to process in Stage 2.")
        return

    if args.dry_run:
        print("--- Dry Run: Pending Files in Stage 2 ---")
        for idx, f in enumerate(unprocessed, 1):
            print(f"  {idx}. {f.relative_to(raw_path)}")
        return

    print(f"Initializing Playwright context using profile: {chrome_profile}")
    with GeminiWebProcessor(user_data_dir=chrome_profile) as processor:
        for idx, raw_file in enumerate(unprocessed, 1):
            print(f"[{idx}/{len(unprocessed)}] Stage 2 Processing: {raw_file.relative_to(raw_path)}")
            try:
                stage2.process_file(raw_file, enriched_path, processor, raw_dir=raw_path)
                print(f"  ✓ Successfully enriched and saved.")
            except Exception as e:
                print(f"  ✗ Error processing {raw_file.name}: {e}")


# ==================== PIPELINE: sync -> stage2 -> process ====================

def run_pipeline_subcommand(args: argparse.Namespace) -> None:
    """Runs full pipeline: sync -> stage2 -> process."""
    print("\n[PIPELINE] Step 1/3: Sync ingestion...")
    run_sync_subcommand(args)

    print("\n[PIPELINE] Step 2/3: Stage 2 AI Enrichment...")
    run_stage2_subcommand(args)

    print("\n[PIPELINE] Step 3/3: Gemini curadoria (Stage 3)...")
    # For Stage 3, we must read from enriched_dir!
    # To do that, we override args.raw_dir to point to args.enriched_dir
    original_raw_dir = args.raw_dir
    args.raw_dir = args.enriched_dir
    try:
        run_process_subcommand(args)
    finally:
        args.raw_dir = original_raw_dir

    print("\n[PIPELINE] Done.")


# ==================== CLI PARSER ====================

def main() -> None:
    # Default subcommand to 'pipeline' (sync + stage2 + process) if not specified
    if len(sys.argv) < 2:
        sys.argv.insert(1, "pipeline")
    elif sys.argv[1] not in ("sync", "stage2", "process", "pipeline", "-h", "--help"):
        sys.argv.insert(1, "pipeline")

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
        "--raw-dir",
        type=str,
        default=str(DEFAULT_RAW_DIR),
        help=f"Ingested files raw output directory (default: {DEFAULT_RAW_DIR})."
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

    # Subcommand: stage2
    stage2_parser = subparsers.add_parser("stage2", help="Pre-process and enrich raw transcripts with Gems.")
    stage2_parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(DEFAULT_RAW_DIR),
        help=f"Raw transcripts directory (default: {DEFAULT_RAW_DIR})."
    )
    stage2_parser.add_argument(
        "--enriched-dir",
        type=str,
        default=str(DEFAULT_ENRICHED_DIR),
        help=f"Enriched output directory (default: {DEFAULT_ENRICHED_DIR})."
    )
    stage2_parser.add_argument(
        "--chrome-profile",
        type=str,
        default=str(DEFAULT_CHROME_PROFILE),
        help=f"Chrome profile for session cookie (default: {DEFAULT_CHROME_PROFILE})."
    )
    stage2_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List pending files to be processed without executing Gems."
    )
    stage2_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit execution to first N files."
    )

    # Subcommand: process
    process_parser = subparsers.add_parser("process", help="Process transcripts with Gemini Web.")
    process_parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(DEFAULT_ENRICHED_DIR),
        help=f"Enriched transcripts directory (default: {DEFAULT_ENRICHED_DIR})."
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

    # Subcommand: pipeline (sync -> stage2 -> process, full run)
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full pipeline: sync -> stage2 -> process.")
    pipeline_parser.add_argument("--days", type=int, default=180)
    pipeline_parser.add_argument("--model", type=str, default="base")
    pipeline_parser.add_argument("--keep-audio", action="store_true")
    pipeline_parser.add_argument("--playlist", type=str, default=str(ISB_ROOT / "playlist.txt"))
    pipeline_parser.add_argument("--csv", type=str, default=str(DEFAULT_WIKI_DIR / "log.md"))
    pipeline_parser.add_argument("--raw-dir", type=str, default=str(DEFAULT_RAW_DIR))
    pipeline_parser.add_argument("--enriched-dir", type=str, default=str(DEFAULT_ENRICHED_DIR))
    pipeline_parser.add_argument("--output-dir", type=str, default=str(DEFAULT_WIKI_DIR))
    pipeline_parser.add_argument("--chrome-profile", type=str, default=str(DEFAULT_CHROME_PROFILE))
    pipeline_parser.add_argument("--dry-run", action="store_true")
    pipeline_parser.add_argument("--limit", type=int, default=None)

    args = parser.parse_args()

    if args.command == "sync":
        run_sync_subcommand(args)
    elif args.command == "stage2":
        run_stage2_subcommand(args)
    elif args.command == "process":
        run_process_subcommand(args)
    elif args.command == "pipeline":
        run_pipeline_subcommand(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)

print("Done!")

