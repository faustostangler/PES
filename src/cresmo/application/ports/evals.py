"""Hexagonal Output Ports for Judge Calibration checkpoints, datasets, and reports.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class CalibrationCheckpointPort(ABC):
    """Port abstracting incremental calibration checkpoint and cooldown persistence."""

    @abstractmethod
    def load_completed_items(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
    ) -> dict[str, dict[str, Any]]:
        """Load checkpointed item verdicts when config_hash matches current configuration."""
        raise NotImplementedError

    @abstractmethod
    def record_item(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Persist one evaluated calibration item atomically."""
        raise NotImplementedError

    @abstractmethod
    def record_cooldown(
        self,
        stage: str,
        provider: str,
        model: str,
        until_ts: float,
    ) -> None:
        """Persist cooldown expiration epoch timestamp for target and shared provider/model."""
        raise NotImplementedError

    @abstractmethod
    def active_cooldown_until(
        self,
        stage: str,
        provider: str,
        model: str,
        now: float | None = None,
    ) -> float | None:
        """Return future cooldown epoch timestamp if active, otherwise None."""
        raise NotImplementedError

    @abstractmethod
    def clear_cooldown(self, stage: str, provider: str, model: str) -> None:
        """Clear cooldown expiration state after target calibration finishes cleanly."""
        raise NotImplementedError


class CalibrationDatasetPort(ABC):
    """Port abstracting calibration golden set and JSON seed dataset loading."""

    @abstractmethod
    def load_items(
        self,
        default_golden_set_path: Path,
        default_seed_path: Path,
        *,
        dataset_path: Path | None = None,
        seed_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Load evaluation items from golden dataset JSON or externalized seed JSON."""
        raise NotImplementedError


class CalibrationReportWriterPort(ABC):
    """Port abstracting durable persistence of formatted calibration reports."""

    @abstractmethod
    def write_report(self, output_path: Path, content: str) -> Path:
        """Write rendered calibration report text to target destination and return resolved path."""
        raise NotImplementedError
