"""Hexagonal Metrics Port and Null-Object implementation.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class MetricsPort(ABC):
    """Hexagonal Port defining time-series operational and domain metrics contracts.

    Conforms to:
    - ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
    - SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform
    """

    @abstractmethod
    def increment_counter(
        self,
        name: str,
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
        name: str,
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


class NoOpMetricsPort(MetricsPort):
    """Hermetic Null-Object implementation of MetricsPort for offline/test environments."""

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge."""
        _ = (name, value, labels)
