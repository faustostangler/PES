"""Hexagonal Metrics Port and Null-Object implementation.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum


class MetricName(StrEnum):
    """Canonical low-cardinality SRE Golden Signals metric identifiers."""

    PIPELINE_STAGE_DURATION = "cresmo_pipeline_stage_duration_seconds"
    MEDIA_INGESTION_DURATION = "cresmo_media_ingestion_duration_seconds"
    LLM_REQUEST_DURATION = "cresmo_llm_request_duration_seconds"
    TRANSCRIPTS_PROCESSED = "cresmo_transcripts_processed_total"
    BATCH_SOURCES_DISCOVERED = "cresmo_batch_sources_discovered_total"
    PIPELINE_ERRORS = "cresmo_pipeline_errors_total"
    JUDGE_RETRY_COUNT = "cresmo_judge_retry_count_total"
    JUDGE_EVALUATIONS = "cresmo_judge_evaluations_total"
    STAGE_QUARANTINES = "cresmo_stage_quarantines_total"
    INGESTION_FAILURES = "cresmo_ingestion_failures_total"
    DISCOVERY_QUEUE_SIZE = "cresmo_discovery_queue_size"
    PROCESS_RESIDENT_MEMORY_BYTES = "cresmo_process_resident_memory_bytes"
    GC_COLLECTIONS = "cresmo_gc_collections_total"


class MetricsPort(ABC):
    """Hexagonal Port defining time-series operational and domain metrics contracts.

    Conforms to:
    - ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
    - SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform
    """

    @abstractmethod
    def increment_counter(
        self,
        name: MetricName,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter by a non-negative value.

        Args:
            name: Canonical metric name conforming to Prometheus naming rules.
            value: Increment value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """

    @abstractmethod
    def observe_histogram(
        self,
        name: MetricName,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution.

        Args:
            name: Canonical metric name.
            value: Observed duration or size value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """

    @abstractmethod
    def set_gauge(
        self,
        name: MetricName,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge.

        Args:
            name: Canonical metric name.
            value: Arbitrary numeric value.
            labels: Optional dimensional key-value pairs.
        """

    def flush(self) -> None:
        """Flush any buffered metrics to the downstream collector."""
        return None


class NoOpMetricsPort(MetricsPort):
    """Hermetic Null-Object implementation of MetricsPort for offline/test environments."""

    def increment_counter(
        self,
        name: MetricName,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")

    def observe_histogram(
        self,
        name: MetricName,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")

    def set_gauge(
        self,
        name: MetricName,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge."""
        _ = (name, value, labels)

    def flush(self) -> None:
        """No-op flush for offline test environments."""
