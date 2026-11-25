"""Hermetic Unit Tests for PipelineStageRunner and Stage Quality Gate Fabric.

Conforms to:
    - ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
    - SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    TelemetryPort,
)
from cresmo.domain.entities import StageTranscript, UserIdentity
from cresmo.domain.exceptions import DomainValidationError, StageQuarantinedError
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    ChannelId,
    Content,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    MediaProvenance,
    PromptKey,
    StageEvaluationSpec,
)
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


def _make_runner(**kwargs: object) -> PipelineStageRunner:
    kwargs.setdefault("prompt_provider", NoOpPromptProviderPort())
    kwargs.setdefault("llm_transformation_port", MagicMock(spec=LLMTransformationPort))
    return PipelineStageRunner(PipelineDependencies(**kwargs))  # type: ignore[arg-type]


class TestStageEvaluationSpec:
    """Test suite for StageEvaluationSpec value object validation."""

    def test_valid_spec_creation(self) -> None:
        spec = StageEvaluationSpec(
            candidate_extractor=lambda res: res["text"],
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            max_attempts=3,
        )
        assert spec.max_attempts == 3
        assert spec.candidate_extractor({"text": "Hello"}) == "Hello"

    def test_invalid_max_attempts_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            StageEvaluationSpec(
                candidate_extractor=lambda res: str(res),
                required_criteria=(),
                max_attempts=0,
            )


class TestPipelineStageRunnerEvaluatedStage:
    """Test suite for PipelineStageRunner.execute_stage closed-loop quality gate."""

    def test_execute_stage_with_pipeline_execution_context(self) -> None:
        """Verify execute_stage cleanly consumes PipelineExecutionContext."""
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.application.pipeline.stage_descriptor import StageConfig
        from cresmo.domain.entities import StageTranscript, UserIdentity
        from cresmo.domain.value_objects import CandidateText, PromptKey
        from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
        from tests.doubles.mock_adapters import MockLLMAdapter

        telemetry = NoOpTelemetryPort()
        metrics = NoOpMetricsPort()
        prompt_provider = JsonPromptProvider()
        llm_port = MockLLMAdapter(responses=["# Synthesized Title\n\nClean body text."])

        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=metrics,
            prompt_provider=prompt_provider,
            llm_transformation_port=llm_port,
        )

        channel = Channel(name="CtxChannel")
        content = Content(
            id=ContentId("vid_ctx_1"), title="CtxTitle", session_id="ch_test:vid_ctx_1"
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=channel,
            content=content,
        )

        descriptor = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
        )

        source = StageTranscript(
            channel=Channel(name="CtxChannel"),
            provenance=MediaProvenance(),
            content=Content(id=ContentId("vid_ctx_1"), title="CtxTitle", text="Raw speech text."),
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
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=MagicMock(spec=LLMTransformationPort),
            judge_blocking=False,
            judge_max_attempts=2,
        )
        runner = PipelineStageRunner(deps)
        assert runner.telemetry_port is telemetry
        assert runner.metrics_port is metrics
        assert runner.judge_max_attempts == 2

    def test_evaluate_candidate_binds_active_observation_id_adr036(self) -> None:
        """Verify evaluate_stage_candidate populates EvaluationContext.observation_id from active TelemetrySpan."""
        from cresmo.application.pipeline.stage_execution import evaluate_stage_candidate

        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_eval.overall_score = 0.9
        mock_judge.evaluate.return_value = mock_eval

        telemetry = InMemoryTelemetryPort(trace_id="1234567890abcdef1234567890abcdef")

        stage_config = StageConfig(
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            ),
        )

        context = PipelineExecutionContext(
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid"), session_id="test_chan:test_vid"),
        )

        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        with telemetry.start_span("cresmo.fluid_prose"):
            result = evaluate_stage_candidate(
                stage_config,
                source="source text",
                candidate=candidate,
                context=context,
                attempt=1,
                llm_judge=mock_judge,
                telemetry_port=telemetry,
                metrics_port=NoOpMetricsPort(),
            )

        assert result is mock_eval
        mock_judge.evaluate.assert_called_once()
        passed_eval_context = mock_judge.evaluate.call_args[0][0]
        assert passed_eval_context.stage_name == "fluid_prose"
        assert passed_eval_context.trace_id == "1234567890abcdef1234567890abcdef"
        assert passed_eval_context.observation_id == telemetry.spans[1].span_id

    def test_evaluate_candidate_opens_chronological_evaluation_span(self) -> None:
        """Verify evaluate_stage_candidate opens cresmo.{stage}.judge span on TelemetryPort (ADR-037, ADR-070)."""
        from cresmo.application.pipeline.stage_execution import evaluate_stage_candidate

        telemetry = InMemoryTelemetryPort()
        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_eval.overall_score = 0.95
        mock_judge.evaluate.return_value = mock_eval

        stage_config = StageConfig(
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
            ),
        )

        context = PipelineExecutionContext(
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid"), session_id="test_chan:test_vid"),
        )
        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        evaluate_stage_candidate(
            stage_config,
            source="source text",
            candidate=candidate,
            context=context,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=telemetry,
            metrics_port=NoOpMetricsPort(),
        )

        assert len(telemetry.spans) == 1
        eval_span = telemetry.spans[0]
        assert eval_span.name == "cresmo.fluid_prose.judge"
        assert eval_span.attributes["judge.stage_name"] == "fluid_prose"
        assert eval_span.attributes["judge.attempt"] == 1
        assert eval_span.attributes["judge.verdict"] == "PASS"
        assert eval_span.attributes["judge.overall_score"] == 0.95


class TestStageRunnerHelperAndInit:
    """Verifies initialization validation, defaults, and warmup."""

    def test_init_requires_both_ports(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        mock_pp = NoOpPromptProviderPort()
        mock_llm = MagicMock(spec=LLMTransformationPort)

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=None,  # type: ignore[arg-type]
                    metrics_port=mock_m,
                    prompt_provider=mock_pp,
                    llm_transformation_port=mock_llm,
                )
            )

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=mock_t,
                    metrics_port=None,  # type: ignore[arg-type]
                    prompt_provider=mock_pp,
                    llm_transformation_port=mock_llm,
                )
            )

        with pytest.raises(ValueError, match=r"^prompt_provider must be provided\.$"):
            PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=mock_t,
                    metrics_port=mock_m,
                    prompt_provider=None,
                    llm_transformation_port=mock_llm,
                )
            )

        with pytest.raises(ValueError, match=r"^llm_transformation_port must be provided\.$"):
            PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=mock_t,
                    metrics_port=mock_m,
                    prompt_provider=mock_pp,
                    llm_transformation_port=None,
                )
            )

    def test_init_defaults(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)

        runner = _make_runner(telemetry_port=mock_t, metrics_port=mock_m)
        assert runner.judge_blocking is False
        assert runner.judge_max_attempts == 2
        assert isinstance(runner.prompt_provider, NoOpPromptProviderPort)
        assert runner.llm_transformation_port is not None
        assert runner.stage_factory is None
        assert runner.critique_synthesizer is None
        assert runner.ledger_port is None

        # Custom judge_max_attempts passed directly to constructor
        runner_custom = _make_runner(
            telemetry_port=mock_t, metrics_port=mock_m, judge_max_attempts=4
        )
        assert runner_custom.judge_max_attempts == 4

    def test_warmup_with_and_without_critique_synthesizer(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        mock_llm = MagicMock()
        mock_synth = MagicMock()

        runner = _make_runner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_transformation_port=mock_llm,
            critique_synthesizer=mock_synth,
        )
        runner.warmup()
        mock_llm.warmup.assert_called_once_with()
        mock_synth.warmup.assert_called_once_with()

        mock_llm_only = MagicMock()
        runner_no_synth = _make_runner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_transformation_port=mock_llm_only,
        )
        runner_no_synth.warmup()
        mock_llm_only.warmup.assert_called_once_with()


class TestStageRunnerResolution:
    """Verifies dependency resolution and critique synthesis."""

    def test_resolve_stage_config(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = _make_runner(telemetry_port=mock_t, metrics_port=mock_m)

        with pytest.raises(
            ValueError,
            match="Cannot resolve stage 'custom' from string without an injected StageFactory.",
        ):
            runner._resolve_stage_config("custom")

        mock_factory = MagicMock()
        mock_cfg = MagicMock(spec=StageConfig)
        mock_factory.build_stage.return_value = mock_cfg

        runner_with_factory = _make_runner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            stage_factory=mock_factory,
        )
        assert runner_with_factory._resolve_stage_config("fluid_prose") is mock_cfg
        mock_factory.build_stage.assert_called_once_with("fluid_prose", max_passes=None)
        assert runner_with_factory._resolve_stage_config(mock_cfg) is mock_cfg

    def test_synthesize_critique(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        mock_synth = MagicMock()
        mock_synth.synthesize.return_value = "Synthesized critique"

        runner_synth = _make_runner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            critique_synthesizer=mock_synth,
        )
        eval_mock = MagicMock(spec=JudgeEvaluation)
        assert runner_synth._synthesize_critique(eval_mock, "fluid_prose") == "Synthesized critique"
        mock_synth.synthesize.assert_called_once_with(eval_mock, "fluid_prose")

        runner_default = _make_runner(telemetry_port=mock_t, metrics_port=mock_m)
        eval_mock.extract_critique.return_value = "Extracted critique"
        assert runner_default._synthesize_critique(eval_mock, "fluid_prose") == "Extracted critique"
        eval_mock.extract_critique.assert_called_once()


class TestStageRunnerMetricsAndTelemetry:
    """Verifies metrics recording and active trace ID derivation."""

    def test_record_evaluation_metrics_exact_parameters(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import record_evaluation_metric

        mock_m = MagicMock()
        record_evaluation_metric(mock_m, stage_name="fluid_prose", passed=True, attempt=1)
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "fluid_prose", "passed": "true", "attempt": "1"},
        )

        mock_m.reset_mock()
        record_evaluation_metric(mock_m, stage_name="gap_filler", passed=False, attempt=2)
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "gap_filler", "passed": "false", "attempt": "2"},
        )


class TestStageRunnerActiveTraceId:
    """Verifies deterministic trace ID derivation across context combinations."""

    def test_trace_id_with_recording_span(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import resolve_active_trace_id

        expected_tid = format(0x1234567890ABCDEF1234567890ABCDEF, "032x")
        telemetry = InMemoryTelemetryPort(trace_id=expected_tid)
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NameA", id=ChannelId("UC_id_a")),
            content=Content(id=ContentId("vid_1001")),
        )

        with telemetry.start_span("cresmo.fluid_prose"):
            assert resolve_active_trace_id(ctx, telemetry_port=telemetry) == expected_tid

    def test_trace_id_without_span(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import resolve_active_trace_id

        telemetry = NoOpTelemetryPort()

        # Channel with id
        ctx_with_id = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NameA", id=ChannelId("UC_id_a")),
            content=Content(id=ContentId("vid_1001")),
        )
        assert (
            resolve_active_trace_id(ctx_with_id, telemetry_port=telemetry)
            == "cresmo_UC_id_a_vid_1001"
        )

        # Channel without id
        ctx_no_id = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NameA", id=None),
            content=Content(id=ContentId("vid_1001")),
        )
        assert (
            resolve_active_trace_id(ctx_no_id, telemetry_port=telemetry) == "cresmo_NameA_vid_1001"
        )

    def test_trace_id_precedence_and_attach_evaluation_null_guards(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import (
            attach_evaluation_span_attributes,
            resolve_active_trace_id,
        )
        from cresmo.application.ports.telemetry import SpanKind
        from tests.doubles.telemetry_fake import RecordedSpan

        explicit_span = RecordedSpan(
            name="cresmo.fluid_prose.judge",
            kind=SpanKind.SPAN,
            trace_id_value="f" * 32,
            span_id_value="1" * 16,
        )
        other_telemetry = InMemoryTelemetryPort(trace_id="0" * 32)
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="HumanChan", id=ChannelId("UC_1")),
            content=Content(id=ContentId("vid_from_obj")),
        )
        with other_telemetry.start_span("cresmo.fluid_prose"):
            assert (
                resolve_active_trace_id(ctx, telemetry_port=other_telemetry, span=explicit_span)
                == "f" * 32
            )

        assert resolve_active_trace_id(ctx) == "cresmo_UC_1_vid_from_obj"

        eval_obj = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(),
            provider="test",
        )
        attach_evaluation_span_attributes(None, eval_obj)
        attach_evaluation_span_attributes(explicit_span, None)
        assert explicit_span.attributes == {}
        assert explicit_span.outputs == []


class TestStageRunnerExecuteStageRetriesAndQuarantine:
    """Verifies end-to-end execute_stage telemetry recording, retries, and quarantine metrics."""

    def test_execute_stage_retries_and_metrics(self) -> None:
        from cresmo.domain.entities import StageTranscript

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_judge = MagicMock()

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

        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=2,
            judge_blocking=False,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=2,
            ),
        )

        source = StageTranscript(
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            provenance=MediaProvenance(),
            content=Content(
                id=ContentId("vid_retry_1"), title="Retry Title", text="Source audio text words."
            ),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content(
                id=ContentId("vid_retry_1"), title="Retry Title", session_id="ret_sess:1"
            ),
        )

        result = runner.execute_stage(stage_cfg, source, context=ctx)
        assert isinstance(result, CandidateText)
        assert result.text == "Final polished prose text"

        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_retry_count_total", 1.0, labels={"stage": "fluid_prose"}
        )

        stage_span = next(s for s in telemetry.spans if s.name == "cresmo.fluid_prose")
        assert stage_span.inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "StageTranscript",
                "source_characters": len("Source audio text words."),
                "source_words": 4,
            }
        ]
        assert stage_span.outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Final polished prose text"),
                "output_words": len(["Final", "polished", "prose", "text"]),
                "attempts": 2,
                "retries": 1,
                "expansion_ratio": round(4 / 4, 3),
                "judge_passed": True,
                "judge_overall_score": 0.92,
            }
        ]
        # Single deterministic flush after stage span closes (no mid-loop flushes)
        assert telemetry.flush_count == 1

    def test_execute_stage_completed_unblocking_status(self) -> None:
        from cresmo.domain.entities import StageTranscript

        telemetry = InMemoryTelemetryPort()
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

        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=1,
            judge_blocking=False,
            prompt_provider=MagicMock(),
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=1,
            ),
        )

        source = StageTranscript(
            channel=Channel(name="UnblockCh"),
            provenance=MediaProvenance(),
            content=Content(
                id=ContentId("vid_unblock"), title="Unblock Title", text="Source text words."
            ),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="UnblockCh"),
            content=Content(
                id=ContentId("vid_unblock"), title="Unblock Title", session_id="unblock_sess:1"
            ),
        )

        result = runner.execute_stage(stage_cfg, source, context=ctx)
        assert result.text == "Unblocked imperfect text"

        stage_span = next(s for s in telemetry.spans if s.name == "cresmo.fluid_prose")
        assert stage_span.outputs == [
            {
                "status": "COMPLETED_UNBLOCKING",
                "output_characters": len("Unblocked imperfect text"),
                "output_words": len(["Unblocked", "imperfect", "text"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": round(3 / 3, 3),
                "judge_passed": False,
                "judge_overall_score": 0.45,
            }
        ]

    def test_execute_stage_quarantine_recorded_when_blocking(self) -> None:
        from cresmo.domain.entities import StageTranscript

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

        runner = _make_runner(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_max_attempts=1,
            judge_blocking=True,
            ledger_port=mock_ledger,
            prompt_provider=MagicMock(),
            llm_transformation_port=mock_llm,
        )

        stage_cfg = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            blocking=True,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                max_attempts=1,
            ),
        )

        source = StageTranscript(
            channel=Channel(name="QuarantineCh", id=ChannelId("UC_quarantine")),
            provenance=MediaProvenance(),
            content=Content(
                id=ContentId("vid_quarantine"), title="Quarantine Title", text="Source text words."
            ),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="QuarantineCh", id=ChannelId("UC_quarantine")),
            content=Content(
                id=ContentId("vid_quarantine"),
                title="Quarantine Title",
                session_id="quarantine_sess:1",
            ),
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
                "channel_id": "UC_quarantine",
            },
        )


class TestStageRunnerCandidateGenerationAndEvaluation:
    """Verifies candidate generation parameters and evaluation span formatting."""

    def test_generate_candidate_exhaustive_parameters(self) -> None:
        from cresmo.application.pipeline.stage_execution import generate_stage_candidate
        from cresmo.application.pipeline.stage_telemetry import resolve_active_trace_id

        telemetry = NoOpTelemetryPort()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Generated text output"

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.stage_name = "fluid_prose"
        mock_stage_cfg.max_passes = 1
        mock_stage_cfg.build_transform_prompt.return_value = "Formatted prompt"

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="TechChan", id=ChannelId("UC_tech")),
            content=Content(id=ContentId("c1234567"), title="Ep 1", session_id="sess:123"),
        )

        candidate = generate_stage_candidate(
            stage_config=mock_stage_cfg,
            source="raw source",
            context=ctx,
            prompt_provider=MagicMock(),
            llm_port=mock_llm,
            attempt=1,
            active_trace_id=resolve_active_trace_id(ctx, telemetry_port=telemetry),
            critique="Improve flow",
            telemetry_port=telemetry,
        )

        mock_stage_cfg.build_transform_prompt.assert_called_once_with(
            mock_stage_cfg.build_transform_prompt.call_args[0][0],
            mock_stage_cfg.build_transform_prompt.call_args[0][1],
            context=ctx,
            critique="Improve flow",
        )
        mock_llm.transform.assert_called_once_with(
            prompt="Formatted prompt",
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
        from cresmo.application.pipeline.stage_execution import generate_stage_candidate

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Text"
        mock_stage_cfg = MagicMock()
        mock_stage_cfg.stage_name = "fluid_prose"
        mock_stage_cfg.max_passes = 1
        mock_stage_cfg.build_transform_prompt.return_value = "P"

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NoIdChan", id=None),
            content=Content(id=ContentId("c7654321"), title="Ep 2", session_id="sess:456"),
        )

        mock_pp = MagicMock()
        mock_src = "src"
        candidate = generate_stage_candidate(
            stage_config=mock_stage_cfg,
            source=mock_src,
            context=ctx,
            prompt_provider=mock_pp,
            llm_port=mock_llm,
            attempt=2,
            active_trace_id="cresmo_NoIdChan_c7654321",
            critique=None,
        )
        assert candidate.metadata["channel_id"] == ""
        assert candidate.metadata["attempt"] == 2
        mock_stage_cfg.build_transform_prompt.assert_called_once_with(
            mock_pp,
            mock_src,
            context=ctx,
            critique=None,
        )

    def test_evaluate_candidate_none_conditions(self) -> None:
        from cresmo.application.pipeline.stage_execution import evaluate_stage_candidate

        mock_t = NoOpTelemetryPort()
        mock_m = MagicMock(spec=NoOpMetricsPort)

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.eval_spec = None
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch"),
            content=Content(id=ContentId("c1234567"), title="T", session_id="s:1"),
        )
        cand = CandidateText(text="hello", stage_name="s", metadata={})
        assert (
            evaluate_stage_candidate(
                mock_stage_cfg,
                "raw",
                cand,
                context=ctx,
                attempt=1,
                llm_judge=None,
                telemetry_port=mock_t,
                metrics_port=mock_m,
            )
            is None
        )

        # Judge present but eval_spec None
        assert (
            evaluate_stage_candidate(
                mock_stage_cfg,
                "raw",
                cand,
                context=ctx,
                attempt=1,
                llm_judge=MagicMock(),
                telemetry_port=mock_t,
                metrics_port=mock_m,
            )
            is None
        )

    def test_evaluate_candidate_recording_span_and_criteria_scores(self) -> None:
        from cresmo.application.pipeline.stage_execution import evaluate_stage_candidate

        telemetry = InMemoryTelemetryPort(trace_id="1234567890abcdef1234567890abcdef")
        mock_m = MagicMock()
        mock_judge = MagicMock()

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

        stage_cfg = StageConfig[str, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
                metadata={"custom_eval_key": "val1"},
            ),
        )

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=ChannelId("UC_1")),
            content=Content(id=ContentId("c1234567"), title="Ep 1", session_id="s:1"),
        )
        cand = CandidateText(text="cleaned prose", stage_name="fluid_prose", metadata={})

        res = evaluate_stage_candidate(
            stage_cfg,
            "raw text",
            cand,
            context=ctx,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        assert res is eval_result
        eval_span = telemetry.spans[0]
        assert eval_span.attributes["judge.verdict"] == "PASS"
        assert eval_span.attributes["judge.overall_score"] == 0.88

        mock_judge.evaluate.assert_called_once()
        eval_ctx = mock_judge.evaluate.call_args[0][0]
        assert eval_ctx.stage_name == "fluid_prose"
        assert eval_ctx.raw_text == "raw text"
        assert eval_ctx.candidate_text == "cleaned prose"
        assert eval_ctx.required_criteria == (JudgeCriterion.ORALITY_REMOVAL,)
        assert eval_ctx.metadata == {
            "channel_id": "UC_1",
            "content_id": "c1234567",
            "channel_name": "Ch",
            "content_title": "Ep 1",
            "attempt": 1,
            "custom_eval_key": "val1",
        }
        assert eval_ctx.trace_id == "1234567890abcdef1234567890abcdef"
        assert eval_ctx.observation_id == eval_span.span_id

        assert len(eval_span.outputs) == 1
        output_dict = eval_span.outputs[0]
        assert output_dict["verdict"] == "PASS"
        assert output_dict["overall_score"] == 0.88
        assert output_dict["scores"]["orality_removal"] == 0.9
        assert output_dict["reasons"]["orality_removal"] == "No filler words"
        assert output_dict["suggestions"]["orality_removal"] == "Keep it up"

    def test_evaluate_candidate_failing_verdict_needs_rewrite(self) -> None:
        from cresmo.application.pipeline.stage_execution import evaluate_stage_candidate

        telemetry = InMemoryTelemetryPort(trace_id="")
        mock_m = MagicMock()
        mock_judge = MagicMock()

        crit_plain = MagicMock()
        crit_plain.criterion = JudgeCriterion.ORALITY_REMOVAL
        crit_plain.score = "0.40"
        crit_plain.reasoning = ""
        crit_plain.improvement_suggestion = ""

        eval_result = MagicMock()
        eval_result.target_stage = "fluid_prose"
        eval_result.passed = False
        eval_result.overall_score = "0.40"
        eval_result.criteria_scores = (crit_plain,)
        eval_result.provider = "gemini"
        mock_judge.evaluate.return_value = eval_result

        stage_cfg = StageConfig[str, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
            ),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=None),
            content=Content(id=ContentId("c1234567"), title="Ep 2", session_id="s:2"),
        )
        cand = CandidateText(text="imperfect", stage_name="fluid_prose", metadata={})

        res = evaluate_stage_candidate(
            stage_cfg,
            "raw",
            cand,
            context=ctx,
            attempt=2,
            llm_judge=mock_judge,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        assert res is eval_result
        eval_span = telemetry.spans[0]
        assert eval_span.attributes["judge.verdict"] == "NEEDS_REWRITE"

        eval_ctx = mock_judge.evaluate.call_args[0][0]
        assert eval_ctx.trace_id == "cresmo_Ch_c1234567"
        assert eval_ctx.metadata["channel_id"] == ""
        assert eval_ctx.metadata["attempt"] == 2
        mock_m.increment_counter.assert_called_with(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": "fluid_prose", "passed": "false", "attempt": "2"},
        )

        output_dict = eval_span.outputs[0]
        assert output_dict["verdict"] == "NEEDS_REWRITE"
        assert output_dict["overall_score"] == 0.4
        assert output_dict["scores"]["orality_removal"] == 0.4
        assert "reasons" not in output_dict
        assert "suggestions" not in output_dict

        class BareScore:
            criterion = JudgeCriterion.ORALITY_REMOVAL
            score = 0.7
            reasoning = ""
            improvement_suggestion = ""

        class BareEval:
            target_stage = "fluid_prose"
            passed = True
            overall_score = 0.7
            criteria_scores = (BareScore(),)

        mock_judge.evaluate.return_value = BareEval()
        evaluate_stage_candidate(
            stage_cfg,
            "raw",
            cand,
            context=ctx,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        class NoCriteriaEval:
            target_stage = "fluid_prose"
            passed = True
            overall_score = 0.8
            criteria_scores: tuple[CriterionScore, ...] = ()

        mock_judge.evaluate.return_value = NoCriteriaEval()
        evaluate_stage_candidate(
            stage_cfg,
            "raw",
            cand,
            context=ctx,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        # NoOpTelemetryPort yields NOOP_TELEMETRY_SPAN (span_id is None, trace_id fallback)
        mock_judge.evaluate.return_value = eval_result
        assert (
            evaluate_stage_candidate(
                stage_cfg,
                "raw",
                cand,
                context=ctx,
                attempt=2,
                llm_judge=mock_judge,
                telemetry_port=NoOpTelemetryPort(),
                metrics_port=mock_m,
            )
            is eval_result
        )
        assert mock_judge.evaluate.call_args[0][0].observation_id is None


class TestStageRunnerStageExecutionAndFallback:
    """Verifies execute_stage delegation, telemetry extraction, and fallback semantics."""

    def test_execute_stage_source_and_output_text_extractions(self) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_pp = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Prose text"

        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="ExChan", id=ChannelId("UC_ex")),
            content=Content(id=ContentId("c1234567"), title="Ex Title", session_id="s:1"),
        )

        # Case 1: source is StageTranscript
        src_stage = StageTranscript(
            channel=Channel(name="ExChan", id=ChannelId("UC_ex")),
            provenance=MediaProvenance(),
            content=Content(
                id=ContentId("c1234567"), title="Ex Title", text="Source body text here"
            ),
        )
        cfg1 = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        res1 = runner.execute_stage(cfg1, src_stage, context=ctx)
        assert res1.text == "Prose text"
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "StageTranscript",
                "source_characters": len("Source body text here"),
                "source_words": len(["Source", "body", "text", "here"]),
            }
        ]

        # Case 2: source is CandidateText
        src_cand = CandidateText(stage_name="fluid_prose", text="Candidate source only")

        cfg2 = StageConfig[CandidateText, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg2, src_cand, context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "CandidateText",
                "source_characters": len("Candidate source only"),
                "source_words": len(["Candidate", "source", "only"]),
            }
        ]

        # Case 3: source is str
        cfg3 = StageConfig[str, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg3, "Plain string source", context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "str",
                "source_characters": len("Plain string source"),
                "source_words": len(["Plain", "string", "source"]),
            }
        ]

        # Case 4: arbitrary source falls back to str(source)
        class SourceBare:
            def __str__(self) -> str:
                return "Bare source string representation"

        cfg4 = StageConfig[SourceBare, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg4, SourceBare(), context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "SourceBare",
                "source_characters": len("Bare source string representation"),
                "source_words": len(["Bare", "source", "string", "representation"]),
            }
        ]

    def test_execute_stage_extended_branches_and_outputs(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_pp = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Candidate output text"
        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Chan", id=ChannelId("UC_1")),
            content=Content(id=ContentId("c1234567"), title="Title", session_id="s:1"),
        )

        cfg = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        res = runner.execute_stage(
            cfg,
            MagicMock(),
            context=ctx,
        )
        assert res.text == "Candidate output text"

        runner_j1 = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            judge_max_attempts=1,
        )
        cfg_max3 = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=3,
            eval_spec=None,
        )
        runner_j1.execute_stage(cfg_max3, MagicMock(), context=ctx)

        mock_judge = MagicMock()
        eval_fail = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.4,
            criteria_scores=(),
            provider="gemini",
        )
        mock_judge.evaluate.return_value = eval_fail
        runner_judge = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=False,
            judge_max_attempts=1,
        )
        spec_max3 = StageEvaluationSpec(
            candidate_extractor=lambda res: res.text,
            max_attempts=3,
        )
        cfg_spec3 = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=1,
            eval_spec=spec_max3,
        )
        with caplog.at_level("WARNING"):
            runner_judge.execute_stage(cfg_spec3, MagicMock(), context=ctx)
        assert mock_judge.evaluate.call_count == 3
        retry_calls_exec = [
            c
            for c in mock_m.increment_counter.call_args_list
            if c[0][0] == "cresmo_judge_retry_count_total"
        ]
        assert len(retry_calls_exec) == 2
        assert any(
            r.message
            == "Quality evaluation for 'fluid_prose' reported low score on attempt 1/3 (overall=0.40, passed=False)."
            for r in caplog.records
        )

        runner_j4 = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=False,
            judge_max_attempts=4,
        )
        spec1 = StageEvaluationSpec(candidate_extractor=lambda res: res.text, max_attempts=1)
        cfg_j4 = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=1,
            eval_spec=spec1,
        )
        mock_judge.reset_mock()
        runner_j4.execute_stage(cfg_j4, MagicMock(), context=ctx)
        assert mock_judge.evaluate.call_count == 4

        with (
            patch(
                "cresmo.application.pipeline.stage_runner.generate_stage_candidate",
                return_value=None,
            ),
            pytest.raises(
                DomainValidationError, match=r"Stage 'fluid_prose' produced no candidate text\."
            ),
        ):
            runner_j1.execute_stage(cfg, MagicMock(), context=ctx)

        from cresmo.domain.value_objects import MediaProvenance

        prov = MediaProvenance(url="https://youtube.com/watch?v=123", description="video")
        source_with_prov = StageTranscript(
            channel=Channel(name="Chan", id=ChannelId("UC_1")),
            provenance=prov,
            content=Content(id=ContentId("c123"), text="Source prov text"),
        )

        runner_blocking = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=True,
            judge_max_attempts=1,
            ledger_port=MagicMock(),
        )
        cfg_blocking = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=1,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                max_attempts=1,
            ),
        )

        mock_synth = MagicMock()
        mock_synth.synthesize.return_value = "Synthesized critique string"
        runner_blocking.critique_synthesizer = mock_synth

        with patch(
            "cresmo.application.pipeline.stage_runner.record_stage_quarantine"
        ) as mock_record_quar:
            res_exec = runner_blocking.execute_stage(cfg_blocking, source_with_prov, context=ctx)
            assert res_exec.text == "Candidate output text"
            assert mock_synth.synthesize.call_count == 1

            mock_record_quar.assert_called_once()
            quar_kwargs = mock_record_quar.call_args[1]
            assert quar_kwargs["stage_name"] == "fluid_prose"
            assert quar_kwargs["context"] is ctx
            assert quar_kwargs["provenance"] is prov
            assert quar_kwargs["evaluation"] is eval_fail
            assert quar_kwargs["effective_max_attempts"] == 1
            assert quar_kwargs["ledger_port"] is runner_blocking.ledger_port
            assert quar_kwargs["metrics_port"] is runner_blocking.metrics_port
            assert quar_kwargs["telemetry_port"] is runner_blocking.telemetry_port
            assert quar_kwargs["critique"] == "Synthesized critique string"

        cfg_blocking_true = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            blocking=True,
            max_attempts=1,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda res: res.text,
                max_attempts=1,
            ),
        )
        runner_non_blocking_judge = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=False,
            judge_max_attempts=1,
            ledger_port=MagicMock(),
        )
        with patch(
            "cresmo.application.pipeline.stage_runner.record_stage_quarantine"
        ) as mock_record_quar2:
            runner_non_blocking_judge.execute_stage(
                cfg_blocking_true, source_with_prov, context=ctx
            )
            mock_record_quar2.assert_called_once()

        cfg_str_src = StageConfig[str, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner_j1.execute_stage(cfg_str_src, "999", context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "str",
                "source_characters": 3,
                "source_words": 1,
            }
        ]

        out_transcript = StageTranscript(
            channel=Channel(name="Chan"),
            provenance=MediaProvenance(),
            content=Content(id=ContentId("c123"), text="Content obj body"),
        )
        cfg_content = StageConfig[str, StageTranscript](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: out_transcript,
        )
        runner_j1.execute_stage(cfg_content, "one two three", context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Content obj body"),
                "output_words": len(["Content", "obj", "body"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 1.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

        cfg_cand_out = StageConfig[str, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: CandidateText(
                stage_name="fluid_prose", text="Candidate obj text"
            ),
        )
        runner_j1.execute_stage(cfg_cand_out, "one two three", context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Candidate obj text"),
                "output_words": len(["Candidate", "obj", "text"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 1.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

        class OutputBare:
            def __str__(self) -> str:
                return ""

        cfg_bare = StageConfig[str, OutputBare](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: OutputBare(),
        )
        runner_j1.execute_stage(cfg_bare, "one two three", context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Candidate output text"),
                "output_words": len(["Candidate", "output", "text"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 1.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

    def test_execute_stage_with_max_passes_override(self) -> None:
        from cresmo.application.pipeline.stage_factory import StageFactory

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_factory = MagicMock(spec=StageFactory)

        cfg = StageConfig[MagicMock, CandidateText](
            stage_name="gap_filler",
            transform_prompt_key=PromptKey.GAP_FILLER,
            max_passes=2,
            eval_spec=None,
        )
        mock_factory.build_stage.return_value = cfg

        mock_trans = MagicMock()
        mock_trans.transform.return_value = "## Test\n\nContent\n\n### Extra Info\n1. Info"

        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            stage_factory=mock_factory,
            llm_transformation_port=mock_trans,
            prompt_provider=MagicMock(),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content(
                id=ContentId("vid_retry_1"), title="Retry Title", session_id="ret_sess:1"
            ),
        )

        runner.execute_stage(
            "gap_filler",
            MagicMock(),
            context=ctx,
            max_passes=2,
        )

        mock_factory.build_stage.assert_called_once_with("gap_filler", max_passes=2)

    def test_measure_stage_execution_sets_active_telemetry_stage(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import measure_stage_execution
        from cresmo.application.ports.telemetry import _get_active_telemetry_stage

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content(
                id=ContentId("vid_stage_ctx"), title="Stage Ctx Title", session_id="ret_sess:2"
            ),
        )

        assert _get_active_telemetry_stage() is None
        with measure_stage_execution(telemetry, mock_m, stage_name="fluid_prose", context=ctx):
            assert _get_active_telemetry_stage() == "fluid_prose"
        assert _get_active_telemetry_stage() is None

    def test_measure_stage_execution_flushes_after_stage_span_closes(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import measure_stage_execution

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content(
                id=ContentId("vid_stage_flush"), title="Flush Title", session_id="ret_sess:3"
            ),
        )

        with measure_stage_execution(telemetry, mock_m, stage_name="gap_filler", context=ctx):
            telemetry.lifecycle_events.append("body")
        assert telemetry.lifecycle_events == [
            "span_enter:cresmo.gap_filler",
            "body",
            "span_exit:cresmo.gap_filler",
            "flush",
        ]

        telemetry.lifecycle_events.clear()
        with (
            pytest.raises(RuntimeError, match="stage boom"),
            measure_stage_execution(telemetry, mock_m, stage_name="gap_filler", context=ctx),
        ):
            raise RuntimeError("stage boom")
        assert telemetry.lifecycle_events == [
            "span_enter:cresmo.gap_filler",
            "span_exit:cresmo.gap_filler",
            "flush",
        ]

    def test_execute_stage_edge_contracts_and_span_forwarding(self) -> None:
        from collections.abc import Generator
        from contextlib import contextmanager

        from cresmo.application.pipeline.stage_execution import (
            evaluate_stage_candidate,
            generate_stage_candidate,
        )
        from cresmo.application.ports.telemetry import (
            NOOP_TELEMETRY_SPAN,
            SessionTelemetrySpec,
            SpanKind,
            TelemetrySpan,
        )
        from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
        from tests.doubles.telemetry_fake import RecordedSpan

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="EdgeChan", id=ChannelId("UC_edge")),
            content=Content(
                id=ContentId("vid_edge_01"), title="Edge Title", session_id="edge:1"
            ),
        )
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Singleword"
        mock_pp = MagicMock()
        mock_judge = MagicMock()
        eval_pass = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="test",
        )
        mock_judge.evaluate.return_value = eval_pass

        # 2. extract_source_text extracts from StageTranscript, preserves critique=None on attempt 1, and rounds ratio to 3 decimals
        seen_critiques: list[str | None] = []
        source_transcript = StageTranscript(
            channel=ctx.channel,
            provenance=MediaProvenance(),
            content=Content(id=ctx.content.id, title=ctx.content.title, text="Alpha beta gamma"),
        )
        dynamic_spec = StageEvaluationSpec(
            candidate_extractor=lambda c: c.text,
            max_attempts=1,
        )
        cfg_dynamic = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=dynamic_spec,
            max_attempts=1,
        )
        runner = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_max_attempts=1,
        )

        def _spy_gen(*args: object, **kwargs: object) -> CandidateText:
            seen_critiques.append(kwargs.get("critique"))  # type: ignore[arg-type]
            return generate_stage_candidate(*args, **kwargs)  # type: ignore[arg-type]

        with patch(
            "cresmo.application.pipeline.stage_runner.generate_stage_candidate",
            side_effect=_spy_gen,
        ):
            runner.execute_stage(cfg_dynamic, source_transcript, context=ctx)

        assert seen_critiques == [None]
        assert mock_judge.evaluate.call_args[0][0].raw_text == "Alpha beta gamma"
        stage_span = next(s for s in telemetry.spans if s.name == "cresmo.fluid_prose")
        assert stage_span.inputs[0]["source_characters"] == len("Alpha beta gamma")
        assert stage_span.inputs[0]["source_words"] == 3
        assert stage_span.outputs[0]["expansion_ratio"] == 0.333

        # 3. stage_config.max_attempts wins in max() over eval_spec and judge_max_attempts
        eval_fail = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.3,
            criteria_scores=(),
            provider="test",
        )
        mock_judge.reset_mock()
        mock_judge.evaluate.return_value = eval_fail
        cfg_stage_attempts = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=dynamic_spec,
            max_attempts=3,
        )
        runner.execute_stage(cfg_stage_attempts, source_transcript, context=ctx)
        assert mock_judge.evaluate.call_count == 3

        # 4. Zero effective_max_attempts raises DomainValidationError (candidate remains None)
        runner_zero = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            judge_max_attempts=0,
        )
        cfg_zero = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=1,
            eval_spec=None,
        )
        with (
            patch(
                "cresmo.application.pipeline.stage_runner.generate_stage_candidate",
                return_value=None,
            ),
            pytest.raises(
                DomainValidationError, match=r"^Stage 'fluid_prose' produced no candidate text\.$"
            ),
        ):
            runner_zero.execute_stage(cfg_zero, source_transcript, context=ctx)

        # 6. Quarantine fallback critique extraction when synthesizer returns empty string and no provenance
        class BareSourceNoProv:
            content = Content(id=ctx.content.id, title=ctx.content.title, text="Bare source")

        mock_synth_empty = MagicMock()
        mock_synth_empty.synthesize.return_value = ""
        eval_with_suggestion = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.3,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.3,
                    passed=False,
                    improvement_suggestion="Fix oral fillers.",
                ),
            ),
            provider="test",
        )
        mock_judge.evaluate.return_value = eval_with_suggestion
        runner_block_bare = _make_runner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=True,
            judge_max_attempts=1,
            critique_synthesizer=mock_synth_empty,
        )
        cfg_bare_q = StageConfig[BareSourceNoProv, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                candidate_extractor=lambda c: c.text, max_attempts=1
            ),
            max_attempts=1,
        )
        with patch(
            "cresmo.application.pipeline.stage_runner.record_stage_quarantine"
        ) as mock_record_q:
            runner_block_bare.execute_stage(cfg_bare_q, BareSourceNoProv(), context=ctx)
            mock_synth_empty.synthesize.assert_called_once_with(eval_with_suggestion, "fluid_prose")
            assert mock_record_q.call_args.kwargs["provenance"] is None
            assert mock_record_q.call_args.kwargs["critique"] == eval_with_suggestion.extract_critique()

        # 7. generate_stage_candidate forwards telemetry_port to emit saturation spans
        sat_telemetry = InMemoryTelemetryPort()
        mock_llm_sat = MagicMock()
        mock_llm_sat.transform.side_effect = ["Pass 1 text.", "Pass 1 text."]
        cfg_multi = StageConfig[StageTranscript, CandidateText](
            stage_name="gap_filler",
            transform_prompt_key=PromptKey.GAP_FILLER,
            max_passes=2,
            saturation_policy=HybridSaturationEvaluator(),
        )
        generate_stage_candidate(
            cfg_multi,
            source_transcript,
            context=ctx,
            prompt_provider=mock_pp,
            llm_port=mock_llm_sat,
            attempt=1,
            active_trace_id="trace_sat_7",
            telemetry_port=sat_telemetry,
        )
        assert "cresmo.gap_filler.saturation.pass_1" in [s.name for s in sat_telemetry.spans]

        # 8. evaluate_stage_candidate uses eval_span directly even when current_span() is NoOp, and tolerates None span
        class YieldingTelemetryPort(TelemetryPort):
            def __init__(self, yielded_span: TelemetrySpan | None) -> None:
                self._yielded_span = yielded_span

            @contextmanager
            def start_session(self, spec: SessionTelemetrySpec) -> Generator[TelemetrySpan]:
                yield NOOP_TELEMETRY_SPAN

            @contextmanager
            def start_span(self, name: str, **_kwargs: object) -> Generator[TelemetrySpan]:
                yield self._yielded_span  # type: ignore[misc]

            def current_span(self) -> TelemetrySpan:
                return NOOP_TELEMETRY_SPAN

            def record_score(self, **_kwargs: object) -> None:
                pass

        isolated_eval_span = RecordedSpan(
            name="cresmo.fluid_prose.judge",
            kind=SpanKind.SPAN,
            trace_id_value="e" * 32,
            span_id_value="b" * 16,
        )
        mock_judge.reset_mock()
        mock_judge.evaluate.return_value = eval_pass
        evaluate_stage_candidate(
            cfg_dynamic,
            source_transcript,
            CandidateText(text="cand", stage_name="fluid_prose"),
            context=ctx,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=YieldingTelemetryPort(isolated_eval_span),
            metrics_port=mock_m,
        )
        assert mock_judge.evaluate.call_args[0][0].trace_id == "e" * 32
        assert mock_judge.evaluate.call_args[0][0].observation_id == "b" * 16

        # NoOpTelemetryPort yields NOOP_TELEMETRY_SPAN whose span_id is None
        mock_judge.reset_mock()
        evaluate_stage_candidate(
            cfg_dynamic,
            source_transcript,
            CandidateText(text="cand", stage_name="fluid_prose"),
            context=ctx,
            attempt=1,
            llm_judge=mock_judge,
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=mock_m,
        )
        assert mock_judge.evaluate.call_args[0][0].observation_id is None
