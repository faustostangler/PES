"""Unit tests for PrometheusMetricsAdapter.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform Specification
"""

from __future__ import annotations

from unittest.mock import patch

import prometheus_client
import pytest
from prometheus_client import REGISTRY, CollectorRegistry, Histogram, generate_latest

from cresmo.infrastructure.adapters.prometheus_metrics_adapter import (
    PrometheusMetricsAdapter,
    get_latest_metrics,
    start_metrics_server,
)

EXPECTED_HISTOGRAMS = {
    "cresmo_pipeline_stage_duration_seconds": {
        "documentation": "Execution duration of pipeline synthesis stages in seconds.",
        "labelnames": ("stage", "channel_id", "channel_name", "status"),
        "buckets": (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    },
    "cresmo_media_ingestion_duration_seconds": {
        "documentation": "Duration of media metadata probing and subtitle/audio extraction in seconds.",
        "labelnames": ("channel_id", "channel_name", "modality", "status"),
        "buckets": (0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 45.0, 90.0, 180.0, 300.0),
    },
    "cresmo_llm_request_duration_seconds": {
        "documentation": "Roundtrip duration of external LLM API calls in seconds.",
        "labelnames": ("model", "system", "role"),
        "buckets": (0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 60.0),
    },
    "cresmo_dora_restore_duration_seconds": {
        "documentation": "Time to restore service from alert firing to healthy recovery in seconds.",
        "labelnames": ("incident_id",),
        "buckets": (10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0),
    },
}

EXPECTED_COUNTERS = {
    "cresmo_transcripts_processed_total": {
        "documentation": "Total count of transcript units consumed by the pipeline.",
        "labelnames": ("channel_id", "channel_name", "content_id", "status", "modality"),
    },
    "cresmo_atomic_notes_synthesized_total": {
        "documentation": "Total count of discrete Obsidian atomic notes synthesized.",
        "labelnames": ("channel_id", "channel_name", "content_id", "note_type"),
    },
    "cresmo_batch_sources_discovered_total": {
        "documentation": "Total count of media items emitted by the discovery generator.",
        "labelnames": ("channel_id", "channel_name", "modality"),
    },
    "cresmo_pipeline_errors_total": {
        "documentation": "Count of unhandled or caught pipeline failures partitioned by error type.",
        "labelnames": ("error_type", "channel_id", "channel_name", "content_id", "stage"),
    },
    "cresmo_judge_retry_count_total": {
        "documentation": "Total count of iterative rewrite cycles triggered by LLM judge failures.",
        "labelnames": ("channel_id", "channel_name", "content_id", "pass_type"),
    },
    "cresmo_ingestion_failures_total": {
        "documentation": "Failures encountered during media extraction partitioned by reason.",
        "labelnames": ("channel_id", "channel_name", "content_id", "reason"),
    },
    "cresmo_gc_collections_total": {
        "documentation": "Count of Python garbage collection sweeps triggered per ADR-020 memory hygiene.",
        "labelnames": ("generation",),
    },
    "cresmo_dora_deployments_total": {
        "documentation": "Total deployment and startup events manifested in environment.",
        "labelnames": ("environment", "role", "status"),
    },
}

EXPECTED_GAUGES = {
    "cresmo_discovery_queue_size": {
        "documentation": "Number of pending items buffered in the bounded discovery stream queue.",
        "labelnames": (),
    },
    "cresmo_process_resident_memory_bytes": {
        "documentation": "Physical resident memory (RSS) occupied by the Python runtime in bytes.",
        "labelnames": ("role",),
    },
    "cresmo_dora_lead_time_seconds": {
        "documentation": "Lead time from commit timestamp to execution activation in seconds.",
        "labelnames": ("branch", "release_tag"),
    },
}


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

    def test_canonical_metrics_exact_specifications(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Section 4: All canonical Golden Signals and DORA metrics pre-registered with exact spec."""
        assert set(adapter._histograms.keys()) == set(EXPECTED_HISTOGRAMS.keys())
        assert set(adapter._counters.keys()) == set(EXPECTED_COUNTERS.keys())
        assert set(adapter._gauges.keys()) == set(EXPECTED_GAUGES.keys())

        for name, spec in EXPECTED_HISTOGRAMS.items():
            hist = adapter._histograms[name]
            assert hist._documentation == spec["documentation"]
            assert hist._labelnames == spec["labelnames"]
            assert tuple(hist._upper_bounds[:-1]) == spec["buckets"]
            assert hist._upper_bounds[-1] == float("inf")
            assert hist is registry._names_to_collectors[name]

        for name, spec in EXPECTED_COUNTERS.items():
            cnt = adapter._counters[name]
            assert cnt._documentation == spec["documentation"]
            assert cnt._labelnames == spec["labelnames"]
            assert cnt is registry._names_to_collectors[name]

        for name, spec in EXPECTED_GAUGES.items():
            gauge = adapter._gauges[name]
            assert gauge._documentation == spec["documentation"]
            assert gauge._labelnames == spec["labelnames"]
            assert gauge is registry._names_to_collectors[name]

    def test_default_registry_initialization(self) -> None:
        """Verify default initialization uses global REGISTRY."""
        adapter = PrometheusMetricsAdapter()
        assert adapter._registry is REGISTRY

    def test_counter_increment_records_correct_sample(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 1: Counter increments monotonically by exact value."""
        adapter.increment_counter(
            "cresmo_transcripts_processed_total",
            2.5,
            labels={
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        assert sample == 2.5

        # Second increment accumulates
        adapter.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        assert sample == 3.5

    def test_increment_counter_boundary_and_defaults(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verify counter increment default 1.0, zero boundary, and negative validation."""
        # Default increment value is 1.0
        adapter.increment_counter("custom_default_cnt")
        assert registry.get_sample_value("custom_default_cnt_total") == 1.0

        # Boundary 0.0 is valid and does not raise
        adapter.increment_counter("custom_default_cnt", 0.0)
        assert registry.get_sample_value("custom_default_cnt_total") == 1.0

        # Fractional 0.5 is valid and does not raise
        adapter.increment_counter("custom_default_cnt", 0.5)
        assert registry.get_sample_value("custom_default_cnt_total") == 1.5

        # Negative value raises exact error
        with pytest.raises(ValueError, match=r"^Counter increment must be non-negative$"):
            adapter.increment_counter("custom_default_cnt", -0.01)

    def test_histogram_observation_records_distribution(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 2: Histogram records sample count, sum, and bucket bounds."""
        adapter.observe_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            3.45,
            labels={
                "stage": "fluid_prose",
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "status": "success",
            },
        )
        count = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_count",
            {
                "stage": "fluid_prose",
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "status": "success",
            },
        )
        total_sum = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_sum",
            {
                "stage": "fluid_prose",
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "status": "success",
            },
        )
        bucket_5 = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_bucket",
            {
                "stage": "fluid_prose",
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "status": "success",
                "le": "5.0",
            },
        )
        bucket_2_5 = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_bucket",
            {
                "stage": "fluid_prose",
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "status": "success",
                "le": "2.5",
            },
        )

        assert count == 1.0
        assert total_sum == pytest.approx(3.45)
        assert bucket_5 == 1.0  # 3.45 <= 5.0
        assert bucket_2_5 == 0.0  # 3.45 > 2.5

    def test_observe_histogram_boundary(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verify histogram observation zero boundary and negative validation."""
        # Boundary 0.0 is valid
        adapter.observe_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            0.0,
            labels={"stage": "s0", "channel_id": "c0", "channel_name": "cn0", "status": "ok"},
        )
        count = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_count",
            {"stage": "s0", "channel_id": "c0", "channel_name": "cn0", "status": "ok"},
        )
        assert count == 1.0

        # Fractional 0.5 is valid
        adapter.observe_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            0.5,
            labels={"stage": "s0", "channel_id": "c0", "channel_name": "cn0", "status": "ok"},
        )
        count = registry.get_sample_value(
            "cresmo_pipeline_stage_duration_seconds_count",
            {"stage": "s0", "channel_id": "c0", "channel_name": "cn0", "status": "ok"},
        )
        assert count == 2.0

        # Negative observation raises exact error
        with pytest.raises(ValueError, match=r"^Histogram observation must be non-negative$"):
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

    def test_dynamic_counter_caching_and_label_sorting(
        self,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verify dynamic counter label sorting and caching behaviour."""
        # Out-of-order labels sorted cleanly
        adapter.increment_counter("dyn_cnt", 1.0, labels={"zebra": "1", "apple": "2"})
        cached = adapter._counters.get("dyn_cnt")
        assert cached is not None
        assert cached._labelnames == ("apple", "zebra")

        # Second call uses cache without re-creating collector
        with patch.object(adapter, "_get_or_create_counter") as mock_create:
            adapter.increment_counter("dyn_cnt", 1.0, labels={"zebra": "1", "apple": "2"})
            mock_create.assert_not_called()

        # Existing canonical metric also hits cache
        with patch.object(adapter, "_get_or_create_counter") as mock_create:
            adapter.increment_counter(
                "cresmo_transcripts_processed_total",
                1.0,
                labels={
                    "channel_id": "c1",
                    "channel_name": "cn1",
                    "content_id": "cid",
                    "status": "s",
                    "modality": "m",
                },
            )
            mock_create.assert_not_called()

    def test_dynamic_histogram_caching_and_label_sorting(
        self,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verify dynamic histogram label sorting and caching behaviour."""
        # Out-of-order labels sorted cleanly
        adapter.observe_histogram("dyn_hist", 1.0, labels={"zebra": "1", "apple": "2"})
        cached = adapter._histograms.get("dyn_hist")
        assert cached is not None
        assert cached._labelnames == ("apple", "zebra")

        # Second call uses cache without re-creating collector
        with patch.object(adapter, "_get_or_create_histogram") as mock_create:
            adapter.observe_histogram("dyn_hist", 1.0, labels={"zebra": "1", "apple": "2"})
            mock_create.assert_not_called()

        # Canonical metric hits cache
        with patch.object(adapter, "_get_or_create_histogram") as mock_create:
            adapter.observe_histogram(
                "cresmo_pipeline_stage_duration_seconds",
                1.0,
                labels={"stage": "s", "channel_id": "c", "channel_name": "cn", "status": "ok"},
            )
            mock_create.assert_not_called()

    def test_dynamic_gauge_caching_and_label_sorting(
        self,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Verify dynamic gauge label sorting and caching behaviour."""
        # Out-of-order labels sorted cleanly
        adapter.set_gauge("dyn_gauge", 42.0, labels={"zebra": "1", "apple": "2"})
        cached = adapter._gauges.get("dyn_gauge")
        assert cached is not None
        assert cached._labelnames == ("apple", "zebra")

        # Second call uses cache without re-creating collector
        with patch.object(adapter, "_get_or_create_gauge") as mock_create:
            adapter.set_gauge("dyn_gauge", 42.0, labels={"zebra": "1", "apple": "2"})
            mock_create.assert_not_called()

        # Canonical gauge hits cache
        with patch.object(adapter, "_get_or_create_gauge") as mock_create:
            adapter.set_gauge("cresmo_discovery_queue_size", 10.0)
            mock_create.assert_not_called()

    def test_get_or_create_counter_branches(self, adapter: PrometheusMetricsAdapter) -> None:
        """Verify _get_or_create_counter doc defaults, labels, and registry fallback."""
        # Default doc
        c1 = adapter._get_or_create_counter("test_cnt_def")
        assert c1._documentation == "Counter for test_cnt_def"
        assert c1._labelnames == ()

        # Custom doc and labelnames
        c2 = adapter._get_or_create_counter(
            "test_cnt_cust",
            documentation="custom_c_doc",
            labelnames=["tag"],
        )
        assert c2._documentation == "custom_c_doc"
        assert c2._labelnames == ("tag",)

        # Cache hit in registry returns same instance
        c1_repeat = adapter._get_or_create_counter("test_cnt_def")
        assert c1_repeat is c1

        # Dummy registry lacking _names_to_collectors attribute
        class MinimalRegistry:
            def register(self, collector: object) -> None:
                pass

        minimal_adapter = PrometheusMetricsAdapter.__new__(PrometheusMetricsAdapter)
        minimal_adapter._registry = MinimalRegistry()  # type: ignore[assignment]
        dummy_c = minimal_adapter._get_or_create_counter("dummy_c")
        assert dummy_c._documentation == "Counter for dummy_c"

    def test_get_or_create_histogram_branches(self, adapter: PrometheusMetricsAdapter) -> None:
        """Verify _get_or_create_histogram doc defaults, buckets, and registry fallback."""
        # Default doc & buckets
        h1 = adapter._get_or_create_histogram("test_hist_def")
        assert h1._documentation == "Histogram for test_hist_def"
        assert h1._labelnames == ()
        assert tuple(h1._upper_bounds) == Histogram.DEFAULT_BUCKETS

        # Custom doc, labels, and buckets
        h2 = adapter._get_or_create_histogram(
            "test_hist_cust",
            documentation="custom_h_doc",
            labelnames=["h_tag"],
            buckets=(1.0, 5.0),
        )
        assert h2._documentation == "custom_h_doc"
        assert h2._labelnames == ("h_tag",)
        assert tuple(h2._upper_bounds[:-1]) == (1.0, 5.0)

        # Cache hit
        h1_repeat = adapter._get_or_create_histogram("test_hist_def")
        assert h1_repeat is h1

        # Dummy registry lacking _names_to_collectors attribute
        class MinimalRegistry:
            def register(self, collector: object) -> None:
                pass

        minimal_adapter = PrometheusMetricsAdapter.__new__(PrometheusMetricsAdapter)
        minimal_adapter._registry = MinimalRegistry()  # type: ignore[assignment]
        dummy_h = minimal_adapter._get_or_create_histogram("dummy_h")
        assert dummy_h._documentation == "Histogram for dummy_h"

    def test_get_or_create_gauge_branches(self, adapter: PrometheusMetricsAdapter) -> None:
        """Verify _get_or_create_gauge doc defaults, labels, and registry fallback."""
        # Default doc
        g1 = adapter._get_or_create_gauge("test_gauge_def")
        assert g1._documentation == "Gauge for test_gauge_def"
        assert g1._labelnames == ()

        # Custom doc and labelnames
        g2 = adapter._get_or_create_gauge(
            "test_gauge_cust",
            documentation="custom_g_doc",
            labelnames=["g_tag"],
        )
        assert g2._documentation == "custom_g_doc"
        assert g2._labelnames == ("g_tag",)

        # Cache hit
        g1_repeat = adapter._get_or_create_gauge("test_gauge_def")
        assert g1_repeat is g1

        # Dummy registry lacking _names_to_collectors attribute
        class MinimalRegistry:
            def register(self, collector: object) -> None:
                pass

        minimal_adapter = PrometheusMetricsAdapter.__new__(PrometheusMetricsAdapter)
        minimal_adapter._registry = MinimalRegistry()  # type: ignore[assignment]
        dummy_g = minimal_adapter._get_or_create_gauge("dummy_g")
        assert dummy_g._documentation == "Gauge for dummy_g"

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
        adapter.set_gauge("cresmo_discovery_queue_size", 7.0)
        raw_bytes, content_type = get_latest_metrics(registry)
        assert isinstance(raw_bytes, bytes)
        assert "text/plain" in content_type
        assert b"cresmo_discovery_queue_size 7.0" in raw_bytes

    def test_get_latest_metrics_defaults(self) -> None:
        """SPEC-008 Scenario 8: get_latest_metrics defaults to global REGISTRY."""
        raw_bytes, content_type = get_latest_metrics()
        assert isinstance(raw_bytes, bytes)
        assert content_type == prometheus_client.CONTENT_TYPE_LATEST

    def test_start_metrics_server_defaults_and_logging(self) -> None:
        """Verify start_metrics_server defaults (9090, 0.0.0.0, REGISTRY) and log output."""
        with (
            patch("prometheus_client.start_http_server") as mock_start,
            patch(
                "cresmo.infrastructure.adapters.prometheus_metrics_adapter.logger"
            ) as mock_logger,
        ):
            start_metrics_server()
            mock_start.assert_called_once_with(port=9090, addr="0.0.0.0", registry=REGISTRY)
            mock_logger.info.assert_called_once_with(
                "Prometheus metrics server active at http://%s:%s/metrics",
                "0.0.0.0",
                9090,
            )

    def test_start_metrics_server_custom_args(self, registry: CollectorRegistry) -> None:
        """Verify start_metrics_server with explicit port, addr, and registry."""
        with (
            patch("prometheus_client.start_http_server") as mock_start,
            patch(
                "cresmo.infrastructure.adapters.prometheus_metrics_adapter.logger"
            ) as mock_logger,
        ):
            start_metrics_server(port=9999, addr="127.0.0.1", registry=registry)
            mock_start.assert_called_once_with(port=9999, addr="127.0.0.1", registry=registry)
            mock_logger.info.assert_called_once_with(
                "Prometheus metrics server active at http://%s:%s/metrics",
                "127.0.0.1",
                9999,
            )

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
            labels={
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        sample = registry.get_sample_value(
            "cresmo_transcripts_processed_total",
            {
                "channel_id": "UC_sandeco",
                "channel_name": "sandeco",
                "content_id": "vid_123",
                "status": "completed",
                "modality": "url",
            },
        )
        assert sample == 1.0

    def test_canonical_metrics_have_no_legacy_channel_label(
        self,
        registry: CollectorRegistry,
        adapter: PrometheusMetricsAdapter,
    ) -> None:
        """Clean-break validation: verifies no canonical metric retains the deprecated 'channel' label."""
        names_to_collectors = registry._names_to_collectors
        for name, collector in names_to_collectors.items():
            if name.startswith("cresmo_"):
                labelnames = getattr(collector, "_labelnames", ())
                assert "channel" not in labelnames, (
                    f"Metric '{name}' still contains deprecated 'channel' label; "
                    "expected 'channel_id' and/or 'channel_name'."
                )

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
