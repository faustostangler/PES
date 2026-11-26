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
from typing import Any, Final

import typer

from cresmo.presentation.error_handler import handle_cli_exception
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_SUCCESS,
)

_LANGFUSE_PK_PREVIEW_LENGTH: Final[int] = 10
_MASK_ELLIPSIS: Final[str] = "..."
_FALLBACK_CONFIG_ERROR_PREFIX: Final[str] = "Unexpected configuration error"


def load_fresh_settings(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import load_fresh_settings as _factory

    return _factory(*args, **kwargs)


def build_preflight_checker(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_preflight_checker as _factory

    return _factory(*args, **kwargs)


def check_config() -> None:
    """Validate runtime environment, storage paths, and secrets fail-fast."""
    code = handle_check_config()
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_check_config() -> int:
    """Validate runtime environment, storage paths, and secrets.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
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
        sys.stdout.write(f"- Vault Root: {settings.storage.vault_dir}\n")
        sys.stdout.write(f"- SQLite Ledger: {settings.storage.sqlite_ledger_path}\n")
        sys.stdout.write(f"- Gemini Model: {settings.llm.gemini.model}\n")
        if settings.llm.gemini.fallback_model:
            sys.stdout.write(f"- Gemini Fallback Model: {settings.llm.gemini.fallback_model}\n")
        if settings.llm.gemini.thinking_level:
            sys.stdout.write(f"- Gemini Thinking Level: {settings.llm.gemini.thinking_level}\n")
        if settings.judge.gemini.model:
            sys.stdout.write(f"- Judge Gemini Model: {settings.judge.gemini.model}\n")
        sys.stdout.write(f"- Batch Size: {settings.pipeline.batch_size}\n")
        langfuse_cfg = settings.observability.langfuse
        lf_pk = langfuse_cfg.public_key
        lf_sk = langfuse_cfg.secret_key
        lf_host = langfuse_cfg.host
        lf_env = langfuse_cfg.environment
        if lf_pk and lf_sk.get_secret_value():
            pk_masked = lf_pk[:_LANGFUSE_PK_PREVIEW_LENGTH] + _MASK_ELLIPSIS
            sys.stdout.write(
                f"- Langfuse Telemetry: Enabled ({lf_host}, env={lf_env}, {pk_masked})\n"
            )
        else:
            sys.stdout.write("- Langfuse Telemetry: Disabled (no credentials configured)\n")
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        return handle_cli_exception(exc, fallback_prefix=_FALLBACK_CONFIG_ERROR_PREFIX)
