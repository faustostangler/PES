"""Unit tests for Mechanical Preflight Judge Decorator.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)


def test_short_circuits_when_mechanical_invariants_fail() -> None:
    mock_inner_judge = MagicMock(spec=LlmJudgePort)
    decorator = MechanicalPreflightJudgeDecorator(inner_judge=mock_inner_judge)

    # Invalid fluid prose: contains em-dash and doesn't start with '## '
    invalid_candidate = "Texto sem título — com travessão proibido."
    context = EvaluationContext(
        stage_name="fluid_prose",
        raw_text="Transcrição original...",
        candidate_text=invalid_candidate,
        required_criteria=(
            JudgeCriterion.ORALITY_REMOVAL,
            JudgeCriterion.STRUCTURAL_COMPLIANCE,
        ),
    )

    evaluation = decorator.evaluate(context)

    # Assert mock_inner_judge was NOT called (zero LLM token spend)
    mock_inner_judge.evaluate.assert_not_called()

    # Assert evaluation failed with mechanical reasons
    assert evaluation.passed is False
    assert evaluation.overall_score == 0.0
    assert evaluation.provider == "mechanical_preflight"
    assert any("em-dash" in c.reasoning.lower() for c in evaluation.criteria_scores)


def test_delegates_to_inner_judge_when_mechanical_invariants_pass() -> None:
    mock_inner_judge = MagicMock(spec=LlmJudgePort)
    expected_evaluation = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.95,
        criteria_scores=(),
        provider="gemini",
    )
    mock_inner_judge.evaluate.return_value = expected_evaluation

    decorator = MechanicalPreflightJudgeDecorator(inner_judge=mock_inner_judge)

    valid_candidate = (
        "## Título Válido\n\nTexto em prosa sem travessões, sem bullets e estruturado corretamente."
    )
    context = EvaluationContext(
        stage_name="fluid_prose",
        raw_text="Transcrição original...",
        candidate_text=valid_candidate,
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
    )

    evaluation = decorator.evaluate(context)

    # Inner judge was called
    mock_inner_judge.evaluate.assert_called_once_with(context)
    assert evaluation == expected_evaluation


def test_short_circuits_gap_filler_and_delegates_unmapped_stage() -> None:
    mock_inner_judge = MagicMock(spec=LlmJudgePort)
    expected_eval = JudgeEvaluation(
        target_stage="custom_stage",
        passed=True,
        overall_score=0.9,
        criteria_scores=(),
        provider="gemini",
    )
    mock_inner_judge.evaluate.return_value = expected_eval
    decorator = MechanicalPreflightJudgeDecorator(inner_judge=mock_inner_judge)

    gap_context = EvaluationContext(
        stage_name="gap_filler",
        raw_text="Fluid prose input...",
        candidate_text="## Título\n\nCorpo sem seção obrigatória.",
        required_criteria=(JudgeCriterion.EXTRA_INFO_GRANULARITY,),
    )
    gap_eval = decorator.evaluate(gap_context)

    mock_inner_judge.evaluate.assert_not_called()
    assert gap_eval.passed is False
    assert gap_eval.criteria_scores[0].criterion is JudgeCriterion.EXTRA_INFO_GRANULARITY
    assert "### Extra Info" in gap_eval.criteria_scores[0].reasoning

    other_context = EvaluationContext(
        stage_name="custom_stage",
        raw_text="Raw input",
        candidate_text="Any output",
        required_criteria=(),
    )
    assert decorator.evaluate(other_context) == expected_eval
    mock_inner_judge.evaluate.assert_called_once_with(other_context)
