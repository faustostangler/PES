"""Prometheus infrastructure adapter for Cresmo Knowledge Synthesis Modular Monolith.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform Specification
"""

from __future__ import annotations

import logging
import threading

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
)

from cresmo.application.ports import MetricsPort

logger = logging.getLogger(__name__)


class PrometheusMetricsAdapter(MetricsPort):
    """Production infrastructure adapter translating MetricsPort calls to prometheus_client."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        """Initialize adapter with optional isolated CollectorRegistry.

        Args:
            registry: Optional Prometheus registry. Defaults to global prometheus_client.REGISTRY.
        """
        self._registry: CollectorRegistry = registry if registry is not None else REGISTRY
        self._lock = threading.Lock()

        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._gauges: dict[str, Gauge] = {}

        self._register_canonical_metrics()

    def _get_or_create_counter(
        self,
        name: str,
        documentation: str = "",
        labelnames: list[str] | None = None,
    ) -> Counter:
        """Retrieve existing counter from registry or create a new one idempotently."""
        existing = getattr(self._registry, "_names_to_collectors", {})
        if name in existing and isinstance(existing[name], Counter):
            return existing[name]
        return Counter(
            name,
            documentation or f"Counter for {name}",
            labelnames=labelnames or [],
            registry=self._registry,
        )

    def _get_or_create_histogram(
        self,
        name: str,
        documentation: str = "",
        labelnames: list[str] | None = None,
        buckets: tuple[float, ...] = Histogram.DEFAULT_BUCKETS,
    ) -> Histogram:
        """Retrieve existing histogram from registry or create a new one idempotently."""
        existing = getattr(self._registry, "_names_to_collectors", {})
        if name in existing and isinstance(existing[name], Histogram):
            return existing[name]
        return Histogram(
            name,
            documentation or f"Histogram for {name}",
            labelnames=labelnames or [],
            buckets=buckets,
            registry=self._registry,
        )

    def _get_or_create_gauge(
        self,
        name: str,
        documentation: str = "",
        labelnames: list[str] | None = None,
    ) -> Gauge:
        """Retrieve existing gauge from registry or create a new one idempotently."""
        existing = getattr(self._registry, "_names_to_collectors", {})
        if name in existing and isinstance(existing[name], Gauge):
            return existing[name]
        return Gauge(
            name,
            documentation or f"Gauge for {name}",
            labelnames=labelnames or [],
            registry=self._registry,
        )

    def _register_canonical_metrics(self) -> None:
        """Pre-register all canonical SRE Golden Signals and DORA metrics per SPEC-008."""
        # 1. Latency Histograms
        self._histograms["cresmo_pipeline_stage_duration_seconds"] = self._get_or_create_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            "Execution duration of pipeline synthesis stages in seconds.",
            labelnames=["stage", "channel_id", "channel_name", "status"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
        )
        self._histograms["cresmo_media_ingestion_duration_seconds"] = self._get_or_create_histogram(
            "cresmo_media_ingestion_duration_seconds",
            "Duration of media metadata probing and subtitle/audio extraction in seconds.",
            labelnames=["channel_id", "channel_name", "modality", "status"],
            buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 45.0, 90.0, 180.0, 300.0),
        )
        self._histograms["cresmo_llm_request_duration_seconds"] = self._get_or_create_histogram(
            "cresmo_llm_request_duration_seconds",
            "Roundtrip duration of external LLM API calls in seconds.",
            labelnames=["model", "system", "role"],
            buckets=(0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 60.0),
        )

        # 2. Traffic Counters
        self._counters["cresmo_transcripts_processed_total"] = self._get_or_create_counter(
            "cresmo_transcripts_processed_total",
            "Total count of transcript units consumed by the pipeline.",
            labelnames=["channel_id", "channel_name", "content_id", "status", "modality"],
        )
        self._counters["cresmo_atomic_notes_synthesized_total"] = self._get_or_create_counter(
            "cresmo_atomic_notes_synthesized_total",
            "Total count of discrete Obsidian atomic notes synthesized.",
            labelnames=["channel_id", "channel_name", "content_id", "note_type"],
        )
        self._counters["cresmo_batch_sources_discovered_total"] = self._get_or_create_counter(
            "cresmo_batch_sources_discovered_total",
            "Total count of media items emitted by the discovery generator.",
            labelnames=["channel_id", "channel_name", "modality"],
        )

        # 3. Error Counters
        self._counters["cresmo_pipeline_errors_total"] = self._get_or_create_counter(
            "cresmo_pipeline_errors_total",
            "Count of unhandled or caught pipeline failures partitioned by error type.",
            labelnames=["error_type", "channel_id", "channel_name", "content_id", "stage"],
        )
        self._counters["cresmo_judge_retry_count_total"] = self._get_or_create_counter(
            "cresmo_judge_retry_count_total",
            "Total count of iterative rewrite cycles triggered by LLM judge failures.",
            labelnames=["channel_id", "channel_name", "content_id", "pass_type"],
        )
        self._counters["cresmo_ingestion_failures_total"] = self._get_or_create_counter(
            "cresmo_ingestion_failures_total",
            "Failures encountered during media extraction partitioned by reason.",
            labelnames=["channel_id", "channel_name", "content_id", "reason"],
        )

        # 4. Saturation Gauges & Counters
        self._gauges["cresmo_discovery_queue_size"] = self._get_or_create_gauge(
            "cresmo_discovery_queue_size",
            "Number of pending items buffered in the bounded discovery stream queue.",
        )
        self._gauges["cresmo_process_resident_memory_bytes"] = self._get_or_create_gauge(
            "cresmo_process_resident_memory_bytes",
            "Physical resident memory (RSS) occupied by the Python runtime in bytes.",
            labelnames=["role"],
        )
        self._counters["cresmo_gc_collections_total"] = self._get_or_create_counter(
            "cresmo_gc_collections_total",
            "Count of Python garbage collection sweeps triggered per ADR-020 memory hygiene.",
            labelnames=["generation"],
        )

        # 5. DORA Four Keys Metrics
        self._counters["cresmo_dora_deployments_total"] = self._get_or_create_counter(
            "cresmo_dora_deployments_total",
            "Total deployment and startup events manifested in environment.",
            labelnames=["environment", "role", "status"],
        )
        self._gauges["cresmo_dora_lead_time_seconds"] = self._get_or_create_gauge(
            "cresmo_dora_lead_time_seconds",
            "Lead time from commit timestamp to execution activation in seconds.",
            labelnames=["branch", "release_tag"],
        )
        self._histograms["cresmo_dora_restore_duration_seconds"] = self._get_or_create_histogram(
            "cresmo_dora_restore_duration_seconds",
            "Time to restore service from alert firing to healthy recovery in seconds.",
            labelnames=["incident_id"],
            buckets=(10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0),
        )

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter.

        Args:
            name: Canonical metric name.
            value: Increment value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")

        with self._lock:
            counter = self._counters.get(name)
            if counter is None:
                label_names = sorted(labels.keys()) if labels else []
                counter = self._get_or_create_counter(name, labelnames=label_names)
                self._counters[name] = counter

        if labels:
            counter.labels(**labels).inc(value)
        else:
            counter.inc(value)

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value.

        Args:
            name: Canonical metric name.
            value: Observed duration or size value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")

        with self._lock:
            histogram = self._histograms.get(name)
            if histogram is None:
                label_names = sorted(labels.keys()) if labels else []
                histogram = self._get_or_create_histogram(name, labelnames=label_names)
                self._histograms[name] = histogram

        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge.

        Args:
            name: Canonical metric name.
            value: Arbitrary numeric value.
            labels: Optional dimensional key-value pairs.
        """
        with self._lock:
            gauge = self._gauges.get(name)
            if gauge is None:
                label_names = sorted(labels.keys()) if labels else []
                gauge = self._get_or_create_gauge(name, labelnames=label_names)
                self._gauges[name] = gauge

        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)


def start_metrics_server(
    port: int = 9090,
    addr: str = "0.0.0.0",
    registry: CollectorRegistry | None = None,
) -> None:
    """Start standalone Prometheus HTTP metrics scraping server.

    Args:
        port: Port to listen on (default: 9090).
        addr: Address to bind to (default: '0.0.0.0').
        registry: Optional CollectorRegistry instance.
    """
    from prometheus_client import start_http_server

    target_registry = registry if registry is not None else REGISTRY
    start_http_server(port=port, addr=addr, registry=target_registry)
    logger.info("Prometheus metrics server active at http://%s:%s/metrics", addr, port)


def get_latest_metrics(registry: CollectorRegistry | None = None) -> tuple[bytes, str]:
    """Return raw Prometheus metrics bytes and MIME content type for HTTP scrapers.

    Args:
        registry: Optional CollectorRegistry instance.

    Returns:
        Tuple of (encoded_metrics_payload, content_type_header).
    """
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    target_registry = registry if registry is not None else REGISTRY
    return generate_latest(target_registry), CONTENT_TYPE_LATEST
