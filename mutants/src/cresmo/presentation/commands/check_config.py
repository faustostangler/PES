"""Command handler for cresmo check-config."""

from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from cresmo.domain.exceptions import PreflightError
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_preflight_checker
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_register_subparser__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_subparser__mutmut)
def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_orig(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_1(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = None
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_2(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        None,
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_3(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help=None,
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_4(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_5(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_6(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "XXcheck-configXX",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_7(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "CHECK-CONFIG",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_8(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="XXValidate environment settings and vault access without calling LLMsXX",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_9(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="validate environment settings and vault access without calling llms",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_10(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="VALIDATE ENVIRONMENT SETTINGS AND VAULT ACCESS WITHOUT CALLING LLMS",
    )
    check_parser.set_defaults(handler=handle_check_config)


def x_register_subparser__mutmut_11(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=None)

mutants_x_register_subparser__mutmut['_mutmut_orig'] = x_register_subparser__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_1'] = x_register_subparser__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_2'] = x_register_subparser__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_3'] = x_register_subparser__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_4'] = x_register_subparser__mutmut_4 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_5'] = x_register_subparser__mutmut_5 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_6'] = x_register_subparser__mutmut_6 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_7'] = x_register_subparser__mutmut_7 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_8'] = x_register_subparser__mutmut_8 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_9'] = x_register_subparser__mutmut_9 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_10'] = x_register_subparser__mutmut_10 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_11'] = x_register_subparser__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_handle_check_config__mutmut)
def handle_check_config(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_orig(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_1(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = None
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_2(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = None
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_3(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=None)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_4(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = None
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_5(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_6(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write(None)
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_7(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("XXPreflight environmental checks failed:\nXX")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_8(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_9(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("PREFLIGHT ENVIRONMENTAL CHECKS FAILED:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_10(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(None)
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_11(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write(None)
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_12(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("XXConfiguration and environment verified successfully:\nXX")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_13(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_14(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("CONFIGURATION AND ENVIRONMENT VERIFIED SUCCESSFULLY:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_15(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_16(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_17(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_18(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(None)
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_19(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = None
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_20(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(None, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_21(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, None, "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_22(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", None)
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_23(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr("langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_24(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_25(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", )
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_26(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "XXlangfuse_public_keyXX", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_27(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "LANGFUSE_PUBLIC_KEY", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_28(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "XXXX")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_29(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = None
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_30(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(None, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_31(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, None, None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_32(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr("langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_33(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_34(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", )
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_35(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "XXlangfuse_secret_keyXX", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_36(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "LANGFUSE_SECRET_KEY", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_37(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = None
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_38(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(None, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_39(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, None, "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_40(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", None)
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_41(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr("langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_42(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_43(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", )
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_44(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "XXlangfuse_hostXX", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_45(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "LANGFUSE_HOST", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_46(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "XXhttps://cloud.langfuse.comXX")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_47(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "HTTPS://CLOUD.LANGFUSE.COM")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_48(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") or lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_49(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk or hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_50(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk or lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_51(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(None, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_52(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, None) and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_53(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr("get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_54(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, ) and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_55(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "XXget_secret_valueXX") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_56(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "GET_SECRET_VALUE") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_57(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = None
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_58(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] - "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_59(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:11] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_60(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "XX...XX"
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_61(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(None)
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_62(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write(None)
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_63(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("XX- Langfuse Telemetry: Disabled (no credentials configured)\nXX")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_64(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- langfuse telemetry: disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_65(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- LANGFUSE TELEMETRY: DISABLED (NO CREDENTIALS CONFIGURED)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_66(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_67(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected configuration error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_check_config__mutmut_68(args: argparse.Namespace) -> int:
    """Validate runtime environment, storage paths, and secrets."""
    try:
        settings = CresmoSettings()
        checker = build_preflight_checker(settings=settings)
        preflight = checker.check_all()
        if not preflight.is_healthy:
            sys.stderr.write("Preflight environmental checks failed:\n")
            for err in preflight.errors:
                sys.stderr.write(f"- {err}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR

        sys.stdout.write("Configuration and environment verified successfully:\n")
        sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(f"- Langfuse Telemetry: Enabled ({lf_host}, {pk_masked})\n")
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except ValidationError as exc:
        sys.stderr.write(f"Configuration validation error:\n{exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)
        return EXIT_INTERNAL_ERROR

mutants_x_handle_check_config__mutmut['_mutmut_orig'] = x_handle_check_config__mutmut_orig # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_1'] = x_handle_check_config__mutmut_1 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_2'] = x_handle_check_config__mutmut_2 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_3'] = x_handle_check_config__mutmut_3 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_4'] = x_handle_check_config__mutmut_4 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_5'] = x_handle_check_config__mutmut_5 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_6'] = x_handle_check_config__mutmut_6 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_7'] = x_handle_check_config__mutmut_7 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_8'] = x_handle_check_config__mutmut_8 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_9'] = x_handle_check_config__mutmut_9 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_10'] = x_handle_check_config__mutmut_10 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_11'] = x_handle_check_config__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_12'] = x_handle_check_config__mutmut_12 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_13'] = x_handle_check_config__mutmut_13 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_14'] = x_handle_check_config__mutmut_14 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_15'] = x_handle_check_config__mutmut_15 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_16'] = x_handle_check_config__mutmut_16 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_17'] = x_handle_check_config__mutmut_17 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_18'] = x_handle_check_config__mutmut_18 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_19'] = x_handle_check_config__mutmut_19 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_20'] = x_handle_check_config__mutmut_20 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_21'] = x_handle_check_config__mutmut_21 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_22'] = x_handle_check_config__mutmut_22 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_23'] = x_handle_check_config__mutmut_23 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_24'] = x_handle_check_config__mutmut_24 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_25'] = x_handle_check_config__mutmut_25 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_26'] = x_handle_check_config__mutmut_26 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_27'] = x_handle_check_config__mutmut_27 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_28'] = x_handle_check_config__mutmut_28 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_29'] = x_handle_check_config__mutmut_29 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_30'] = x_handle_check_config__mutmut_30 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_31'] = x_handle_check_config__mutmut_31 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_32'] = x_handle_check_config__mutmut_32 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_33'] = x_handle_check_config__mutmut_33 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_34'] = x_handle_check_config__mutmut_34 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_35'] = x_handle_check_config__mutmut_35 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_36'] = x_handle_check_config__mutmut_36 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_37'] = x_handle_check_config__mutmut_37 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_38'] = x_handle_check_config__mutmut_38 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_39'] = x_handle_check_config__mutmut_39 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_40'] = x_handle_check_config__mutmut_40 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_41'] = x_handle_check_config__mutmut_41 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_42'] = x_handle_check_config__mutmut_42 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_43'] = x_handle_check_config__mutmut_43 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_44'] = x_handle_check_config__mutmut_44 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_45'] = x_handle_check_config__mutmut_45 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_46'] = x_handle_check_config__mutmut_46 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_47'] = x_handle_check_config__mutmut_47 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_48'] = x_handle_check_config__mutmut_48 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_49'] = x_handle_check_config__mutmut_49 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_50'] = x_handle_check_config__mutmut_50 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_51'] = x_handle_check_config__mutmut_51 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_52'] = x_handle_check_config__mutmut_52 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_53'] = x_handle_check_config__mutmut_53 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_54'] = x_handle_check_config__mutmut_54 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_55'] = x_handle_check_config__mutmut_55 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_56'] = x_handle_check_config__mutmut_56 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_57'] = x_handle_check_config__mutmut_57 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_58'] = x_handle_check_config__mutmut_58 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_59'] = x_handle_check_config__mutmut_59 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_60'] = x_handle_check_config__mutmut_60 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_61'] = x_handle_check_config__mutmut_61 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_62'] = x_handle_check_config__mutmut_62 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_63'] = x_handle_check_config__mutmut_63 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_64'] = x_handle_check_config__mutmut_64 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_65'] = x_handle_check_config__mutmut_65 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_66'] = x_handle_check_config__mutmut_66 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_67'] = x_handle_check_config__mutmut_67 # type: ignore # mutmut generated
mutants_x_handle_check_config__mutmut['x_handle_check_config__mutmut_68'] = x_handle_check_config__mutmut_68 # type: ignore # mutmut generated
