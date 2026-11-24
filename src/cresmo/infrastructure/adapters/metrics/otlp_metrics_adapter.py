"""Prometheus v3 Native OTLP HTTP Metrics Adapter (ADR-076).

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- ADR-076: Codebase Hygiene, Contract Minimalism & OTLP Metrics
"""

from __future__ import annotations

import threading
from typing import Final

import structlog
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import Counter, Histogram, _Gauge
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from cresmo.application.ports.metrics import MetricsPort
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import probe_http_endpoint

logger = structlog.get_logger(__name__)

HIGH_CARDINALITY_LABELS: Final[frozenset[str]] = frozenset(
    {"content_id", "channel_name", "incident_id"}
)


def probe_prometheus_ready(endpoint: str, timeout_seconds: float = 2.0) -> bool:
    """Verify whether Prometheus v3 HTTP server is ready to ingest OTLP metrics."""
    normalized = endpoint.rstrip("/")
    probe_url = f"{normalized}/-/ready"
    if probe_http_endpoint(probe_url, timeout_seconds=timeout_seconds):
        return True
    if "localhost" in normalized:
        fallback_url = probe_url.replace("localhost", "127.0.0.1")
        return probe_http_endpoint(fallback_url, timeout_seconds=timeout_seconds)
    return False


class OtlpMetricsAdapter(MetricsPort):
    """MetricsPort implementation pushing low-cardinality OTLP HTTP metrics to Prometheus v3."""

    def __init__(
        self,
        endpoint: str = "http://localhost:9090",
        *,
        export_interval_millis: float = 15_000.0,
        metric_exporter: MetricExporter | None = None,
        meter_provider: MeterProvider | None = None,
        service_name: str = "cresmo",
        service_version: str | None = None,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._lock = threading.Lock()
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._gauges: dict[str, _Gauge] = {}

        if meter_provider is not None:
            self._meter_provider = meter_provider
        else:
            resource_attrs: dict[str, str] = {"service.name": service_name}
            if service_version:
                resource_attrs["service.version"] = service_version
            exporter = metric_exporter or OTLPMetricExporter(
                endpoint=f"{self._endpoint}/api/v1/otlp/v1/metrics",
            )
            reader = PeriodicExportingMetricReader(
                exporter,
                export_interval_millis=export_interval_millis,
            )
            self._meter_provider = MeterProvider(
                resource=Resource.create(resource_attrs),
                metric_readers=[reader],
            )

        self._meter = self._meter_provider.get_meter("cresmo.metrics")

    @staticmethod
    def _sanitize_labels(labels: dict[str, str] | None) -> dict[str, str]:
        """Strip high-cardinality labels and normalize values to strings."""
        if not labels:
            return {}
        return {
            str(k): str(v)
            for k, v in labels.items()
            if str(k) not in HIGH_CARDINALITY_LABELS
        }

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonic OTel Counter by a non-negative value."""
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")
        key = str(name)
        with self._lock:
            counter = self._counters.get(key)
            if counter is None:
                counter = self._meter.create_counter(name=key)
                self._counters[key] = counter
        counter.add(value, attributes=self._sanitize_labels(labels))

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a non-negative observation into an OTel Histogram."""
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")
        key = str(name)
        with self._lock:
            histogram = self._histograms.get(key)
            if histogram is None:
                histogram = self._meter.create_histogram(name=key)
                self._histograms[key] = histogram
        histogram.record(value, attributes=self._sanitize_labels(labels))

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the instantaneous value of a synchronous OTel Gauge."""
        key = str(name)
        with self._lock:
            gauge = self._gauges.get(key)
            if gauge is None:
                gauge = self._meter.create_gauge(name=key)
                self._gauges[key] = gauge
        gauge.set(value, attributes=self._sanitize_labels(labels))

    def flush(self) -> None:
        """Force-flush buffered OTLP metrics without crashing on collector errors."""
        try:
            self._meter_provider.force_flush()
        except Exception as exc:  # noqa: BLE001 - Graceful degradation if Prometheus restarts
            logger.warning("[OtlpMetricsAdapter] Failed to flush metrics: %s", exc)

    def shutdown(self) -> None:
        """Flush and shut down the underlying OpenTelemetry MeterProvider."""
        try:
            self._meter_provider.shutdown()
        except Exception as exc:  # noqa: BLE001
            logger.warning("[OtlpMetricsAdapter] Failed to shutdown MeterProvider: %s", exc)
