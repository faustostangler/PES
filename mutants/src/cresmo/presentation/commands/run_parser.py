"""Subparser registration and argument parsing for cresmo run command.

Conforms to:
- ADR-002: Presentation CLI & Humble Object
- SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path


def register_run_subparser(
    subparsers: argparse._SubParsersAction,
    handler: Callable[[argparse.Namespace], int],
) -> None:
    """Register 'run' subcommand parser with argument options.

    Args:
        subparsers: Root CLI subparsers action object.
        handler: Default execution handler callable.
    """
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.add_argument(
        "--no-crawl",
        action="store_true",
        default=False,
        help="Disable crawling channel feeds and strictly process manifest seed items",
    )
    run_parser.add_argument(
        "--web-index",
        action="store_true",
        default=False,
        help="Use Gemini API for raw transcript conceptual indexing instead of local Ollama",
    )
    # ADR-012: Multi-criteria filtering flags
    run_parser.add_argument(
        "--channel",
        dest="channels",
        nargs="*",
        default=None,
        metavar="CHANNEL",
        help=(
            "Filter batch discovery to one or more channel names, handles, or URLs. "
            "Accepts comma-separated values (e.g. --channel Ancapsu,Mises)."
        ),
    )
    run_parser.add_argument(
        "--category",
        "-c",
        dest="categories",
        nargs="*",
        default=None,
        metavar="CATEGORY",
        help=(
            "Filter batch discovery by domain category or volatility type. "
            "Domain names: politics_br, tech_ai, history, philosophy, finance, "
            "engineering, architecture, health, entertainment, geopolitics. "
            "Volatility: perennial, volatile. Accepts comma-separated values."
        ),
    )
    run_parser.add_argument(
        "--video",
        dest="video_ids",
        nargs="*",
        default=None,
        metavar="VIDEO_ID",
        help=(
            "Restrict batch discovery to specific video IDs or YouTube watch URLs. "
            "Accepts comma-separated values."
        ),
    )
    run_parser.set_defaults(handler=handler)
