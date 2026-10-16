"""Unit tests for Fluid Prose Judge Calibration Harness.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)
from scripts.calibrate_fluid_prose_judge import (
    ConfusionMatrix,
    evaluate_single_item,
    run_local_calibration,
)


def test_confusion_matrix_perfect_score() -> None:
    matrix = ConfusionMatrix(tp=10, fp=0, fn=0, tn=10)
    assert matrix.total_valid == 20
    assert matrix.accuracy == 1.0
    assert matrix.precision == 1.0
    assert matrix.recall == 1.0
    assert matrix.f1 == 1.0


def test_confusion_matrix_zero_divisions() -> None:
    matrix = ConfusionMatrix(tp=0, fp=0, fn=0, tn=0)
    assert matrix.total_valid == 0
    assert matrix.accuracy == 0.0
    assert matrix.precision == 0.0
    assert matrix.recall == 0.0
    assert matrix.f1 == 0.0


def test_confusion_matrix_with_errors() -> None:
    # 8 TP, 2 FP, 2 FN, 8 TN
    matrix = ConfusionMatrix(tp=8, fp=2, fn=2, tn=8)
    assert matrix.total_valid == 20
    assert matrix.accuracy == 16 / 20  # 0.80
    assert matrix.precision == 8 / 10  # 0.80
    assert matrix.recall == 8 / 10  # 0.80
    assert matrix.f1 == pytest.approx(0.80)


def test_evaluate_single_item_with_mock_judge() -> None:
    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.return_value = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.92,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                score=0.95,
                passed=True,
                reasoning="Orality purged",
            ),
        ),
        provider="gemini",
    )

    item = {
        "id": "test_item",
        "input": {
            "raw_text": "Transcrição original",
            "candidate_text": "## Texto Válido\n\nCorpo em prosa.",
        },
        "expected_output": {"verdict": "PASS"},
    }

    actual, expected, score, reasoning = evaluate_single_item(mock_judge, item)

    assert actual == "PASS"
    assert expected == "PASS"
    assert score == 0.92
    assert "Quality threshold not met" in reasoning or reasoning == "Quality threshold not met."


def test_run_local_calibration_computes_counts() -> None:
    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.return_value = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.20,
        criteria_scores=(),
        provider="mechanical_preflight",
    )

    items = [
        {
            "id": "item1",
            "input": {"raw_text": "raw", "candidate_text": "bad"},
            "expected_output": {"verdict": "FAIL"},
        },
        {
            "id": "item2",
            "input": {"raw_text": "raw", "candidate_text": "bad"},
            "expected_output": {"verdict": "PASS"},
        },
    ]

    matrix = run_local_calibration(mock_judge, items)
    # item1: expected FAIL, actual FAIL -> TN
    # item2: expected PASS, actual FAIL -> FN
    assert matrix.tn == 1
    assert matrix.fn == 1
    assert matrix.tp == 0
    assert matrix.fp == 0
