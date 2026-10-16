"""Cresmo Command-Line Interface (CLI) Entrypoint.

Follows the Humble Object pattern per Clean/Hexagonal Architecture.
Responsible solely for argument parsing, subcommand routing, and exit code propagation.
All domain workflows and command options reside in isolated command modules.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Protocol

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
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class CommandModule(Protocol):
    """Structural protocol defining the contract for CLI subcommand modules."""

    def register_subparser(self, subparsers: argparse._SubParsersAction) -> None:
        """Register subcommand parser and default handler."""
        ...


__all__ = [
    "COMMAND_MODULES",
    "EXIT_CONFIG_OR_USAGE_ERROR",
    "EXIT_DOMAIN_VALIDATION_ERROR",
    "EXIT_INGESTION_ERROR",
    "EXIT_INTERNAL_ERROR",
    "EXIT_RATE_LIMIT_EXCEEDED",
    "EXIT_SUCCESS",
    "CommandModule",
    "_create_parser",
    "main",
]

COMMAND_MODULES: tuple[CommandModule, ...] = (
    run,
    check_config,
    sync,
    worker,
    dedupe,
    export_cookies,
    concat_master,
    seed_prompts,
)


def _create_parser() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers.

    Returns:
        Configured ArgumentParser with all registered subcommand handlers.
    """
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.

    Args:
        argv: Optional sequence of command-line argument strings. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer conforming to the exit code taxonomy in exit_codes.py.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    parser = _create_parser()

    # Dynamically extract registered subcommand choices from subparsers action
    subparsers_action = next(
        (action for action in parser._actions if isinstance(action, argparse._SubParsersAction)),
        None,
    )
    known_subcommands = set(subparsers_action.choices.keys()) if subparsers_action else set()

    # Default implicit command routing to 'run' if no subcommand is supplied
    if not argv:
        argv = ["run"]
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-h", "--help")):
        argv = ["run", *argv]

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
