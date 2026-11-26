"""Command handler for cresmo concat-master.

Consolidates enriched markdown documents into sequential master documents per channel category.
Applies bounded word thresholds (default: 500k words) without splitting individual documents.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Master RAG Consolidation)
"""

from __future__ import annotations

import sys
from typing import Annotated, Any, Final

import typer

from cresmo.domain.value_objects import ChannelName
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

_MIN_MAX_WORDS: Final[int] = 1


def resolve_shared_settings(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import resolve_shared_settings as _factory

    return _factory(*args, **kwargs)


def build_concat_master_use_case(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_concat_master_use_case as _factory

    return _factory(*args, **kwargs)


def concat_master(
    channel: Annotated[
        str | None,
        typer.Option(
            "--channel",
            "-c",
            help="Target specific channel name to consolidate (default: all channels in wide_expander/)",
        ),
    ] = None,
    max_words: Annotated[
        int | None,
        typer.Option(
            "--max-words",
            "-w",
            min=_MIN_MAX_WORDS,
            help="Maximum word count per master document (default: 500,000, never splitting files in the middle)",
        ),
    ] = None,
) -> None:
    """Consolidate enriched compendiums into master documents."""
    code = handle_concat_master(channel=channel, max_words=max_words)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_concat_master(
    channel: str | None = None,
    max_words: int | None = None,
) -> int:
    """Consolidate enriched compendiums into master documents.

    Args:
        channel: Optional channel name string override.
        max_words: Optional maximum words per master document override.

    Returns:
        Process exit code integer.
    """
    try:
        settings = resolve_shared_settings()
        use_case = build_concat_master_use_case(settings=settings)

        if channel:
            sys.stdout.write(f"Consolidating master documents for channel: '{channel}'...\n")
            results = use_case.execute(channel_name=ChannelName(channel), max_words=max_words)
            if not results:
                sys.stdout.write(f"No enriched documents found for channel '{channel}'.\n")
                return EXIT_SUCCESS

            total_words = sum(r.word_count for r in results)
            sys.stdout.write(
                f"Generated {len(results)} master document(s) for '{channel}' ({total_words:,} words):\n"
            )
            for r in results:
                sys.stdout.write(
                    f"  • Part {r.part_number:03d} -> {r.output_path.name} "
                    f"({r.word_count:,} words, {r.document_count} documents)\n"
                )
            return EXIT_SUCCESS

        sys.stdout.write(
            "Consolidating master documents across all channels in wide_expander/...\n"
        )
        all_results = use_case.execute_all(max_words=max_words)
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
