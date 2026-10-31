"""Unit tests for Cresmo Stage 2 (gap_filler) Golden Dataset.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
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
    extract_complementary_section,
    validate_fluid_prose_mechanical_invariants,
    validate_gap_filler_mechanical_invariants,
)
from cresmo.domain.value_objects.quality import JudgeCriterion

REPO_ROOT = Path(__file__).resolve().parents[3]
GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"
)

EXPECTED_CRITERIA = {
    JudgeCriterion.FACTUAL_GROUNDING.value,
    JudgeCriterion.SOCRATIC_EPISTEMIC_DEPTH.value,
    JudgeCriterion.CAUSAL_STRATIFICATION_AGENCY.value,
    JudgeCriterion.COMPLEMENTARY_SUBSTANCE.value,
    JudgeCriterion.AUTHORIAL_NATURALISM.value,
}


@pytest.fixture(scope="module")
def golden_set_items() -> list[dict[str, Any]]:
    """Load the canonical gap_filler golden dataset."""
    assert GOLDEN_SET_PATH.exists(), (
        f"Golden dataset not found at {GOLDEN_SET_PATH}. "
        "Run `python scripts/gap_filler/llm_judge/builder.py` to generate it."
    )
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        items = json.load(f)
    assert isinstance(items, list), "Golden set root must be a list of items."
    return items


def test_golden_set_size_and_criteria_distribution(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate 35 items total, 5 criteria x 7 items, 20 PASS / 15 FAIL."""
    assert len(golden_set_items) == 35, (
        f"Expected exactly 35 items (5 criteria x 7), got {len(golden_set_items)}."
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

    assert total_pass == 20, f"Expected 20 PASS, got {total_pass}"
    assert total_fail == 15, f"Expected 15 FAIL, got {total_fail}"

    for crit, counts in criterion_counts.items():
        assert counts["PASS"] == 4, f"Criterion '{crit}' has {counts['PASS']} PASS, expected 4"
        assert counts["FAIL"] == 3, f"Criterion '{crit}' has {counts['FAIL']} FAIL, expected 3"

    assert difficulty_counts["borderline"]["PASS"] == 5
    assert difficulty_counts["borderline"]["FAIL"] == 5
    assert difficulty_counts["easy"]["PASS"] == 5
    assert difficulty_counts["easy"]["FAIL"] == 5
    assert difficulty_counts["typical"]["PASS"] == 10
    assert difficulty_counts["typical"]["FAIL"] == 5


def test_golden_set_source_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that input raw_text is a valid, de-oralized FluidTranscript."""
    for item in golden_set_items:
        raw_text = item["input"]["raw_text"].strip()
        item_id = item["id"]

        assert len(raw_text.split()) >= 40, (
            f"Item '{item_id}' raw_text too short: {len(raw_text.split())} words."
        )
        assert raw_text.startswith("## "), (
            f"Item '{item_id}' raw_text must start with '## ' (FluidTranscript contract)."
        )

        violations = validate_fluid_prose_mechanical_invariants(raw_text)
        assert not violations, (
            f"Item '{item_id}' raw_text has fluid_prose mechanical violations: {violations}"
        )


def test_golden_set_candidate_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that candidate_text follows EnrichedCompendium structural rules."""
    for item in golden_set_items:
        cand = item["input"]["candidate_text"].strip()
        item_id = item["id"]
        meta = item["metadata"]

        assert cand.startswith("## "), f"Item '{item_id}' candidate_text must start with '## '."
        assert "## Informações Complementares" in cand, (
            f"Item '{item_id}' missing mandatory '## Informações Complementares'."
        )

        comp_section = extract_complementary_section(cand)
        assert comp_section, f"Item '{item_id}' complementary section is empty."

        # If it's NOT an intentional mechanical defect item (e.g. cs_04 testing bullet formatting),
        # it must pass full gap_filler mechanical validation
        if meta.get("expected_anomaly") != "bullet_markers_in_complementary":
            violations = validate_gap_filler_mechanical_invariants(cand)
            assert not violations, (
                f"Item '{item_id}' has unintended mechanical violations: {violations}"
            )


def test_golden_set_metadata_and_defect_isolation(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate defect isolation and anomaly attribution."""
    for item in golden_set_items:
        item_id = item["id"]
        meta = item["metadata"]
        verdict = item["expected_output"]["verdict"]

        assert "video_id" in meta and len(meta["video_id"]) >= 3, (
            f"Item '{item_id}' missing valid video_id."
        )

        if verdict == "PASS":
            assert meta.get("expected_anomaly") == "none", (
                f"PASS item '{item_id}' should have expected_anomaly='none'."
            )
            assert meta.get("defect_location") == "none", (
                f"PASS item '{item_id}' should have defect_location='none'."
            )
        else:
            assert meta.get("expected_anomaly") not in (None, "none", ""), (
                f"FAIL item '{item_id}' must specify expected_anomaly."
            )
            assert meta.get("defect_location") not in (None, "none", ""), (
                f"FAIL item '{item_id}' must specify defect_location."
            )
