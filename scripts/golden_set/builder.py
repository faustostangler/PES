"""Golden Dataset Builder for Stage 1 (fluid_prose) Calibration.

Assembles, validates, and exports the canonical 42-item Golden Set conforming to:
- ADR-039 (Canonical Judge Criteria & Mechanical Gates)
- SPEC-015 (Fluid Prose Quality Gates and Calibration Framework)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.golden_set.criterion_epistemic import ITEMS_EPISTEMIC
from scripts.golden_set.criterion_faithfulness import ITEMS_FAITHFULNESS
from scripts.golden_set.criterion_ner import ITEMS_NER
from scripts.golden_set.criterion_orality import ITEMS_ORALITY
from scripts.golden_set.criterion_structure import ITEMS_STRUCTURE
from scripts.golden_set.criterion_voice import ITEMS_VOICE

OUTPUT_PATH = Path("data/golden_sets/fluid_prose_golden_set_42.json")

EXPECTED_CRITERIA = {
    "orality_removal": ITEMS_ORALITY,
    "semantic_faithfulness": ITEMS_FAITHFULNESS,
    "epistemic_critique": ITEMS_EPISTEMIC,
    "ner_preservation": ITEMS_NER,
    "structural_compliance": ITEMS_STRUCTURE,
    "authorial_voice": ITEMS_VOICE,
}


def build_and_validate_golden_set() -> list[dict[str, Any]]:
    """Assemble all criterion modules, validate distributions and invariants."""
    all_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    print("=" * 70)
    print("CRESMO FLUID_PROSE GOLDEN DATASET BUILDER (42 ITEMS)")
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
            else:
                fail_count += 1

            diff = metadata["difficulty"]
            assert diff in difficulty_counts, f"Item '{item_id}' unknown difficulty '{diff}'"
            difficulty_counts[diff][verdict] += 1

            # Validate text format and invariants
            raw_text = item["input"]["raw_text"]
            candidate_text = item["input"]["candidate_text"].strip()

            assert len(raw_text.split()) >= 30, (
                f"Item '{item_id}' raw_text too short: {len(raw_text.split())} words"
            )

            # Check heading and paragraph structure (exempting intentional structural defects)
            if criterion_name != "structural_compliance" or verdict == "PASS":
                assert candidate_text.startswith("## "), (
                    f"Item '{item_id}' candidate_text does not start with '## '"
                )
                prose_paragraphs = [
                    p.strip()
                    for p in candidate_text.split("\n\n")
                    if p.strip() and not p.strip().startswith("#")
                ]
                assert 2 <= len(prose_paragraphs) <= 5, (
                    f"Item '{item_id}' has {len(prose_paragraphs)} prose paragraphs, expected 2-5"
                )

            word_count = len(candidate_text.split())
            if word_count < 150 or word_count > 600:
                print(f"! Warning: Item '{item_id}' candidate word count = {word_count}")

            all_items.append(item)

        assert pass_count == 4 and fail_count == 3, (
            f"Criterion '{criterion_name}' distribution mismatch: {pass_count} PASS / {fail_count} FAIL. Expected 4/3."
        )

        assert difficulty_counts["borderline"]["PASS"] == 1, (
            f"Criterion '{criterion_name}' borderline PASS mismatch: {difficulty_counts['borderline']['PASS']}"
        )
        assert difficulty_counts["borderline"]["FAIL"] == 1, (
            f"Criterion '{criterion_name}' borderline FAIL mismatch: {difficulty_counts['borderline']['FAIL']}"
        )
        assert difficulty_counts["easy"]["PASS"] == 1, (
            f"Criterion '{criterion_name}' easy PASS mismatch: {difficulty_counts['easy']['PASS']}"
        )
        assert difficulty_counts["easy"]["FAIL"] == 1, (
            f"Criterion '{criterion_name}' easy FAIL mismatch: {difficulty_counts['easy']['FAIL']}"
        )
        assert difficulty_counts["typical"]["PASS"] == 2, (
            f"Criterion '{criterion_name}' typical PASS mismatch: {difficulty_counts['typical']['PASS']}"
        )
        assert difficulty_counts["typical"]["FAIL"] == 1, (
            f"Criterion '{criterion_name}' typical FAIL mismatch: {difficulty_counts['typical']['FAIL']}"
        )

        print(
            f"✓ Criterion '{criterion_name:<22}': 7 items (4 PASS / 3 FAIL) | "
            f"Borderline: 1P/1F | Easy: 1P/1F | Typical: 2P/1F"
        )

    # Global Assertions
    total_items = len(all_items)
    total_pass = sum(1 for x in all_items if x["expected_output"]["verdict"] == "PASS")
    total_fail = sum(1 for x in all_items if x["expected_output"]["verdict"] == "FAIL")

    assert total_items == 42, f"Total items {total_items} != 42"
    assert total_pass == 24, f"Total PASS {total_pass} != 24"
    assert total_fail == 18, f"Total FAIL {total_fail} != 18"

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
