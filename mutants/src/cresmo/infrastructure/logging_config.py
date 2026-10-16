"""Centralized structured logging for Loki integration per ADR-025.

Configures stdlib logging with JSON formatter (python-json-logger) and
OpenTelemetry trace correlation filter for Grafana Loki -> Langfuse pivot.
"""

from __future__ import annotations

import logging
import logging.config
from typing import Any

from opentelemetry import trace


class CresmoOTelTraceCorrelationFilter(logging.Filter):
    """Inject OTel trace_id, span_id, and session_id into every log record.

    Enables Grafana Loki -> Langfuse trace correlation per ADR-016 Section 2.2
    and ADR-020 Pillar 5 canonical naming.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Enrich LogRecord with otelTraceID, otelSpanID, and session_id."""
        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        if ctx and ctx.trace_id:
            record.otelTraceID = format(ctx.trace_id, "032x")
            record.otelSpanID = format(ctx.span_id, "016x")
        else:
            record.otelTraceID = "0" * 32
            record.otelSpanID = "0" * 16

        record.session_id = ""
        if hasattr(span, "attributes") and span.attributes:
            sid = span.attributes.get("langfuse.session.id")
            if sid:
                record.session_id = str(sid)
        return True


_LOGGING_CONFIGURED: bool = False


def configure_logging(level: str = "WARNING", fmt: str = "json") -> None:
    """Configure root logger with JSON or text formatter.

    Idempotent: subsequent calls with the same arguments are no-ops. Calling
    with different arguments reconfigures. This prevents test-session stream
    replacement when composition root is exercised across multiple unit tests.

    Args:
        level: Root log level string.
        fmt: 'json' for Loki-compatible structured output, 'text' for dev.
    """
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        # Only update root level; do not replace handlers (avoids closed-stream
        # I/O errors in pytest when dictConfig replaces stdout StreamHandlers).
        logging.getLogger().setLevel(level.upper())
        return
    _LOGGING_CONFIGURED = True

    if fmt == "json":
        formatter_cfg: dict[str, Any] = {
            "class": "pythonjsonlogger.json.JsonFormatter",
            "format": (
                "%(asctime)s %(name)s %(levelname)s %(message)s "
                "%(otelTraceID)s %(otelSpanID)s %(session_id)s"
            ),
        }
    else:
        formatter_cfg = {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"otel_trace": {"()": CresmoOTelTraceCorrelationFilter}},
            "formatters": {"default": formatter_cfg},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                    "filters": ["otel_trace"],
                },
            },
            "root": {"level": level.upper(), "handlers": ["console"]},
            "loggers": {
                "httpx": {"level": "WARNING"},
                "httpcore": {"level": "WARNING"},
                "opentelemetry": {"level": "WARNING"},
                "urllib3": {"level": "WARNING"},
                "google_genai": {"level": "ERROR"},
                "google_genai.models": {"level": "ERROR"},
            },
        }
    )
