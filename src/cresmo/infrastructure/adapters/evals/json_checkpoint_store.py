"""Atomic JSON filesystem adapter implementing CalibrationCheckpointPort.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown Checkpointing
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cresmo.application.ports.evals import CalibrationCheckpointPort


class JsonCalibrationCheckpointStore(CalibrationCheckpointPort):
    """Atomic JSON checkpoint and shared cooldown store under a target directory."""

    def __init__(self, checkpoint_dir: Path | None = None) -> None:
        self.checkpoint_dir = checkpoint_dir or (Path("data") / "calibration_checkpoints")

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", value.strip())

    def _target_path(self, stage: str, provider: str, model: str) -> Path:
        filename = f"{self._slug(stage)}__{self._slug(provider)}__{self._slug(model)}.json"
        return self.checkpoint_dir / filename

    @property
    def _cooldowns_path(self) -> Path:
        return self.checkpoint_dir / "cooldowns.json"

    @staticmethod
    def _shared_key(provider: str, model: str) -> str:
        return f"{provider.strip().lower()}:{model.strip()}"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
        return raw if isinstance(raw, dict) else {}

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp_path, path)

    def load_completed_items(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
    ) -> dict[str, dict[str, Any]]:
        """Load checkpointed item verdicts only when `config_hash` matches current config."""
        data = self._read_json(self._target_path(stage, provider, model))
        if not data or data.get("config_hash") != config_hash:
            return {}
        items = data.get("items")
        if not isinstance(items, dict):
            return {}
        return {str(k): v for k, v in items.items() if isinstance(v, dict)}

    def record_item(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Atomically append or update one evaluated item in the target checkpoint file."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        if existing.get("config_hash") != config_hash:
            items: dict[str, Any] = {}
        else:
            raw_items = existing.get("items")
            items = dict(raw_items) if isinstance(raw_items, dict) else {}
        items[item_id] = payload
        updated: dict[str, Any] = {
            "stage": stage,
            "provider": provider,
            "model": model,
            "config_hash": config_hash,
            "updated_at": datetime.now(UTC).isoformat(),
            "items": items,
        }
        if isinstance(existing.get("cooldown_until"), int | float):
            updated["cooldown_until"] = float(existing["cooldown_until"])
        self._write_json_atomic(path, updated)

    def record_cooldown(
        self,
        stage: str,
        provider: str,
        model: str,
        until_ts: float,
    ) -> None:
        """Persist cooldown expiration timestamp for `(stage, provider, model)` and shared model."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        existing.setdefault("stage", stage)
        existing.setdefault("provider", provider)
        existing.setdefault("model", model)
        prev_target_cd = existing.get("cooldown_until")
        if isinstance(prev_target_cd, int | float):
            existing["cooldown_until"] = max(float(prev_target_cd), until_ts)
        else:
            existing["cooldown_until"] = until_ts
        self._write_json_atomic(path, existing)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        prev_shared = cooldowns.get(shared_key)
        if isinstance(prev_shared, int | float):
            cooldowns[shared_key] = max(float(prev_shared), until_ts)
        else:
            cooldowns[shared_key] = until_ts
        self._write_json_atomic(self._cooldowns_path, cooldowns)

    def active_cooldown_until(
        self,
        stage: str,
        provider: str,
        model: str,
        now: float | None = None,
    ) -> float | None:
        """Return future cooldown epoch timestamp if still active, else None."""
        current_now = time.time() if now is None else now
        candidates: list[float] = []

        target_data = self._read_json(self._target_path(stage, provider, model))
        target_cd = target_data.get("cooldown_until")
        if isinstance(target_cd, int | float) and float(target_cd) > current_now:
            candidates.append(float(target_cd))

        cooldowns = self._read_json(self._cooldowns_path)
        shared_cd = cooldowns.get(self._shared_key(provider, model))
        if isinstance(shared_cd, int | float) and float(shared_cd) > current_now:
            candidates.append(float(shared_cd))

        return max(candidates) if candidates else None

    def clear_cooldown(self, stage: str, provider: str, model: str) -> None:
        """Clear cooldown metadata after target completes cleanly."""
        path = self._target_path(stage, provider, model)
        target_data = self._read_json(path)
        if "cooldown_until" in target_data:
            del target_data["cooldown_until"]
            self._write_json_atomic(path, target_data)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        if shared_key in cooldowns:
            del cooldowns[shared_key]
            self._write_json_atomic(self._cooldowns_path, cooldowns)
