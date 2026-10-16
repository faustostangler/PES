"""Telemetry adapters package for Cresmo observability."""

from cresmo.infrastructure.adapters.telemetry.noop import NoOpTelemetryAdapter
from cresmo.infrastructure.adapters.telemetry.thread_naming import name_telemetry_threads

__all__ = [
    "NoOpTelemetryAdapter",
    "name_telemetry_threads",
]
