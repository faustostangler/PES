"""Hermetic tests for Infrastructure calibration adapters and JSON seed SSOT.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import json
from pathlib import Path

from cresmo.infrastructure.adapters.evals import (
    FileCalibrationReportWriter,
    JsonCalibrationCheckpointStore,
    JsonCalibrationDatasetLoader,
)


class TestInfrastructureEvalsAdapters:
    """Tests covering atomic JSON checkpoints, dataset/seed loading, and report file writing."""

    def test_checkpoint_store_atomic_persistence_cooldowns_and_reset_on_hash_change(
        self, tmp_path: Path
    ) -> None:
        store = JsonCalibrationCheckpointStore(checkpoint_dir=tmp_path)
        assert store.load_completed_items("fluid_prose", "gemini", "m1", "h1") == {}

        store.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            config_hash="h1",
            item_id="it_1",
            payload={"actual": "PASS", "expected": "PASS", "score": 0.9},
        )
        loaded = store.load_completed_items("fluid_prose", "gemini", "m1", "h1")
        assert loaded["it_1"]["actual"] == "PASS"
        assert store.load_completed_items("fluid_prose", "gemini", "m1", "h2") == {}

        store.record_cooldown("fluid_prose", "gemini", "m1", 2000.0)
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1500.0) == 2000.0
        assert store.active_cooldown_until("gap_filler", "gemini", "m1", now=1500.0) == 2000.0

        store.clear_cooldown("fluid_prose", "gemini", "m1")
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1500.0) is None

        # Corrupted JSON gracefully returns empty dict
        bad_file = tmp_path / "fluid_prose__gemini__broken.json"
        bad_file.write_text("{corrupted", encoding="utf-8")
        assert store.load_completed_items("fluid_prose", "gemini", "broken", "h1") == {}

    def test_dataset_loader_loads_golden_set_and_falls_back_to_seed_json(
        self, tmp_path: Path
    ) -> None:
        golden = tmp_path / "golden.json"
        seed = tmp_path / "seed.json"
        golden.write_text(json.dumps([{"id": "g1"}]), encoding="utf-8")
        seed.write_text(json.dumps([{"id": "s1"}]), encoding="utf-8")

        loader = JsonCalibrationDatasetLoader()
        assert loader.load_items("fluid_prose", golden, seed, seed_only=True) == [{"id": "s1"}]
        assert loader.load_items("fluid_prose", golden, seed) == [{"id": "g1"}]
        assert loader.load_items("fluid_prose", tmp_path / "missing.json", seed) == [{"id": "s1"}]

        override = tmp_path / "override.json"
        override.write_text(json.dumps([{"id": "o1"}]), encoding="utf-8")
        assert loader.load_items("fluid_prose", golden, seed, dataset_path=override) == [
            {"id": "o1"}
        ]

    def test_real_externalized_seed_json_ssot_files_exist_and_validate(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        fp_seed = json.loads(
            (repo_root / "evals" / "datasets" / "seeds" / "fluid_prose_seed.json").read_text(
                encoding="utf-8"
            )
        )
        gf_seed = json.loads(
            (repo_root / "evals" / "datasets" / "seeds" / "gap_filler_seed.json").read_text(
                encoding="utf-8"
            )
        )
        assert len(fp_seed) == 5
        assert {item["expected_output"]["verdict"] for item in fp_seed} == {"PASS", "FAIL"}
        assert len(gf_seed) == 2
        assert {item["expected_output"]["verdict"] for item in gf_seed} == {"PASS", "FAIL"}

    def test_file_report_writer_creates_parent_directories(self, tmp_path: Path) -> None:
        writer = FileCalibrationReportWriter()
        dest = tmp_path / "nested" / "report.txt"
        out = writer.write_report(dest, "CALIBRATION CONTENT")
        assert out == dest
        assert dest.read_text(encoding="utf-8") == "CALIBRATION CONTENT"
