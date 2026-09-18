"""Command handler for cresmo dedupe.

Orchestrates Stage 7 knowledge graph entity resolution, non-destructive note merging,
and cross-vault inbound WikiLink rewriting per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Stage 7: Deduplication)
"""

from __future__ import annotations

import argparse
import sys

from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_unify_duplicates_use_case
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser.

    Args:
        subparsers: Root CLI subparsers action object.
    """
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def handle_dedupe(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        use_case = build_unify_duplicates_use_case(settings=settings)
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR
