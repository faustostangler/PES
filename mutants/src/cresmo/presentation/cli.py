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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__create_parser__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__create_parser__mutmut)
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


def x__create_parser__mutmut_orig() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_1() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = None
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_2() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog=None,
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_3() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description=None,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_4() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_5() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_6() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="XXcresmoXX",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_7() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="CRESMO",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_8() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="XXCresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)XX",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_9() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="cresmo knowledge synthesis cli (hexagonal modular monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_10() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="CRESMO KNOWLEDGE SYNTHESIS CLI (HEXAGONAL MODULAR MONOLITH)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_11() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = None

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_12() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest=None, help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_13() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help=None)

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_14() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_15() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", )

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_16() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="XXsubcommandXX", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_17() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="SUBCOMMAND", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_18() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="XXAvailable subcommandsXX")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_19() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_20() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="AVAILABLE SUBCOMMANDS")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(subparsers)

    return parser


def x__create_parser__mutmut_21() -> argparse.ArgumentParser:
    """Construct root parser and register command subparsers."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd_module in COMMAND_MODULES:
        cmd_module.register_subparser(None)

    return parser

mutants_x__create_parser__mutmut['_mutmut_orig'] = x__create_parser__mutmut_orig # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_1'] = x__create_parser__mutmut_1 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_2'] = x__create_parser__mutmut_2 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_3'] = x__create_parser__mutmut_3 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_4'] = x__create_parser__mutmut_4 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_5'] = x__create_parser__mutmut_5 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_6'] = x__create_parser__mutmut_6 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_7'] = x__create_parser__mutmut_7 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_8'] = x__create_parser__mutmut_8 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_9'] = x__create_parser__mutmut_9 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_10'] = x__create_parser__mutmut_10 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_11'] = x__create_parser__mutmut_11 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_12'] = x__create_parser__mutmut_12 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_13'] = x__create_parser__mutmut_13 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_14'] = x__create_parser__mutmut_14 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_15'] = x__create_parser__mutmut_15 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_16'] = x__create_parser__mutmut_16 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_17'] = x__create_parser__mutmut_17 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_18'] = x__create_parser__mutmut_18 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_19'] = x__create_parser__mutmut_19 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_20'] = x__create_parser__mutmut_20 # type: ignore # mutmut generated
mutants_x__create_parser__mutmut['x__create_parser__mutmut_21'] = x__create_parser__mutmut_21 # type: ignore # mutmut generated
mutants_x_main__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_main__mutmut)
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


def x_main__mutmut_orig(argv: Sequence[str] | None = None) -> int:
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


def x_main__mutmut_1(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is not None:
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


def x_main__mutmut_2(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = None
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


def x_main__mutmut_3(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[2:]
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


def x_main__mutmut_4(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = None

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


def x_main__mutmut_5(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(None)

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


def x_main__mutmut_6(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = None

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


def x_main__mutmut_7(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"XXrunXX", "check-config", "sync", "worker", "dedupe"}

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


def x_main__mutmut_8(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"RUN", "check-config", "sync", "worker", "dedupe"}

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


def x_main__mutmut_9(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "XXcheck-configXX", "sync", "worker", "dedupe"}

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


def x_main__mutmut_10(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "CHECK-CONFIG", "sync", "worker", "dedupe"}

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


def x_main__mutmut_11(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "XXsyncXX", "worker", "dedupe"}

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


def x_main__mutmut_12(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "SYNC", "worker", "dedupe"}

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


def x_main__mutmut_13(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "XXworkerXX", "dedupe"}

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


def x_main__mutmut_14(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "WORKER", "dedupe"}

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


def x_main__mutmut_15(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "worker", "XXdedupeXX"}

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


def x_main__mutmut_16(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "worker", "DEDUPE"}

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


def x_main__mutmut_17(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002: Humble Object CLI Controller with strictly segregated
    process exit codes and dependency injection via composition root.
    """
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)

    known_subcommands = {"run", "check-config", "sync", "worker", "dedupe"}

    if argv:
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


def x_main__mutmut_18(argv: Sequence[str] | None = None) -> int:
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
        argv = None
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


def x_main__mutmut_19(argv: Sequence[str] | None = None) -> int:
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
        argv = ["XXrunXX"]
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


def x_main__mutmut_20(argv: Sequence[str] | None = None) -> int:
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
        argv = ["RUN"]
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


def x_main__mutmut_21(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands or not argv[0].startswith(("-h", "--help")):
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


def x_main__mutmut_22(argv: Sequence[str] | None = None) -> int:
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
    elif argv[1] not in known_subcommands and not argv[0].startswith(("-h", "--help")):
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


def x_main__mutmut_23(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] in known_subcommands and not argv[0].startswith(("-h", "--help")):
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


def x_main__mutmut_24(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and argv[0].startswith(("-h", "--help")):
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


def x_main__mutmut_25(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[0].startswith(None):
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


def x_main__mutmut_26(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[1].startswith(("-h", "--help")):
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


def x_main__mutmut_27(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[0].startswith(("XX-hXX", "--help")):
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


def x_main__mutmut_28(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-H", "--help")):
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


def x_main__mutmut_29(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-h", "XX--helpXX")):
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


def x_main__mutmut_30(argv: Sequence[str] | None = None) -> int:
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
    elif argv[0] not in known_subcommands and not argv[0].startswith(("-h", "--HELP")):
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


def x_main__mutmut_31(argv: Sequence[str] | None = None) -> int:
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
        argv = None

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


def x_main__mutmut_32(argv: Sequence[str] | None = None) -> int:
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
        argv = ["XXrunXX", *argv]

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


def x_main__mutmut_33(argv: Sequence[str] | None = None) -> int:
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
        argv = ["RUN", *argv]

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


def x_main__mutmut_34(argv: Sequence[str] | None = None) -> int:
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

    parser = None

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


def x_main__mutmut_35(argv: Sequence[str] | None = None) -> int:
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
        args = None
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_36(argv: Sequence[str] | None = None) -> int:
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
        args = parser.parse_args(None)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_37(argv: Sequence[str] | None = None) -> int:
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
        if exc.code != 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_38(argv: Sequence[str] | None = None) -> int:
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
        if exc.code == 1:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_39(argv: Sequence[str] | None = None) -> int:
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

    handler = None
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_40(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(None, "handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_41(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(args, None, None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_42(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr("handler", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_43(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(args, None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_44(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(args, "handler", )
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_45(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(args, "XXhandlerXX", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_46(argv: Sequence[str] | None = None) -> int:
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

    handler = getattr(args, "HANDLER", None)
    if handler is not None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_47(argv: Sequence[str] | None = None) -> int:
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
    if handler is None:
        return handler(args)

    return EXIT_CONFIG_OR_USAGE_ERROR


def x_main__mutmut_48(argv: Sequence[str] | None = None) -> int:
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
        return handler(None)

    return EXIT_CONFIG_OR_USAGE_ERROR

mutants_x_main__mutmut['_mutmut_orig'] = x_main__mutmut_orig # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_1'] = x_main__mutmut_1 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_2'] = x_main__mutmut_2 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_3'] = x_main__mutmut_3 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_4'] = x_main__mutmut_4 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_5'] = x_main__mutmut_5 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_6'] = x_main__mutmut_6 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_7'] = x_main__mutmut_7 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_8'] = x_main__mutmut_8 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_9'] = x_main__mutmut_9 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_10'] = x_main__mutmut_10 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_11'] = x_main__mutmut_11 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_12'] = x_main__mutmut_12 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_13'] = x_main__mutmut_13 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_14'] = x_main__mutmut_14 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_15'] = x_main__mutmut_15 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_16'] = x_main__mutmut_16 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_17'] = x_main__mutmut_17 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_18'] = x_main__mutmut_18 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_19'] = x_main__mutmut_19 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_20'] = x_main__mutmut_20 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_21'] = x_main__mutmut_21 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_22'] = x_main__mutmut_22 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_23'] = x_main__mutmut_23 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_24'] = x_main__mutmut_24 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_25'] = x_main__mutmut_25 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_26'] = x_main__mutmut_26 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_27'] = x_main__mutmut_27 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_28'] = x_main__mutmut_28 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_29'] = x_main__mutmut_29 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_30'] = x_main__mutmut_30 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_31'] = x_main__mutmut_31 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_32'] = x_main__mutmut_32 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_33'] = x_main__mutmut_33 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_34'] = x_main__mutmut_34 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_35'] = x_main__mutmut_35 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_36'] = x_main__mutmut_36 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_37'] = x_main__mutmut_37 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_38'] = x_main__mutmut_38 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_39'] = x_main__mutmut_39 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_40'] = x_main__mutmut_40 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_41'] = x_main__mutmut_41 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_42'] = x_main__mutmut_42 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_43'] = x_main__mutmut_43 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_44'] = x_main__mutmut_44 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_45'] = x_main__mutmut_45 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_46'] = x_main__mutmut_46 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_47'] = x_main__mutmut_47 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_48'] = x_main__mutmut_48 # type: ignore # mutmut generated


if __name__ == "__main__":
    sys.exit(main())
