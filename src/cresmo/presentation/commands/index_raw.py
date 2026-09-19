"""CLI command handler for cresmo index-raw.

Performs offline paratactic conceptual indexing of raw transcripts into channel-specific
semantic catalogs (_canal.md) and the global tabular registry (brain.csv).

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Raw Transcript Indexing)
"""

from __future__ import annotations

import argparse
import sys

from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_index_raw_use_case,
    build_preflight_checker,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'index-raw' subcommand parser with argument options.

    Args:
        subparsers: Root CLI subparsers action object.
    """
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
    """Handle execution of cresmo index-raw.

    Args:
        args: Parsed CLI argument namespace containing channel, web_index, model, and force options.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        settings.ensure_directories()

        if not args.web_index and getattr(settings, "enable_preflight_probes", True):
            timeout = getattr(settings, "preflight_probe_timeout_seconds", 1.0)
            preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=False)
            if not preflight_checker.check_ollama_probe(
                settings.ollama_base_url, timeout_seconds=timeout
            ):
                sys.stderr.write(
                    f"[preflight] Local Ollama daemon at '{settings.ollama_base_url}' is unreachable.\n"
                    "            Run 'ollama serve' to start Ollama or pass '--web-index' to use cloud Gemini API.\n"
                )
                return EXIT_CONFIG_OR_USAGE_ERROR

        use_case = build_index_raw_use_case(
            settings=settings,
            web_index=args.web_index,
            model_override=args.model,
        )

        provider_name = (
            "Gemini Cloud API"
            if args.web_index
            else f"Local Ollama ({args.model or settings.ollama_model})"
        )
        sys.stdout.write(f"Starting raw transcript conceptual indexing using {provider_name}...\n")

        if not args.web_index:
            effective_model = args.model or settings.ollama_model
            sys.stdout.write(
                f"Dispatched background warmup for local Ollama model '{effective_model}' "
                f"(keepalive: {settings.ollama_keep_alive})...\n"
            )
            use_case.llm.warmup()

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
