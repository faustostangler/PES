"""Hermetic unit tests for centralized CLI error handler.

Conforms to:
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

import io

import pytest
from pydantic import BaseModel, ValidationError

from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    QuotaPoolExhaustedError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.presentation.error_handler import (
    format_cli_error,
    handle_cli_exception,
    map_exception_to_exit_code,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
)


def _make_pydantic_validation_error() -> ValidationError:
    class _Dummy(BaseModel):
        count: int

    try:
        _Dummy.model_validate({"count": "not-an-int"})
    except ValidationError as exc:
        return exc
    raise AssertionError("Expected ValidationError")


class TestCliErrorHandler:
    """Unit tests verifying canonical exception-to-exit-code translation."""

    @pytest.mark.parametrize(
        ("exc", "expected_code", "expected_prefix"),
        [
            (
                QuotaPoolExhaustedError("pool empty", retry_after_seconds=12.0),
                EXIT_RATE_LIMIT_EXCEEDED,
                "Rate limit exceeded: pool empty",
            ),
            (
                RateLimitExceededError("429 upstream"),
                EXIT_RATE_LIMIT_EXCEEDED,
                "Rate limit exceeded: 429 upstream",
            ),
            (
                IngestionNetworkError("socket timeout"),
                EXIT_INGESTION_ERROR,
                "Ingestion network error: socket timeout",
            ),
            (
                PreflightError("ffmpeg missing"),
                EXIT_CONFIG_OR_USAGE_ERROR,
                "Preflight error: ffmpeg missing",
            ),
            (
                SecurityViolationError("path escape"),
                EXIT_CONFIG_OR_USAGE_ERROR,
                "Security boundary violation: path escape",
            ),
            (
                DomainValidationError("bad domain value"),
                EXIT_DOMAIN_VALIDATION_ERROR,
                "Domain validation error: bad domain value",
            ),
            (
                CresmoDomainError("invariant violated"),
                EXIT_DOMAIN_VALIDATION_ERROR,
                "Domain validation error: invariant violated",
            ),
            (
                RuntimeError("boom"),
                EXIT_INTERNAL_ERROR,
                "Unexpected internal error: boom",
            ),
        ],
    )
    def test_exception_mapping_and_formatting(
        self,
        exc: BaseException,
        expected_code: int,
        expected_prefix: str,
    ) -> None:
        assert map_exception_to_exit_code(exc) == expected_code
        assert format_cli_error(exc) == expected_prefix

    def test_validation_error_and_stream_writing(self) -> None:
        val_err = _make_pydantic_validation_error()
        stream = io.StringIO()
        code = handle_cli_exception(val_err, err_stream=stream)
        assert code == EXIT_CONFIG_OR_USAGE_ERROR
        assert stream.getvalue().startswith("Configuration error:")

        fallback_stream = io.StringIO()
        code2 = handle_cli_exception(
            RuntimeError("Disk error"),
            fallback_prefix="Deduplication error",
            err_stream=fallback_stream,
        )
        assert code2 == EXIT_INTERNAL_ERROR
        assert fallback_stream.getvalue() == "Deduplication error: Disk error\n"
