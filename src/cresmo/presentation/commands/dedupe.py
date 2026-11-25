"""Command handler for cresmo dedupe.

Orchestrates knowledge graph entity resolution, non-destructive note merging,
and cross-vault inbound WikiLink rewriting per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-001: Core Knowledge Synthesis Specifications (Deduplication)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from cresmo.presentation.error_handler import handle_cli_exception
from cresmo.presentation.exit_codes import EXIT_SUCCESS


def resolve_shared_settings(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import resolve_shared_settings as _factory

    return _factory(*args, **kwargs)


def build_unify_duplicates_use_case(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_unify_duplicates_use_case as _factory

    return _factory(*args, **kwargs)


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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Execute graph entity resolution, non-destructive merging, and link rewriting."""
    code = handle_dedupe(vault=vault, verbose=verbose)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_dedupe(
    vault: Path | None = None,
    verbose: bool = False,
) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph.

    Args:
        vault: Optional vault directory path override.
        verbose: Whether to emit extended diagnostics.

    Returns:
        Process exit code integer.
    """
    try:
        settings = resolve_shared_settings()
        if vault is not None:
            settings = settings.model_copy(
                update={"storage": settings.storage.model_copy(update={"vault_dir": vault})}
            )
        use_case = build_unify_duplicates_use_case(settings=settings)
        report = use_case.execute()
        if verbose:
            sys.stdout.write(f"Vault directory: {settings.storage.vault_dir}\n")
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
        return handle_cli_exception(exc, fallback_prefix="Deduplication error")
