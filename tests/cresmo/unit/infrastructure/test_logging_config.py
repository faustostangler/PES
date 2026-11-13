"""Unit tests for CresmoOTelTraceCorrelationFilter and configure_logging.

Conforms to:
    - ADR-025: Grafana Loki Structured Log Aggregation
    - ADR-016: OpenTelemetry trace correlation fields
    - ADR-020 Pillar 5: Canonical naming conventions
"""

from __future__ import annotations

import json
import logging
from collections.abc import Generator
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_logging_configured_sentinel() -> Generator[None]:
    """Reset module-level sentinel and logger levels between tests for hermetic isolation."""
    import cresmo.infrastructure.logging_config as lc_module

    def _reset() -> None:
        lc_module._LOGGING_CONFIGURED = False
        for name in (
            "httpx",
            "httpcore",
            "opentelemetry",
            "urllib3",
            "google_genai",
            "google_genai.models",
        ):
            if name in logging.Logger.manager.loggerDict:
                logging.getLogger(name).setLevel(logging.NOTSET)
        logging.root.handlers.clear()

    _reset()
    yield
    _reset()


class TestConfigureLoggingJsonFormat:
    """Verify JSON formatter produces Loki-compatible structured output."""

    def test_json_format_produces_valid_json(self) -> None:
        """Log message with fmt='json' must emit parseable JSON with required keys."""
        import sys

        import pythonjsonlogger.json

        from cresmo.infrastructure.logging_config import (
            CresmoOTelTraceCorrelationFilter,
            configure_logging,
        )

        configure_logging(level="DEBUG", fmt="json")
        console_handler = logging.root.handlers[0]
        assert isinstance(console_handler, logging.StreamHandler)
        assert console_handler.stream is sys.stdout
        assert isinstance(console_handler.formatter, pythonjsonlogger.json.JsonFormatter)
        expected_fmt = (
            "%(asctime)s %(name)s %(levelname)s %(message)s "
            "%(otelTraceID)s %(otelSpanID)s %(session_id)s"
        )
        assert console_handler.formatter._fmt == expected_fmt
        assert len(console_handler.filters) == 1
        assert isinstance(console_handler.filters[0], CresmoOTelTraceCorrelationFilter)

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
        import sys

        import pythonjsonlogger.json

        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="DEBUG", fmt="text")
        console_handler = logging.root.handlers[0]
        assert isinstance(console_handler, logging.StreamHandler)
        assert console_handler.stream is sys.stdout
        assert not isinstance(console_handler.formatter, pythonjsonlogger.json.JsonFormatter)
        assert console_handler.formatter is not None
        assert console_handler.formatter._fmt == "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

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
        from types import SimpleNamespace

        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        mock_ctx = MagicMock()
        mock_ctx.trace_id = 0x1111111111111111
        mock_ctx.span_id = 0x2222222222222222

        span_obj = SimpleNamespace(
            get_span_context=lambda: mock_ctx,
            attributes={"langfuse.session.id": "content:sandeco:ep042"},
        )

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
            "cresmo.infrastructure.logging_config.trace.get_current_span", return_value=span_obj
        ):
            log_filter.filter(record)

        assert record.session_id == "content:sandeco:ep042"  # type: ignore[attr-defined]


class TestNoisyLoggerSuppression:
    """Verify third-party logger levels are elevated to WARNING or ERROR."""

    def test_noisy_loggers_suppressed_after_configure(self) -> None:
        """httpx, httpcore, opentelemetry, urllib3 must be WARNING; google_genai must be ERROR."""
        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="DEBUG", fmt="json")

        for noisy in ("httpx", "httpcore", "opentelemetry", "urllib3"):
            assert logging.getLogger(noisy).level == logging.WARNING, (
                f"Logger '{noisy}' should be strictly WARNING"
            )
        for genai in ("google_genai", "google_genai.models"):
            assert logging.getLogger(genai).level == logging.ERROR, (
                f"Logger '{genai}' should be strictly ERROR"
            )


class TestConfigureLoggingLifecycle:
    """Verify configure_logging defaults, idempotency, and re-leveling."""

    def test_configure_logging_defaults(self) -> None:
        """Default call must set root logger to WARNING, sys.stdout, and format JSON."""
        import sys

        import pythonjsonlogger.json

        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging()
        assert logging.getLogger().level == logging.WARNING
        assert len(logging.root.handlers) > 0
        h = logging.root.handlers[0]
        assert isinstance(h, logging.StreamHandler)
        assert h.stream is sys.stdout
        assert isinstance(h.formatter, pythonjsonlogger.json.JsonFormatter)

    def test_configure_logging_idempotency_level_update(self) -> None:
        """Subsequent call must update root level without replacing handlers."""
        from cresmo.infrastructure.logging_config import configure_logging

        configure_logging(level="WARNING", fmt="json")
        initial_handler = logging.root.handlers[0]
        assert logging.getLogger().level == logging.WARNING

        configure_logging(level="INFO")
        assert logging.getLogger().level == logging.INFO
        assert logging.root.handlers[0] is initial_handler


class TestCresmoOTelTraceCorrelationFilterEdgeCases:
    """Edge cases for span context and attribute inspection."""

    def test_zero_trace_id_falls_back_to_zero_padded_string(self) -> None:
        """ctx with trace_id == 0 must emit 32 zeros."""
        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        mock_ctx = MagicMock()
        mock_ctx.trace_id = 0
        mock_ctx.span_id = 0

        mock_span = MagicMock()
        mock_span.get_span_context.return_value = mock_ctx
        mock_span.attributes = None

        log_filter = CresmoOTelTraceCorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="zero trace",
            args=(),
            exc_info=None,
        )

        with patch(
            "cresmo.infrastructure.logging_config.trace.get_current_span", return_value=mock_span
        ):
            assert log_filter.filter(record) is True

        assert record.otelTraceID == "0" * 32  # type: ignore[attr-defined]
        assert record.otelSpanID == "0" * 16  # type: ignore[attr-defined]
        assert record.session_id == ""  # type: ignore[attr-defined]

    def test_span_without_attributes_member(self) -> None:
        """Span lacking attributes attribute must leave session_id empty without error."""
        from cresmo.infrastructure.logging_config import CresmoOTelTraceCorrelationFilter

        class BareSpan:
            def get_span_context(self) -> None:
                return None

        log_filter = CresmoOTelTraceCorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="bare span",
            args=(),
            exc_info=None,
        )

        with patch(
            "cresmo.infrastructure.logging_config.trace.get_current_span", return_value=BareSpan()
        ):
            assert log_filter.filter(record) is True

        assert record.session_id == ""  # type: ignore[attr-defined]
