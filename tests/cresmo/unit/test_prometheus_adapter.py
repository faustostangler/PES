"""Unit tests for PrometheusMetricsAdapter.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform Specification
"""

from __future__ import annotations

import pytest
from prometheus_client import CollectorRegistry, generate_latest

from cresmo.infrastructure.adapters.prometheus_metrics_adapter import PrometheusMetricsAdapter


class TestPrometheusMetricsAdapter:
    """Verifies PrometheusMetricsAdapter adherence to SPEC-008 acceptance criteria."""

    @pytest.fixture
    def registry(self) -> CollectorRegistry:
        """Create an isolated CollectorRegistry for hermetic testing."""
        return CollectorRegistry(auto_describe=True)

    @pytest.fixture
    def adapter(self, registry: CollectorRegistry) -> PrometheusMetricsAdapter:
        """Instantiate adapter wired with isolated registry."""
        return PrometheusMetricsAdapter(registry=registry)

    def test_canonical_metrics_are_pre_registered(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Section 4: All canonical Golden Signals and DORA metrics must be pre-registered."""
        registered_names = set(registry._names_to_collectors.keys())
        expected_metrics = [
            "cresmo_pipeline_stage_duration_seconds",
            "cresmo_media_ingestion_duration_seconds",
            "cresmo_llm_request_duration_seconds",
            "cresmo_transcripts_processed_total",
            "cresmo_atomic_notes_synthesized_total",
            "cresmo_batch_sources_discovered_total",
            "cresmo_pipeline_errors_total",
            "cresmo_judge_retry_count_total",
            "cresmo_ingestion_failures_total",
            "cresmo_discovery_queue_size",
            "cresmo_process_resident_memory_bytes",
            "cresmo_gc_collections_total",
            "cresmo_dora_deployments_total",
            "cresmo_dora_lead_time_seconds",
            "cresmo_dora_restore_duration_seconds",
        ]
        for metric_name in expected_metrics:
            assert metric_name in registered_names, (
                f"Expected canonical metric '{metric_name}' in registry"
            )

    def test_counter_increment_records_correct_sample(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 1: Counter increments monotonically by exact value."""
        adapter.increment_counter(
            "cresmo_transcripts_processed_total",
            2.5,
            labels={"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        assert sample == 2.5

        # Second increment accumulates
        adapter.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        assert sample == 3.5

    def test_counter_increment_rejects_negative_value(
        self,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 1: Negative counter increment raises ValueError."""
        with pytest.raises(ValueError, match="Counter increment must be non-negative"):
            adapter.increment_counter("cresmo_transcripts_processed_total", -1.0)

    def test_histogram_observation_records_distribution(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 2: Histogram records sample count, sum, and bucket bounds."""
        adapter.observe_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            3.45,
            labels={"stage": "fluid_prose", "channel": "sandeco", "status": "success"},
        )
        count = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_count",
            {"stage": "fluid_prose", "channel": "sandeco", "status": "success"},
        )
        total_sum = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_sum",
            {"stage": "fluid_prose", "channel": "sandeco", "status": "success"},
        )
        bucket_5 = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_bucket",
            {"stage": "fluid_prose", "channel": "sandeco", "status": "success", "le": "5.0"},
        )
        bucket_2_5 = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_bucket",
            {"stage": "fluid_prose", "channel": "sandeco", "status": "success", "le": "2.5"},
        )

        assert count == 1.0
        assert total_sum == pytest.approx(3.45)
        assert bucket_5 == 1.0  # 3.45 <= 5.0
        assert bucket_2_5 == 0.0  # 3.45 > 2.5

    def test_histogram_observation_rejects_negative_value(
        self,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 2: Negative histogram observation raises ValueError."""
        with pytest.raises(ValueError, match="Histogram observation must be non-negative"):
            adapter.observe_histogram("cresmo_pipeline_stage_duration_seconds", -0.05)

    def test_gauge_set_records_instantaneous_value(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 3: Gauge reflects exact instantaneous value and zero drain."""
        adapter.set_gauge("cresmo_discovery_queue_size", 12.0)
        sample = registry.get_sample_value("cresmo_discovery_queue_size")
        assert sample == 12.0

        adapter.set_gauge("cresmo_discovery_queue_size", 0.0)
        sample = registry.get_sample_value("cresmo_discovery_queue_size")
        assert sample == 0.0

    def test_dynamic_metric_creation_if_unregistered(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verifies that dynamic/unregistered metric names are handled cleanly."""
        adapter.increment_counter("custom_transient_counter", 1.0, {"env": "test"})
        sample = registry.get_sample_value("custom_transient_counter_total", {"env": "test"})
        assert sample == 1.0

    def test_exposition_text_format(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 8: Prometheus exposition text is valid."""
        adapter.set_gauge("cresmo_discovery_queue_size", 5.0)
        payload = generate_latest(registry).decode("utf-8")
        assert "# HELP cresmo_discovery_queue_size" in payload
        assert "# TYPE cresmo_discovery_queue_size gauge" in payload
        assert "cresmo_discovery_queue_size 5.0" in payload

    def test_get_latest_metrics_helper(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 8: get_latest_metrics returns encoded bytes and content type."""
        from cresmo.infrastructure.adapters.prometheus_metrics_adapter import get_latest_metrics

        adapter.set_gauge("cresmo_discovery_queue_size", 7.0)
        raw_bytes, content_type = get_latest_metrics(registry)
        assert isinstance(raw_bytes, bytes)
        assert "text/plain" in content_type
        assert b"cresmo_discovery_queue_size 7.0" in raw_bytes

    def test_start_metrics_server_invokes_prometheus_client(self) -> None:
        """SPEC-008 Scenario 8: start_metrics_server calls prometheus_client start_http_server."""
        from unittest.mock import patch

        from cresmo.infrastructure.adapters.prometheus_metrics_adapter import start_metrics_server

        with patch("prometheus_client.start_http_server") as mock_start:
            start_metrics_server(port=9099, addr="127.0.0.1")
            mock_start.assert_called_once()
            _args, kwargs = mock_start.call_args
            assert kwargs["port"] == 9099
            assert kwargs["addr"] == "127.0.0.1"

    def test_shared_registry_idempotency_reuses_collectors(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verifies that re-instantiating adapter on same registry reuses existing collectors."""
        second_adapter = PrometheusMetricsAdapter(registry=registry)
        assert second_adapter is not None
        # Verify second adapter increments into the same counter
        second_adapter.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {"channel": "sandeco", "status": "completed", "modality": "url"},
        )
        assert sample == 1.0

    def test_dynamic_histogram_and_gauge_without_and_with_labels(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verifies dynamic histogram and gauge creation with and without labels."""
        # Counter without labels
        adapter.increment_counter("custom_unlabeled_counter", 3.0)
        assert registry.get_sample_value("custom_unlabeled_counter_total") == 3.0

        # Dynamic histogram with and without labels
        adapter.observe_histogram("custom_unlabeled_hist", 1.5)
        assert registry.get_sample_value("custom_unlabeled_hist_count") == 1.0

        adapter.observe_histogram("custom_labeled_hist", 2.0, {"env": "prod"})
        assert registry.get_sample_value("custom_labeled_hist_count", {"env": "prod"}) == 1.0

        # Dynamic gauge with labels
        adapter.set_gauge("custom_labeled_gauge", 99.0, {"service": "cresmo"})
        assert registry.get_sample_value("custom_labeled_gauge", {"service": "cresmo"}) == 99.0
