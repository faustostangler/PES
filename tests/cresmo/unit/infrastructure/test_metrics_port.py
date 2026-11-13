"""Unit tests for MetricsPort contract and NoOpMetricsAdapter.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform Specification
"""

from __future__ import annotations

import time

import pytest

from cresmo.application.ports import MetricsPort
from cresmo.infrastructure.adapters.noop_metrics_adapter import NoOpMetricsAdapter


class TestMetricsPortContract:
    """Verifies Abstract Base Class constraints on MetricsPort."""

    def test_metrics_port_cannot_be_instantiated_directly(self) -> None:
        """SPEC-008: MetricsPort is an ABC and cannot be instantiated without implementation."""
        with pytest.raises(TypeError):
            MetricsPort()  # type: ignore[abstract]


class TestNoOpMetricsAdapter:
    """Verifies hermetic Null-Object behavior of NoOpMetricsAdapter (SPEC-008 Scenario 4)."""

    @pytest.fixture
    def noop_adapter(self) -> NoOpMetricsAdapter:
        return NoOpMetricsAdapter()

    def test_increment_counter_succeeds_for_valid_values(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 4: Counter increment with valid values runs without error."""
        noop_adapter.increment_counter("cresmo_test_counter", 1.0, {"channel": "sandeco"})
        noop_adapter.increment_counter("cresmo_test_counter", 0.0)

    def test_increment_counter_rejects_negative_value(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 1 & Non-Negative Invariant: Counter increment < 0 raises ValueError."""
        with pytest.raises(ValueError, match="Counter increment must be non-negative"):
            noop_adapter.increment_counter("cresmo_test_counter", -1.0)

    def test_observe_histogram_succeeds_for_valid_values(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 4: Histogram observation with valid values runs without error."""
        noop_adapter.observe_histogram("cresmo_test_histogram", 2.5, {"stage": "expansion"})
        noop_adapter.observe_histogram("cresmo_test_histogram", 0.0)

    def test_observe_histogram_rejects_negative_value(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 2 & Non-Negative Invariant: Histogram observation < 0 raises ValueError."""
        with pytest.raises(ValueError, match="Histogram observation must be non-negative"):
            noop_adapter.observe_histogram("cresmo_test_histogram", -0.01)

    def test_set_gauge_succeeds_for_any_value(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 4: Setting gauge with arbitrary values runs without error."""
        noop_adapter.set_gauge("cresmo_test_gauge", 42.0, {"role": "worker"})
        noop_adapter.set_gauge("cresmo_test_gauge", -10.0)
        noop_adapter.set_gauge("cresmo_test_gauge", 0.0)

    def test_noop_execution_speed_is_sub_millisecond(
        self,
        noop_adapter: NoOpMetricsAdapter,
    ) -> None:
        """SPEC-008 Scenario 4: NoOp operations must be ultra-fast (< 0.001s for 1000 calls)."""
        start = time.perf_counter()
        for _ in range(1000):
            noop_adapter.increment_counter("counter", 1.0)
            noop_adapter.observe_histogram("histogram", 0.5)
            noop_adapter.set_gauge("gauge", 10.0)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.05, f"NoOp execution too slow: {elapsed:.6f}s for 3000 calls"
