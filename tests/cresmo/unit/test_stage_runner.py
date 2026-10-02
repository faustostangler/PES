"""Hermetic Unit Tests for PipelineStageRunner and Stage Quality Gate Fabric.

Conforms to:
    - ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
    - SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import NoOpMetricsPort, NoOpTelemetryPort
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    JudgeCriterion,
    JudgeEvaluation,
    StageEvaluationSpec,
)


class TestStageEvaluationSpec:
    """Test suite for StageEvaluationSpec value object validation."""

    def test_valid_spec_creation(self) -> None:
        spec = StageEvaluationSpec(
            raw_text="Raw ground truth",
            candidate_extractor=lambda res: res["text"],
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=3,
        )
        assert spec.raw_text == "Raw ground truth"
        assert spec.max_attempts == 3
        assert spec.candidate_extractor({"text": "Hello"}) == "Hello"

    def test_invalid_max_attempts_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            StageEvaluationSpec(
                raw_text="Raw ground truth",
                candidate_extractor=lambda res: str(res),
                required_criteria=(),
                max_attempts=0,
            )


class TestPipelineStageRunnerEvaluatedStage:
    """Test suite for PipelineStageRunner.run_evaluated_stage closed-loop quality gate."""

    def test_run_evaluated_stage_without_spec_executes_once(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        call_count = 0

        def sample_action() -> str:
            nonlocal call_count
            call_count += 1
            return "Generated Result"

        result = runner.run_evaluated_stage(
            "fluid_prose",
            sample_action,
            channel_name=ChannelName("Test Channel"),
            content_id=ContentId("content_1"),
            eval_spec=None,
        )

        assert result == "Generated Result"
        assert call_count == 1
        assert mock_judge.evaluate.call_count == 0

    def test_run_evaluated_stage_without_judge_executes_once(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=None,
        )

        spec = StageEvaluationSpec(
            raw_text="Raw",
            candidate_extractor=lambda res: str(res),
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=3,
        )

        result = runner.run_evaluated_stage(
            "fluid_prose",
            lambda: "Direct Output",
            channel_name=ChannelName("Test Channel"),
            content_id=ContentId("content_2"),
            eval_spec=spec,
        )

        assert result == "Direct Output"

    def test_run_evaluated_stage_passes_first_attempt(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()

        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="gemini",
        )

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        spec = StageEvaluationSpec(
            raw_text="Raw Source",
            candidate_extractor=lambda res: str(res),
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=3,
        )

        result = runner.run_evaluated_stage(
            "fluid_prose",
            lambda: "Clean Prose",
            channel_name=ChannelName("Test Channel"),
            content_id=ContentId("content_3"),
            eval_spec=spec,
        )

        assert result == "Clean Prose"
        assert mock_judge.evaluate.call_count == 1
        eval_ctx = mock_judge.evaluate.call_args[0][0]
        assert eval_ctx.stage_name == "fluid_prose"
        assert eval_ctx.candidate_text == "Clean Prose"
        assert eval_ctx.raw_text == "Raw Source"

    def test_run_evaluated_stage_retries_on_failure_and_succeeds(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()

        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.40,
            criteria_scores=(),
            provider="gemini",
        )
        pass_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.90,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.side_effect = [fail_eval, pass_eval]

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
        )

        attempts = 0

        def flaky_action() -> str:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                return "Draft with filler words"
            return "Refined clean prose"

        spec = StageEvaluationSpec(
            raw_text="Raw Source",
            candidate_extractor=lambda res: str(res),
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=3,
        )

        result = runner.run_evaluated_stage(
            "fluid_prose",
            flaky_action,
            channel_name=ChannelName("Test Channel"),
            content_id=ContentId("content_4"),
            eval_spec=spec,
        )

        assert result == "Refined clean prose"
        assert attempts == 2
        assert mock_judge.evaluate.call_count == 2

    def test_run_evaluated_stage_fails_all_attempts_non_blocking_returns_candidate(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()

        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.50,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = fail_eval

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
            judge_blocking=False,
        )

        spec = StageEvaluationSpec(
            raw_text="Raw Source",
            candidate_extractor=lambda res: str(res),
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=2,
        )

        result = runner.run_evaluated_stage(
            "fluid_prose",
            lambda: "Candidate With Imperfections",
            channel_name=ChannelName("Test Channel"),
            content_id=ContentId("content_5"),
            eval_spec=spec,
        )

        assert result == "Candidate With Imperfections"
        assert mock_judge.evaluate.call_count == 2

    def test_run_evaluated_stage_fails_all_attempts_blocking_raises_domain_error(self) -> None:
        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        mock_judge = MagicMock()

        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.42,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = fail_eval

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            llm_judge=mock_judge,
            judge_blocking=True,
        )

        spec = StageEvaluationSpec(
            raw_text="Raw Source",
            candidate_extractor=lambda res: str(res),
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=2,
        )

        with pytest.raises(DomainValidationError, match="fluid_prose quality evaluation failed"):
            runner.run_evaluated_stage(
                "fluid_prose",
                lambda: "Failed Candidate",
                channel_name=ChannelName("Test Channel"),
                content_id=ContentId("content_6"),
                eval_spec=spec,
            )

        assert mock_judge.evaluate.call_count == 2

    def test_execute_stage_with_pipeline_execution_context(self) -> None:
        """Verify execute_stage cleanly consumes PipelineExecutionContext."""
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.application.pipeline.stage_descriptor import StageDescriptor
        from cresmo.domain.entities import PipelineSessionId, SourceTranscript, UserIdentity
        from cresmo.domain.value_objects import CandidateText, PromptKey
        from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
        from tests.doubles.mock_adapters import MockLLMAdapter

        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        prompt_provider = JsonPromptProvider()
        llm_port = MockLLMAdapter(responses=["# Synthesized Title\n\nClean body text."])

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            prompt_provider=prompt_provider,
            llm_transformation_port=llm_port,
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("ch_test:vid_ctx_1"),
            user_identity=UserIdentity.worker(),
            channel_name=ChannelName("CtxChannel"),
            content_id=ContentId("vid_ctx_1"),
        )

        descriptor = StageDescriptor[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )

        source = SourceTranscript(
            content_id=ContentId("vid_ctx_1"),
            channel_name=ChannelName("CtxChannel"),
            body="Raw speech text.",
        )

        result = runner.execute_stage(descriptor, source, context=ctx)
        assert isinstance(result, CandidateText)
        assert "Clean body text." in result.text
