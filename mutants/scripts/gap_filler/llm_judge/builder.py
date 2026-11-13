"""Golden Dataset Builder for Stage 2 (gap_filler) Calibration.

Assembles, validates, and exports the canonical 35-item Golden Set conforming to:
- ADR-039 (Progressive LLM-as-a-Judge Calibration Lifecycle)
- ADR-028 (Decoupling Fluid Prose and Socratic Gap Filling)
- SPEC-015 (Quality Gates and Calibration Framework)
"""

from __future__ import annotations

import json
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
from scripts.gap_filler.llm_judge.criterion_causal_agency import ITEMS_CAUSAL_AGENCY
from scripts.gap_filler.llm_judge.criterion_complementary import ITEMS_COMPLEMENTARY
from scripts.gap_filler.llm_judge.criterion_factual_grounding import (
    ITEMS_FACTUAL_GROUNDING,
)
from scripts.gap_filler.llm_judge.criterion_naturalism import ITEMS_NATURALISM
from scripts.gap_filler.llm_judge.criterion_socratic_depth import ITEMS_SOCRATIC_DEPTH

OUTPUT_PATH = REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"

EXPECTED_CRITERIA = {
    "factual_grounding": ITEMS_FACTUAL_GROUNDING,
    "socratic_epistemic_depth": ITEMS_SOCRATIC_DEPTH,
    "causal_stratification_agency": ITEMS_CAUSAL_AGENCY,
    "complementary_substance": ITEMS_COMPLEMENTARY,
    "authorial_naturalism": ITEMS_NATURALISM,
}


def build_and_validate_golden_set() -> list[dict[str, Any]]:
    """Assemble all criterion modules, validate distributions and invariants."""
    all_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    print("=" * 70)
    print("CRESMO GAP_FILLER GOLDEN DATASET BUILDER (35 ITEMS)")
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
            assert "## Informações Complementares" in candidate_text, (
                f"Item '{item_id}' candidate_text missing '## Informações Complementares'"
            )
            comp_section = extract_complementary_section(candidate_text)
            assert comp_section, f"Item '{item_id}' complementary section is empty."

            # Verify that unless it is an intentional mechanical defect item, it passes full gap_filler mechanical validation
            if metadata.get("expected_anomaly") != "bullet_markers_in_complementary":
                gf_violations = validate_gap_filler_mechanical_invariants(candidate_text)
                assert not gf_violations, (
                    f"Item '{item_id}' candidate_text has mechanical violations: {gf_violations}"
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

    assert total_items == 35, f"Total items {total_items} != 35"
    assert total_pass == 20, f"Total PASS {total_pass} != 20"
    assert total_fail == 15, f"Total FAIL {total_fail} != 15"

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
