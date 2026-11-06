"""Unit tests for Cresmo Stage 1 (fluid_prose) Golden Dataset.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - ADR-011: Zero Hardcoded Tunables
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Fluid Prose Quality Gates and Calibration Framework
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from cresmo.domain.services.mechanical_validator import (
    validate_fluid_prose_mechanical_invariants,
)
from cresmo.domain.value_objects.quality import JudgeCriterion

REPO_ROOT = Path(__file__).resolve().parents[3]
GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "fluid_prose" / "golden_sets" / "fluid_prose_golden_set.json"
)

EXPECTED_CRITERIA = {
    JudgeCriterion.ORALITY_REMOVAL.value,
    JudgeCriterion.SEMANTIC_FAITHFULNESS.value,
    JudgeCriterion.EPISTEMIC_CRITIQUE.value,
    JudgeCriterion.NER_PRESERVATION.value,
    JudgeCriterion.STRUCTURAL_COMPLIANCE.value,
    JudgeCriterion.AUTHORIAL_VOICE.value,
}


@pytest.fixture(scope="module")
def golden_set_items() -> list[dict[str, Any]]:
    """Load the canonical fluid_prose golden dataset."""
    assert GOLDEN_SET_PATH.exists(), (
        f"Golden dataset not found at {GOLDEN_SET_PATH}. "
        "Run `python scripts/fluid_prose/llm_judge/builder.py` to generate it."
    )
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        items = json.load(f)
    assert isinstance(items, list), "Golden set root must be a list of items."
    return items


def test_golden_set_size_and_criteria_distribution(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate 42 items total, 6 criteria x 7 items, 24 PASS / 18 FAIL."""
    assert len(golden_set_items) == 42, (
        f"Expected exactly 42 items (6 criteria x 7), got {len(golden_set_items)}."
    )

    seen_ids: set[str] = set()
    total_pass = 0
    total_fail = 0
    criterion_counts: dict[str, dict[str, int]] = {
        c: {"PASS": 0, "FAIL": 0} for c in EXPECTED_CRITERIA
    }
    difficulty_counts: dict[str, dict[str, int]] = {
        "borderline": {"PASS": 0, "FAIL": 0},
        "easy": {"PASS": 0, "FAIL": 0},
        "typical": {"PASS": 0, "FAIL": 0},
    }

    for item in golden_set_items:
        item_id = item["id"]
        assert item_id not in seen_ids, f"Duplicate item id: '{item_id}'"
        seen_ids.add(item_id)

        meta = item["metadata"]
        criterion = meta["criterion"]
        assert criterion in EXPECTED_CRITERIA, (
            f"Unknown criterion '{criterion}' in item '{item_id}'"
        )

        verdict = item["expected_output"]["verdict"]
        assert verdict in ("PASS", "FAIL"), f"Invalid verdict '{verdict}' in item '{item_id}'"
        assert meta["target_verdict"] == verdict, (
            f"Verdict mismatch in '{item_id}': expected_output={verdict} vs target_verdict={meta['target_verdict']}"
        )

        diff = meta["difficulty"]
        assert diff in difficulty_counts, f"Unknown difficulty '{diff}' in item '{item_id}'"
        difficulty_counts[diff][verdict] += 1

        criterion_counts[criterion][verdict] += 1
        if verdict == "PASS":
            total_pass += 1
        else:
            total_fail += 1

    assert total_pass == 24, f"Expected 24 PASS, got {total_pass}"
    assert total_fail == 18, f"Expected 18 FAIL, got {total_fail}"

    for crit, counts in criterion_counts.items():
        assert counts["PASS"] == 4, f"Criterion '{crit}' has {counts['PASS']} PASS, expected 4"
        assert counts["FAIL"] == 3, f"Criterion '{crit}' has {counts['FAIL']} FAIL, expected 3"

    assert difficulty_counts["borderline"]["PASS"] == 6
    assert difficulty_counts["borderline"]["FAIL"] == 6
    assert difficulty_counts["easy"]["PASS"] == 6
    assert difficulty_counts["easy"]["FAIL"] == 6
    assert difficulty_counts["typical"]["PASS"] == 12
    assert difficulty_counts["typical"]["FAIL"] == 6


def test_golden_set_source_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that input raw_text has sufficient substance."""
    for item in golden_set_items:
        raw_text = item["input"]["raw_text"].strip()
        item_id = item["id"]

        assert len(raw_text.split()) >= 30, (
            f"Item '{item_id}' raw_text too short: {len(raw_text.split())} words."
        )


def test_golden_set_candidate_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that candidate_text adheres to FluidTranscript structure."""
    for item in golden_set_items:
        cand = item["input"]["candidate_text"].strip()
        item_id = item["id"]
        meta = item["metadata"]
        verdict = item["expected_output"]["verdict"]

        if meta["criterion"] != JudgeCriterion.STRUCTURAL_COMPLIANCE.value or verdict == "PASS":
            assert cand.startswith("## "), f"Item '{item_id}' candidate_text must start with '## '."
            prose_paragraphs = [
                p.strip() for p in cand.split("\n\n") if p.strip() and not p.strip().startswith("#")
            ]
            assert 2 <= len(prose_paragraphs) <= 5, (
                f"Item '{item_id}' has {len(prose_paragraphs)} prose paragraphs, expected 2-5."
            )

        # For valid PASS items, must strictly pass all mechanical preflight invariants
        if verdict == "PASS":
            violations = validate_fluid_prose_mechanical_invariants(cand)
            assert not violations, (
                f"PASS Item '{item_id}' failed mechanical validation: {violations}"
            )


def test_golden_set_metadata_and_defect_isolation(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate defect metadata and anomaly isolation across all items."""
    for item in golden_set_items:
        item_id = item["id"]
        meta = item["metadata"]
        verdict = item["expected_output"]["verdict"]

        assert "criterion" in meta and meta["criterion"] in EXPECTED_CRITERIA, (
            f"Item '{item_id}' has invalid criterion in metadata."
        )
        assert meta.get("difficulty") in ("borderline", "easy", "typical"), (
            f"Item '{item_id}' has invalid difficulty in metadata."
        )

        if verdict == "PASS":
            assert meta.get("target_verdict") == "PASS", (
                f"PASS Item '{item_id}' target_verdict must be PASS."
            )
        else:
            assert meta.get("target_verdict") == "FAIL", (
                f"FAIL Item '{item_id}' target_verdict must be FAIL."
            )
