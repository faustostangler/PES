"""Command handler for cresmo check-config.

Validates environment settings, secret credentials, runtime storage directories,
and external binaries (ffmpeg) without making billable LLM API requests.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-005: Operational Staging Validation
"""

from __future__ import annotations

import sys
from typing import Any

import typer

from cresmo.bootstrap.composition import (
    build_preflight_checker,
    load_fresh_settings,
)
from cresmo.presentation.error_handler import handle_cli_exception
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_SUCCESS,
)


def check_config() -> None:
    """Validate runtime environment, storage paths, and secrets fail-fast."""
    code = handle_check_config(None)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_check_config(args: Any = None) -> int:
    """Validate runtime environment, storage paths, and secrets.

    Args:
        args: Unused legacy positional parameter kept only for zero-arg direct calls.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    _ = args
    try:
        settings = load_fresh_settings()
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
        fallback_model = getattr(settings, "gemini_fallback_model", None)
        if isinstance(fallback_model, str) and fallback_model:
            sys.stdout.write(f"- Gemini Fallback Model: {fallback_model}\n")
        thinking_level = getattr(settings, "gemini_thinking_level", None)
        if isinstance(thinking_level, str) and thinking_level:
            sys.stdout.write(f"- Gemini Thinking Level: {thinking_level}\n")
        judge_model = getattr(settings, "judge_gemini_model", None)
        if isinstance(judge_model, str) and judge_model:
            sys.stdout.write(f"- Judge Gemini Model: {judge_model}\n")
        sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
        lf_pk = getattr(settings, "langfuse_public_key", "")
        lf_sk = getattr(settings, "langfuse_secret_key", None)
        lf_host = getattr(settings, "langfuse_host", "https://cloud.langfuse.com")
        lf_env = getattr(settings, "langfuse_environment", "staging")
        if lf_pk and lf_sk and hasattr(lf_sk, "get_secret_value") and lf_sk.get_secret_value():
            pk_masked = lf_pk[:10] + "..."
            sys.stdout.write(
                f"- Langfuse Telemetry: Enabled ({lf_host}, env={lf_env}, {pk_masked})\n"
            )
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        return handle_cli_exception(exc, fallback_prefix="Unexpected configuration error")
