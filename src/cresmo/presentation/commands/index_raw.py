"""CLI command handler for cresmo index-raw.

Performs offline paratactic conceptual indexing of raw transcripts into channel-specific
semantic catalogs (_canal.md) and the global tabular registry (brain.csv).
"""

from __future__ import annotations

import argparse
import sys

from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_index_raw_use_case
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'index-raw' subcommand parser with argument options."""
    index_parser = subparsers.add_parser(
        "index-raw",
        help="Incrementally index raw transcripts into channel catalog (_canal.md) and brain.csv",
    )
    index_parser.add_argument(
        "--channel",
        required=False,
        default=None,
        help="Optional target channel name to index (default: all channels in data/raw)",
    )
    index_parser.add_argument(
        "--web-index",
        action="store_true",
        default=False,
        help="Use Gemini cloud API instead of local Ollama for conceptual synthesis",
    )
    index_parser.add_argument(
        "--model",
        required=False,
        default=None,
        help="Model override (e.g. 'qwen2.5:7b', 'gemma2:2b', or Gemini model name)",
    )
    index_parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force re-indexing and update existing entries",
    )
    index_parser.set_defaults(handler=handle_index_raw)


def handle_index_raw(args: argparse.Namespace) -> int:
    """Handle execution of cresmo index-raw."""
    try:
        settings = CresmoSettings()
        settings.ensure_directories()

        use_case = build_index_raw_use_case(
            settings=settings,
            web_index=args.web_index,
            model_override=args.model,
        )

        provider_name = "Gemini Cloud API" if args.web_index else f"Local Ollama ({args.model or settings.ollama_model})"
        sys.stdout.write(f"Starting raw transcript conceptual indexing using {provider_name}...\n")

        if args.channel:
            sys.stdout.write(f"Indexing channel: {args.channel}\n")
            entries = use_case.index_channel(args.channel, force=args.force)
            sys.stdout.write(
                f"Completed: {len(entries)} transcript(s) indexed for channel '{args.channel}'.\n"
            )
        else:
            sys.stdout.write("Indexing all channels in data/raw/...\n")
            all_results = use_case.index_all_channels(force=args.force)
            total_indexed = sum(len(entries) for entries in all_results.values())
            sys.stdout.write(
                f"Completed: {total_indexed} transcript(s) indexed across {len(all_results)} channel(s).\n"
            )

        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Error during raw transcript indexing: {exc}\n")
        return EXIT_INTERNAL_ERROR
