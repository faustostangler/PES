"""Telemetry adapters package for Cresmo observability."""

from cresmo.infrastructure.adapters.telemetry.genai import build_genai_attributes
from cresmo.infrastructure.adapters.telemetry.otel_span import (
    OTelTelemetrySpan,
    wrap_current_otel_span,
)
from cresmo.infrastructure.adapters.telemetry.thread_naming import name_telemetry_threads

__all__ = [
    "OTelTelemetrySpan",
    "build_genai_attributes",
    "name_telemetry_threads",
    "wrap_current_otel_span",
]
