"""Hermetic Unit Tests for PipelineStageRunner and Stage Quality Gate Fabric.

Conforms to:
    - ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
    - SPEC-013: Stage Quality Gate and Closed-Loop Evaluator Fabric Specification
"""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import NoOpMetricsPort, NoOpTelemetryPort, TelemetryPort
from cresmo.domain.entities import PipelineSessionId, StageTranscript, UserIdentity
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
    MediaProvenance,
    PromptKey,
    StageEvaluationSpec,
)
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


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
    """Test suite for PipelineStageRunner.execute_stage closed-loop quality gate."""

    def test_execute_stage_with_pipeline_execution_context(self) -> None:
        """Verify execute_stage cleanly consumes PipelineExecutionContext."""
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.application.pipeline.stage_descriptor import StageConfig
        from cresmo.domain.entities import StageTranscript, UserIdentity
        from cresmo.domain.value_objects import CandidateText, PromptKey
        from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
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
        content = Content.create(
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
        """Verify _evaluate_candidate populates EvaluationContext.observation_id from active TelemetrySpan."""
        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_eval.overall_score = 0.9
        mock_judge.evaluate.return_value = mock_eval

        telemetry = InMemoryTelemetryPort(trace_id="1234567890abcdef1234567890abcdef")
        runner = PipelineStageRunner(
            telemetry_port=telemetry,
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
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid"), session_id="test_chan:test_vid"),
        )

        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        with telemetry.start_span("cresmo.fluid_prose"):
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
        assert passed_eval_context.stage_name == "fluid_prose"
        assert passed_eval_context.trace_id == "1234567890abcdef1234567890abcdef"
        assert passed_eval_context.observation_id == telemetry.spans[1].span_id

    def test_evaluate_candidate_opens_chronological_evaluation_span(self) -> None:
        """Verify _evaluate_candidate opens cresmo.{stage}.judge span on TelemetryPort (ADR-037, ADR-070)."""
        telemetry = InMemoryTelemetryPort()
        mock_judge = MagicMock()
        mock_eval = MagicMock(spec=JudgeEvaluation)
        mock_eval.passed = True
        mock_eval.overall_score = 0.95
        mock_judge.evaluate.return_value = mock_eval

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
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
            user_identity=UserIdentity.anonymous(),
            channel=Channel(name="TestChan"),
            content=Content(id=ContentId("test_vid"), session_id="test_chan:test_vid"),
        )
        candidate = CandidateText(text="candidate prose", stage_name="fluid_prose")

        runner._evaluate_candidate(
            stage_config,
            source="source text",
            candidate=candidate,
            context=context,
            attempt=1,
        )

        assert len(telemetry.spans) == 1
        eval_span = telemetry.spans[0]
        assert eval_span.name == "cresmo.fluid_prose.judge"
        assert eval_span.attributes["judge.stage_name"] == "fluid_prose"
        assert eval_span.attributes["judge.attempt"] == 1
        assert eval_span.attributes["judge.verdict"] == "PASS"
        assert eval_span.attributes["judge.overall_score"] == 0.95


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
        from cresmo.application.pipeline.models import PipelineDependencies

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

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(
                PipelineDependencies(telemetry_port=None, metrics_port=mock_m)  # type: ignore[arg-type]
            )

        with pytest.raises(
            ValueError, match=r"^Both telemetry_port and metrics_port must be provided\.$"
        ):
            PipelineStageRunner(
                PipelineDependencies(telemetry_port=mock_t, metrics_port=None)  # type: ignore[arg-type]
            )

    def test_init_defaults(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)

        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)
        assert runner.judge_blocking is False
        assert runner.judge_max_attempts == 2
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

        with pytest.raises(
            ValueError,
            match="Cannot resolve stage 'custom' from string without an injected StageFactory.",
        ):
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
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        mock_note1 = MagicMock()
        mock_note2 = MagicMock()
        mock_moc = MagicMock()

        class RealInventoryStub:
            items: ClassVar[list[str]] = ["c1", "c2", "c3"]

        real_inv = RealInventoryStub()
        mock_dedup = MagicMock()
        mock_dedup.duplicates_unified_count = 1

        with telemetry.start_span("cresmo.coordinator"):
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
        # Check session coherence score + span event + span output (atomic_notes seam)
        assert len(telemetry.scores) == 1
        assert telemetry.scores[0].name == "session_coherence"
        assert abs(telemetry.scores[0].value - (2 / 3)) < 1e-6
        assert telemetry.scores[0].comment == "Coherence for vid_sess"
        root = telemetry.spans[0]
        assert telemetry.scores[0].trace_id == root.trace_id
        assert telemetry.scores[0].observation_id == root.span_id
        assert root.outputs[0] == {
            "coherence_score": pytest.approx(2 / 3),
            "synthesized_notes_count": 2,
            "inventory_count": 3,
            "mocs_count": 1,
            "duplicates_unified": 1,
        }
        assert len(root.events) == 1
        evt_name, evt_attrs = root.events[0]
        assert evt_name == "session_coherence"
        assert evt_attrs["eval.session_id"] == "ch_s:vid_s"
        assert evt_attrs["eval.content_id"] == "vid_sess"
        assert evt_attrs["eval.channel_id"] == "ch_s"
        assert abs(float(evt_attrs["eval.coherence_score"]) - (2 / 3)) < 1e-6  # type: ignore[arg-type]
        assert evt_attrs["eval.details.synthesized_notes_count"] == 2
        assert evt_attrs["eval.details.inventory_count"] == 3
        assert evt_attrs["eval.details.mocs_count"] == 1
        assert evt_attrs["eval.details.duplicates_unified"] == 1

    def test_record_session_completion_forwards_span_ids_and_parses_session_prefixes(self) -> None:
        from cresmo.application.ports.telemetry import SpanKind
        from tests.doubles.telemetry_fake import RecordedSpan

        mock_t = MagicMock(spec=TelemetryPort)
        explicit_span = RecordedSpan(
            name="cresmo.coordinator",
            kind=SpanKind.SPAN,
            trace_id_value="trace_explicit_coherence",
            span_id_value="obs_explicit_01",
        )
        mock_t.current_span.return_value = explicit_span
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=mock_t, metrics_port=mock_m)

        runner.record_session_completion(
            session_id="content:vid_two_parts",
            content_id="vid_two_parts",
            channel_name="Chan",
            synthesized_notes=[],
            inventory=MagicMock(items=["i1"]),
            mocs=[],
            dedup_report=MagicMock(duplicates_unified_count=0),
        )
        mock_t.record_score.assert_called_once_with(
            name="session_coherence",
            value=0.0,
            comment="Coherence for vid_two_parts",
            trace_id="trace_explicit_coherence",
            observation_id="obs_explicit_01",
        )
        assert explicit_span.events[-1][1]["eval.channel_id"] == "content"

    def test_record_session_completion_with_string_inputs_and_no_items(self) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        mock_inv_no_items = object()  # Has no .items attribute
        mock_dedup = MagicMock()
        mock_dedup.duplicates_unified_count = 0

        with telemetry.start_span("cresmo.coordinator"):
            runner.record_session_completion(
                session_id="content:chan_str:c1234567",
                content_id="c1234567",
                channel_name="StrChan",
                synthesized_notes=[],
                inventory=mock_inv_no_items,  # type: ignore[arg-type]
                mocs=[],
                dedup_report=mock_dedup,
                channel_id=None,
            )

        assert telemetry.scores[0].value == 0.0
        evt_name, evt_attrs = telemetry.spans[0].events[0]
        assert evt_name == "session_coherence"
        assert evt_attrs["eval.session_id"] == "content:chan_str:c1234567"
        assert evt_attrs["eval.content_id"] == "c1234567"
        assert evt_attrs["eval.channel_id"] == "chan_str"
        assert telemetry.spans[0].outputs[0] == {
            "coherence_score": 0.0,
            "synthesized_notes_count": 0,
            "inventory_count": 1,
            "mocs_count": 0,
            "duplicates_unified": 0,
        }

    def test_record_session_completion_score_cap_and_zero_items(self) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

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
        assert telemetry.scores[-1].value == 1.0

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
        assert telemetry.scores[-1].value == 1.0

        class SingleItemStub:
            items: ClassVar[list[str]] = ["c1"]

        runner.record_session_completion(
            session_id=PipelineSessionId("ch_s:vid_s"),
            content_id=ContentId("c1234567"),
            channel_name=ChannelName("Chan"),
            synthesized_notes=[MagicMock()],
            inventory=SingleItemStub(),  # type: ignore[arg-type]
            mocs=[],
            dedup_report=MagicMock(duplicates_unified_count=0),
        )
        assert telemetry.scores[-1].value == 1.0


class TestStageRunnerActiveTraceId:
    """Verifies deterministic trace ID derivation across context combinations."""

    def test_trace_id_with_recording_span(self) -> None:
        expected_tid = format(0x1234567890ABCDEF1234567890ABCDEF, "032x")
        telemetry = InMemoryTelemetryPort(trace_id=expected_tid)
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=NoOpMetricsPort())

        with telemetry.start_span("cresmo.fluid_prose"):
            assert runner._get_active_trace_id() == expected_tid

    def test_trace_id_without_span(self) -> None:
        runner = PipelineStageRunner(
            telemetry_port=NoOpTelemetryPort(), metrics_port=NoOpMetricsPort()
        )

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
        assert (
            runner._get_active_trace_id("RawChannel", ContentId("cid_str"))
            == "cresmo_RawChannel_cid_str"
        )

        # content_id and channel_id as kwargs
        assert (
            runner._get_active_trace_id(
                channel=None, content=None, channel_id="UC_kw", content_id="cid_kw"
            )
            == "cresmo_UC_kw_cid_kw"
        )

        # channel_name as kwarg
        assert (
            runner._get_active_trace_id(
                channel=None, content=None, channel_name="CName_kw", content_id="cid_kw2"
            )
            == "cresmo_CName_kw_cid_kw2"
        )

        # All none
        assert runner._get_active_trace_id() == "cresmo_cresmo_"

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
        runner = PipelineStageRunner(telemetry_port=other_telemetry, metrics_port=NoOpMetricsPort())
        with other_telemetry.start_span("cresmo.fluid_prose"):
            assert (
                resolve_active_trace_id(telemetry_port=other_telemetry, span=explicit_span)
                == "f" * 32
            )
            assert runner._get_active_trace_id(span=explicit_span) == "f" * 32

        # Content object takes precedence over content_id kwarg
        assert (
            resolve_active_trace_id(
                content=Content(id=ContentId("vid_from_obj")),
                content_id="vid_from_kw",
                channel_id="UC_1",
            )
            == "cresmo_UC_1_vid_from_obj"
        )
        # Explicit channel_name kwarg takes precedence over positional non-ChannelId channel
        assert (
            resolve_active_trace_id(
                channel="PositionalChan",
                channel_name="ExplicitKwChan",
                content_id="vid_kw_01",
            )
            == "cresmo_ExplicitKwChan_vid_kw_01"
        )

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

        runner = PipelineStageRunner(
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
                raw_text="source text",
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
            content=Content.create(
                id=ContentId("vid_retry_1"), title="Retry Title", session_id="ret_sess:1"
            ),
        )

        result = runner.execute_stage(stage_cfg, source, context=ctx)
        assert isinstance(result, CandidateText)
        assert result.text == "Final polished prose text"

        mock_m.increment_counter.assert_any_call(
            "cresmo_judge_retries_total", 1.0, labels={"stage": "fluid_prose"}
        )

        stage_span = next(s for s in telemetry.spans if s.name == "cresmo.fluid_prose")
        assert stage_span.inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "StageTranscript",
                "source_characters": len("source text"),
                "source_words": len(["source", "text"]),
            }
        ]
        assert stage_span.outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Final polished prose text"),
                "output_words": len(["Final", "polished", "prose", "text"]),
                "attempts": 2,
                "retries": 1,
                "expansion_ratio": round(4 / 2, 3),
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

        runner = PipelineStageRunner(
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
                raw_text="source text",
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
            content=Content.create(
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
                "expansion_ratio": round(3 / 2, 3),
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

        stage_cfg = StageConfig[StageTranscript, CandidateText](
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
            content=Content.create(
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
                "channel_name": "QuarantineCh",
            },
        )


class TestStageRunnerCandidateGenerationAndEvaluation:
    """Verifies candidate generation parameters and evaluation span formatting."""

    def test_generate_candidate_exhaustive_parameters(self) -> None:
        telemetry = NoOpTelemetryPort()
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Generated text output"

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.stage_name = "fluid_prose"
        mock_stage_cfg.temperature = 0.7
        mock_stage_cfg.build_transform_prompt.return_value = "Formatted prompt"

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="TechChan", id=ChannelId("UC_tech")),
            content=Content.create(id=ContentId("c1234567"), title="Ep 1", session_id="sess:123"),
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
            context=ctx,
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
            user_identity=UserIdentity.worker(),
            channel=Channel(name="NoIdChan", id=None),
            content=Content.create(id=ContentId("c7654321"), title="Ep 2", session_id="sess:456"),
        )

        mock_pp = MagicMock()
        mock_src = MagicMock()
        candidate = runner._generate_candidate(
            stage_config=mock_stage_cfg,
            prompt_provider=mock_pp,
            source=mock_src,
            context=ctx,
            llm_port=mock_llm,
            attempt=2,
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
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=NoOpMetricsPort)
        runner_no_judge = PipelineStageRunner(
            telemetry_port=mock_t, metrics_port=mock_m, llm_judge=None
        )

        mock_stage_cfg = MagicMock()
        mock_stage_cfg.eval_spec = None
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch"),
            content=Content.create(id=ContentId("c1234567"), title="T", session_id="s:1"),
        )
        cand = CandidateText(text="hello", stage_name="s", metadata={})
        assert (
            runner_no_judge._evaluate_candidate(
                mock_stage_cfg, MagicMock(), cand, context=ctx, attempt=1
            )
            is None
        )

        # Judge present but eval_spec None
        runner_with_judge = PipelineStageRunner(
            telemetry_port=mock_t, metrics_port=mock_m, llm_judge=MagicMock()
        )
        assert (
            runner_with_judge._evaluate_candidate(
                mock_stage_cfg, MagicMock(), cand, context=ctx, attempt=1
            )
            is None
        )

    def test_evaluate_candidate_recording_span_and_criteria_scores(self) -> None:
        telemetry = InMemoryTelemetryPort(trace_id="1234567890abcdef1234567890abcdef")
        mock_m = MagicMock()
        mock_judge = MagicMock()

        runner = PipelineStageRunner(
            telemetry_port=telemetry, metrics_port=mock_m, llm_judge=mock_judge
        )

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
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=ChannelId("UC_1")),
            content=Content.create(id=ContentId("c1234567"), title="Ep 1", session_id="s:1"),
        )
        cand = CandidateText(text="cleaned prose", stage_name="fluid_prose", metadata={})

        source_stub = MagicMock()
        res = runner._evaluate_candidate(stage_cfg, source_stub, cand, context=ctx, attempt=1)

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
        telemetry = InMemoryTelemetryPort(trace_id="")
        mock_m = MagicMock()
        mock_judge = MagicMock()

        runner = PipelineStageRunner(
            telemetry_port=telemetry, metrics_port=mock_m, llm_judge=mock_judge
        )

        crit_plain = MagicMock()
        crit_plain.criterion = "plain_metric"
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

        stage_cfg = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=StageEvaluationSpec(
                raw_text="raw",
                candidate_extractor=lambda res: res.text,
            ),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Ch", id=None),
            content=Content.create(id=ContentId("c1234567"), title="Ep 2", session_id="s:2"),
        )
        cand = CandidateText(text="imperfect", stage_name="fluid_prose", metadata={})

        source_mock = MagicMock()
        res = runner._evaluate_candidate(stage_cfg, source_mock, cand, context=ctx, attempt=2)

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
        assert output_dict["overall_score"] == "0.40"
        assert output_dict["scores"]["plain_metric"] == "0.40"
        assert "reasons" not in output_dict
        assert "suggestions" not in output_dict

        class BareScore:
            criterion = "bare_metric"
            score = 0.7

        class BareEval:
            target_stage = "fluid_prose"
            passed = True
            overall_score = 0.7
            criteria_scores = (BareScore(),)

        mock_judge.evaluate.return_value = BareEval()
        runner._evaluate_candidate(stage_cfg, source_mock, cand, context=ctx, attempt=1)

        class NoCriteriaEval:
            target_stage = "fluid_prose"
            passed = True
            overall_score = 0.8

        mock_judge.evaluate.return_value = NoCriteriaEval()
        runner._evaluate_candidate(stage_cfg, source_mock, cand, context=ctx, attempt=1)

        # NoOpTelemetryPort yields NOOP_TELEMETRY_SPAN (span_id is None, trace_id fallback)
        noop_runner = PipelineStageRunner(
            telemetry_port=NoOpTelemetryPort(), metrics_port=mock_m, llm_judge=mock_judge
        )
        mock_judge.evaluate.return_value = eval_result
        assert (
            noop_runner._evaluate_candidate(stage_cfg, source_mock, cand, context=ctx, attempt=2)
            is eval_result
        )
        assert mock_judge.evaluate.call_args[0][0].observation_id is None


class TestStageRunnerStageExecutionAndFallback:
    """Verifies run_stage and run_evaluated_stage delegation, exceptions, and fallback semantics."""

    def test_run_stage_default_parameters_and_unknown_fallbacks(self) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        # Both channel and content None
        res = runner.run_stage("test_stage", lambda: "ret_val")
        assert res == "ret_val"
        assert telemetry.spans[-1].name == "cresmo.test_stage"
        assert telemetry.spans[-1].attributes == {
            "cresmo.stage.channel.id": "",
            "cresmo.stage.content.id": "unknown",
            "cresmo.stage.channel.name": "unknown",
            "cresmo.stage.content.title": "",
        }

        # channel_name provided as string, content_id provided as string
        res2 = runner.run_stage(
            "test_stage",
            lambda: "ret_val_2",
            channel_name="CustomChan",
            content_id="c1234567",
            content_title="My Title",
        )
        assert res2 == "ret_val_2"
        assert telemetry.spans[-1].attributes == {
            "cresmo.stage.channel.id": "",
            "cresmo.stage.content.id": "c1234567",
            "cresmo.stage.channel.name": "CustomChan",
            "cresmo.stage.content.title": "My Title",
        }

        # channel_id provided without Channel object
        res3 = runner.run_stage(
            "test_stage",
            lambda: "ret_val_3",
            channel_id="UC_custom",
            content_id="c1234567",
        )
        assert res3 == "ret_val_3"
        assert telemetry.spans[-1].attributes == {
            "cresmo.stage.channel.id": "UC_custom",
            "cresmo.stage.content.id": "c1234567",
            "cresmo.stage.channel.name": "unknown",
            "cresmo.stage.content.title": "",
        }

    def test_run_stage_non_fatal_exception_returns_fallback(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        def failing_fn() -> None:
            raise RuntimeError("Temporary glitch")

        with caplog.at_level("WARNING"):
            # Callable fallback
            res = runner.run_stage(
                "test_stage",
                failing_fn,
                fatal=False,
                fallback=lambda: "recovered",
                content_id="c1234567",
            )
            assert res == "recovered"
            assert (
                caplog.records[0].message
                == "[Pipeline] test_stage skipped for c1234567: Temporary glitch"
            )

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
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        def fatal_fn() -> None:
            raise KeyError("Missing resource")

        ch = Channel(name="FailCh", id=ChannelId("UC_fail"))
        cnt = Content(id=ContentId("c1234567"), title="Fail Title")

        with pytest.raises(KeyError, match="Missing resource"):
            runner.run_stage("fatal_stage", fatal_fn, channel=ch, content=cnt)

        assert len(telemetry.spans) == 1
        assert len(telemetry.spans[0].errors) == 1
        assert isinstance(telemetry.spans[0].errors[0], KeyError)
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

    def test_execute_stage_source_and_output_text_extractions(self) -> None:
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        mock_pp = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Prose text"

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="ExChan", id=ChannelId("UC_ex")),
            content=Content.create(id=ContentId("c1234567"), title="Ex Title", session_id="s:1"),
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

        # Case 2: source has .text string
        class SourceWithText:
            text = "Source text only"

        cfg2 = StageConfig[SourceWithText, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg2, SourceWithText(), context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "SourceWithText",
                "source_characters": len("Source text only"),
                "source_words": len(["Source", "text", "only"]),
            }
        ]

        # Case 3: source has .content that is Content
        class SourceWithContent:
            content = Content(id=ContentId("c1234567"), text="Content body text")

        cfg3 = StageConfig[SourceWithContent, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner.execute_stage(cfg3, SourceWithContent(), context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "SourceWithContent",
                "source_characters": len("Content body text"),
                "source_words": len(["Content", "body", "text"]),
            }
        ]

        # Case 4: source with neither, falls back to str(source)
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
        runner = PipelineStageRunner(telemetry_port=telemetry, metrics_port=mock_m)

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="Chan", id=ChannelId("UC_1")),
            content=Content.create(id=ContentId("c1234567"), title="Title", session_id="s:1"),
        )

        mock_pp = MagicMock()
        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Candidate output text"

        cfg = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        res = runner.execute_stage(
            cfg,
            MagicMock(),
            context=ctx,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
        )
        assert res.text == "Candidate output text"

        runner_j1 = PipelineStageRunner(
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
        runner_judge = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=False,
            judge_max_attempts=1,
        )
        spec_max3 = StageEvaluationSpec(
            raw_text="raw",
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
            if c[0][0] == "cresmo_judge_retries_total"
        ]
        assert len(retry_calls_exec) == 2
        assert any(
            r.message
            == "Quality evaluation for 'fluid_prose' reported low score on attempt 1/3 (overall=0.40, passed=False)."
            for r in caplog.records
        )

        runner_j4 = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=False,
            judge_max_attempts=4,
        )
        spec1 = StageEvaluationSpec(
            raw_text="raw", candidate_extractor=lambda res: res.text, max_attempts=1
        )
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
            patch.object(runner_j1, "_generate_candidate", return_value=None),
            pytest.raises(
                DomainValidationError, match=r"Stage 'fluid_prose' produced no candidate text\."
            ),
        ):
            runner_j1.execute_stage(cfg, MagicMock(), context=ctx)

        from cresmo.domain.value_objects import MediaProvenance

        prov = MediaProvenance(url="https://youtube.com/watch?v=123", description="video")
        source_with_prov = MagicMock()
        source_with_prov.provenance = prov
        source_with_prov.content = Content(id=ContentId("c123"), text="Source prov text")

        runner_blocking = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_blocking=True,
            judge_max_attempts=1,
            ledger_port=MagicMock(),
        )
        cfg_blocking = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=1,
            eval_spec=StageEvaluationSpec(
                raw_text="raw",
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

        cfg_blocking_true = StageConfig[MagicMock, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            blocking=True,
            max_attempts=1,
            eval_spec=StageEvaluationSpec(
                raw_text="raw",
                candidate_extractor=lambda res: res.text,
                max_attempts=1,
            ),
        )
        runner_non_blocking_judge = PipelineStageRunner(
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

        class SourceWithIntText:
            text = 999

        cfg_int_src = StageConfig[SourceWithIntText, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
        )
        runner_j1.execute_stage(cfg_int_src, SourceWithIntText(), context=ctx)
        assert telemetry.spans[-1].inputs == [
            {
                "stage_name": "fluid_prose",
                "source_type": "SourceWithIntText",
                "source_characters": 0,
                "source_words": 0,
            }
        ]

        class OutputWithContent:
            def __init__(self) -> None:
                self.content = Content(id=ContentId("c123"), text="Content obj body")

        cfg_content = StageConfig[MagicMock, OutputWithContent](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: OutputWithContent(),
        )
        runner_j1.execute_stage(cfg_content, MagicMock(), context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Content obj body"),
                "output_words": len(["Content", "obj", "body"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 3.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

        class OutputWithStage:
            def __init__(self) -> None:
                self.content = Content(id=ContentId("c123"), text="Content obj text")

        cfg_stage = StageConfig[MagicMock, OutputWithStage](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: OutputWithStage(),
        )
        runner_j1.execute_stage(cfg_stage, MagicMock(), context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Content obj text"),
                "output_words": len(["Content", "obj", "text"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 3.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

        class OutputBare:
            pass

        cfg_bare = StageConfig[MagicMock, OutputBare](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: OutputBare(),
        )
        runner_j1.execute_stage(cfg_bare, MagicMock(), context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": len("Candidate output text"),
                "output_words": len(["Candidate", "output", "text"]),
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 3.0,
                "judge_passed": None,
                "judge_overall_score": None,
            }
        ]

        class OutputWithInt:
            def __init__(self) -> None:
                self.text = 123

        cfg_int = StageConfig[MagicMock, OutputWithInt](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=None,
            post_processor=lambda cand, src: OutputWithInt(),
        )
        runner_j1.execute_stage(cfg_int, MagicMock(), context=ctx)
        assert telemetry.spans[-1].outputs == [
            {
                "status": "APPROVED",
                "output_characters": 0,
                "output_words": 0,
                "attempts": 1,
                "retries": 0,
                "expansion_ratio": 0.0,
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

        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            stage_factory=mock_factory,
            llm_transformation_port=mock_trans,
            prompt_provider=MagicMock(),
        )
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content.create(
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
        from cresmo.application.ports import get_active_telemetry_stage

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content.create(
                id=ContentId("vid_stage_ctx"), title="Stage Ctx Title", session_id="ret_sess:2"
            ),
        )

        assert get_active_telemetry_stage() is None
        with measure_stage_execution(telemetry, mock_m, stage_name="fluid_prose", context=ctx):
            assert get_active_telemetry_stage() == "fluid_prose"
        assert get_active_telemetry_stage() is None

    def test_measure_stage_execution_flushes_after_stage_span_closes(self) -> None:
        from cresmo.application.pipeline.stage_telemetry import measure_stage_execution

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock()
        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="RetCh", id=ChannelId("UC_ret")),
            content=Content.create(
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

        from cresmo.application.pipeline.stage_runner import _extract_stage_telemetry_text
        from cresmo.application.ports.telemetry import (
            NOOP_TELEMETRY_SPAN,
            SessionTelemetrySpec,
            SpanKind,
            TelemetrySpan,
        )
        from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
        from tests.doubles.telemetry_fake import RecordedSpan

        # 1. _extract_stage_telemetry_text rejects non-str .text directly
        class NonStrText:
            text = 42

        assert _extract_stage_telemetry_text(NonStrText()) == ""

        ctx = PipelineExecutionContext(
            user_identity=UserIdentity.worker(),
            channel=Channel(name="EdgeChan", id=ChannelId("UC_edge")),
            content=Content.create(
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

        # 2. Dynamic eval_spec extracts from source, preserves critique=None on attempt 1, and rounds ratio to 3 decimals
        seen_critiques: list[str | None] = []
        source_transcript = StageTranscript(
            channel=ctx.channel,
            provenance=MediaProvenance(),
            content=Content(id=ctx.content.id, title=ctx.content.title, text="Alpha beta gamma"),
        )
        dynamic_spec = StageEvaluationSpec(
            raw_text="",
            source_extractor=lambda s: s.content.text,
            candidate_extractor=lambda c: c.text,
            max_attempts=1,
        )
        cfg_dynamic = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=dynamic_spec,
            max_attempts=1,
        )
        runner = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            llm_judge=mock_judge,
            judge_max_attempts=1,
        )
        orig_gen = runner._generate_candidate

        def _spy_gen(*args: object, **kwargs: object) -> CandidateText:
            seen_critiques.append(kwargs.get("critique"))  # type: ignore[arg-type]
            return orig_gen(*args, **kwargs)  # type: ignore[arg-type]

        with patch.object(runner, "_generate_candidate", side_effect=_spy_gen):
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
        runner_zero = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            judge_max_attempts=0,
        )
        cfg_zero = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            max_attempts=0,
            eval_spec=None,
        )
        with pytest.raises(
            DomainValidationError, match=r"^Stage 'fluid_prose' produced no candidate text\.$"
        ):
            runner_zero.execute_stage(cfg_zero, source_transcript, context=ctx)

        # 5. Non-str source_text from eval_spec.extract_source_text yields 0 chars/words
        non_str_spec = StageEvaluationSpec(
            raw_text="",
            source_extractor=lambda _s: None,  # type: ignore[arg-type,return-value]
            candidate_extractor=lambda c: c.text,
            max_attempts=1,
        )
        cfg_non_str = StageConfig[StageTranscript, CandidateText](
            stage_name="fluid_prose",
            transform_prompt_key=PromptKey.FLUID_PROSE,
            eval_spec=non_str_spec,
            max_attempts=1,
        )
        runner_no_judge = PipelineStageRunner(
            telemetry_port=telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            judge_max_attempts=1,
        )
        runner_no_judge.execute_stage(cfg_non_str, source_transcript, context=ctx)
        assert telemetry.spans[-1].inputs[0]["source_characters"] == 0
        assert telemetry.spans[-1].inputs[0]["source_words"] == 0

        # 6. Quarantine fallback critique synthesis and source without .provenance attribute
        class BareSourceNoProv:
            content = Content(id=ctx.content.id, title=ctx.content.title, text="Bare source")

        mock_synth_empty = MagicMock()
        mock_synth_empty.synthesize.side_effect = ["", "Recovered fallback critique"]
        runner_block_bare = PipelineStageRunner(
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
                raw_text="Bare source", candidate_extractor=lambda c: c.text, max_attempts=1
            ),
            max_attempts=1,
        )
        with patch(
            "cresmo.application.pipeline.stage_runner.record_stage_quarantine"
        ) as mock_record_q:
            runner_block_bare.execute_stage(cfg_bare_q, BareSourceNoProv(), context=ctx)
            assert mock_synth_empty.synthesize.call_count == 2
            assert mock_synth_empty.synthesize.call_args_list[1].args == (eval_fail, "fluid_prose")
            assert mock_record_q.call_args.kwargs["provenance"] is None
            assert mock_record_q.call_args.kwargs["critique"] == "Recovered fallback critique"

        # 7. _generate_candidate forwards self.telemetry_port to emit saturation spans
        sat_telemetry = InMemoryTelemetryPort()
        mock_llm_sat = MagicMock()
        mock_llm_sat.transform.side_effect = ["Pass 1 text.", "Pass 1 text."]
        runner_sat = PipelineStageRunner(
            telemetry_port=sat_telemetry,
            metrics_port=mock_m,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm_sat,
        )
        cfg_multi = StageConfig[StageTranscript, CandidateText](
            stage_name="gap_filler",
            transform_prompt_key=PromptKey.GAP_FILLER,
            max_passes=2,
            saturation_policy=HybridSaturationEvaluator(),
        )
        runner_sat._generate_candidate(
            cfg_multi,
            source_transcript,
            context=ctx,
            prompt_provider=mock_pp,
            llm_port=mock_llm_sat,
            attempt=1,
        )
        assert "cresmo.gap_filler.saturation.pass_1" in [s.name for s in sat_telemetry.spans]

        # 8. run_stage prefers Content object over content_id without parsing invalid content_id
        assert (
            runner.run_stage(
                "test_stage",
                lambda: "content_wins",
                content=Content(id=ContentId("vid_valid_99")),
                content_id="invalid id!",
            )
            == "content_wins"
        )

        # 9. evaluate_stage_candidate uses eval_span directly even when current_span() is NoOp, and tolerates None span
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
        runner_iso = PipelineStageRunner(
            telemetry_port=YieldingTelemetryPort(isolated_eval_span),
            metrics_port=mock_m,
            llm_judge=mock_judge,
        )
        mock_judge.reset_mock()
        mock_judge.evaluate.return_value = eval_pass
        runner_iso._evaluate_candidate(
            cfg_dynamic,
            source_transcript,
            CandidateText(text="cand", stage_name="fluid_prose"),
            context=ctx,
            attempt=1,
        )
        assert mock_judge.evaluate.call_args[0][0].trace_id == "e" * 32
        assert mock_judge.evaluate.call_args[0][0].observation_id == "b" * 16

        runner_none_span = PipelineStageRunner(
            telemetry_port=YieldingTelemetryPort(None),
            metrics_port=mock_m,
            llm_judge=mock_judge,
        )
        mock_judge.reset_mock()
        runner_none_span._evaluate_candidate(
            cfg_dynamic,
            source_transcript,
            CandidateText(text="cand", stage_name="fluid_prose"),
            context=ctx,
            attempt=1,
        )
        assert mock_judge.evaluate.call_args[0][0].observation_id is None
