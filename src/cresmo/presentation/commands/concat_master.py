"""Command handler for cresmo concat-master.

Consolidates enriched markdown documents into sequential master documents per channel category.
Applies bounded word thresholds (default: 500k words) without splitting individual documents.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Master RAG Consolidation)
"""

from __future__ import annotations

import argparse
import sys

from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_concat_master_use_case
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'concat-master' subcommand parser.

    Args:
        subparsers: Root CLI subparsers action object.
    """
    concat_parser = subparsers.add_parser(
        "concat-master",
        help="Consolidate enriched compendiums in ascending chronological order into master RAG files",
    )
    concat_parser.add_argument(
        "--channel",
        "-c",
        type=str,
        default=None,
        help="Target specific channel name to consolidate (default: all channels in enriched/)",
    )
    concat_parser.add_argument(
        "--max-words",
        "-w",
        type=int,
        default=None,
        help="Maximum word count per master document (default: 500,000, never splitting files in the middle)",
    )
    concat_parser.set_defaults(handler=handle_concat_master)


def handle_concat_master(args: argparse.Namespace) -> int:
    """Consolidate enriched compendiums into master documents.

    Args:
        args: Parsed CLI argument namespace containing channel filter and word limits.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        use_case = build_concat_master_use_case(settings=settings)

        if args.channel:
            sys.stdout.write(f"Consolidating master documents for channel: '{args.channel}'...\n")
            results = use_case.execute_for_channel(
                channel_name=args.channel, max_words=args.max_words
            )
            if not results:
                sys.stdout.write(f"No enriched documents found for channel '{args.channel}'.\n")
                return EXIT_SUCCESS

            total_words = sum(r.word_count for r in results)
            sys.stdout.write(
                f"Generated {len(results)} master document(s) for '{args.channel}' ({total_words:,} words):\n"
            )
            for r in results:
                sys.stdout.write(
                    f"  • Part {r.part_number:03d} -> {r.output_path.name} "
                    f"({r.word_count:,} words, {r.document_count} documents)\n"
                )
            return EXIT_SUCCESS

        sys.stdout.write("Consolidating master documents across all channels in enriched/...\n")
        all_results = use_case.execute_all(max_words=args.max_words)
        if not all_results:
            sys.stdout.write("No enriched channel directories found to consolidate.\n")
            return EXIT_SUCCESS

        total_files = sum(len(parts) for parts in all_results.values())
        total_words = sum(sum(p.word_count for p in parts) for parts in all_results.values())

        sys.stdout.write(
            f"\nMaster Consolidation Summary:\n"
            f"- Total Channels Processed: {len(all_results)}\n"
            f"- Master Documents Generated: {total_files}\n"
            f"- Total Words Aggregated: {total_words:,}\n"
        )
        for parts in all_results.values():
            for p in parts:
                sys.stdout.write(
                    f"  ✓ [{p.channel_category}] {p.output_path.name} "
                    f"({p.word_count:,} words, {p.document_count} docs)\n"
                )

        return EXIT_SUCCESS

    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Master consolidation error: {exc}\n")
        return EXIT_INTERNAL_ERROR
