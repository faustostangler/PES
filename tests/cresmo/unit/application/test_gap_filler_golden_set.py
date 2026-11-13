"""Unit tests for Cresmo Stage 2 (gap_filler) Golden Dataset.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-011: Zero Hardcoded Tunables
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Fluid Prose Quality Gates and Calibration Framework
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from cresmo.domain.services.mechanical_validator import (
    extract_complementary_section,
    validate_fluid_prose_mechanical_invariants,
    validate_gap_filler_mechanical_invariants,
)
from cresmo.domain.value_objects.quality import JudgeCriterion

REPO_ROOT = Path(__file__).resolve().parents[4]
GOLDEN_SET_PATH = REPO_ROOT / "evals" / "datasets" / "gap_filler_golden_set.json"

CRITERION_PREFIXES: dict[str, str] = {
    JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION.value: "eg_",
    JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION.value: "cm_",
    JudgeCriterion.BRAUDELIAN_STRATIFICATION.value: "bs_",
    JudgeCriterion.GENEALOGY_HIDDEN_AGENCY.value: "gh_",
    JudgeCriterion.COMPETING_HYPOTHESES.value: "ch_",
    JudgeCriterion.EXTRA_INFO_GRANULARITY.value: "ei_",
    JudgeCriterion.LINEAR_STYLE_NATURALISM.value: "ls_",
}
EXPECTED_CRITERIA = set(CRITERION_PREFIXES.keys())
RESTRICTED_VOCAB_RE = re.compile(r"\b(?:forj|oper|mold|abrig|fardo)\w*\b", re.IGNORECASE)
BINARY_ANTITHESIS_RE = re.compile(
    r"\bnão\s+(?:apenas|somente|só|se trata|se resum\w+|decorre|reside|desempenha|constitui|é|era|foi|são|foram)"
    r"[^.!?\n]{1,120}\b(?:mas|e sim|senão)\b",
    re.IGNORECASE,
)
SYNTHETIC_VIDEO_PREFIXES = ("tel_", "fin_", "ach_")
MECHANICAL_EXEMPTIONS = {
    "bullet_markers_in_complementary",
    "em_dash_style_violation",
}


@pytest.fixture(scope="module")
def golden_set_items() -> list[dict[str, Any]]:
    """Load the canonical gap_filler golden dataset."""
    assert GOLDEN_SET_PATH.exists(), f"Golden dataset SSOT not found at {GOLDEN_SET_PATH}."
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        items = json.load(f)
    assert isinstance(items, list), "Golden set root must be a list of items."
    return items


def test_golden_set_size_and_criteria_distribution(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate 49 items total, 7 criteria x 7 items, 28 PASS / 21 FAIL."""
    assert len(golden_set_items) == 49, (
        f"Expected exactly 49 items (7 criteria x 7), got {len(golden_set_items)}."
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

    assert total_pass == 28, f"Expected 28 PASS, got {total_pass}"
    assert total_fail == 21, f"Expected 21 FAIL, got {total_fail}"

    for crit, counts in criterion_counts.items():
        assert counts["PASS"] == 4, f"Criterion '{crit}' has {counts['PASS']} PASS, expected 4"
        assert counts["FAIL"] == 3, f"Criterion '{crit}' has {counts['FAIL']} FAIL, expected 3"

    assert difficulty_counts["borderline"]["PASS"] == 7
    assert difficulty_counts["borderline"]["FAIL"] == 7
    assert difficulty_counts["easy"]["PASS"] == 7
    assert difficulty_counts["easy"]["FAIL"] == 7
    assert difficulty_counts["typical"]["PASS"] == 14
    assert difficulty_counts["typical"]["FAIL"] == 7


def test_golden_set_source_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that input raw_text is a valid, de-oralized StageTranscript."""
    for item in golden_set_items:
        raw_text = item["input"]["raw_text"].strip()
        item_id = item["id"]

        assert len(raw_text.split()) >= 40, (
            f"Item '{item_id}' raw_text too short: {len(raw_text.split())} words."
        )
        assert raw_text.startswith("## "), (
            f"Item '{item_id}' raw_text must start with '## ' (StageTranscript contract)."
        )

        violations = validate_fluid_prose_mechanical_invariants(raw_text)
        assert not violations, (
            f"Item '{item_id}' raw_text has fluid_prose mechanical violations: {violations}"
        )


def test_golden_set_candidate_text_invariants(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate that candidate_text follows StageTranscript structural rules."""
    for item in golden_set_items:
        cand = item["input"]["candidate_text"].strip()
        item_id = item["id"]
        meta = item["metadata"]

        assert cand.startswith("## "), f"Item '{item_id}' candidate_text must start with '## '."
        assert "### Extra Info" in cand, f"Item '{item_id}' missing mandatory '### Extra Info'."

        comp_section = extract_complementary_section(cand)
        assert comp_section, f"Item '{item_id}' complementary section is empty."

        # If it's NOT an intentional mechanical defect item (e.g. ei_04 testing bullet formatting
        # or ls_07 testing em-dash violation), it must pass full gap_filler mechanical validation
        if meta.get("expected_anomaly") not in MECHANICAL_EXEMPTIONS:
            violations = validate_gap_filler_mechanical_invariants(cand)
            assert not violations, (
                f"Item '{item_id}' has unintended mechanical violations: {violations}"
            )


def test_golden_set_metadata_and_defect_isolation(
    golden_set_items: list[dict[str, Any]],
) -> None:
    """Validate ADR-060 canonical prefixes, authentic video_ids, and strict orthogonality."""
    for item in golden_set_items:
        item_id = item["id"]
        meta = item["metadata"]
        criterion = meta["criterion"]
        verdict = item["expected_output"]["verdict"]
        cand = item["input"]["candidate_text"].strip()

        expected_prefix = CRITERION_PREFIXES[criterion]
        assert item_id.startswith(expected_prefix), (
            f"Item '{item_id}' must use canonical ADR-060 prefix '{expected_prefix}'."
        )

        video_id = meta.get("video_id", "")
        assert len(video_id) >= 3 and not video_id.startswith(SYNTHETIC_VIDEO_PREFIXES), (
            f"Item '{item_id}' must reference an authentic FluidTranscript video_id, got '{video_id}'."
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

        # Cross-criterion orthogonality: zero style-ban leaks outside linear_style_naturalism FAIL
        is_style_fail = (
            criterion == JudgeCriterion.LINEAR_STYLE_NATURALISM.value and verdict == "FAIL"
        )
        if not is_style_fail:
            vocab_hits = RESTRICTED_VOCAB_RE.findall(cand)
            assert not vocab_hits, (
                f"Item '{item_id}' leaks restricted vocabulary outside style FAIL: {vocab_hits}"
            )
            antithesis_hits = BINARY_ANTITHESIS_RE.findall(cand)
            assert not antithesis_hits, (
                f"Item '{item_id}' leaks binary antithesis outside style FAIL: {antithesis_hits}"
            )

        # Extra Info must contain >= 2 numbered continuous paragraphs unless testing extra_info_granularity FAIL
        is_extra_fail = (
            criterion == JudgeCriterion.EXTRA_INFO_GRANULARITY.value and verdict == "FAIL"
        )
        if not is_extra_fail:
            comp_section = extract_complementary_section(cand) or ""
            numbered = [
                line.strip()
                for line in comp_section.splitlines()
                if re.match(r"^\d+\.\s", line.strip())
            ]
            assert len(numbered) >= 2, (
                f"Item '{item_id}' must have >= 2 numbered Extra Info items, got {len(numbered)}."
            )
