#!/usr/bin/env python3
"""Cresmo Unified GOD Main Entrypoint (cresmo_main.py).

Provides a single CLI interface to run individual stages or the full Cresmo pipeline:
- `python cresmo_main.py sync`     : Runs Stage 1 Raw Ingestion.
- `python cresmo_main.py process`  : Runs Stages 2 through 6 Cresmo Skills Pipeline.
- `python cresmo_main.py full`     : Runs the complete end-to-end flow (Stage 1 Ingestion -> Stage 2-6 Pipeline).
"""

import argparse
from pathlib import Path
import sys

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cresmo_ingestion import run_cresmo_ingestion
from cresmo_pipeline import run_cresmo_pipeline
from cresmo_shared import (
    CRESMO_ROOT,
    DEFAULT_BRAIN_CSV,
    DEFAULT_CATEGORIES,
    DEFAULT_COOKIES_FILE,
    DEFAULT_CRESMO_DIR,
    DEFAULT_ENRICHED_DIR,
    DEFAULT_PLAYLIST_FILE,
    DEFAULT_PLAYLIST_PRIORITY_FILE,
    DEFAULT_RAW_DIR,
)
from export_cookies import ensure_cookies

# --- CLI & Pipeline Defaults ---
DEFAULT_DAYS: int = 365 * 2
DEFAULT_WHISPER_MODEL: str = "base"
DEFAULT_MAX_WORKERS: int = 5
DEFAULT_KEEP_AUDIO: bool = False
DEFAULT_ISOLATE_CONTEXT: bool = True
DEFAULT_RESTART_SERVER: bool = False
DEFAULT_COMMAND: str = "sync" # "full"

CLI_EPILOG_EXAMPLES: str = """
Examples:
  # Run Stage 1 Raw Ingestion only
  .venv/bin/python playground/cresmo/cresmo_main.py sync --days 14

  # Run Stage 2->6 Pipeline on downloaded raw transcripts
  .venv/bin/python playground/cresmo/cresmo_main.py process --limit 5

  # Run Stage 2->6 Pipeline filtered by category (e.g. politics_br)
  .venv/bin/python playground/cresmo/cresmo_main.py process --category politics_br --limit 5

  # Run Stage 2->6 Pipeline filtered by multiple categories
  .venv/bin/python playground/cresmo/cresmo_main.py process --category politics_br,tech_ai

  # Run FULL End-to-End Pipeline (Sync + Process) filtered by category
  .venv/bin/python playground/cresmo/cresmo_main.py full --days 7 --category politics_br --limit 10
"""


def build_parser() -> argparse.ArgumentParser:
    """Construct and configure the argument parser for Cresmo CLI."""
    parser = argparse.ArgumentParser(
        description="Cresmo Unified Entrypoint CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_EPILOG_EXAMPLES,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- Sync Subcommand (Stage 1) ---
    sync_parser = subparsers.add_parser("sync", help="Run Stage 1 Raw Ingestion")
    sync_parser.add_argument("--playlist", default=str(DEFAULT_PLAYLIST_FILE), help="Path to seed playlist file")
    sync_parser.add_argument("--csv", default=str(DEFAULT_BRAIN_CSV), help="Path to brain metadata CSV")
    sync_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw output directory")
    sync_parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Days limit to check back")
    sync_parser.add_argument("--model", default=DEFAULT_WHISPER_MODEL, help="Whisper fallback model size")
    sync_parser.add_argument("--keep-audio", action="store_true", default=DEFAULT_KEEP_AUDIO, help="Keep downloaded audio files")
    sync_parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help="Max worker threads")
    sync_parser.add_argument(
        "--priority-playlist",
        default=str(DEFAULT_PLAYLIST_PRIORITY_FILE),
        help="Path to priority playlist text file (default: playground/cresmo/playlist-priority.txt)",
    )

    # --- Process Subcommand (Stages 2 -> 6) ---
    process_parser = subparsers.add_parser("process", help="Run Stages 2->6 Cresmo Skills Pipeline")
    process_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    process_parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched directory")
    process_parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    process_parser.add_argument(
        "--category", "--categories", "-c",
        dest="categories",
        nargs="+",
        default=list(DEFAULT_CATEGORIES),
        help="Filter videos by category (default: 'politics_br,tech_ai'. Use 'all' for all categories)",
    )
    process_parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process")
    process_parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")
    process_parser.add_argument(
        "--isolate-context",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ISOLATE_CONTEXT,
        help="Purge session transcript and message history before each dispatch to isolate context (default: True)",
    )
    process_parser.add_argument(
        "--restart-server",
        action="store_true",
        default=DEFAULT_RESTART_SERVER,
        help="Restart Language Server process before each dispatch to isolate context (default: False)",
    )
    process_parser.add_argument(
        "--priority-playlist",
        default=str(DEFAULT_PLAYLIST_PRIORITY_FILE),
        help="Path to priority playlist text file (default: playground/cresmo/playlist-priority.txt)",
    )
    process_parser.add_argument(
        "--auto-sync",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Automatically download/transcribe missing priority videos on-demand (default: True)",
    )

    # --- Full Subcommand (Stage 1 -> Stage 6) ---
    full_parser = subparsers.add_parser("full", help="Run FULL end-to-end pipeline (Sync + Process)")
    full_parser.add_argument("--playlist", default=str(DEFAULT_PLAYLIST_FILE), help="Path to seed playlist file")
    full_parser.add_argument("--csv", default=str(DEFAULT_BRAIN_CSV), help="Path to brain metadata CSV")
    full_parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    full_parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched directory")
    full_parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    full_parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Days limit to check back for ingestion")
    full_parser.add_argument("--model", default=DEFAULT_WHISPER_MODEL, help="Whisper fallback model size")
    full_parser.add_argument("--keep-audio", action="store_true", default=DEFAULT_KEEP_AUDIO, help="Keep downloaded audio files")
    full_parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help="Max worker threads")
    full_parser.add_argument(
        "--category", "--categories", "-c",
        dest="categories",
        nargs="+",
        default=list(DEFAULT_CATEGORIES),
        help="Filter videos by category (default: 'politics_br,tech_ai'. Use 'all' for all categories)",
    )
    full_parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process in pipeline")
    full_parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")
    full_parser.add_argument(
        "--isolate-context",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ISOLATE_CONTEXT,
        help="Purge session transcript and message history before each dispatch to isolate context (default: True)",
    )
    full_parser.add_argument(
        "--restart-server",
        action="store_true",
        default=DEFAULT_RESTART_SERVER,
        help="Restart Language Server process before each dispatch to isolate context (default: False)",
    )
    full_parser.add_argument(
        "--priority-playlist",
        default=str(DEFAULT_PLAYLIST_PRIORITY_FILE),
        help="Path to priority playlist text file (default: playground/cresmo/playlist-priority.txt)",
    )
    full_parser.add_argument(
        "--auto-sync",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Automatically download/transcribe missing priority videos on-demand (default: True)",
    )

    return parser


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments and apply default fallbacks."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        args.command = DEFAULT_COMMAND
        args.playlist = getattr(args, "playlist", str(DEFAULT_PLAYLIST_FILE))
        args.csv = getattr(args, "csv", str(DEFAULT_BRAIN_CSV))
        args.raw_dir = getattr(args, "raw_dir", str(DEFAULT_RAW_DIR))
        args.enriched_dir = getattr(args, "enriched_dir", str(DEFAULT_ENRICHED_DIR))
        args.cresmo_dir = getattr(args, "cresmo_dir", str(DEFAULT_CRESMO_DIR))
        args.days = getattr(args, "days", DEFAULT_DAYS)
        args.model = getattr(args, "model", DEFAULT_WHISPER_MODEL)
        args.keep_audio = getattr(args, "keep_audio", DEFAULT_KEEP_AUDIO)
        args.max_workers = getattr(args, "max_workers", DEFAULT_MAX_WORKERS)
        args.categories = getattr(args, "categories", list(DEFAULT_CATEGORIES))
        args.limit = getattr(args, "limit", None)
        args.force = getattr(args, "force", False)
        args.isolate_context = getattr(args, "isolate_context", DEFAULT_ISOLATE_CONTEXT)
        args.restart_server = getattr(args, "restart_server", DEFAULT_RESTART_SERVER)
        args.priority_playlist = getattr(args, "priority_playlist", str(DEFAULT_PLAYLIST_PRIORITY_FILE))
        args.auto_sync = getattr(args, "auto_sync", True)

    return args


def main() -> None:
    args = parse_cli_args()

    # Ensure fresh Netscape cookies file is active when ingestion / yt-dlp is required
    if args.command in {"sync", "full", "all"}:
        ensure_cookies(output_file=DEFAULT_COOKIES_FILE, verbose=True)

    if args.command == "sync":
        run_cresmo_ingestion(
            playlist_path=Path(args.playlist),
            csv_path=Path(args.csv),
            output_dir=Path(args.raw_dir),
            days=args.days,
            model_name=args.model,
            keep_audio=getattr(args, "keep_audio", DEFAULT_KEEP_AUDIO),
            max_workers=getattr(args, "max_workers", DEFAULT_MAX_WORKERS),
            priority_playlist=Path(args.priority_playlist) if getattr(args, "priority_playlist", None) else None,
        )

    elif args.command == "process":
        run_cresmo_pipeline(
            raw_dir=Path(args.raw_dir),
            enriched_dir=Path(args.enriched_dir),
            cresmo_dir=Path(args.cresmo_dir),
            categories=getattr(args, "categories", list(DEFAULT_CATEGORIES)),
            limit=args.limit,
            force=args.force,
            isolate_context=args.isolate_context,
            restart_server=args.restart_server,
            priority_playlist=Path(args.priority_playlist) if getattr(args, "priority_playlist", None) else None,
            auto_sync=getattr(args, "auto_sync", True),
        )

    elif args.command in {"full", "all"}:
        run_cresmo_ingestion(
            playlist_path=Path(args.playlist),
            csv_path=Path(args.csv),
            output_dir=Path(args.raw_dir),
            days=args.days,
            model_name=args.model,
            keep_audio=getattr(args, "keep_audio", DEFAULT_KEEP_AUDIO),
            max_workers=getattr(args, "max_workers", DEFAULT_MAX_WORKERS),
            priority_playlist=Path(args.priority_playlist) if getattr(args, "priority_playlist", None) else None,
        )
        run_cresmo_pipeline(
            raw_dir=Path(args.raw_dir),
            enriched_dir=Path(args.enriched_dir),
            cresmo_dir=Path(args.cresmo_dir),
            categories=getattr(args, "categories", list(DEFAULT_CATEGORIES)),
            limit=args.limit,
            force=args.force,
            isolate_context=args.isolate_context,
            restart_server=args.restart_server,
            priority_playlist=Path(args.priority_playlist) if getattr(args, "priority_playlist", None) else None,
            auto_sync=getattr(args, "auto_sync", True),
        )


if __name__ == "__main__":
    main()
