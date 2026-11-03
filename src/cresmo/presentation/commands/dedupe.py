"""Command handler for cresmo dedupe.

Orchestrates knowledge graph entity resolution, non-destructive note merging,
and cross-vault inbound WikiLink rewriting per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Deduplication)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from cresmo.presentation.composition import (
    build_unify_duplicates_use_case,
    resolve_shared_settings,
)
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def dedupe(
    vault: Annotated[
        Path | None,
        typer.Option(
            "--vault",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help="Path to Obsidian vault directory override",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Simulate deduplication without modifying notes"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Execute graph entity resolution, non-destructive merging, and link rewriting."""
    code = handle_dedupe(vault=vault, dry_run=dry_run, verbose=verbose)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_dedupe(
    args: Any = None,
    vault: Path | None = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph.

    Args:
        args: Parsed CLI argument namespace or None.
        vault: Optional vault directory path override.
        dry_run: Whether to simulate deduplication without modifying disk.
        verbose: Whether to emit extended diagnostics.

    Returns:
        Process exit code integer.
    """
    if args is not None:
        vault = getattr(args, "vault", vault)
        dry_run = getattr(args, "dry_run", dry_run)
        verbose = getattr(args, "verbose", verbose)

    try:
        settings = resolve_shared_settings()
        if vault is not None:
            settings = settings.model_copy(update={"vault_dir": vault})
        use_case = build_unify_duplicates_use_case(settings=settings)
        report = use_case.execute()
        if verbose:
            sys.stdout.write(f"Vault directory: {settings.vault_dir}\n")
            sys.stdout.write(f"Dry-run mode: {dry_run}\n")
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
