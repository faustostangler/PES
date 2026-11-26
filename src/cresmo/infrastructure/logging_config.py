"""Centralized structured logging for Loki integration per ADR-025, ADR-044, and ADR-070.

Configures structlog and stdlib logging with JSON formatter (python-json-logger) and
OpenTelemetry trace correlation filter/processor for Grafana Loki -> Langfuse pivot.
"""

from __future__ import annotations

import logging
import logging.config
from collections.abc import MutableMapping
from typing import Any, Final

import structlog
from opentelemetry import trace

_TRACE_ID_HEX_FORMAT: Final[str] = "032x"
_SPAN_ID_HEX_FORMAT: Final[str] = "016x"
_ZERO_TRACE_ID: Final[str] = "0" * 32
_ZERO_SPAN_ID: Final[str] = "0" * 16
_ATTR_SESSION_ID: Final[str] = "langfuse.session.id"
_FIELD_OTEL_TRACE_ID: Final[str] = "otelTraceID"
_FIELD_OTEL_SPAN_ID: Final[str] = "otelSpanID"
_FIELD_SESSION_ID: Final[str] = "session_id"
DEFAULT_LOG_LEVEL: Final[str] = "WARNING"
DEFAULT_LOG_FORMAT: Final[str] = "json"
_JSON_FORMATTER_CLASS: Final[str] = "pythonjsonlogger.json.JsonFormatter"
_JSON_LOG_FORMAT_TEMPLATE: Final[str] = (
    "%(asctime)s %(name)s %(levelname)s %(message)s "
    "%(otelTraceID)s %(otelSpanID)s %(session_id)s"
)
_TEXT_LOG_FORMAT_TEMPLATE: Final[str] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_TIMESTAMP_FORMAT_ISO: Final[str] = "iso"
_THIRD_PARTY_LOG_LEVELS: Final[dict[str, dict[str, str]]] = {
    "httpx": {"level": "WARNING"},
    "httpcore": {"level": "WARNING"},
    "opentelemetry": {"level": "WARNING"},
    "urllib3": {"level": "WARNING"},
    "google_genai": {"level": "ERROR"},
    "google_genai.models": {"level": "ERROR"},
}


def _extract_otel_log_context() -> tuple[str, str, str]:
    """Extract (otelTraceID, otelSpanID, session_id) from active OTel span with zero fallback."""
    span = trace.get_current_span()
    span_context = span.get_span_context() if span else None
    if span_context and span_context.trace_id:
        otel_trace_id = format(span_context.trace_id, _TRACE_ID_HEX_FORMAT)
        otel_span_id = format(span_context.span_id, _SPAN_ID_HEX_FORMAT)
    else:
        otel_trace_id = _ZERO_TRACE_ID
        otel_span_id = _ZERO_SPAN_ID

    session_id = ""
    if hasattr(span, "attributes") and span.attributes:
        session_id_attr = span.attributes.get(_ATTR_SESSION_ID)
        if session_id_attr:
            session_id = str(session_id_attr)
    return otel_trace_id, otel_span_id, session_id


class CresmoOTelTraceCorrelationFilter(logging.Filter):
    """Inject OTel trace_id, span_id, and session_id into every log record.

    Enables Grafana Loki -> Langfuse trace correlation per ADR-016 Section 2.2
    and ADR-020 Pillar 5 canonical naming.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Enrich LogRecord with otelTraceID, otelSpanID, and session_id."""
        otel_trace_id, otel_span_id, session_id = _extract_otel_log_context()
        record.otelTraceID = otel_trace_id
        record.otelSpanID = otel_span_id
        record.session_id = session_id
        return True


def _add_opentelemetry_context(
    logger: Any,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Structlog processor injecting OTel trace_id, span_id, and session_id into event_dict."""
    _ = (logger, method_name)
    otel_trace_id, otel_span_id, session_id = _extract_otel_log_context()
    event_dict[_FIELD_OTEL_TRACE_ID] = otel_trace_id
    event_dict[_FIELD_OTEL_SPAN_ID] = otel_span_id
    event_dict[_FIELD_SESSION_ID] = session_id
    return event_dict


_LOGGING_CONFIGURED: bool = False


def configure_logging(
    level: str = DEFAULT_LOG_LEVEL,
    fmt: str = DEFAULT_LOG_FORMAT,
) -> None:
    """Configure root logger and structlog with JSON or text formatter.

    Idempotent: subsequent calls after initialization update only the root log level,
    preventing test-session stream replacement when composition root runs repeatedly.

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

    if fmt == DEFAULT_LOG_FORMAT:
        formatter_cfg: dict[str, Any] = {
            "class": _JSON_FORMATTER_CLASS,
            "format": _JSON_LOG_FORMAT_TEMPLATE,
        }
    else:
        formatter_cfg = {
            "format": _TEXT_LOG_FORMAT_TEMPLATE,
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
            "loggers": _THIRD_PARTY_LOG_LEVELS,
        }
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt=_TIMESTAMP_FORMAT_ISO),
            _add_opentelemetry_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


get_logger = structlog.get_logger
