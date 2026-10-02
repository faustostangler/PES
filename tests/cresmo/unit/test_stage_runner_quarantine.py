"""Unit tests for PipelineStageRunner Closed-Loop Reflexion and Fail-Fast Quarantine (ADR-031)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
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
    ChannelId,
    ChannelName,
    ContentId,
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
    PipelineStatus,
)


def _create_sample_context() -> PipelineExecutionContext:
    return PipelineExecutionContext(
        session_id=PipelineSessionId("test_chan:content_123"),
        user_identity=UserIdentity.worker(),
        channel_name=ChannelName("Test Channel"),
        content_id=ContentId("content_123"),
        channel_id=ChannelId("UC_test"),
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
        content_id=ctx.content_id,
        channel_name=ctx.channel_name,
        body="Original source transcript.",
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content_id == ctx.content_id
    assert "Transformed text output." in result.body
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
        content_id=ctx.content_id,
        channel_name=ctx.channel_name,
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
        content_id=ctx.content_id,
        channel_name=ctx.channel_name,
        body="Verbatim transcript with hesitation.",
    )

    result = runner.execute_stage("fluid_prose", source=raw, context=ctx)
    assert result.content_id == ctx.content_id
    assert "Refined candidate text." in result.body

    # Verify synthesizer was called with the failed evaluation
    assert mock_synthesizer.synthesize.call_count == 1
    call_args = mock_synthesizer.synthesize.call_args
    assert call_args[0][0] == failed_eval
    assert call_args[0][1] == "fluid_prose"

    # Verify critique was injected into prompt on attempt 2
    prompt_attempt_2 = mock_llm.transform.call_args_list[1].kwargs.get("prompt")
    assert "Direcionamento crítico" in prompt_attempt_2


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
        content_id=ctx.content_id,
        channel_name=ctx.channel_name,
        body="Text that repeatedly fails.",
    )

    with pytest.raises(StageQuarantinedError) as exc_info:
        runner.execute_stage("fluid_prose", source=raw, context=ctx)

    # 1. Check StageQuarantinedError properties
    err = exc_info.value
    assert err.stage_name == "fluid_prose"
    assert err.content_id == ctx.content_id.value
    assert err.attempts == 2
    assert "Crítica direcionada irrevogável" in err.critique
    assert err.overall_score == 0.35

    # 2. Check SQLite Ledger Quarantine record
    assert mock_ledger.save_entry.call_count == 1
    saved_entry = mock_ledger.save_entry.call_args[0][0]
    assert saved_entry.content_id == ctx.content_id
    assert saved_entry.channel_name == ctx.channel_name
    assert saved_entry.status == PipelineStatus.QUARANTINED
    assert "Stage 'fluid_prose' quarantined" in saved_entry.error_message

    # 3. Check Prometheus metric incremented
    mock_metrics.increment_counter.assert_any_call(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": "fluid_prose", "channel_name": ctx.channel_name.value},
    )
