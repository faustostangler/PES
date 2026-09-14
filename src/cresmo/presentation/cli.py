"""Cresmo Command-Line Interface (CLI) Entrypoint.

Follows the Humble Object pattern per Clean/Hexagonal Architecture.
Responsible solely for argument parsing, subcommand routing, and exit code propagation.
All domain workflows and command options reside in isolated command modules.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from cresmo.presentation.commands import (
    check_config,
    dedupe,
    run,
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

__all__ = [
    "EXIT_CONFIG_OR_USAGE_ERROR",
    "EXIT_DOMAIN_VALIDATION_ERROR",
    "EXIT_INGESTION_ERROR",
    "EXIT_INTERNAL_ERROR",
    "EXIT_RATE_LIMIT_EXCEEDED",
    "EXIT_SUCCESS",
    "_create_parser",
    "main",
]

COMMAND_MODULES = (
    run,
    check_config,
    sync,
    worker,
    dedupe,
)


def _create_parser() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
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
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "worker", "dedupe"}

    if not argv:
        argv = ["run"]
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-h", "--help")):
        argv = ["run", *argv]

    parser = _create_parser()

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
