"""Centralized CLI exception-to-exit-code mapper for Humble Presentation commands.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

import sys
from typing import TextIO

from pydantic import ValidationError

from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
)

_EXCEPTION_MAPPINGS: tuple[tuple[type[BaseException], int, str], ...] = (
    (RateLimitExceededError, EXIT_RATE_LIMIT_EXCEEDED, "Rate limit exceeded"),
    (IngestionNetworkError, EXIT_INGESTION_ERROR, "Ingestion network error"),
    (PreflightError, EXIT_CONFIG_OR_USAGE_ERROR, "Preflight error"),
    (SecurityViolationError, EXIT_CONFIG_OR_USAGE_ERROR, "Security boundary violation"),
    (DomainValidationError, EXIT_DOMAIN_VALIDATION_ERROR, "Domain validation error"),
    (CresmoDomainError, EXIT_DOMAIN_VALIDATION_ERROR, "Domain validation error"),
    (ValidationError, EXIT_CONFIG_OR_USAGE_ERROR, "Configuration error"),
)


def map_exception_to_exit_code(exc: BaseException) -> int:
    """Translate domain, validation, preflight, network, or runtime exceptions to exit codes.

    Args:
        exc: Raised exception instance.

    Returns:
        Canonical integer process exit code from ``exit_codes.py``.
    """
    for exc_type, exit_code, _ in _EXCEPTION_MAPPINGS:
        if isinstance(exc, exc_type):
            return exit_code
    return EXIT_INTERNAL_ERROR


def format_cli_error(
    exc: BaseException,
    *,
    fallback_prefix: str = "Unexpected internal error",
) -> str:
    """Format a user-facing error message line without trailing newline.

    Args:
        exc: Raised exception instance.
        fallback_prefix: Prefix used when ``exc`` has no domain/validation mapping.

    Returns:
        Formatted single-line diagnostic string without trailing newline.
    """
    for exc_type, _, prefix in _EXCEPTION_MAPPINGS:
        if isinstance(exc, exc_type):
            return f"{prefix}: {exc}"
    return f"{fallback_prefix}: {exc}"


def handle_cli_exception(
    exc: BaseException,
    *,
    fallback_prefix: str = "Unexpected internal error",
    err_stream: TextIO | None = None,
) -> int:
    """Write formatted error to stderr stream and return canonical process exit code.

    Args:
        exc: Raised exception instance.
        fallback_prefix: Fallback diagnostic prefix for unexpected errors.
        err_stream: Optional text stream override defaulting to ``sys.stderr``.

    Returns:
        Canonical integer process exit code from ``exit_codes.py``.
    """
    stream = err_stream or sys.stderr
    stream.write(f"{format_cli_error(exc, fallback_prefix=fallback_prefix)}\n")
    return map_exception_to_exit_code(exc)
