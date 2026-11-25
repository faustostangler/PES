"""In-memory Hexagonal Test Doubles for Evals calibration ports (ADR-008).

Conforms to:
    - ADR-008: Isolation of Test Doubles to tests/doubles/
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
"""

from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Any

from cresmo.application.ports.evals import (
    CalibrationCheckpointPort,
    CalibrationDatasetPort,
    CalibrationReportWriterPort,
)


class InMemoryCalibrationCheckpointFake(CalibrationCheckpointPort):
    """Hermetic in-memory fake implementing CalibrationCheckpointPort."""

    def __init__(self) -> None:
        self._targets: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._shared_cooldowns: dict[tuple[str, str], float] = {}

    @staticmethod
    def _target_key(stage: str, provider: str, model: str) -> tuple[str, str, str]:
        return (stage.strip(), provider.strip().lower(), model.strip())

    @staticmethod
    def _shared_key(provider: str, model: str) -> tuple[str, str]:
        return (provider.strip().lower(), model.strip())

    def load_completed_items(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
    ) -> dict[str, dict[str, Any]]:
        """Return saved item payloads iff config_hash matches."""
        entry = self._targets.get(self._target_key(stage, provider, model))
        if not entry or entry.get("config_hash") != config_hash:
            return {}
        return copy.deepcopy(dict(entry.get("items", {})))

    def record_item(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Store evaluated item payload under current config_hash."""
        key = self._target_key(stage, provider, model)
        existing = self._targets.get(key, {})
        items = (
            dict(existing.get("items", {})) if existing.get("config_hash") == config_hash else {}
        )
        items[item_id] = copy.deepcopy(payload)
        updated: dict[str, Any] = {
            "config_hash": config_hash,
            "items": items,
        }
        if isinstance(existing.get("cooldown_until"), int | float):
            updated["cooldown_until"] = float(existing["cooldown_until"])
        self._targets[key] = updated

    def record_cooldown(
        self,
        stage: str,
        provider: str,
        model: str,
        until_ts: float,
    ) -> None:
        """Record target and shared cooldown expiration timestamps."""
        tkey = self._target_key(stage, provider, model)
        entry = self._targets.setdefault(tkey, {})
        prev_t = entry.get("cooldown_until")
        entry["cooldown_until"] = (
            max(float(prev_t), until_ts) if isinstance(prev_t, int | float) else until_ts
        )

        skey = self._shared_key(provider, model)
        prev_s = self._shared_cooldowns.get(skey)
        self._shared_cooldowns[skey] = max(prev_s, until_ts) if prev_s is not None else until_ts

    def active_cooldown_until(
        self,
        stage: str,
        provider: str,
        model: str,
        now: float | None = None,
    ) -> float | None:
        """Return max future expiration timestamp across target and shared cooldowns."""
        current_now = time.time() if now is None else now
        candidates: list[float] = []
        entry = self._targets.get(self._target_key(stage, provider, model), {})
        t_cd = entry.get("cooldown_until")
        if isinstance(t_cd, int | float) and float(t_cd) > current_now:
            candidates.append(float(t_cd))
        s_cd = self._shared_cooldowns.get(self._shared_key(provider, model))
        if s_cd is not None and s_cd > current_now:
            candidates.append(s_cd)
        return max(candidates) if candidates else None

    def clear_cooldown(self, stage: str, provider: str, model: str) -> None:
        """Clear target and shared cooldown markers."""
        tkey = self._target_key(stage, provider, model)
        if tkey in self._targets:
            self._targets[tkey].pop("cooldown_until", None)
        self._shared_cooldowns.pop(self._shared_key(provider, model), None)


class InMemoryCalibrationDatasetFake(CalibrationDatasetPort):
    """Hermetic in-memory fake mapping stage/path datasets and seed fallbacks."""

    def __init__(
        self,
        *,
        golden_by_stage: dict[str, list[dict[str, Any]]] | None = None,
        seeds_by_stage: dict[str, list[dict[str, Any]]] | None = None,
        by_path: dict[Path, list[dict[str, Any]]] | None = None,
    ) -> None:
        self._golden_by_stage = golden_by_stage or {}
        self._seeds_by_stage = seeds_by_stage or {}
        self._by_path = by_path or {}
        self.calls: list[dict[str, Any]] = []

    def load_items(
        self,
        default_golden_set_path: Path,
        default_seed_path: Path,
        *,
        dataset_path: Path | None = None,
        seed_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Return configured items or seed fallback without touching disk."""
        self.calls.append(
            {
                "default_golden_set_path": default_golden_set_path,
                "default_seed_path": default_seed_path,
                "dataset_path": dataset_path,
                "seed_only": seed_only,
            }
        )
        all_stages = tuple(self._golden_by_stage.keys() | self._seeds_by_stage.keys())
        stems = f"{default_golden_set_path.stem} {default_seed_path.stem}"
        stage_name = next(
            (s for s in all_stages if s in stems),
            default_golden_set_path.parent.name,
        )
        if seed_only:
            return copy.deepcopy(self._seeds_by_stage.get(stage_name, []))
        target_path = dataset_path if dataset_path is not None else default_golden_set_path
        if self._by_path.get(target_path):
            return copy.deepcopy(self._by_path[target_path])
        if dataset_path is None and self._golden_by_stage.get(stage_name):
            return copy.deepcopy(self._golden_by_stage[stage_name])
        return copy.deepcopy(self._seeds_by_stage.get(stage_name, []))


class InMemoryCalibrationReportWriterFake(CalibrationReportWriterPort):
    """Hermetic in-memory fake recording written calibration reports."""

    def __init__(self) -> None:
        self.written_reports: dict[Path, str] = {}

    def write_report(self, output_path: Path, content: str) -> Path:
        """Store formatted report content keyed by destination path."""
        self.written_reports[output_path] = content
        return output_path
