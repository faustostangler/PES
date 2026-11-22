"""Unit tests for TelemetryJudgeDecorator (SPEC-070 §3.3)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.application.ports.telemetry import NoOpTelemetryPort, TelemetryPort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


class TestTelemetryJudgeDecorator:
    """Verify judge evaluation score emission strictly through TelemetryPort."""

    def test_emits_stage_namespaced_scores_with_observation_id_and_zero_flushes(self) -> None:
        inner = MagicMock(spec=LlmJudgePort)
        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.95,
                    passed=True,
                    reasoning="Clean prose",
                ),
                CriterionScore(
                    criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                    score=0.85,
                    passed=True,
                    reasoning="Facts preserved",
                ),
            ),
            provider="gemini",
            trace_id="trace_eval_1",
        )
        inner.evaluate.return_value = eval_result
        telemetry = InMemoryTelemetryPort()

        decorator = TelemetryJudgeDecorator(inner_judge=inner, telemetry_port=telemetry)
        ctx = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="candidate",
            trace_id="trace_ctx_fallback",
            observation_id="obs_1234567890ab",
        )

        out = decorator.evaluate(ctx)

        inner.evaluate.assert_called_once_with(ctx)
        assert out is eval_result
        assert telemetry.flush_count == 0
        assert len(telemetry.scores) == 2
        assert telemetry.scores[0].name == "fluid_prose.orality_removal"
        assert telemetry.scores[0].value == 0.95
        assert telemetry.scores[0].comment == "Clean prose"
        assert telemetry.scores[0].trace_id == "trace_eval_1"
        assert telemetry.scores[0].observation_id == "obs_1234567890ab"
        assert telemetry.scores[1].name == "fluid_prose.semantic_faithfulness"
        assert telemetry.scores[1].value == 0.85

    def test_falls_back_to_context_trace_id_and_unprefixed_score_when_stage_empty(self) -> None:
        inner = MagicMock(spec=LlmJudgePort)
        eval_result = JudgeEvaluation(
            target_stage="",
            passed=True,
            overall_score=0.8,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.8,
                    passed=True,
                    reasoning="Solid",
                ),
            ),
            provider="ollama",
            trace_id=None,
        )
        inner.evaluate.return_value = eval_result
        telemetry = InMemoryTelemetryPort()
        decorator = TelemetryJudgeDecorator(inner_judge=inner, telemetry_port=telemetry)

        ctx = EvaluationContext(
            stage_name="",
            raw_text="raw",
            candidate_text="cand",
            trace_id="trace_from_ctx",
        )
        decorator.evaluate(ctx)

        assert len(telemetry.scores) == 1
        assert telemetry.scores[0].name == "orality_removal"
        assert telemetry.scores[0].trace_id == "trace_from_ctx"
        assert telemetry.scores[0].observation_id is None

    def test_skips_score_emission_when_trace_id_missing_and_defaults_to_noop_port(self) -> None:
        inner = MagicMock(spec=LlmJudgePort)
        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.9,
                    passed=True,
                    reasoning="Ok",
                ),
            ),
            provider="ollama",
            trace_id=None,
        )
        inner.evaluate.return_value = eval_result

        decorator = TelemetryJudgeDecorator(inner_judge=inner, telemetry_port=None)
        assert isinstance(decorator._telemetry, NoOpTelemetryPort)

        telemetry = InMemoryTelemetryPort()
        decorator_with_spy = TelemetryJudgeDecorator(inner_judge=inner, telemetry_port=telemetry)
        ctx = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            trace_id=None,
        )
        assert decorator_with_spy.evaluate(ctx) is eval_result
        assert telemetry.scores == []

    def test_fail_silent_resilience_when_record_score_raises(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        inner = MagicMock(spec=LlmJudgePort)
        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.9,
                    passed=True,
                    reasoning="Ok",
                ),
            ),
            provider="gemini",
            trace_id="tr_err",
        )
        inner.evaluate.return_value = eval_result

        broken_telemetry = MagicMock(spec=TelemetryPort)
        broken_telemetry.record_score.side_effect = RuntimeError("backend down")
        decorator = TelemetryJudgeDecorator(inner_judge=inner, telemetry_port=broken_telemetry)

        ctx = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw",
            candidate_text="cand",
            trace_id="tr_err",
        )
        with caplog.at_level(logging.WARNING):
            result = decorator.evaluate(ctx)

        assert result is eval_result
        assert [r.getMessage() for r in caplog.records] == [
            "Failed to emit telemetry score for criterion 'orality_removal': backend down"
        ]
