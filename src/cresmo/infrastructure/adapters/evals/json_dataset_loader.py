"""JSON dataset and seed SSOT loader implementing CalibrationDatasetPort.

Conforms to:
    - ADR-062: Structural Consolidation & JSON Golden Set SSOT
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cresmo.application.ports.evals import CalibrationDatasetPort


class JsonCalibrationDatasetLoader(CalibrationDatasetPort):
    """Filesystem JSON adapter loading calibration golden sets and externalized seed files."""

    @staticmethod
    def _read_json_list(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, list):
            return [dict(item) for item in loaded if isinstance(item, dict)]
        return []

    def load_items(
        self,
        default_golden_set_path: Path,
        default_seed_path: Path,
        *,
        dataset_path: Path | None = None,
        seed_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Load golden set JSON list for a stage or fall back to canonical seed JSON."""
        if seed_only:
            return self._read_json_list(default_seed_path)

        target_path = dataset_path if dataset_path is not None else default_golden_set_path
        items = self._read_json_list(target_path)
        if items:
            return items
        return self._read_json_list(default_seed_path)
