#!/usr/bin/env python3
"""Cresmo Unified GOD Main Entrypoint (cresmo-main.py).

Provides a single CLI interface to run individual stages or the full Cresmo pipeline:
- `python cresmo-main.py sync`     : Runs Stage 1 Raw Ingestion.
- `python cresmo-main.py process`  : Runs Stages 2 through 6 Cresmo Skills Pipeline.
- `python cresmo-main.py full`     : Runs the complete end-to-end flow (Stage 1 Ingestion -> Stage 2-6 Pipeline).
"""

import argparse
import sys
from pathlib import Path

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cresmo_ingestion import run_cresmo_ingestion
from cresmo_pipeline import run_cresmo_pipeline
from cresmo_shared import (
    CRESMO_ROOT,
    DEFAULT_CRESMO_DIR,
    DEFAULT_ENRICHED_DIR,
    DEFAULT_RAW_DIR,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cresmo Unified Entrypoint CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Stage 1 Raw Ingestion only
  .venv/bin/python playground/cresmo/cresmo-main.py sync --days 14

  # Run Stage 2->6 Pipeline on downloaded raw transcripts
  .venv/bin/python playground/cresmo/cresmo-main.py process --limit 5

  # Run FULL End-to-End Pipeline (Sync + Process)
  .venv/bin/python playground/cresmo/cresmo-main.py full --days 7 --limit 10
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- Sync Subcommand (Stage 1) ---
    sync_parser = subparsers.add_parser("sync", help="Run Stage 1 Raw Ingestion")
    sync_parser.add_argument("--playlist", default=str(CRESMO_ROOT / "playlist.txt"), help="Path to seed playlist file")
    sync_parser.add_argument("--csv", default=str(CRESMO_ROOT / "brain.csv"), help="Path to brain metadata CSV")
    sync_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw output directory")
    sync_parser.add_argument("--days", type=int, default=30, help="Days limit to check back")
    sync_parser.add_argument("--model", default="base", help="Whisper fallback model size")
    sync_parser.add_argument("--keep-audio", action="store_true", help="Keep downloaded audio files")
    sync_parser.add_argument("--max-workers", type=int, default=1, help="Max worker threads")

    # --- Process Subcommand (Stages 2 -> 6) ---
    process_parser = subparsers.add_parser("process", help="Run Stages 2->6 Cresmo Skills Pipeline")
    process_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    process_parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched directory")
    process_parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    process_parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process")
    process_parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")

    # --- Full Subcommand (Stage 1 -> Stage 6) ---
    full_parser = subparsers.add_parser("full", help="Run FULL end-to-end pipeline (Sync + Process)")
    full_parser.add_argument("--playlist", default=str(CRESMO_ROOT / "playlist.txt"), help="Path to seed playlist file")
    full_parser.add_argument("--csv", default=str(CRESMO_ROOT / "brain.csv"), help="Path to brain metadata CSV")
    full_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    full_parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched directory")
    full_parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    full_parser.add_argument("--days", type=int, default=30, help="Days limit to check back for ingestion")
    full_parser.add_argument("--model", default="base", help="Whisper fallback model size")
    full_parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process in pipeline")
    full_parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")

    args = parser.parse_args()

    if not args.command:
        print("ℹ️ No subcommand specified. Defaulting to FULL Cresmo Pipeline execution ('full').\n")
        args.command = "full"
        args.playlist = getattr(args, "playlist", str(CRESMO_ROOT / "playlist.txt"))
        args.csv = getattr(args, "csv", str(CRESMO_ROOT / "brain.csv"))
        args.raw_dir = getattr(args, "raw_dir", str(DEFAULT_RAW_DIR))
        args.enriched_dir = getattr(args, "enriched_dir", str(DEFAULT_ENRICHED_DIR))
        args.cresmo_dir = getattr(args, "cresmo_dir", str(DEFAULT_CRESMO_DIR))
        args.days = getattr(args, "days", 30)
        args.model = getattr(args, "model", "base")
        args.limit = getattr(args, "limit", None)
        args.force = getattr(args, "force", False)

    if args.command == "sync":
        run_cresmo_ingestion(
            playlist_path=Path(args.playlist),
            csv_path=Path(args.csv),
            output_dir=Path(args.raw_dir),
            days=args.days,
            model_name=args.model,
            keep_audio=args.keep_audio,
            max_workers=args.max_workers,
        )

    elif args.command == "process":
        run_cresmo_pipeline(
            raw_dir=Path(args.raw_dir),
            enriched_dir=Path(args.enriched_dir),
            cresmo_dir=Path(args.cresmo_dir),
            limit=args.limit,
            force=args.force,
        )

    elif args.command in {"full", "all"}:
        run_cresmo_pipeline(
            raw_dir=Path(args.raw_dir),
            enriched_dir=Path(args.enriched_dir),
            cresmo_dir=Path(args.cresmo_dir),
            limit=args.limit,
            force=args.force,
        )


if __name__ == "__main__":
    main()
