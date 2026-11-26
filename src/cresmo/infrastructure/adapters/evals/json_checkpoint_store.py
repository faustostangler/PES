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
from typing import Any, Final

from cresmo.application.ports.evals import CalibrationCheckpointPort

DEFAULT_CHECKPOINT_DIR: Final[Path] = Path("data") / "calibration_checkpoints"
_SLUG_SANITIZE_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^a-zA-Z0-9_\-\.]")
_SLUG_REPLACEMENT_CHAR: Final[str] = "_"
_CHECKPOINT_KEY_SEPARATOR: Final[str] = "__"
_CHECKPOINT_FILE_EXTENSION: Final[str] = ".json"
_COOLDOWNS_FILENAME: Final[str] = "cooldowns.json"
_SHARED_KEY_SEPARATOR: Final[str] = ":"
_UTF8_ENCODING: Final[str] = "utf-8"
_TMP_FILE_SUFFIX: Final[str] = ".json.tmp"
_JSON_INDENT_SPACES: Final[int] = 2
_KEY_CONFIG_HASH: Final[str] = "config_hash"
_KEY_ITEMS: Final[str] = "items"
_KEY_STAGE: Final[str] = "stage"
_KEY_PROVIDER: Final[str] = "provider"
_KEY_MODEL: Final[str] = "model"
_KEY_UPDATED_AT: Final[str] = "updated_at"
_KEY_COOLDOWN_UNTIL: Final[str] = "cooldown_until"


class JsonCalibrationCheckpointStore(CalibrationCheckpointPort):
    """Atomic JSON checkpoint and shared cooldown store under a target directory."""

    def __init__(self, checkpoint_dir: Path | None = None) -> None:
        self.checkpoint_dir = checkpoint_dir or DEFAULT_CHECKPOINT_DIR

    @staticmethod
    def _slug(value: str) -> str:
        return _SLUG_SANITIZE_PATTERN.sub(_SLUG_REPLACEMENT_CHAR, value.strip())

    def _target_path(self, stage: str, provider: str, model: str) -> Path:
        filename = (
            f"{self._slug(stage)}{_CHECKPOINT_KEY_SEPARATOR}"
            f"{self._slug(provider)}{_CHECKPOINT_KEY_SEPARATOR}"
            f"{self._slug(model)}{_CHECKPOINT_FILE_EXTENSION}"
        )
        return self.checkpoint_dir / filename

    @property
    def _cooldowns_path(self) -> Path:
        return self.checkpoint_dir / _COOLDOWNS_FILENAME

    @staticmethod
    def _shared_key(provider: str, model: str) -> str:
        return f"{provider.strip().lower()}{_SHARED_KEY_SEPARATOR}{model.strip()}"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding=_UTF8_ENCODING))
        except Exception:  # noqa: BLE001
            return {}
        return raw if isinstance(raw, dict) else {}

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(_TMP_FILE_SUFFIX)
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=_JSON_INDENT_SPACES),
            encoding=_UTF8_ENCODING,
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
        if not data or data.get(_KEY_CONFIG_HASH) != config_hash:
            return {}
        items = data.get(_KEY_ITEMS)
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
        if existing.get(_KEY_CONFIG_HASH) != config_hash:
            items: dict[str, Any] = {}
        else:
            raw_items = existing.get(_KEY_ITEMS)
            items = dict(raw_items) if isinstance(raw_items, dict) else {}
        items[item_id] = payload
        updated: dict[str, Any] = {
            _KEY_STAGE: stage,
            _KEY_PROVIDER: provider,
            _KEY_MODEL: model,
            _KEY_CONFIG_HASH: config_hash,
            _KEY_UPDATED_AT: datetime.now(UTC).isoformat(),
            _KEY_ITEMS: items,
        }
        if isinstance(existing.get(_KEY_COOLDOWN_UNTIL), int | float):
            updated[_KEY_COOLDOWN_UNTIL] = float(existing[_KEY_COOLDOWN_UNTIL])
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
        existing.setdefault(_KEY_STAGE, stage)
        existing.setdefault(_KEY_PROVIDER, provider)
        existing.setdefault(_KEY_MODEL, model)
        prev_target_cd = existing.get(_KEY_COOLDOWN_UNTIL)
        if isinstance(prev_target_cd, int | float):
            existing[_KEY_COOLDOWN_UNTIL] = max(float(prev_target_cd), until_ts)
        else:
            existing[_KEY_COOLDOWN_UNTIL] = until_ts
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
        target_cd = target_data.get(_KEY_COOLDOWN_UNTIL)
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
        if _KEY_COOLDOWN_UNTIL in target_data:
            del target_data[_KEY_COOLDOWN_UNTIL]
            self._write_json_atomic(path, target_data)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        if shared_key in cooldowns:
            del cooldowns[shared_key]
            self._write_json_atomic(self._cooldowns_path, cooldowns)
