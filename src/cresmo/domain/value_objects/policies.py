"""Pure Domain Policy Value Objects for pipeline execution, discovery, and compaction.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity (Zero framework/I/O dependencies)
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.convergence import ConvergenceMode, SaturationThresholds


def _require_int_range(
    value: int,
    field_name: str,
    *,
    min_value: int,
    max_value: int | None = None,
) -> None:
    """Validate non-boolean integer within [min_value, max_value]."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise DomainValidationError(f"{field_name} must be an integer, got {value!r}.")
    if value < min_value:
        raise DomainValidationError(f"{field_name} must be >= {min_value}, got {value!r}.")
    if max_value is not None and value > max_value:
        raise DomainValidationError(f"{field_name} must be <= {max_value}, got {value!r}.")


def _require_strict_bool(value: bool, field_name: str) -> None:
    """Validate strict boolean value."""
    if not isinstance(value, bool):
        raise DomainValidationError(f"{field_name} must be a bool, got {value!r}.")


@dataclass(frozen=True, slots=True)
class StageExecutionPolicy:
    """Immutable domain policy governing multi-pass stage execution and quality gates."""

    expansion_max_passes: int = 5
    long_expander_max_passes: int = 7
    judge_max_attempts: int = 2
    judge_blocking: bool = False
    saturation_thresholds: SaturationThresholds = field(default_factory=SaturationThresholds)

    def __post_init__(self) -> None:
        """Enforce construction-time domain invariants for stage execution."""
        _require_int_range(
            self.expansion_max_passes,
            "expansion_max_passes",
            min_value=1,
            max_value=10,
        )
        _require_int_range(
            self.long_expander_max_passes,
            "long_expander_max_passes",
            min_value=1,
            max_value=10,
        )
        _require_int_range(
            self.judge_max_attempts,
            "judge_max_attempts",
            min_value=1,
        )
        _require_strict_bool(self.judge_blocking, "judge_blocking")
        if not isinstance(self.saturation_thresholds, SaturationThresholds):
            raise DomainValidationError(
                "saturation_thresholds must be a SaturationThresholds instance."
            )

    def resolve_max_passes(self, stage_name: str, convergence_mode: ConvergenceMode) -> int:
        """Resolve maximum pass budget for a stage according to domain execution policy."""
        if stage_name == "long_expander":
            return self.long_expander_max_passes
        if convergence_mode == ConvergenceMode.HYBRID_SEMANTIC:
            return self.expansion_max_passes
        return 1


@dataclass(frozen=True, slots=True)
class DiscoveryPolicy:
    """Immutable domain policy governing batch source discovery and crawler concurrency."""

    lookback_days: int = 365
    discovery_workers: int = 10
    queue_maxsize: int = 50
    enable_channel_crawler: bool = False

    def __post_init__(self) -> None:
        """Enforce construction-time domain invariants for batch discovery."""
        _require_int_range(self.lookback_days, "lookback_days", min_value=0)
        _require_int_range(self.discovery_workers, "discovery_workers", min_value=1)
        _require_int_range(self.queue_maxsize, "queue_maxsize", min_value=1)
        _require_strict_bool(self.enable_channel_crawler, "enable_channel_crawler")


@dataclass(frozen=True, slots=True)
class CompendiumRolloverPolicy:
    """Immutable domain policy defining word limits before master compendium rollover."""

    max_words: int = 500_000

    def __post_init__(self) -> None:
        """Enforce positive word budget invariant."""
        _require_int_range(self.max_words, "max_words", min_value=1)


__all__ = [
    "CompendiumRolloverPolicy",
    "DiscoveryPolicy",
    "StageExecutionPolicy",
]
