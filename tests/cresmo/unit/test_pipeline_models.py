"""Hermetic Unit Tests for Pipeline Models Parameter Objects and Aggregates.

Conforms to:
    - ADR-026: Rule 7 (Parameter Objects for Cross-Cutting Execution)
    - SPEC-013: Pipeline Result & Dependencies Contracts
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.models import (
    PipelineDependencies,
    PipelineResult,
    StageExecutionOptions,
)
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MetricsPort,
    PromptProviderPort,
    TelemetryPort,
)
from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    FluidTranscript,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ChannelId,
    ChannelName,
    ContentId,
    RawIndexEntry,
)


class TestPipelineDependencies:
    """Test suite for PipelineDependencies parameter object."""

    def test_default_values(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)

        deps = PipelineDependencies(telemetry_port=mock_t, metrics_port=mock_m)

        assert deps.telemetry_port is mock_t
        assert deps.metrics_port is mock_m
        assert deps.llm_judge is None
        assert deps.judge_blocking is False
        assert deps.judge_max_attempts == 1
        assert deps.prompt_provider is None
        assert deps.llm_transformation_port is None
        assert deps.stage_factory is None
        assert deps.critique_synthesizer is None
        assert deps.ledger_port is None

    def test_custom_values_and_immutability(self) -> None:
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_pp = MagicMock(spec=PromptProviderPort)
        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_factory = MagicMock()
        mock_synth = MagicMock(spec=CritiqueSynthesizerPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)

        deps = PipelineDependencies(
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_judge=mock_judge,
            judge_blocking=True,
            judge_max_attempts=3,
            prompt_provider=mock_pp,
            llm_transformation_port=mock_llm,
            stage_factory=mock_factory,
            critique_synthesizer=mock_synth,
            ledger_port=mock_ledger,
        )

        assert deps.judge_blocking is True
        assert deps.judge_max_attempts == 3
        assert deps.llm_judge is mock_judge
        assert deps.prompt_provider is mock_pp
        assert deps.llm_transformation_port is mock_llm
        assert deps.stage_factory is mock_factory
        assert deps.critique_synthesizer is mock_synth
        assert deps.ledger_port is mock_ledger

        with pytest.raises(FrozenInstanceError):
            deps.judge_blocking = False  # type: ignore[misc]


class TestStageExecutionOptions:
    """Test suite for StageExecutionOptions parameter object."""

    def test_default_values(self) -> None:
        opts = StageExecutionOptions()

        assert opts.channel_name is None
        assert opts.content_id is None
        assert opts.channel_id is None
        assert opts.session_id is None
        assert opts.user_id is None
        assert opts.fatal is True
        assert opts.fallback is None

    def test_custom_values_and_immutability(self) -> None:
        opts = StageExecutionOptions(
            channel_name=ChannelName("Ch1"),
            content_id=ContentId("c1234567"),
            channel_id=ChannelId("UC_abc"),
            session_id="sess_42",
            user_id="user_admin",
            fatal=False,
            fallback="fallback_value",
        )

        assert opts.channel_name == ChannelName("Ch1")
        assert opts.content_id == ContentId("c1234567")
        assert opts.channel_id == ChannelId("UC_abc")
        assert opts.session_id == "sess_42"
        assert opts.user_id == "user_admin"
        assert opts.fatal is False
        assert opts.fallback == "fallback_value"

        with pytest.raises(FrozenInstanceError):
            opts.fatal = True  # type: ignore[misc]


class TestPipelineResult:
    """Test suite for PipelineResult aggregate."""

    def test_default_values(self) -> None:
        cid = ContentId("c1234567")
        res = PipelineResult(content_id=cid, success=True)

        assert res.content_id == cid
        assert res.success is True
        assert res.synthesized_notes == ()
        assert res.reconciled_mocs == ()
        assert res.source_transcript is None
        assert res.fluid_transcript is None
        assert res.index_entry is None
        assert res.compendium is None
        assert res.inventory is None
        assert res.dedup_report is None
        assert res.duplicates_unified == 0
        assert res.already_processed is False
        assert res.error_message is None

    def test_custom_values_and_immutability(self) -> None:
        cid = ContentId("c1234567")
        mock_note = MagicMock(spec=AtomicNote)
        mock_moc = MagicMock(spec=MapOfContent)
        mock_source = MagicMock(spec=SourceTranscript)
        mock_fluid = MagicMock(spec=FluidTranscript)
        mock_idx = MagicMock(spec=RawIndexEntry)
        mock_compendium = MagicMock(spec=EnrichedCompendium)
        mock_inventory = MagicMock(spec=AtomicEntityInventory)
        mock_dedup = MagicMock(spec=DeduplicationReport)

        res = PipelineResult(
            content_id=cid,
            success=False,
            synthesized_notes=(mock_note,),
            reconciled_mocs=(mock_moc,),
            source_transcript=mock_source,
            fluid_transcript=mock_fluid,
            index_entry=mock_idx,
            compendium=mock_compendium,
            inventory=mock_inventory,
            dedup_report=mock_dedup,
            duplicates_unified=5,
            already_processed=True,
            error_message="Stage timeout",
        )

        assert res.success is False
        assert res.synthesized_notes == (mock_note,)
        assert res.reconciled_mocs == (mock_moc,)
        assert res.source_transcript is mock_source
        assert res.fluid_transcript is mock_fluid
        assert res.index_entry is mock_idx
        assert res.compendium is mock_compendium
        assert res.inventory is mock_inventory
        assert res.dedup_report is mock_dedup
        assert res.duplicates_unified == 5
        assert res.already_processed is True
        assert res.error_message == "Stage timeout"

        with pytest.raises(FrozenInstanceError):
            res.success = True  # type: ignore[misc]
