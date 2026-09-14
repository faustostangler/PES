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


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'check-config' subcommand parser."""
    check_parser = subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )
    check_parser.set_defaults(handler=handle_check_config)


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
