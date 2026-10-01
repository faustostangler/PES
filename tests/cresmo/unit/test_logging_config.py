"""Unit tests for CresmoOTelTraceCorrelationFilter and configure_logging.

Conforms to:
    - ADR-025: Grafana Loki Structured Log Aggregation
    - ADR-016: OpenTelemetry trace correlation fields
    - ADR-020 Pillar 5: Canonical naming conventions
"""

from __future__ import annotations

import json
import logging
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_logging_configured_sentinel() -> None:
    """Reset module-level sentinel between tests for hermetic isolation.

    Ensures configure_logging() always runs its dictConfig block in each test,
    preventing test-ordering effects on the _LOGGING_CONFIGURED guard.
    """
    import cresmo.infrastructure.logging_config as lc_module

    lc_module._LOGGING_CONFIGURED = False
    yield
    lc_module._LOGGING_CONFIGURED = False


class TestConfigureLoggingJsonFormat:
    """Verify JSON formatter produces Loki-compatible structured output."""

    def test_json_format_produces_valid_json(self) -> None:
        """Log message with fmt='json' must emit parseable JSON with required keys."""
        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="DEBUG", fmt="json")

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.root.handlers[0].formatter)
        for f in logging.root.handlers[0].filters:
            handler.addFilter(f)

        test_logger = logging.getLogger("test.json_format")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.DEBUG)

        test_logger.info("Loki structured test message")

        output = stream.getvalue().strip()
        assert output, "Expected JSON log output on stdout"

        record = json.loads(output)
        assert record["message"] == "Loki structured test message"
        assert record["levelname"] == "INFO"
        assert "otelTraceID" in record
        assert "otelSpanID" in record
        assert "session_id" in record

        test_logger.removeHandler(handler)

    def test_text_format_produces_human_readable(self) -> None:
        """Log message with fmt='text' must emit plain bracketed format."""
        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="DEBUG", fmt="text")

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.root.handlers[0].formatter)

        test_logger = logging.getLogger("test.text_format")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.DEBUG)

        test_logger.info("Human readable test")

        output = stream.getvalue().strip()
        assert "[INFO]" in output
        assert "Human readable test" in output

        test_logger.removeHandler(handler)


class TestCresmoOTelTraceCorrelationFilter:
    """Verify OTel trace/span/session injection into log records."""

    def test_injects_zero_trace_when_no_active_span(self) -> None:
        """Without an active OTel span, trace fields must be zero-padded."""
        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        log_filter = CresmoOTelTraceCorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="no span",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert record.otelTraceID == "0" * 32  # type: ignore[attr-defined]
        assert record.otelSpanID == "0" * 16  # type: ignore[attr-defined]
        assert record.session_id == ""  # type: ignore[attr-defined]

    def test_injects_real_trace_id_under_active_span(self) -> None:
        """With a mocked active span, trace_id must be formatted as 32-char hex."""
        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        mock_ctx = MagicMock()
        mock_ctx.trace_id = 0xABCDEF1234567890ABCDEF1234567890
        mock_ctx.span_id = 0x1234567890ABCDEF

        mock_span = MagicMock()
        mock_span.get_span_context.return_value = mock_ctx
        mock_span.attributes = {}

        log_filter = CresmoOTelTraceCorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="with span",
            args=(),
            exc_info=None,
        )

        with patch(
            "cresmo.infrastructure.logging_config.trace.get_current_span", return_value=mock_span
        ):
            result = log_filter.filter(record)

        assert result is True
        assert record.otelTraceID == format(0xABCDEF1234567890ABCDEF1234567890, "032x")  # type: ignore[attr-defined]
        assert record.otelSpanID == format(0x1234567890ABCDEF, "016x")  # type: ignore[attr-defined]

    def test_session_id_extracted_from_span_attributes(self) -> None:
        """session_id must be extracted from langfuse.session.id span attribute."""
        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        mock_ctx = MagicMock()
        mock_ctx.trace_id = 0x1111111111111111
        mock_ctx.span_id = 0x2222222222222222

        mock_span = MagicMock()
        mock_span.get_span_context.return_value = mock_ctx
        mock_span.attributes = {"langfuse.session.id": "content:sandeco:ep042"}

        log_filter = CresmoOTelTraceCorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="session test",
            args=(),
            exc_info=None,
        )

        with patch(
            "cresmo.infrastructure.logging_config.trace.get_current_span", return_value=mock_span
        ):
            log_filter.filter(record)

        assert record.session_id == "content:sandeco:ep042"  # type: ignore[attr-defined]


class TestNoisyLoggerSuppression:
    """Verify third-party logger levels are elevated to WARNING."""

    def test_noisy_loggers_suppressed_after_configure(self) -> None:
        """httpx, httpcore, opentelemetry, urllib3 must be WARNING or higher."""
        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="DEBUG", fmt="json")

        for noisy in ("httpx", "httpcore", "opentelemetry", "urllib3"):
            assert logging.getLogger(noisy).level >= logging.WARNING, (
                f"Logger '{noisy}' should be suppressed to WARNING or higher"
            )
