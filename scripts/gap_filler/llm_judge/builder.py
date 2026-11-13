"""Golden Dataset Builder for Stage 2 (gap_filler) Calibration.

Assembles, validates, and exports the canonical 49-item Golden Set conforming to:
- ADR-060 (Gap Filler Judge Criteria v2: 7 Orthogonal Criteria)
- ADR-039 (Progressive LLM-as-a-Judge Calibration Lifecycle)
- ADR-028 (Decoupling Fluid Prose and Socratic Gap Filling)
- ADR-010 (Zero Legacy Shims)
- SPEC-015 (Quality Gates and Calibration Framework)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path when invoked directly as a script / debugger
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cresmo.domain.services.mechanical_validator import (
    extract_complementary_section,
    validate_fluid_prose_mechanical_invariants,
    validate_gap_filler_mechanical_invariants,
)
from scripts.gap_filler.llm_judge.criterion_braudelian_stratification import (
    ITEMS_BRAUDELIAN_STRATIFICATION,
)
from scripts.gap_filler.llm_judge.criterion_competing_hypotheses import (
    ITEMS_COMPETING_HYPOTHESES,
)
from scripts.gap_filler.llm_judge.criterion_conceptual_mechanical_decomposition import (
    ITEMS_CONCEPTUAL_MECHANICAL_DECOMPOSITION,
)
from scripts.gap_filler.llm_judge.criterion_epistemic_grounding_segregation import (
    ITEMS_EPISTEMIC_GROUNDING_SEGREGATION,
)
from scripts.gap_filler.llm_judge.criterion_extra_info_granularity import (
    ITEMS_EXTRA_INFO_GRANULARITY,
)
from scripts.gap_filler.llm_judge.criterion_genealogy_hidden_agency import (
    ITEMS_GENEALOGY_HIDDEN_AGENCY,
)
from scripts.gap_filler.llm_judge.criterion_linear_style_naturalism import (
    ITEMS_LINEAR_STYLE_NATURALISM,
)

OUTPUT_PATH = REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"

EXPECTED_CRITERIA: dict[str, list[dict[str, Any]]] = {
    "epistemic_grounding_segregation": ITEMS_EPISTEMIC_GROUNDING_SEGREGATION,
    "conceptual_mechanical_decomposition": ITEMS_CONCEPTUAL_MECHANICAL_DECOMPOSITION,
    "braudelian_stratification": ITEMS_BRAUDELIAN_STRATIFICATION,
    "genealogy_hidden_agency": ITEMS_GENEALOGY_HIDDEN_AGENCY,
    "competing_hypotheses": ITEMS_COMPETING_HYPOTHESES,
    "extra_info_granularity": ITEMS_EXTRA_INFO_GRANULARITY,
    "linear_style_naturalism": ITEMS_LINEAR_STYLE_NATURALISM,
}

CRITERION_PREFIXES: dict[str, str] = {
    "epistemic_grounding_segregation": "eg_",
    "conceptual_mechanical_decomposition": "cm_",
    "braudelian_stratification": "bs_",
    "genealogy_hidden_agency": "gh_",
    "competing_hypotheses": "ch_",
    "extra_info_granularity": "ei_",
    "linear_style_naturalism": "ls_",
}

RESTRICTED_VOCAB_RE = re.compile(r"\b(?:forj|oper|mold|abrig|fardo)\w*\b", re.IGNORECASE)
BINARY_ANTITHESIS_RE = re.compile(
    r"\bnão\s+(?:apenas|somente|só|se trata|se resum\w+|decorre|reside|desempenha|constitui|é|era|foi|são|foram)"
    r"[^.!?\n]{1,120}\b(?:mas|e sim|senão)\b",
    re.IGNORECASE,
)
MECHANICAL_EXEMPTIONS = {
    "bullet_markers_in_complementary",
    "em_dash_style_violation",
}


def build_and_validate_golden_set() -> list[dict[str, Any]]:
    """Assemble all criterion modules, validate distributions and invariants."""
    all_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    print("=" * 70)
    print("CRESMO GAP_FILLER GOLDEN DATASET BUILDER (49 ITEMS)")
    print("=" * 70)

    for criterion_name, items in EXPECTED_CRITERIA.items():
        assert len(items) == 7, (
            f"Criterion '{criterion_name}' has {len(items)} items, expected exactly 7."
        )

        pass_count = 0
        fail_count = 0
        difficulty_counts: dict[str, dict[str, int]] = {
            "borderline": {"PASS": 0, "FAIL": 0},
            "easy": {"PASS": 0, "FAIL": 0},
            "typical": {"PASS": 0, "FAIL": 0},
        }

        for item in items:
            item_id = item["id"]
            assert item_id not in seen_ids, f"Duplicate item id: '{item_id}'"
            seen_ids.add(item_id)
            expected_prefix = CRITERION_PREFIXES[criterion_name]
            assert item_id.startswith(expected_prefix), (
                f"Item '{item_id}' must start with canonical ADR-060 prefix '{expected_prefix}'"
            )

            metadata = item["metadata"]
            assert metadata["criterion"] == criterion_name, (
                f"Item '{item_id}' has criterion '{metadata['criterion']}', expected '{criterion_name}'"
            )

            verdict = item["expected_output"]["verdict"]
            assert verdict in ("PASS", "FAIL"), f"Item '{item_id}' has invalid verdict: '{verdict}'"
            assert metadata["target_verdict"] == verdict, (
                f"Item '{item_id}' target_verdict mismatch: {metadata['target_verdict']} vs {verdict}"
            )

            if verdict == "PASS":
                pass_count += 1
                assert metadata.get("expected_anomaly") == "none", (
                    f"PASS item '{item_id}' must have expected_anomaly='none'"
                )
                assert metadata.get("defect_location") == "none", (
                    f"PASS item '{item_id}' must have defect_location='none'"
                )
            else:
                fail_count += 1
                assert metadata.get("expected_anomaly") not in (None, "none", ""), (
                    f"FAIL item '{item_id}' must specify expected_anomaly"
                )
                assert metadata.get("defect_location") not in (None, "none", ""), (
                    f"FAIL item '{item_id}' must specify defect_location"
                )

            diff = metadata["difficulty"]
            assert diff in difficulty_counts, f"Item '{item_id}' unknown difficulty '{diff}'"
            difficulty_counts[diff][verdict] += 1

            # Validate text format and invariants
            raw_text = item["input"]["raw_text"].strip()
            candidate_text = item["input"]["candidate_text"].strip()

            assert len(raw_text.split()) >= 40, (
                f"Item '{item_id}' raw_text too short: {len(raw_text.split())} words"
            )
            assert raw_text.startswith("## "), (
                f"Item '{item_id}' raw_text does not start with '## '"
            )
            fp_violations = validate_fluid_prose_mechanical_invariants(raw_text)
            assert not fp_violations, (
                f"Item '{item_id}' raw_text has mechanical violations: {fp_violations}"
            )

            # Check candidate_text invariants
            assert candidate_text.startswith("## "), (
                f"Item '{item_id}' candidate_text does not start with '## '"
            )
            assert "### Extra Info" in candidate_text, (
                f"Item '{item_id}' candidate_text missing '### Extra Info'"
            )
            comp_section = extract_complementary_section(candidate_text)
            assert comp_section, f"Item '{item_id}' complementary section is empty."

            # Verify that unless it is an intentional mechanical defect item, it passes full gap_filler mechanical validation
            if metadata.get("expected_anomaly") not in MECHANICAL_EXEMPTIONS:
                gf_violations = validate_gap_filler_mechanical_invariants(candidate_text)
                assert not gf_violations, (
                    f"Item '{item_id}' candidate_text has mechanical violations: {gf_violations}"
                )

            # Enforce strict cross-criterion orthogonality
            is_style_fail = criterion_name == "linear_style_naturalism" and verdict == "FAIL"
            if not is_style_fail:
                vocab_hits = RESTRICTED_VOCAB_RE.findall(candidate_text)
                assert not vocab_hits, (
                    f"Item '{item_id}' leaks restricted vocabulary outside style FAIL: {vocab_hits}"
                )
                antithesis_hits = BINARY_ANTITHESIS_RE.findall(candidate_text)
                assert not antithesis_hits, (
                    f"Item '{item_id}' leaks binary antithesis outside style FAIL: {antithesis_hits}"
                )

            is_extra_fail = criterion_name == "extra_info_granularity" and verdict == "FAIL"
            if not is_extra_fail:
                numbered = [
                    line.strip()
                    for line in comp_section.splitlines()
                    if re.match(r"^\d+\.\s", line.strip())
                ]
                assert len(numbered) >= 2, (
                    f"Item '{item_id}' must have >= 2 numbered Extra Info items, got {len(numbered)}"
                )

            all_items.append(item)

        assert pass_count == 4 and fail_count == 3, (
            f"Criterion '{criterion_name}' distribution mismatch: {pass_count} PASS / {fail_count} FAIL. Expected 4/3."
        )

        assert difficulty_counts["borderline"]["PASS"] == 1
        assert difficulty_counts["borderline"]["FAIL"] == 1
        assert difficulty_counts["easy"]["PASS"] == 1
        assert difficulty_counts["easy"]["FAIL"] == 1
        assert difficulty_counts["typical"]["PASS"] == 2
        assert difficulty_counts["typical"]["FAIL"] == 1

        print(
            f"✓ Criterion '{criterion_name:<30}': 7 items (4 PASS / 3 FAIL) | "
            f"Borderline: 1P/1F | Easy: 1P/1F | Typical: 2P/1F"
        )

    # Global Assertions
    total_items = len(all_items)
    total_pass = sum(1 for x in all_items if x["expected_output"]["verdict"] == "PASS")
    total_fail = sum(1 for x in all_items if x["expected_output"]["verdict"] == "FAIL")

    assert total_items == 49, f"Total items {total_items} != 49"
    assert total_pass == 28, f"Total PASS {total_pass} != 28"
    assert total_fail == 21, f"Total FAIL {total_fail} != 21"

    print("-" * 70)
    print(f"Total Dataset: {total_items} items")
    print(f"PASS Verdicts: {total_pass} ({total_pass / total_items * 100:.1f}%)")
    print(f"FAIL Verdicts: {total_fail} ({total_fail / total_items * 100:.1f}%)")
    print("=" * 70)

    return all_items


def main() -> None:
    items = build_and_validate_golden_set()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved canonical Golden Set to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
