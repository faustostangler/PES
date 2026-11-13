"""Cresmo Command-Line Interface (CLI) Entrypoint.

Follows the Humble Object pattern per Clean/Hexagonal Architecture.
Responsible solely for Typer argument parsing, subcommand routing, and exit code propagation.
All domain workflows and command options reside in isolated command modules.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-042: Modern Typer Presentation CLI Driving Adapter
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-042: Modern Typer Presentation CLI Specifications
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

import click
import typer

from cresmo.presentation.commands import (
    check_config,
    concat_master,
    dedupe,
    export_cookies,
    run,
    seed_prompts,
    sync,
    worker,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

__all__ = [
    "app",
    "main",
]

app = typer.Typer(
    name="cresmo",
    help="Cresmo Knowledge Synthesis",
    no_args_is_help=True,
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.command(
    name="run",
    help="Run end-to-end knowledge synthesis for a video or manifest playlist",
)(run)

app.command(
    name="check-config",
    help="Validate runtime environment, storage paths, and secrets fail-fast",
)(check_config)

app.command(
    name="sync",
    help="Poll and synchronize video feeds from YouTube channels or playlists",
)(sync)

app.command(
    name="worker",
    help="Run continuous polling worker daemon with heartbeat health reporting",
)(worker)

app.command(
    name="dedupe",
    help="Execute graph entity resolution, non-destructive merging, and link rewriting",
)(dedupe)

app.command(
    name="export-cookies",
    help="Extract and validate YouTube authentication cookies from installed web browsers",
)(export_cookies)

app.command(
    name="concat-master",
    help="Consolidate enriched compendiums in ascending chronological order into master RAG files",
)(concat_master)

app.command(
    name="seed-prompts",
    help="Synchronize canonical prompt templates into Langfuse prompt management",
)(seed_prompts)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002, SPEC-042, and ADR-042: Humble Object CLI Controller
    with strictly segregated process exit codes.

    Args:
        argv: Optional sequence of command-line argument strings. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer conforming to the exit code taxonomy in exit_codes.py.
    """
    try:
        res = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return EXIT_SUCCESS if res is None else int(res)
    except typer.Exit as exc:
        return exc.exit_code
    except typer.exceptions.TyperException as exc:
        return getattr(exc, "exit_code", EXIT_CONFIG_OR_USAGE_ERROR)
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        return getattr(exc, "exit_code", EXIT_CONFIG_OR_USAGE_ERROR)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
