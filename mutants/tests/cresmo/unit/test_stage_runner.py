"""Hermetic Unit Tests for PipelineStageRunner and Stage Quality Gate Fabric.

Conforms to:
    - ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
    - SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import NoOpMetricsPort, NoOpTelemetryPort, TelemetryPort
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.exceptions import DomainValidationError, StageQuarantinedError
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    CriterionScore,
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


class TestStageRunnerHelperAndInit:
    """Verifies _as_str, initialization validation, defaults, and warmup."""

    def test_as_str_exhaustive(self) -> None:
        from cresmo.application.pipeline.stage_runner import _as_str
        from cresmo.domain.entities import PipelineSessionId, UserIdentity
        from cresmo.domain.value_objects import ChannelId, ChannelName, ContentId

        assert _as_str(None) == ""
        assert _as_str("raw_string") == "raw_string"
        assert _as_str(ChannelName("Ch1")) == "Ch1"
        assert _as_str(ContentId("c1234567")) == "c1234567"
        assert _as_str(ChannelId("UC_abc")) == "UC_abc"
        assert _as_str(PipelineSessionId("sess:123")) == "sess:123"
        assert _as_str(UserIdentity.worker()) == "system:worker"

    def test_init_requires_both_ports(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(telemetry_port=None, metrics_port=mock_m)

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(telemetry_port=mock_t, metrics_port=None)

    def test_init_defaults(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)

        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)
        assert runner.judge_blocking is False
        assert runner.judge_max_attempts == 1
        assert runner.prompt_provider is None
        assert runner.llm_transformation_port is None
        assert runner.stage_factory is None
        assert runner.critique_synthesizer is None
        assert runner.ledger_port is None

        # Custom judge_max_attempts passed directly to constructor
        runner_custom = PipelineStageRunner(
            telemetry_port=mock_t, metrics_port=mock_m, judge_max_attempts=4
        )
        assert runner_custom.judge_max_attempts == 4

    def test_warmup_with_and_without_llm_port(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        mock_llm = MagicMock()

        runner = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_transformation_port=mock_llm,
        )
        runner.warmup(timeout_seconds=3.5)
        mock_llm.warmup.assert_called_once_with(timeout_seconds=3.5)

        # Without LLM transformation port, warmup is a no-op
        runner_none = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)
        runner_none.warmup(timeout_seconds=2.0)


class TestStageRunnerResolution:
    """Verifies dependency resolution and critique synthesis."""

    def test_resolve_prompt_provider(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        with pytest.raises(
            ValueError,
            match=r"^PromptProviderPort must be provided via constructor or execute_stage argument$",
        ):
            runner._resolve_prompt_provider(None)

        custom_pp = MagicMock()
        assert runner._resolve_prompt_provider(custom_pp) is custom_pp

    def test_resolve_llm_transformation_port(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        with pytest.raises(
            ValueError,
            match=r"^LLMTransformationPort must be provided via constructor or execute_stage argument$",
        ):
            runner._resolve_llm_transformation_port(None)

        custom_llm = MagicMock()
        assert runner._resolve_llm_transformation_port(custom_llm) is custom_llm

    def test_resolve_stage_config(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        with pytest.raises(ValueError, match="Cannot resolve stage 'custom' from string without an injected StageFactory."):
            runner._resolve_stage_config("custom")

        mock_factory = MagicMock()
        mock_cfg = MagicMock(spec=StageConfig)
        mock_factory.build_stage.return_value = mock_cfg

        runner_with_factory = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            stage_factory=mock_factory,
        )
        assert runner_with_factory._resolve_stage_config("fluid_prose") is mock_cfg
        mock_factory.build_stage.assert_called_once_with("fluid_prose")
        assert runner_with_factory._resolve_stage_descriptor("fluid_prose") is mock_cfg
        assert runner_with_factory._resolve_stage_config(mock_cfg) is mock_cfg

    def test_synthesize_critique(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        mock_synth = MagicMock()
        mock_synth.synthesize.return_value = "Synthesized critique"

        runner_synth = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            critique_synthesizer=mock_synth,
        )
        eval_mock = MagicMock(spec=JudgeEvaluation)
        assert runner_synth._synthesize_critique(eval_mock, "fluid_prose") == "Synthesized critique"
        mock_synth.synthesize.assert_called_once_with(eval_mock, "fluid_prose")

        runner_default = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)
        eval_mock.extract_critique.return_value = "Extracted critique"
        assert runner_default._synthesize_critique(eval_mock, "fluid_prose") == "Extracted critique"
        eval_mock.extract_critique.assert_called_once()


class TestStageRunnerMetricsAndTelemetry:
    """Verifies metrics recording, duration observing, and session coherence reporting."""

    def test_record_evaluation_metrics_exact_parameters(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        runner._record_evaluation_metrics("fluid_prose", True, 1)
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "fluid_prose", "passed": "true", "attempt": "1"},
        )

        mock_m.reset_mock()
        runner._record_evaluation_metrics("gap_filler", False, 2)
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "gap_filler", "passed": "false", "attempt": "2"},
        )

    def test_record_error_metric_exact_parameters(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        ch = Channel(name="MyChan", id=ChannelId("UC_err"))
        cnt = Content(id=ContentId("vid_err_1"), title="ErrTitle")
        err = RuntimeError("Disk full")

        runner._record_error_metric(err, "fluid_prose", ch, cnt)
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_pipeline_errors_total",
            1.0,
            labels={
                "error_type": "RuntimeError",
                "channel_id": "UC_err",
                "content_id": "vid_err_1",
                "channel_name": "MyChan",
                "stage": "fluid_prose",
            },
        )

        # When channel has no id, channel_id label is empty string
        ch_no_id = Channel(name="MyChan", id=None)
        runner._record_error_metric(err, "fluid_prose", ch_no_id, cnt)
        mock_m.increment_counter.assert_called_with(
            "cresmo_pipeline_errors_total",
            1.0,
            labels={
                "error_type": "RuntimeError",
                "channel_id": "",
                "content_id": "vid_err_1",
                "channel_name": "MyChan",
                "stage": "fluid_prose",
            },
        )

    def test_record_duration_metric_exact_parameters(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        ch = Channel(name="MyChan", id=ChannelId("UC_dur"))
        cnt = Content(id=ContentId("vid_dur_1"), title="DurTitle")

        runner._record_duration_metric(0.85, "fluid_prose", ch, cnt, "success")
        mock_m.observe_histogram.assert_called_once_with(
            "cresmo_pipeline_stage_duration_seconds",
            0.85,
            labels={
                "stage": "fluid_prose",
                "channel_id": "UC_dur",
                "channel_name": "MyChan",
                "status": "success",
            },
        )

        # When channel has no id, channel_id label is empty string
        ch_no_id = Channel(name="MyChan", id=None)
        runner._record_duration_metric(0.50, "fluid_prose", ch_no_id, cnt, "failure")
        mock_m.observe_histogram.assert_called_with(
            "cresmo_pipeline_stage_duration_seconds",
            0.50,
            labels={
                "stage": "fluid_prose",
                "channel_id": "",
                "channel_name": "MyChan",
                "status": "failure",
            },
        )

    def test_record_session_completion_exact_parameters(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_note1 = MagicMock()
        mock_note2 = MagicMock()
        mock_moc = MagicMock()

        class RealInventoryStub:
            items = ["c1", "c2", "c3"]

        real_inv = RealInventoryStub()
        mock_dedup = MagicMock()
        mock_dedup.duplicates_unified_count = 1

        runner.record_session_completion(
            session_id=PipelineSessionId("ch_s:vid_s"),
            content_id=ContentId("vid_sess"),
            channel_name=ChannelName("Chan"),
            synthesized_notes=[mock_note1, mock_note2],
            inventory=real_inv,  # type: ignore[arg-type]
            mocs=[mock_moc],
            dedup_report=mock_dedup,
            channel_id=ChannelId("UC_sess"),
        )

        # Check transcript counter
        mock_m.increment_counter.assert_any_call(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": "UC_sess",
                "channel_name": "Chan",
                "content_id": "vid_sess",
                "status": "completed",
                "modality": "transcript",
            },
        )
        # Check notes counter
        mock_m.increment_counter.assert_any_call(
            "cresmo_atomic_notes_synthesized_total",
            2.0,
            labels={
                "channel_id": "UC_sess",
                "channel_name": "Chan",
                "content_id": "vid_sess",
                "note_type": "all",
            },
        )
        # Check session coherence telemetry
        mock_t.record_session_coherence.assert_called_once()
        coherence_call = mock_t.record_session_coherence.call_args[1]
        assert coherence_call["session_id"].value == "ch_s:vid_s"
        assert coherence_call["content_id"].value == "vid_sess"
        assert abs(coherence_call["score"] - (2 / 3)) < 1e-6
        assert coherence_call["details"] == {
            "synthesized_notes_count": 2,
            "inventory_count": 3,
            "mocs_count": 1,
            "duplicates_unified": 1,
        }

    def test_record_session_completion_with_string_inputs_and_no_items(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_inv_no_items = object()  # Has no .items attribute
        mock_dedup = MagicMock()
        mock_dedup.duplicates_unified_count = 0

        runner.record_session_completion(
            session_id="chan_str:c1234567",
            content_id="c1234567",
            channel_name="StrChan",
            synthesized_notes=[],
            inventory=mock_inv_no_items,  # type: ignore[arg-type]
            mocs=[],
            dedup_report=mock_dedup,
            channel_id=None,
        )

        coherence_call = mock_t.record_session_coherence.call_args[1]
        assert coherence_call["session_id"].value == "chan_str:c1234567"
        assert coherence_call["content_id"].value == "c1234567"
        assert coherence_call["score"] == 0.0
        assert coherence_call["details"] == {
            "synthesized_notes_count": 0,
            "inventory_count": 1,
            "mocs_count": 0,
            "duplicates_unified": 0,
        }

    def test_record_session_completion_score_cap_and_zero_items(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        # Cap score at 1.0 when synthesized_notes > items
        mock_inv = MagicMock()
        mock_inv.items = ["c1"]
        runner.record_session_completion(
            session_id=PipelineSessionId("ch_s:vid_s"),
            content_id=ContentId("c1234567"),
            channel_name=ChannelName("Chan"),
            synthesized_notes=[MagicMock(), MagicMock(), MagicMock()],
            inventory=mock_inv,
            mocs=[],
            dedup_report=MagicMock(duplicates_unified_count=0),
        )
        assert mock_t.record_session_coherence.call_args[1]["score"] == 1.0

        # When items is empty list (item_count = 0), score is 1.0
        mock_inv_zero = MagicMock()
        mock_inv_zero.items = []
        runner.record_session_completion(
            session_id=PipelineSessionId("ch_s:vid_s"),
            content_id=ContentId("c1234567"),
            channel_name=ChannelName("Chan"),
            synthesized_notes=[],
            inventory=mock_inv_zero,
            mocs=[],
            dedup_report=MagicMock(duplicates_unified_count=0),
        )
        assert mock_t.record_session_coherence.call_args[1]["score"] == 1.0

        # When synthesized_notes has 1 item and inventory has 1 item (kills max(2, item_count))
        class SingleItemStub:
            items = ["c1"]

        runner.record_session_completion(
            session_id=PipelineSessionId("ch_s:vid_s"),
            content_id=ContentId("c1234567"),
            channel_name=ChannelName("Chan"),
            synthesized_notes=[MagicMock()],
            inventory=SingleItemStub(),  # type: ignore[arg-type]
            mocs=[],
            dedup_report=MagicMock(duplicates_unified_count=0),
        )
        assert mock_t.record_session_coherence.call_args[1]["score"] == 1.0


class TestStageRunnerActiveTraceId:
    """Verifies deterministic trace ID derivation across context combinations."""

    def test_trace_id_with_recording_span(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_span = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        mock_span.get_span_context.return_value = mock_ctx
        with patch("cresmo.application.pipeline.stage_runner.trace.get_current_span", return_value=mock_span):
            tid = runner._get_active_trace_id()
            assert tid == format(0x1234567890ABCDEF1234567890ABCDEF, "032x")

    def test_trace_id_without_span(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        # Channel with id
        ch_with_id = Channel(name="NameA", id=ChannelId("UC_id_a"))
        cnt = Content(id=ContentId("vid_1001"))
        assert runner._get_active_trace_id(ch_with_id, cnt) == "cresmo_UC_id_a_vid_1001"

        # Channel without id
        ch_no_id = Channel(name="NameA", id=None)
        assert runner._get_active_trace_id(ch_no_id, cnt) == "cresmo_NameA_vid_1001"

        # ChannelId alone
        cid = ChannelId("UC_alone")
        assert runner._get_active_trace_id(cid, cnt) == "cresmo_UC_alone_vid_1001"

        # ChannelName alone
        cname = ChannelName("CNameAlone")
        assert runner._get_active_trace_id(cname, cnt) == "cresmo_CNameAlone_vid_1001"

        # None channel
        assert runner._get_active_trace_id(None, cnt) == "cresmo_cresmo_vid_1001"

        # String channel and ContentId content
        assert runner._get_active_trace_id("RawChannel", ContentId("cid_str")) == "cresmo_RawChannel_cid_str"

        # content_id and channel_id as kwargs
        assert runner._get_active_trace_id(channel=None, content=None, channel_id="UC_kw", content_id="cid_kw") == "cresmo_UC_kw_cid_kw"

        # channel_name as kwarg
        assert runner._get_active_trace_id(channel=None, content=None, channel_name="CName_kw", content_id="cid_kw2") == "cresmo_CName_kw_cid_kw2"

        # All none
        assert runner._get_active_trace_id() == "cresmo_cresmo_"


class TestStageRunnerExecuteStageRetriesAndQuarantine:
    """Verifies end-to-end execute_stage telemetry recording, retries, and quarantine metrics."""

    def test_execute_stage_retries_and_metrics(self) -> None:
        from cresmo.domain.entities import SourceTranscript

        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()

        # Two failed attempts followed by passing attempt
        eval_fail = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.45,
            criteria_scores=(),
            provider="gemini",
        )
        eval_pass = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.92,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.side_effect = [eval_fail, eval_pass]

        mock_llm = MagicMock()
        mock_llm.transform.side_effect = ["Draft 1 prose text", "Final polished prose text"]

        mock_pp = MagicMock()

        runner = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=2,
            judge_blocking=False,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="source text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=2,
            ),
        )

        source = SourceTranscript(
            content_id=ContentId("vid_retry_1"),
            channel_name=ChannelName("RetCh"),
            body="Source audio text words.",
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("ret_sess:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content.create(id=ContentId("vid_retry_1"), title="Retry Title"),
        )

        result = runner.execute_stage(stage_cfg, source, context=ctx)
        assert isinstance(result, CandidateText)
        assert result.text == "Final polished prose text"

        # Verify retry counter incremented
        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_retries_total", 1.0, labels={"stage": "fluid_prose"}
        )

        # Verify stage IO input and output payloads
        mock_t.record_stage_io.assert_any_call(
            input_payload={
                "stage_name": "fluid_prose",
                "source_type": "SourceTranscript",
                "source_characters": len("source text"),
                "source_words": len("source text".split()),
            }
        )
        mock_t.record_stage_io.assert_any_call(
            output_payload={
                "status": "APPROVED",
                "output_characters": len("Final polished prose text"),
                "output_words": len("Final polished prose text".split()),
                "attempts": 2,
            }
        )

    def test_execute_stage_completed_unblocking_status(self) -> None:
        from cresmo.domain.entities import SourceTranscript

        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()

        eval_fail = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.45,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_fail

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Unblocked imperfect text"

        runner = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=1,
            judge_blocking=False,
            prompt_provider=MagicMock(),
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="source text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=1,
            ),
        )

        source = SourceTranscript(
            content_id=ContentId("vid_unblock"),
            channel_name=ChannelName("UnblockCh"),
            body="Source text words.",
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("unblock_sess:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="UnblockCh"),
            content=Content.create(id=ContentId("vid_unblock"), title="Unblock Title"),
        )

        result = runner.execute_stage(stage_cfg, source, context=ctx)
        assert result.text == "Unblocked imperfect text"

        # Verify output payload status is COMPLETED_UNBLOCKING
        mock_t.record_stage_io.assert_any_call(
            output_payload={
                "status": "COMPLETED_UNBLOCKING",
                "output_characters": len("Unblocked imperfect text"),
                "output_words": len("Unblocked imperfect text".split()),
                "attempts": 1,
            }
        )

    def test_execute_stage_quarantine_recorded_when_blocking(self) -> None:
        from cresmo.domain.entities import SourceTranscript

        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()
        mock_ledger = MagicMock()

        eval_fail = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.30,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_fail

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Substandard prose"

        runner = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=1,
            judge_blocking=True,
            ledger_port=mock_ledger,
            prompt_provider=MagicMock(),
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[SourceTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            blocking=True,
            eval_spec=StageEvaluationSpec(
                raw_text="source text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=1,
            ),
        )

        source = SourceTranscript(
            content_id=ContentId("vid_quarantine"),
            channel_name=ChannelName("QuarantineCh"),
            body="Source text words.",
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("quarantine_sess:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="QuarantineCh", id=ChannelId("UC_quarantine")),
            content=Content.create(id=ContentId("vid_quarantine"), title="Quarantine Title"),
        )

        with pytest.raises(StageQuarantinedError) as exc_info:
            runner.execute_stage(stage_cfg, source, context=ctx)
        assert exc_info.value.stage_name == "fluid_prose"
        assert exc_info.value.content_id == "vid_quarantine"
        assert exc_info.value.attempts == 1

        # Verify quarantine recorded in ledger and metrics
        mock_ledger.save_entry.assert_called_once()
        mock_m.increment_counter.assert_any_call(
            "cresmo_stage_quarantines_total",
            1.0,
            labels={
                "stage": "fluid_prose",
                "channel_name": "QuarantineCh",
            },
        )


class TestStageRunnerCandidateGenerationAndEvaluation:
    """Verifies candidate generation parameters and evaluation span formatting."""

    def test_generate_candidate_exhaustive_parameters(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Generated text output"

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.stage_name = "fluid_prose"
        mock_stage_cfg.temperature = 0.7
        mock_stage_cfg.build_transform_prompt.return_value = "Formatted prompt"

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:123"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="TechChan", id=ChannelId("UC_tech")),
            content=Content.create(id=ContentId("c1234567"), title="Ep 1"),
        )

        candidate = runner._generate_candidate(
            stage_config=mock_stage_cfg,
            prompt_provider=MagicMock(),
            source=MagicMock(),
            context=ctx,
            llm_port=mock_llm,
            attempt=1,
            critique="Improve flow",
        )

        mock_stage_cfg.build_transform_prompt.assert_called_once_with(
            mock_stage_cfg.build_transform_prompt.call_args[0][0],
            mock_stage_cfg.build_transform_prompt.call_args[0][1],
            channel=ctx.channel,
            content=ctx.content,
            critique="Improve flow",
        )
        mock_llm.transform.assert_called_once_with(
            prompt="Formatted prompt",
            temperature=0.7,
            trace_id="cresmo_UC_tech_c1234567",
            session_id="sess:123",
            user_id="system:worker",
        )
        assert candidate.text == "Generated text output"
        assert candidate.stage_name == "fluid_prose"
        assert candidate.metadata == {
            "channel_id": "UC_tech",
            "content_id": "c1234567",
            "channel_name": "TechChan",
            "content_title": "Ep 1",
            "attempt": 1,
        }

    def test_generate_candidate_channel_without_id(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Text"
        mock_stage_cfg = MagicMock()
        mock_stage_cfg.stage_name = "fluid_prose"
        mock_stage_cfg.temperature = 0.5
        mock_stage_cfg.build_transform_prompt.return_value = "P"

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("sess:456"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NoIdChan", id=None),
            content=Content.create(id=ContentId("c7654321"), title="Ep 2"),
        )

        candidate = runner._generate_candidate(
            stage_config=mock_stage_cfg,
            prompt_provider=MagicMock(),
            source=MagicMock(),
            context=ctx,
            llm_port=mock_llm,
            attempt=2,
            critique=None,
        )
        assert candidate.metadata["channel_id"] == ""
        assert candidate.metadata["attempt"] == 2

    def test_evaluate_candidate_none_conditions(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner_no_judge = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=None)

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.eval_spec = None
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("s:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch"),
            content=Content.create(id=ContentId("c1234567"), title="T"),
        )
        cand = CandidateText(text="hello", stage_name="s", metadata={})
        assert runner_no_judge._evaluate_candidate(mock_stage_cfg, MagicMock(), cand, context=ctx, attempt=1) is None

        # Judge present but eval_spec None
        runner_with_judge = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=MagicMock())
        assert runner_with_judge._evaluate_candidate(mock_stage_cfg, MagicMock(), cand, context=ctx, attempt=1) is None

    def test_evaluate_candidate_recording_span_and_criteria_scores(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()

        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=mock_judge)

        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_ctx = MagicMock()
        mock_ctx.is_valid = True
        mock_ctx.span_id = 0x1234ABCD
        mock_ctx.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        mock_span.get_span_context.return_value = mock_ctx

        score1 = CriterionScore(
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            score=0.9,
            passed=True,
            reasoning="No filler words",
            improvement_suggestion="Keep it up",
        )
        score2 = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.85,
            passed=True,
            reasoning="Facts intact",
            improvement_suggestion="",
        )
        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.88,
            criteria_scores=(score1, score2),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_result

        stage_cfg = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="raw text",
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                metadata={"custom_eval_key": "val1"},
            ),
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("s:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=ChannelId("UC_1")),
            content=Content.create(id=ContentId("c1234567"), title="Ep 1"),
        )
        cand = CandidateText(text="cleaned prose", stage_name="fluid_prose", metadata={})

        with patch("cresmo.application.pipeline.stage_runner.trace.get_current_span", return_value=mock_span):
            res = runner._evaluate_candidate(stage_cfg, MagicMock(), cand, context=ctx, attempt=1)

        assert res is eval_result
        mock_span.set_attribute.assert_any_call("judge.verdict", "PASS")
        mock_span.set_attribute.assert_any_call("judge.overall_score", 0.88)

        # Check serialized output in span
        output_calls = [c for c in mock_span.set_attribute.call_args_list if c[0][0] == "output.value"]
        assert len(output_calls) == 1
        output_dict = json.loads(output_calls[0][0][1])
        assert output_dict["verdict"] == "PASS"
        assert output_dict["overall_score"] == 0.88
        assert output_dict["scores"]["orality_removal"] == 0.9
        assert output_dict["reasons"]["orality_removal"] == "No filler words"
        assert output_dict["suggestions"]["orality_removal"] == "Keep it up"

    def test_evaluate_candidate_failing_verdict_needs_rewrite(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()

        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=mock_judge)

        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_span.get_span_context.return_value = MagicMock(is_valid=False, trace_id=0)

        eval_result = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.40,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_result

        stage_cfg = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="raw",
                candidate_extractor=lambda res: res.text,
            ),
        )
        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("s:2"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=None),
            content=Content.create(id=ContentId("c1234567"), title="Ep 2"),
        )
        cand = CandidateText(text="imperfect", stage_name="fluid_prose", metadata={})

        with patch("cresmo.application.pipeline.stage_runner.trace.get_current_span", return_value=mock_span):
            res = runner._evaluate_candidate(stage_cfg, MagicMock(), cand, context=ctx, attempt=2)

        assert res is eval_result
        mock_span.set_attribute.assert_any_call("judge.verdict", "NEEDS_REWRITE")
        mock_span.set_attribute.assert_any_call("judge.overall_score", 0.40)


class TestStageRunnerStageExecutionAndFallback:
    """Verifies run_stage and run_evaluated_stage delegation, exceptions, and fallback semantics."""

    def test_run_stage_default_parameters_and_unknown_fallbacks(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        # Both channel and content None
        res = runner.run_stage("test_stage", lambda: "ret_val")
        assert res == "ret_val"

        # channel_name provided as string, content_id provided as string
        res2 = runner.run_stage(
            "test_stage",
            lambda: "ret_val_2",
            channel_name="CustomChan",
            content_id="c1234567",
            content_title="My Title",
        )
        assert res2 == "ret_val_2"

    def test_run_stage_non_fatal_exception_returns_fallback(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        def failing_fn() -> None:
            raise RuntimeError("Temporary glitch")

        # Callable fallback
        res = runner.run_stage(
            "test_stage",
            failing_fn,
            fatal=False,
            fallback=lambda: "recovered",
            content_id="c1234567",
        )
        assert res == "recovered"

        # Static fallback
        res2 = runner.run_stage(
            "test_stage",
            failing_fn,
            fatal=False,
            fallback="static_rec",
            content_id="c1234567",
        )
        assert res2 == "static_rec"

    def test_run_stage_fatal_exception_records_metrics_and_raises(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        mock_span = MagicMock()
        mock_span.is_recording.return_value = True

        def fatal_fn() -> None:
            raise KeyError("Missing resource")

        ch = Channel(name="FailCh", id=ChannelId("UC_fail"))
        cnt = Content(id=ContentId("c1234567"), title="Fail Title")

        with patch("cresmo.application.pipeline.stage_runner.trace.get_current_span", return_value=mock_span):
            with pytest.raises(KeyError, match="Missing resource"):
                runner.run_stage("fatal_stage", fatal_fn, channel=ch, content=cnt, fatal=True)

        mock_span.record_exception.assert_called_once()
        mock_span.set_attribute.assert_called_with("langfuse.observation.level", "ERROR")
        mock_m.increment_counter.assert_called_with(
            "cresmo_pipeline_errors_total",
            1.0,
            labels={
                "error_type": "KeyError",
                "channel_id": "UC_fail",
                "content_id": "c1234567",
                "channel_name": "FailCh",
                "stage": "fatal_stage",
            },
        )
        mock_m.observe_histogram.assert_called_with(
            "cresmo_pipeline_stage_duration_seconds",
            mock_m.observe_histogram.call_args[0][1],
            labels={
                "stage": "fatal_stage",
                "channel_id": "UC_fail",
                "channel_name": "FailCh",
                "status": "failure",
            },
        )

    def test_run_evaluated_stage_delegation_without_judge_or_eval_spec(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=None)

        res = runner.run_evaluated_stage(
            "delegated_stage",
            lambda: "delegated_val",
            channel_name="DChan",
            content_id="c1234567",
            channel_id="UC_d",
            content_title="DTitle",
            fatal=False,
            fallback="fb",
        )
        assert res == "delegated_val"

    def test_run_evaluated_stage_candidate_none_returns_fallback(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m, llm_judge=mock_judge)

        spec = StageEvaluationSpec(
            raw_text="raw",
            candidate_extractor=lambda res: res,
        )

        # When run_stage returns None (e.g. failing_fn with fatal=False)
        res = runner.run_evaluated_stage(
            "empty_stage",
            lambda: None,
            channel_name="EChan",
            content_id="c1234567",
            eval_spec=spec,
            fallback=lambda: "empty_fallback",
        )
        assert res == "empty_fallback"

    def test_run_evaluated_stage_retries_and_blocking_threshold(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_judge = MagicMock()

        eval_fail = JudgeEvaluation(
            target_stage="eval_stage",
            passed=False,
            overall_score=0.40,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_fail

        runner_blocking = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_blocking=True,
            judge_max_attempts=2,
        )

        cand_mock = MagicMock()
        cand_mock.title = "MockCandTitle"

        spec = StageEvaluationSpec(
            raw_text="raw text",
            candidate_extractor=lambda res: "extracted",
            max_attempts=2,
        )

        with pytest.raises(
            DomainValidationError,
            match=r"eval_stage quality evaluation failed threshold after 2 attempts: 0\.40",
        ):
            runner_blocking.run_evaluated_stage(
                "eval_stage",
                lambda: cand_mock,
                channel_name="EvalCh",
                content_id="c1234567",
                channel_id="UC_eval",
                eval_spec=spec,
            )

        # Check retries counter incremented on attempt 1
        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_retries_total", 1.0, labels={"stage": "eval_stage"}
        )
        # Check evaluation counter incremented for both attempts
        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "eval_stage", "passed": "false", "attempt": "1"},
        )
        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "eval_stage", "passed": "false", "attempt": "2"},
        )

    def test_execute_stage_source_and_output_text_extractions(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock()
        mock_pp = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Prose text"

        runner = PipelineStageRunner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        ctx = PipelineExecutionContext(
            session_id=PipelineSessionId("s:1"),
            user_identity=UserIdentity.worker(),
            channel=Channel(name="ExChan", id=ChannelId("UC_ex")),
            content=Content.create(id=ContentId("c1234567"), title="Ex Title"),
        )

        # Case 1: source has .body string, eval_spec is None
        class SourceWithBody:
            body = "Source body text here"

        cfg1 = StageConfig[SourceWithBody, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        res1 = runner.execute_stage(cfg1, SourceWithBody(), context=ctx)
        assert res1.text == "Prose text"
        mock_t.record_stage_io.assert_any_call(
            input_payload={
                "stage_name": "fluid_prose",
                "source_type": "SourceWithBody",
                "source_characters": len("Source body text here"),
                "source_words": len("Source body text here".split()),
            }
        )

        # Case 2: source has .text string
        class SourceWithText:
            text = "Source text only"

        mock_t.reset_mock()
        cfg2 = StageConfig[SourceWithText, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg2, SourceWithText(), context=ctx)
        mock_t.record_stage_io.assert_any_call(
            input_payload={
                "stage_name": "fluid_prose",
                "source_type": "SourceWithText",
                "source_characters": len("Source text only"),
                "source_words": len("Source text only".split()),
            }
        )

        # Case 3: source has .content that is Content
        class SourceWithContent:
            content = Content(id=ContentId("c1234567"), body="Content body text")

        mock_t.reset_mock()
        cfg3 = StageConfig[SourceWithContent, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg3, SourceWithContent(), context=ctx)
        mock_t.record_stage_io.assert_any_call(
            input_payload={
                "stage_name": "fluid_prose",
                "source_type": "SourceWithContent",
                "source_characters": len("Content body text"),
                "source_words": len("Content body text".split()),
            }
        )

        # Case 4: source with neither, falls back to str(source)
        class SourceBare:
            def __str__(self) -> str:
                return "Bare source string representation"

        mock_t.reset_mock()
        cfg4 = StageConfig[SourceBare, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg4, SourceBare(), context=ctx)
        mock_t.record_stage_io.assert_any_call(
            input_payload={
                "stage_name": "fluid_prose",
                "source_type": "SourceBare",
                "source_characters": len("Bare source string representation"),
                "source_words": len("Bare source string representation".split()),
            }
        )


