"""OpenTelemetry span handle adapting OTel spans to the Hexagonal TelemetrySpan Protocol.

Conforms to:
- ADR-037: Lean Telemetry Topography & Canonical I/O Attributes
- ADR-063: Zero Attribute Duplication
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Final

from opentelemetry import trace
from opentelemetry.trace import Span

from cresmo.application.ports.telemetry import (
    NOOP_TELEMETRY_SPAN,
    TelemetryAttributeValue,
    TelemetryPayload,
    TelemetrySpan,
)

_TRACE_ID_HEX_FORMAT: Final[str] = "032x"
_SPAN_ID_HEX_FORMAT: Final[str] = "016x"
_ATTR_INPUT_VALUE: Final[str] = "input.value"
_ATTR_LANGFUSE_OBS_INPUT: Final[str] = "langfuse.observation.input"
_ATTR_LANGFUSE_TRACE_INPUT: Final[str] = "langfuse.trace.input"
_ATTR_OUTPUT_VALUE: Final[str] = "output.value"
_ATTR_LANGFUSE_OBS_OUTPUT: Final[str] = "langfuse.observation.output"
_ATTR_LANGFUSE_TRACE_OUTPUT: Final[str] = "langfuse.trace.output"
_ATTR_CRESMO_OUTPUT_PREFIX: Final[str] = "cresmo.output."
_ATTR_LANGFUSE_OBS_LEVEL: Final[str] = "langfuse.observation.level"
_LEVEL_ERROR: Final[str] = "ERROR"


def _serialize_io_payload(payload: TelemetryPayload) -> str:
    """Serialize structured I/O payloads into JSON strings while preserving plain strings."""
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, default=str)


def is_valid_otel_value(value: object) -> bool:
    """Check whether an attribute value is a supported OpenTelemetry primitive or string tuple."""
    if isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, tuple):
        return all(isinstance(item, str) for item in value)
    return False


class OTelTelemetrySpan:
    """Infrastructure adapter wrapping an OpenTelemetry Span behind TelemetrySpan."""

    def __init__(self, span: Span, *, is_root: bool = False) -> None:
        self._span = span
        self._is_root = is_root

    @property
    def trace_id(self) -> str | None:
        """Return 32-char lowercase hex trace ID when span is recording and valid."""
        if not self._span.is_recording():
            return None
        ctx = self._span.get_span_context()
        if ctx and ctx.trace_id:
            return format(ctx.trace_id, _TRACE_ID_HEX_FORMAT)
        return None

    @property
    def span_id(self) -> str | None:
        """Return 16-char lowercase hex span/observation ID when span is recording and valid."""
        if not self._span.is_recording():
            return None
        ctx = self._span.get_span_context()
        if ctx and ctx.span_id:
            return format(ctx.span_id, _SPAN_ID_HEX_FORMAT)
        return None

    def set_attributes(self, attributes: Mapping[str, TelemetryAttributeValue]) -> None:
        """Attach validated OTel scalar or string-sequence attributes to the recording span."""
        if not self._span.is_recording():
            return
        for key, value in attributes.items():
            if is_valid_otel_value(value):
                self._span.set_attribute(key, value)

    def set_input(self, payload: TelemetryPayload) -> None:
        """Write canonical CNCF OTel and Langfuse input attributes onto the active span."""
        if not self._span.is_recording():
            return
        serialized = _serialize_io_payload(payload)
        self._span.set_attribute(_ATTR_INPUT_VALUE, serialized)
        self._span.set_attribute(_ATTR_LANGFUSE_OBS_INPUT, serialized)
        if self._is_root:
            self._span.set_attribute(_ATTR_LANGFUSE_TRACE_INPUT, serialized)

    def set_output(self, payload: TelemetryPayload) -> None:
        """Write canonical CNCF OTel and Langfuse output attributes onto the active span."""
        if not self._span.is_recording():
            return
        serialized = _serialize_io_payload(payload)
        self._span.set_attribute(_ATTR_OUTPUT_VALUE, serialized)
        self._span.set_attribute(_ATTR_LANGFUSE_OBS_OUTPUT, serialized)
        if self._is_root:
            self._span.set_attribute(_ATTR_LANGFUSE_TRACE_OUTPUT, serialized)
            if isinstance(payload, Mapping):
                for key, val in payload.items():
                    self._span.set_attribute(f"{_ATTR_CRESMO_OUTPUT_PREFIX}{key}", str(val))

    def add_event(
        self,
        name: str,
        attributes: Mapping[str, TelemetryAttributeValue] | None = None,
    ) -> None:
        """Record a named span event when the span is recording."""
        if not self._span.is_recording():
            return
        filtered = (
            {k: v for k, v in attributes.items() if is_valid_otel_value(v)}
            if attributes is not None
            else None
        )
        self._span.add_event(name, attributes=filtered)

    def record_error(self, exc: BaseException) -> None:
        """Record exception details, set OTel ERROR status, and flag Langfuse observation level."""
        if not self._span.is_recording():
            return
        self._span.record_exception(exc)
        self._span.set_status(trace.StatusCode.ERROR, str(exc))
        self._span.set_attribute(_ATTR_LANGFUSE_OBS_LEVEL, _LEVEL_ERROR)


def wrap_current_otel_span(*, is_root: bool = False) -> TelemetrySpan:
    """Return OTelTelemetrySpan for the active recording OTel span, or NOOP_TELEMETRY_SPAN."""
    current = trace.get_current_span()
    if current and current.is_recording():
        return OTelTelemetrySpan(current, is_root=is_root)
    return NOOP_TELEMETRY_SPAN
