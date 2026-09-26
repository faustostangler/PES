"""Hermetic Null-Object Metrics Adapter for Cresmo Knowledge Synthesis Modular Monolith.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort Specification
"""

from __future__ import annotations

from cresmo.application.ports import MetricsPort


class NoOpMetricsAdapter(MetricsPort):
    """Null-Object implementation of MetricsPort performing zero-overhead no-ops.

    Used during isolated unit testing, offline execution, or when Prometheus
    monitoring is disabled.
    """

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter.

        Args:
            name: Metric name.
            value: Increment value (must be >= 0.0).
            labels: Optional label mapping.

        Raises:
            ValueError: If value is negative.
        """
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value.

        Args:
            name: Metric name.
            value: Observed value (must be >= 0.0).
            labels: Optional label mapping.

        Raises:
            ValueError: If value is negative.
        """
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current value of a gauge.

        Args:
            name: Metric name.
            value: Arbitrary numeric value.
            labels: Optional label mapping.
        """
        # Silent no-op for Null Object pattern
