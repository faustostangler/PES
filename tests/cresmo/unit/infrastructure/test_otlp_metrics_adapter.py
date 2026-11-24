"""Unit tests for OtlpMetricsAdapter and probe_prometheus_ready (ADR-076)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from cresmo.application.ports.metrics import MetricName, MetricsPort
from cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter import (
    HIGH_CARDINALITY_LABELS,
    OtlpMetricsAdapter,
    probe_prometheus_ready,
)


class TestMetricNameVocabulary:
    """Verify canonical 16 low-cardinality MetricName StrEnum members."""

    def test_metric_name_has_sixteen_canonical_members(self) -> None:
        assert len(MetricName) == 16
        assert MetricName.PIPELINE_STAGE_DURATION == "cresmo_pipeline_stage_duration_seconds"
        assert MetricName.JUDGE_RETRY_COUNT == "cresmo_judge_retry_count_total"
        assert MetricName.STAGE_QUARANTINES == "cresmo_stage_quarantines_total"
        assert MetricName.DORA_DEPLOYMENTS == "cresmo_dora_deployments_total"


class TestProbePrometheusReady:
    """Verify preflight /-/ready probe for Prometheus v3."""

    def test_probe_prometheus_ready_hits_ready_endpoint_and_localhost_fallback(self) -> None:
        with patch(
            "cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter.probe_http_endpoint",
            side_effect=[False, True],
        ) as mock_probe:
            assert probe_prometheus_ready("http://localhost:9090/", timeout_seconds=1.5) is True
            assert mock_probe.call_count == 2
            assert mock_probe.call_args_list[0].args == ("http://localhost:9090/-/ready",)
            assert mock_probe.call_args_list[1].args == ("http://127.0.0.1:9090/-/ready",)

    def test_probe_prometheus_ready_non_localhost_returns_false_directly(self) -> None:
        with patch(
            "cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter.probe_http_endpoint",
            return_value=False,
        ) as mock_probe:
            assert probe_prometheus_ready("http://prom.internal:9090", timeout_seconds=1.0) is False
            mock_probe.assert_called_once_with(
                "http://prom.internal:9090/-/ready", timeout_seconds=1.0
            )


class TestOtlpMetricsAdapter:
    """Verify OtlpMetricsAdapter instrumentation, label cardinality scrubbing, and flush."""

    @pytest.fixture
    def reader_and_adapter(self) -> tuple[InMemoryMetricReader, OtlpMetricsAdapter]:
        reader = InMemoryMetricReader()
        provider = MeterProvider(metric_readers=[reader])
        adapter = OtlpMetricsAdapter(meter_provider=provider)
        return reader, adapter

    def test_implements_metrics_port_and_strips_high_cardinality_labels(
        self,
        reader_and_adapter: tuple[InMemoryMetricReader, OtlpMetricsAdapter],
    ) -> None:
        reader, adapter = reader_and_adapter
        assert isinstance(adapter, MetricsPort)
        assert HIGH_CARDINALITY_LABELS == frozenset({"content_id", "channel_name", "incident_id"})

        adapter.increment_counter(
            MetricName.TRANSCRIPTS_PROCESSED,
            1.0,
            labels={
                "channel_id": "UC_123",
                "channel_name": "ShouldBeStripped",
                "content_id": "vid_strip_1",
                "status": "completed",
            },
        )
        adapter.observe_histogram(
            MetricName.DORA_RESTORE_DURATION,
            12.5,
            labels={"incident_id": "inc_strip", "stage": "sync"},
        )
        adapter.set_gauge(
            MetricName.PROCESS_RESIDENT_MEMORY_BYTES,
            1024.0,
            labels={"role": "cli"},
        )

        data = reader.get_metrics_data()
        assert data is not None
        recorded: dict[str, list[dict[str, object]]] = {}
        for rm in data.resource_metrics:
            for sm in rm.scope_metrics:
                for metric in sm.metrics:
                    recorded[metric.name] = [
                        dict(dp.attributes or {}) for dp in metric.data.data_points
                    ]

        assert recorded[MetricName.TRANSCRIPTS_PROCESSED] == [
            {"channel_id": "UC_123", "status": "completed"}
        ]
        assert recorded[MetricName.DORA_RESTORE_DURATION] == [{"stage": "sync"}]
        assert recorded[MetricName.PROCESS_RESIDENT_MEMORY_BYTES] == [{"role": "cli"}]

    def test_rejects_negative_counter_and_histogram_values(
        self,
        reader_and_adapter: tuple[InMemoryMetricReader, OtlpMetricsAdapter],
    ) -> None:
        _, adapter = reader_and_adapter
        with pytest.raises(ValueError, match="Counter increment must be non-negative"):
            adapter.increment_counter(MetricName.PIPELINE_ERRORS, -1.0)
        with pytest.raises(ValueError, match="Histogram observation must be non-negative"):
            adapter.observe_histogram(MetricName.PIPELINE_STAGE_DURATION, -0.5)

    def test_default_otlp_exporter_endpoint_and_graceful_flush_degradation(self) -> None:
        with patch(
            "cresmo.infrastructure.adapters.metrics.otlp_metrics_adapter.OTLPMetricExporter"
        ) as mock_exporter_cls:
            mock_provider = MagicMock(spec=MeterProvider)
            mock_provider.force_flush.side_effect = RuntimeError("Prometheus down")

            adapter = OtlpMetricsAdapter(endpoint="http://localhost:9090/", service_version="1.0.0")
            mock_exporter_cls.assert_called_once_with(
                endpoint="http://localhost:9090/api/v1/otlp/v1/metrics"
            )
            adapter.shutdown()

            degraded = OtlpMetricsAdapter(meter_provider=mock_provider)
            degraded.flush()
            mock_provider.force_flush.assert_called_once()
