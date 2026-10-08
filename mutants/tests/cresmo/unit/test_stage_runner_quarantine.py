"""Unit tests for PipelineStageRunner Closed-Loop Reflexion and Fail-Fast Quarantine (ADR-031)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LLMTransformationPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
)
from cresmo.domain.entities import PipelineSessionId, SourceTranscript, UserIdentity
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
)


def _create_sample_context() -> PipelineExecutionContext:
    channel = Channel(name="Test Channel", id=ChannelId("UC_test"))
    content = Content.create(id=ContentId("content_123"), title="Sample Content")
    return PipelineExecutionContext(
        session_id=PipelineSessionId("test_chan:content_123"),
        user_identity=UserIdentity.worker(),
        channel=channel,
        content=content,
    )


def test_execute_stage_with_string_identifier_and_factory() -> None:
    """Verify execute_stage resolves stage descriptor from string identifier via injected StageFactory."""
    settings = DefaultPipelineSettings(judge_blocking=False, judge_max_attempts=1)
    factory = StageFactory(settings=settings)

    mock_llm = MagicMock(spec=LLMTransformationPort)
    mock_llm.transform.return_value = "Transformed text output."

    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=factory,
    )

    ctx = _create_sample_context()
    raw = SourceTranscript(
        content_id=ctx.content.id,
        channel_name=ChannelName(ctx.channel.name),
        body="Original source transcript.",
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content.id == ctx.content.id
    assert "Transformed text output." in result.content.body
    assert mock_llm.transform.call_count == 1


def test_execute_stage_string_without_factory_raises_value_error() -> None:
    """Verify execute_stage raises ValueError if stage name is provided but no StageFactory was injected."""
    runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=MagicMock(spec=LLMTransformationPort),
        stage_factory=None,
    )

    ctx = _create_sample_context()
    raw = SourceTranscript(
        content_id=ctx.content.id,
        channel_name=ChannelName(ctx.channel.name),
        body="Some text",
    )

    with pytest.raises(ValueError, match="Cannot resolve stage 'fluid_prose' from string"):
        runner.execute_stage("fluid_prose", source=raw, context=ctx)


def test_execute_stage_closed_loop_critique_synthesizer_integration() -> None:
    """Verify CritiqueSynthesizer is invoked on failed attempt to produce directed critique for prompt reflection."""
    settings = DefaultPipelineSettings(judge_blocking=True, judge_max_attempts=2)
    factory = StageFactory(settings=settings)

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
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=metrics,
        llm_judge=mock_judge,
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=factory,
        critique_synthesizer=mock_synthesizer,
    )

    ctx = _create_sample_context()
    raw = SourceTranscript(
        content_id=ctx.content.id,
        channel_name=ChannelName(ctx.channel.name),
        body="Verbatim transcript with hesitation.",
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content.id == ctx.content.id
    assert "Refined candidate text." in result.content.body

    # Verify synthesizer was called with the failed evaluation
    assert mock_synthesizer.synthesize.call_count == 1
    call_args = mock_synthesizer.synthesize.call_args
    assert call_args[0][0] == failed_eval
    assert call_args[0][1] == "fluid_prose"

    # Verify critique was injected into prompt on attempt 2
    prompt_attempt_2 = mock_llm.transform.call_args_list[1].kwargs.get("prompt")
    assert "Direcionamento crítico" in prompt_attempt_2.get_last_user_content()


def test_execute_stage_fail_fast_quarantine_protocol() -> None:
    """Verify Fail-Fast with Quarantine executes all 4 protocol actions on exhausted retry failures."""
    settings = DefaultPipelineSettings(judge_blocking=True, judge_max_attempts=2)
    factory = StageFactory(settings=settings)

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
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=mock_metrics,
        llm_judge=mock_judge,
        prompt_provider=NoOpPromptProviderPort(),
        llm_transformation_port=mock_llm,
        stage_factory=factory,
        critique_synthesizer=mock_synthesizer,
        ledger_port=mock_ledger,
    )

    ctx = _create_sample_context()
    raw = SourceTranscript(
        content_id=ctx.content.id,
        channel_name=ChannelName(ctx.channel.name),
        body="Text that repeatedly fails.",
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
        labels={"stage": "fluid_prose", "channel_name": ctx.channel.name},
    )


def test_record_stage_quarantine_requires_content_or_content_id() -> None:
    """Verify record_stage_quarantine raises ValueError when neither content nor content_id is provided."""
    eval_mock = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.2,
        criteria_scores=(),
        provider="test",
    )
    with pytest.raises(
        ValueError,
        match=r"^content or content_id must be provided to record_stage_quarantine$",
    ):
        record_stage_quarantine(
            stage_name="fluid_prose",
            content=None,
            content_id=None,
            evaluation=eval_mock,
            critique="fail",
            effective_max_attempts=2,
            ledger_port=None,
            metrics_port=NoOpMetricsPort(),
        )


def test_record_stage_quarantine_with_channel_and_content_objects_and_span() -> None:
    """Verify record_stage_quarantine with Channel, Content, OpenTelemetry span, and new Ledger entry."""
    eval_mock = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.42,
        criteria_scores=(),
        provider="test",
    )
    ch = Channel(name="TestChannel", id=ChannelId("UC_123"))
    cnt = Content.create(id=ContentId("vid_999"), title="Title 999")
    prov = MediaProvenance(url="https://yt.be/999")
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None
    mock_metrics = MagicMock(spec=NoOpMetricsPort())

    mock_span = MagicMock()
    with (
        patch(
            "cresmo.application.pipeline.quarantine.trace.get_current_span", return_value=mock_span
        ),
        pytest.raises(StageQuarantinedError) as exc_info,
    ):
        record_stage_quarantine(
            stage_name="fluid_prose",
            channel=ch,
            content=cnt,
            provenance=prov,
            evaluation=eval_mock,
            critique="Critical defect",
            effective_max_attempts=3,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
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

    # Verify telemetry span attributes
    mock_span.set_attribute.assert_any_call("quarantined", True)
    mock_span.set_attribute.assert_any_call("quarantine.stage", "fluid_prose")
    mock_span.set_attribute.assert_any_call("quarantine.critique", "Critical defect")
    mock_span.set_attribute.assert_any_call("quarantine.attempts", 3)
    mock_span.set_attribute.assert_any_call("quarantine.overall_score", 0.42)
    mock_span.set_attribute.assert_any_call("cresmo.content.id", "vid_999")
    mock_span.set_attribute.assert_any_call("cresmo.channel.id", "UC_123")
    mock_span.set_attribute.assert_any_call("cresmo.channel.name", "TestChannel")
    mock_span.set_attribute.assert_any_call("cresmo.content.title", "Title 999")

    # Verify metric
    mock_metrics.increment_counter.assert_called_once_with(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": "fluid_prose", "channel_name": "TestChannel"},
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
    cnt = Content.create(id=ContentId("vid_existing"), title="")
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

    mock_span = MagicMock()
    with (
        patch(
            "cresmo.application.pipeline.quarantine.trace.get_current_span", return_value=mock_span
        ),
        pytest.raises(StageQuarantinedError),
    ):
        record_stage_quarantine(
            stage_name="stage_2",
            channel=ch,
            content=cnt,
            evaluation=eval_mock,
            critique="failed check",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=NoOpMetricsPort(),
        )

    mock_ledger.get_entry.assert_called_once_with(ContentId("vid_existing"))
    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.media_url == "https://existing.media.url"
    assert saved.title == "Existing Master Title"
    assert saved.started_at == started_time
    assert saved.status == PipelineStatus.QUARANTINED
    mock_span.set_attribute.assert_any_call("cresmo.channel.id", "OldChannel")


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
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None

    mock_span = MagicMock()
    with (
        patch(
            "cresmo.application.pipeline.quarantine.trace.get_current_span", return_value=mock_span
        ),
        pytest.raises(StageQuarantinedError) as exc_info,
    ):
        record_stage_quarantine(
            stage_name="stage_3",
            channel=None,
            content=cnt,
            channel_name="",
            channel_id="",
            evaluation=eval_mock,
            critique="",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=NoOpMetricsPort(),
        )

    assert exc_info.value.critique == ""
    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.media_url == "https://cresmo.internal/content/vid_fallback"
    assert saved.title == "Quarantined Content vid_fallback"
    assert saved.channel_name == ChannelName("unknown")
    mock_span.set_attribute.assert_any_call("cresmo.channel.name", "")
    mock_span.set_attribute.assert_any_call("cresmo.channel.id", "")
    mock_span.set_attribute.assert_any_call("cresmo.content.title", "vid_fallback")
    mock_span.set_attribute.assert_any_call("quarantine.critique", "")


def test_record_stage_quarantine_legacy_channel_args() -> None:
    """Verify legacy channel_name and channel_id parameter coercion."""
    eval_mock = JudgeEvaluation(
        target_stage="stage_4",
        passed=False,
        overall_score=0.5,
        criteria_scores=(),
        provider="test",
    )
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.return_value = None
    mock_metrics = MagicMock(spec=NoOpMetricsPort())

    # Case 1: channel_name as ChannelName VO, channel_id as ChannelId VO
    with pytest.raises(StageQuarantinedError):
        record_stage_quarantine(
            stage_name="stage_4",
            content_id=ContentId("vid_legacy"),
            channel_name=ChannelName("CustomChan"),
            channel_id=ChannelId("UC_custom"),
            content_title="CustomTitle",
            evaluation=eval_mock,
            critique="crit",
            effective_max_attempts=2,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
        )

    saved = mock_ledger.save_entry.call_args[0][0]
    assert saved.channel_name == ChannelName("CustomChan")
    assert saved.title == "CustomTitle"

    # Case 2: raw strings for channel_name and channel_id, with default content_title
    mock_span = MagicMock()
    with (
        patch(
            "cresmo.application.pipeline.quarantine.trace.get_current_span", return_value=mock_span
        ),
        pytest.raises(StageQuarantinedError),
    ):
        record_stage_quarantine(
            stage_name="stage_4",
            content_id=ContentId("vid_legacy_str"),
            channel_name="RawChan",
            channel_id="raw_id",
            evaluation=eval_mock,
            critique="crit",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
        )

    saved_str = mock_ledger.save_entry.call_args[0][0]
    assert saved_str.channel_name == ChannelName("RawChan")
    assert saved_str.title == "Quarantined Content vid_legacy_str"
    mock_span.set_attribute.assert_any_call("cresmo.channel.name", "RawChan")
    mock_span.set_attribute.assert_any_call("cresmo.channel.id", "raw_id")


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
    cnt = Content.create(id=ContentId("vid_err"), title="T")
    mock_ledger = MagicMock(spec=LedgerRepositoryPort)
    mock_ledger.get_entry.side_effect = RuntimeError("Database locked")
    mock_metrics = MagicMock(spec=NoOpMetricsPort())

    with pytest.raises(StageQuarantinedError) as exc_info:
        record_stage_quarantine(
            stage_name="stage_5",
            channel=ch,
            content=cnt,
            evaluation=eval_mock,
            critique="error test",
            effective_max_attempts=1,
            ledger_port=mock_ledger,
            metrics_port=mock_metrics,
        )

    assert exc_info.value.content_id == "vid_err"
    mock_metrics.increment_counter.assert_called_once()
    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_records) == 1
    assert error_records[0].msg == "Failed to record quarantine entry in ledger for %s: %s"
    assert error_records[0].args == ("vid_err", mock_ledger.get_entry.side_effect)
