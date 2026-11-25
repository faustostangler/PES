"""Unit tests for PipelineStageRunner Closed-Loop Reflexion and Fail-Fast Quarantine (ADR-031)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LedgerRepositoryPort,
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
)
from cresmo.domain.entities import StageTranscript, UserIdentity
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    MediaProvenance,
    PipelineStatus,
    StageExecutionPolicy,
)
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


def _create_sample_context() -> PipelineExecutionContext:
    channel = Channel(name="Test Channel", id=ChannelId("UC_test"))
    content = Content(
        id=ContentId("content_123"), title="Sample Content", session_id="test_chan:content_123"
    )
    return PipelineExecutionContext(
        user_identity=UserIdentity.worker(),
        channel=channel,
        content=content,
    )


def test_execute_stage_with_string_identifier_and_factory() -> None:
    """Verify execute_stage resolves stage descriptor from string identifier via injected StageFactory."""
    policy = StageExecutionPolicy(judge_blocking=False, judge_max_attempts=1)
    factory = StageFactory(policy=policy)

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "Transformed text output."

    runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=mock_llm,
            stage_factory=factory,
        )
    )

    ctx = _create_sample_context()
    raw = StageTranscript(
        channel=Channel(name=ChannelName(ctx.channel.name)),
        provenance=MediaProvenance(),
        content=Content(id=ctx.content.id, text="Original source transcript."),
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content.id == ctx.content.id
    assert "Transformed text output." in result.content.text
    assert mock_llm.transform.call_count == 1


def test_execute_stage_string_without_factory_raises_value_error() -> None:
    """Verify execute_stage raises ValueError if stage name is provided but no StageFactory was injected."""
    runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=MagicMock(spec=LLMTransformationPort),
            stage_factory=None,
        )
    )

    ctx = _create_sample_context()
    raw = StageTranscript(
        channel=Channel(name=ChannelName(ctx.channel.name)),
        provenance=MediaProvenance(),
        content=Content(id=ctx.content.id, text="Some text"),
    )

    with pytest.raises(ValueError, match="Cannot resolve stage 'fluid_prose' from string"):
        runner.execute_stage("fluid_prose", source=raw, context=ctx)


def test_execute_stage_closed_loop_critique_synthesizer_integration() -> None:
    """Verify CritiqueSynthesizer is invoked on failed attempt to produce directed critique for prompt reflection."""
    policy = StageExecutionPolicy(judge_blocking=True, judge_max_attempts=2)
    factory = StageFactory(policy=policy)

    mock_judge = MagicMock()
    failed_eval = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.45,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                score=0.45,
                passed=False,
                reasoning="Excessive colloquialisms.",
            ),
        ),
        provider="ollama",
    )
    passed_eval = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.95,
        criteria_scores=(),
        provider="ollama",
    )
    mock_judge.evaluate.side_effect = [failed_eval, passed_eval]

    mock_synthesizer = MagicMock(spec=CritiqueSynthesizerPort)
    mock_synthesizer.synthesize.return_value = (
        "Direcionamento crítico: Eliminar todos os vícios de linguagem e hesitações."
    )

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.side_effect = [
        "Candidate with colloquialisms.",
        "Refined candidate text.",
    ]

    metrics = MagicMock(spec=NoOpMetricsPort())
    runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=metrics,
            llm_judge=mock_judge,
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=mock_llm,
            stage_factory=factory,
            critique_synthesizer=mock_synthesizer,
        )
    )

    ctx = _create_sample_context()
    raw = StageTranscript(
        channel=Channel(name=ChannelName(ctx.channel.name)),
        provenance=MediaProvenance(),
        content=Content(id=ctx.content.id, text="Verbatim transcript with hesitation."),
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content.id == ctx.content.id
    assert "Refined candidate text." in result.content.text

    # Verify synthesizer was called with the failed evaluation
    assert mock_synthesizer.synthesize.call_count == 1
    call_args = mock_synthesizer.synthesize.call_args
    assert call_args[0][0] == failed_eval
    assert call_args[0][1] == "fluid_prose"

    # Verify critique was injected into prompt on attempt 2
    prompt_attempt_2 = mock_llm.transform.call_args_list[1].kwargs.get("prompt")
    assert "Direcionamento crítico" in prompt_attempt_2.messages[-1].content


def test_execute_stage_fail_fast_quarantine_protocol() -> None:
    """Verify Fail-Fast with Quarantine executes all 4 protocol actions on exhausted retry failures."""
    policy = StageExecutionPolicy(judge_blocking=True, judge_max_attempts=2)
    factory = StageFactory(policy=policy)

    mock_judge = MagicMock()
    failed_eval = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.35,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                score=0.35,
                passed=False,
                reasoning="Irreparable verbal noise.",
            ),
        ),
        provider="ollama",
    )
    mock_judge.evaluate.return_value = failed_eval

    mock_synthesizer = MagicMock(spec=CritiqueSynthesizerPort)
    mock_synthesizer.synthesize.return_value = "Crítica direcionada irrevogável."

    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None

    mock_metrics = MagicMock(spec=NoOpMetricsPort())
    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "Failed candidate draft."

    runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=mock_metrics,
            llm_judge=mock_judge,
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=mock_llm,
            stage_factory=factory,
            critique_synthesizer=mock_synthesizer,
            ledger_port=mock_ledger,
        )
    )

    ctx = _create_sample_context()
    raw = StageTranscript(
        channel=Channel(name=ChannelName(ctx.channel.name)),
        provenance=MediaProvenance(),
        content=Content(id=ctx.content.id, text="Text that repeatedly fails."),
    )

    with pytest.raises(StageQuarantinedError) as exc_info:
        runner.execute_stage("fluid_prose", source=raw, context=ctx)

    # 1. Check StageQuarantinedError properties
    err = exc_info.value
    assert err.stage_name == "fluid_prose"
    assert err.content_id == ctx.content.id.value
    assert err.attempts == 2
    assert "Crítica direcionada irrevogável" in err.critique
    assert err.overall_score == 0.35

    # 2. Check SQLite Ledger Quarantine record
    assert mock_ledger.save_entry.call_count == 1
    saved_entry = mock_ledger.save_entry.call_args[0][0]
    assert saved_entry.content_id == ctx.content.id
    assert saved_entry.channel_name.value == ctx.channel.name
    assert saved_entry.status == PipelineStatus.QUARANTINED
    assert "Stage 'fluid_prose' quarantined" in saved_entry.error_message

    # 3. Check Prometheus metric incremented
    mock_metrics.increment_counter.assert_any_call(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": "fluid_prose", "channel_id": "UC_test"},
    )


def test_record_stage_quarantine_with_channel_and_content_objects_and_span() -> None:
    """Verify record_stage_quarantine with PipelineExecutionContext, TelemetryPort span, and new Ledger entry."""
    eval_mock = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.42,
        criteria_scores=(),
        provider="test",
    )
    ch = Channel(name="TestChannel", id=ChannelId("UC_123"))
    cnt = Content(id=ContentId("vid_999"), title="Title 999")
    prov = MediaProvenance(url="https://yt.be/999")
    ctx = PipelineExecutionContext(user_identity=UserIdentity.worker(), channel=ch, content=cnt)
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None
    mock_metrics = MagicMock(spec=NoOpMetricsPort())
    telemetry = InMemoryTelemetryPort()

    with (
        pytest.raises(StageQuarantinedError) as exc_info,
        telemetry.start_span("cresmo.fluid_prose"),
    ):
        record_stage_quarantine(
            stage_name="fluid_prose",
            context=ctx,
            provenance=prov,
            evaluation=eval_mock,
            critique="Critical defect",
            effective_max_attempts=3,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
            telemetry_port=telemetry,
        )

    # Verify StageQuarantinedError fields
    err = exc_info.value
    assert err.stage_name == "fluid_prose"
    assert err.content_id == "vid_999"
    assert err.attempts == 3
    assert err.critique == "Critical defect"
    assert err.overall_score == 0.42

    # Verify ledger saved entry
    assert mock_ledger.save_entry.call_count == 1
    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.content_id == ContentId("vid_999")
    assert saved.media_url == "https://yt.be/999"
    assert saved.title == "Title 999"
    assert saved.channel_name == ChannelName("TestChannel")
    assert saved.status == PipelineStatus.QUARANTINED
    assert saved.error_message == "Stage 'fluid_prose' quarantined: Critical defect"
    assert saved.started_at is None
    assert saved.completed_at is not None
    assert saved.completed_at.tzinfo == UTC

    # Verify telemetry span attributes recorded through TelemetryPort
    span_attrs = telemetry.spans[0].attributes
    assert span_attrs["quarantined"] is True
    assert span_attrs["quarantine.stage"] == "fluid_prose"
    assert span_attrs["quarantine.critique"] == "Critical defect"
    assert span_attrs["quarantine.attempts"] == 3
    assert span_attrs["quarantine.overall_score"] == 0.42
    assert span_attrs["cresmo.content.id"] == "vid_999"
    assert span_attrs["cresmo.channel.id"] == "UC_123"
    assert span_attrs["cresmo.channel.name"] == "TestChannel"
    assert span_attrs["cresmo.content.title"] == "Title 999"

    # Verify metric
    mock_metrics.increment_counter.assert_called_once_with(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": "fluid_prose", "channel_id": "UC_123"},
    )


def test_record_stage_quarantine_preserves_existing_ledger_entry() -> None:
    """Verify record_stage_quarantine preserves media_url, title, and started_at from existing ledger entry."""
    eval_mock = JudgeEvaluation(
        target_stage="stage_2",
        passed=False,
        overall_score=0.1,
        criteria_scores=(),
        provider="test",
    )
    ch = Channel(name="OldChannel", id=None)
    cnt = Content(id=ContentId("vid_existing"), title="")
    started_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    from cresmo.domain.value_objects import LedgerEntry

    existing = LedgerEntry(
        content_id=ContentId("vid_existing"),
        media_url="https://existing.media.url",
        title="Existing Master Title",
        channel_name=ChannelName("OldChannel"),
        status=PipelineStatus.RUNNING,
        started_at=started_time,
    )
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = existing
    telemetry = InMemoryTelemetryPort()

    ctx = PipelineExecutionContext(user_identity=UserIdentity.worker(), channel=ch, content=cnt)
    with pytest.raises(StageQuarantinedError), telemetry.start_span("cresmo.stage_2"):
        record_stage_quarantine(
            stage_name="stage_2",
            context=ctx,
            evaluation=eval_mock,
            critique="failed check",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=NoOpMetricsPort(),
            telemetry_port=telemetry,
        )

    mock_ledger.get_entry.assert_called_once_with(ContentId("vid_existing"))
    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.media_url == "https://existing.media.url"
    assert saved.title == "Existing Master Title"
    assert saved.started_at == started_time
    assert saved.status == PipelineStatus.QUARANTINED
    assert telemetry.spans[0].attributes["cresmo.channel.id"] == "OldChannel"


def test_record_stage_quarantine_fallback_urls_and_titles() -> None:
    """Verify URL and title fallbacks when Content has empty url and title."""
    eval_mock = JudgeEvaluation(
        target_stage="stage_3",
        passed=False,
        overall_score=0.3,
        criteria_scores=(),
        provider="test",
    )
    cnt = Content(id=ContentId("vid_fallback"), title="")
    ctx = PipelineExecutionContext(
        user_identity=UserIdentity.worker(),
        channel=Channel(name="unknown"),
        content=cnt,
    )
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None
    telemetry = InMemoryTelemetryPort()

    with pytest.raises(StageQuarantinedError) as exc_info, telemetry.start_span("cresmo.stage_3"):
        record_stage_quarantine(
            stage_name="stage_3",
            context=ctx,
            evaluation=eval_mock,
            critique="",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=NoOpMetricsPort(),
            telemetry_port=telemetry,
        )

    assert exc_info.value.critique == ""
    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.media_url == "https://cresmo.internal/content/vid_fallback"
    assert saved.title == "Quarantined Content vid_fallback"
    assert saved.channel_name == ChannelName("unknown")
    span_attrs = telemetry.spans[0].attributes
    assert span_attrs["cresmo.channel.name"] == "unknown"
    assert span_attrs["cresmo.channel.id"] == "unknown"
    assert span_attrs["cresmo.content.title"] == "vid_fallback"
    assert span_attrs["quarantine.critique"] == ""


def test_record_stage_quarantine_ledger_exception_resilience(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify ledger save failure is logged and does not prevent quarantine raise or metric increment."""
    eval_mock = JudgeEvaluation(
        target_stage="stage_5",
        passed=False,
        overall_score=0.5,
        criteria_scores=(),
        provider="test",
    )
    ch = Channel(name="Chan", id=None)
    cnt = Content(id=ContentId("vid_err"), title="T")
    ctx = PipelineExecutionContext(user_identity=UserIdentity.worker(), channel=ch, content=cnt)
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.side_effect = RuntimeError("Database locked")
    mock_metrics = MagicMock(spec=NoOpMetricsPort())

    with pytest.raises(StageQuarantinedError) as exc_info:
        record_stage_quarantine(
            stage_name="stage_5",
            context=ctx,
            evaluation=eval_mock,
            critique="error test",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
            telemetry_port=NoOpTelemetryPort(),
        )

    assert exc_info.value.content_id == "vid_err"
    mock_metrics.increment_counter.assert_called_once()
    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_records) == 1
    assert (
        error_records[0].getMessage()
        == "Failed to record quarantine entry in ledger for vid_err: Database locked"
    )
