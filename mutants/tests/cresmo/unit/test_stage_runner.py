"""Hermetic Unit Tests for PipelineStageRunner and Stage Quality Gate Fabric.

Conforms to:
    - ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
    - SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import NoOpMetricsPort, NoOpTelemetryPort, TelemetryPort
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelName,
    Content,
    ContentId,
    JudgeCriterion,
    JudgeEvaluation,
    PromptKey,
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
        from cresmo.application.pipeline.stage_descriptor import StageConfig
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

        channel = Channel(name="CtxChannel")
        content = Content.create(id=ContentId("vid_ctx_1"), title="CtxTitle")
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("ch_test:vid_ctx_1"),
            user_identity=UserIdentity.worker(),
            channel=channel,
            content=content,
        )

        descriptor = StageConfig[SourceTranscript, CandidateText](
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

    def test_pipeline_stage_runner_with_dependencies_parameter_object(self) -> None:
        """Verify PipelineStageRunner instantiates and operates via PipelineDependencies DTO."""
        from cresmo.application.pipeline.models import PipelineDependencies

        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        deps = PipelineDependencies(
            telemetry_port=telemetry,
            metrics_port=metrics,
            judge_blocking=False,
            judge_max_attempts=2,
        )
        runner = PipelineStageRunner(deps)
        assert runner.telemetry_port is telemetry
        assert runner.metrics_port is metrics
        assert runner.judge_max_attempts == 2

        executed = runner.run_stage(
            "dummy_stage",
            lambda: "result",
            channel_name=ChannelName("TestChan"),
            content_id=ContentId("vid_dep_1"),
        )
        assert executed == "result"

    def test_run_stage_lazy_fallback_callable_not_called_on_success(self) -> None:
        """Verify callable fallback supplier is never called on successful execution (ADR-026 Rule 19)."""
        runner = PipelineStageRunner(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
        )
        mock_fallback_supplier = MagicMock(return_value="lazy_fallback_value")

        result = runner.run_stage(
            "test_stage",
            lambda: "success_value",
            channel_name=ChannelName("TestChan"),
            content_id=ContentId("vid_1"),
            fatal=False,
            fallback=mock_fallback_supplier,
        )

        assert result == "success_value"
        mock_fallback_supplier.assert_not_called()

    def test_run_stage_lazy_fallback_callable_called_on_non_fatal_error(self) -> None:
        """Verify callable fallback supplier is called only on failure (ADR-026 Rule 19)."""
        runner = PipelineStageRunner(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
        )
        mock_fallback_supplier = MagicMock(return_value="lazy_fallback_value")

        def failing_action() -> str:
            raise RuntimeError("Transient pipeline failure")

        result = runner.run_stage(
            "test_stage",
            failing_action,
            channel_name=ChannelName("TestChan"),
            content_id=ContentId("vid_1"),
            fatal=False,
            fallback=mock_fallback_supplier,
        )

        assert result == "lazy_fallback_value"
        mock_fallback_supplier.assert_called_once()

    def test_evaluate_candidate_binds_active_observation_id_adr036(self) -> None:
        """Verify _evaluate_candidate populates EvaluationContext.observation_id from active OTel span (ADR-036)."""
        from opentelemetry.sdk.trace import TracerProvider

        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.application.pipeline.stage_descriptor import StageConfig
        from cresmo.domain.entities import PipelineSessionId, UserIdentity
        from cresmo.domain.value_objects import CandidateText, PromptKey

        provider = TracerProvider()
        tracer = provider.get_tracer("test_tracer")

        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_judge.evaluate.return_value = mock_eval

        runner = PipelineStageRunner(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            llm_judge=mock_judge,
        )

        stage_config = StageConfig(
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="source text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            ),
        )

        context = PipelineExecutionContext(
            session_id=PipelineSessionId.create(channel="test_chan", content_id="test_vid"),
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid")),
        )

        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        with tracer.start_as_current_span("cresmo.stage.fluid_prose"):
            result = runner._evaluate_candidate(
                stage_config,
                source="source text",
                candidate=candidate,
                context=context,
                attempt=1,
            )

        assert result is mock_eval
        mock_judge.evaluate.assert_called_once()
        passed_eval_context = mock_judge.evaluate.call_args[0][0]
        # In ADR-036 it was stage span; in ADR-037 it binds to active evaluation span (or stage fallback)
        assert passed_eval_context.stage_name == "fluid_prose"
        assert passed_eval_context.observation_id is not None

    def test_evaluate_candidate_opens_chronological_evaluation_span(self) -> None:
        """Verify _evaluate_candidate calls start_stage_evaluation_span on TelemetryPort (ADR-037)."""
        mock_telemetry = MagicMock(spec=TelemetryPort)
        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_eval.overall_score = 0.95
        mock_judge.evaluate.return_value = mock_eval

        runner = PipelineStageRunner(
            telemetry_port=mock_telemetry,
            metrics_port=NoOpMetricsPort(),
            llm_judge=mock_judge,
        )

        stage_config = StageConfig(
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="source text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            ),
        )

        context = PipelineExecutionContext(
            session_id=PipelineSessionId.create(channel="test_chan", content_id="test_vid"),
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid")),
        )
        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        runner._evaluate_candidate(
            stage_config,
            source="source text",
            candidate=candidate,
            context=context,
            attempt=1,
        )

        mock_telemetry.start_stage_evaluation_span.assert_called_once_with(
            stage_name="fluid_prose",
            attempt=1,
            attributes={
                "judge.stage_name": "fluid_prose",
                "judge.attempt": 1,
            },
        )
