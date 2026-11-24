"""Hermetic Unit Tests for CresmoPipeline Orchestrator (coordinator.py).

Conforms to:
    - ADR-007: Pipeline Template Method DRY
    - ADR-021: Unified Pipeline Execution Template Method and Telemetry
    - ADR-031: Quality Gate & Pipeline Execution Context Fabric
    - SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import inspect
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.models import PipelineResult
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    ChannelTaxonomyPort,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpMetricsPort,
    NoOpTelemetryPort,
    PromptProviderPort,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    BatchId,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
)
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


class TestCresmoPipelineInitializationAndProperties:
    """Verifies constructor dependency wiring, defaults, and accessor properties."""

    def test_init_raises_when_vault_port_is_none(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        with pytest.raises(ValueError, match=r"^vault_port must be provided$"):
            CresmoPipeline(
                media_ingestion_port=mock_ingestion,
                vault_port=None,  # type: ignore[arg-type]
                stage_runner=mock_runner,
            )

    def test_init_raises_when_stage_runner_is_none(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)

        with pytest.raises(ValueError, match=r"^stage_runner must be provided$"):
            CresmoPipeline(
                media_ingestion_port=mock_ingestion,
                vault_port=mock_vault,
                stage_runner=None,  # type: ignore[arg-type]
            )

    def test_init_with_direct_stage_runner_uses_provided_and_runner_ports(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_factory = MagicMock(spec=StageFactory)
        mock_llm = MagicMock(spec=LLMTransformationPort)
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_prompt = MagicMock(spec=PromptProviderPort)

        runner = MagicMock(spec=PipelineStageRunner)
        runner.telemetry_port = mock_t
        runner.metrics_port = mock_m
        runner.stage_factory = mock_factory
        runner.llm_transformation_port = mock_llm
        runner.llm_judge = mock_judge
        runner.prompt_provider = mock_prompt

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=runner,
        )

        assert pipeline.media_ingestion_port is mock_ingestion
        assert pipeline.vault_port is mock_vault
        assert pipeline.ingest_raw_transcript.ingestion_port is mock_ingestion
        assert pipeline.ingest_raw_transcript.vault_port is mock_vault
        assert pipeline.stage_runner is runner
        assert pipeline.telemetry_port is mock_t
        assert pipeline.metrics_port is mock_m
        assert pipeline.stage_runner.stage_factory is mock_factory
        assert pipeline.stage_runner.llm_transformation_port is mock_llm
        assert pipeline.stage_runner.llm_judge is mock_judge
        assert pipeline.stage_runner.prompt_provider is mock_prompt
        assert pipeline.llm_indexing_port is mock_llm

    def test_init_with_direct_stage_runner_without_runner_ports_defaults_to_noop(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)

        runner = MagicMock(spec=PipelineStageRunner)
        runner.telemetry_port = None
        runner.metrics_port = None
        runner.llm_transformation_port = None

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=runner,
        )

        assert isinstance(pipeline.telemetry_port, NoOpTelemetryPort)
        assert isinstance(pipeline.metrics_port, NoOpMetricsPort)

    def test_init_with_explicit_override_ports_and_taxonomy(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_llm_index = MagicMock(spec=LLMTransformationPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_taxonomy = MagicMock(spec=ChannelTaxonomyPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        from cresmo.domain.value_objects import StageExecutionPolicy

        stage_policy = StageExecutionPolicy(judge_blocking=True, judge_max_attempts=4)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_indexing_port=mock_llm_index,
            ledger_port=mock_ledger,
            taxonomy_port=mock_taxonomy,
            stage_policy=stage_policy,
        )

        assert pipeline.taxonomy_port is mock_taxonomy
        assert pipeline.telemetry_port is mock_t
        assert pipeline.metrics_port is mock_m
        assert pipeline.llm_indexing_port is mock_llm_index
        assert pipeline.ledger_port is mock_ledger
        assert pipeline.stage_policy is stage_policy


class TestCresmoPipelineWarmup:
    """Verifies warmup propagation to indexing and stage runner transformation ports."""

    def test_warmup_calls_both_ports_when_distinct(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_index_llm = MagicMock(spec=LLMTransformationPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_synth_llm = MagicMock(spec=LLMTransformationPort)
        mock_runner.llm_transformation_port = mock_synth_llm

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            llm_indexing_port=mock_index_llm,
        )

        pipeline.warmup(timeout_seconds=5.0)

        mock_index_llm.warmup.assert_called_once_with(timeout_seconds=5.0)
        mock_runner.warmup.assert_called_once_with(timeout_seconds=5.0)

    def test_warmup_calls_runner_only_once_when_ports_are_identical(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_shared_llm = MagicMock(spec=LLMTransformationPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.llm_transformation_port = mock_shared_llm

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            llm_indexing_port=mock_shared_llm,
        )

        pipeline.warmup(timeout_seconds=2.5)

        mock_shared_llm.warmup.assert_called_once_with(timeout_seconds=2.5)
        mock_runner.warmup.assert_not_called()

    def test_warmup_handles_none_ports_gracefully(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.llm_transformation_port = None

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            llm_indexing_port=None,
        )

        pipeline.warmup(timeout_seconds=1.0)
        mock_runner.warmup.assert_not_called()


class TestCresmoPipelineExecutionAndIdempotency:
    """Verifies pipeline execution lifecycle, root telemetry metadata, and idempotency checks."""

    @pytest.fixture
    def sample_source_transcript(self) -> StageTranscript:
        return StageTranscript(
            channel=Channel(name="Economics & Society", id=ChannelId("UC_econ101")),
            provenance=MediaProvenance(
                url="https://youtube.com/watch?v=1234567",
                description="Lecture video",
                publication_date=datetime(2024, 5, 20, 10, 30, tzinfo=UTC),
            ),
            content=Content(
                id=ContentId("c1234567"),
                title="Vilfredo Pareto and Circulation of Elites",
                text="Raw spoken audio transcript discussing Pareto optimal states and elite rotation.",
            ),
        )

    def test_execute_happy_path_produces_full_result_and_telemetry(
        self, sample_source_transcript: StageTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock(spec=MetricsPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        fluid_res = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=ContentId("c1234567"),
                title="Polished Fluid Title",
                text="Synthesized fluid prose text.",
            ),
        )
        gaps_res = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=ContentId("c1234567"),
                title="Polished Pareto Essay",
                text="Synthesized Pareto prose text with higher conceptual density and no verbal noise.",
            ),
        )
        long_res = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=ContentId("c1234567"),
                title="Polished Pareto Essay",
                text=(
                    "Multi-secular Pareto prose anchoring elite circulation across fiscal and "
                    "institutional regimes.\n\n### Extra Info\n\n1. Historical archive note."
                ),
            ),
        )
        wide_res = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=ContentId("c1234567"),
                title="Polished Pareto Essay",
                text=(
                    "Synchronic global networks and parallel imperial fiscal adaptations compared "
                    "across connected monetary zones.\n\n### Extra Info\n\n1. Global silver note."
                ),
            ),
        )

        mock_runner.execute_stage.side_effect = [fluid_res, gaps_res, long_res, wide_res]

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        user = UserIdentity.worker()
        batch = BatchId.generate()

        res = pipeline.execute(
            sample_source_transcript,
            expansion_max_passes=3,
            force_reprocess=False,
            user=user,
            batch_id=batch,
        )

        assert res.success is True
        assert res.content_id == ContentId("c1234567")
        assert res.source_transcript is sample_source_transcript
        assert res.stage_artifacts[StageName.FLUID_PROSE] is fluid_res
        assert res.stage_artifacts[StageName.GAP_FILLER] is gaps_res
        assert res.stage_artifacts[StageName.LONG_EXPANDER] is long_res
        assert res.stage_artifacts[StageName.WIDE_EXPANDER] is wide_res
        assert res.final_transcript is wide_res

        # Verify stage transcripts saved with exact stage identifiers
        assert mock_vault.save_stage_transcript.call_count == 4
        assert mock_vault.save_stage_transcript.call_args_list[0].args == (
            StageName.FLUID_PROSE,
            fluid_res,
        )
        assert mock_vault.save_stage_transcript.call_args_list[1].args == (
            StageName.GAP_FILLER,
            gaps_res,
        )
        assert mock_vault.save_stage_transcript.call_args_list[2].args == (
            StageName.LONG_EXPANDER,
            long_res,
        )
        assert mock_vault.save_stage_transcript.call_args_list[3].args == (
            StageName.WIDE_EXPANDER,
            wide_res,
        )

        # Verify SessionTelemetrySpec passed to start_session
        assert len(telemetry.spans) == 1
        root_span = telemetry.spans[0]
        assert root_span.is_root is True
        spec = root_span.session_spec
        assert spec is not None
        assert spec.user_id == user
        assert spec.channel_tenant_id == sample_source_transcript.channel.tenant_key
        assert spec.trace_name == "cresmo.pipeline"
        assert spec.source == "transcript"
        assert spec.channel_id == "UC_econ101"
        assert spec.channel_name == "Economics & Society"
        assert spec.content_id == "c1234567"
        assert spec.content_title == "Vilfredo Pareto and Circulation of Elites"
        assert spec.raw_characters == len(sample_source_transcript.content.text)
        assert spec.raw_words == len(sample_source_transcript.content.text.split())
        assert spec.expansion_max_passes == 3
        assert spec.force_reprocess is False
        assert spec.batch_id == batch.value
        assert spec.video_url == "https://youtube.com/watch?v=1234567"
        assert spec.publication_date == "2024-05-20"

        # Verify execute_stage calls for conveyor pipeline
        # (fluid_prose, gap_filler, long_expander, wide_expander)
        assert mock_runner.execute_stage.call_count == 4
        first_call = mock_runner.execute_stage.call_args_list[0]
        assert first_call[0][0] == "fluid_prose"
        assert first_call[1]["source"] is sample_source_transcript
        assert first_call[1]["context"].content.id == ContentId("c1234567")
        assert first_call[1]["context"].user_identity == user

        second_call = mock_runner.execute_stage.call_args_list[1]
        assert second_call[0][0] == "gap_filler"
        assert second_call[1]["source"] is fluid_res
        assert second_call[1]["context"].content.id == ContentId("c1234567")
        assert second_call[1]["max_passes"] == 3

        third_call = mock_runner.execute_stage.call_args_list[2]
        assert third_call[0][0] == "long_expander"
        assert third_call[1]["source"] is gaps_res
        assert third_call[1]["context"].content.id == ContentId("c1234567")
        assert third_call[1]["max_passes"] == 3

        fourth_call = mock_runner.execute_stage.call_args_list[3]
        assert fourth_call[0][0] == "wide_expander"
        assert fourth_call[1]["source"] is long_res
        assert fourth_call[1]["context"].content.id == ContentId("c1234567")
        assert fourth_call[1]["max_passes"] == 3

        # Verify root_span.set_output with all canonical fields
        assert len(root_span.outputs) == 1
        output_payload = root_span.outputs[0]
        assert output_payload["status"] == "COMPLETED"
        assert output_payload["stage"] == "wide_expander"
        assert output_payload["stages_completed"] == [
            "fluid_prose",
            "gap_filler",
            "long_expander",
            "wide_expander",
        ]
        assert output_payload["content_title"] == "Polished Pareto Essay"
        raw_words = len(sample_source_transcript.content.text.split())
        synth_words = len(wide_res.content.text.split())
        assert output_payload["word_count"] == synth_words
        assert output_payload["char_count"] == len(wide_res.content.text)
        assert output_payload["source_words"] == raw_words
        assert output_payload["synthesized_words"] == synth_words
        assert output_payload["expansion_ratio"] == round(synth_words / max(raw_words, 1), 3)
        assert output_payload["source_characters"] == len(sample_source_transcript.content.text)
        assert output_payload["synthesized_characters"] == len(wide_res.content.text)
        assert output_payload["stages_reused_from_cache"] == []
        assert output_payload["cache_hit_count"] == 0
        assert output_payload["cache_hit_ratio"] == 0.0
        assert output_payload["force_reprocess"] is False
        assert output_payload["expansion_max_passes"] == 3

    def test_execute_records_stage_cache_hit_insights(
        self,
        sample_source_transcript: StageTranscript,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify ADR-063 session output tracks cached stages and cache_hit_ratio."""
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        telemetry = InMemoryTelemetryPort()
        mock_runner = MagicMock(spec=PipelineStageRunner)

        cached_fluid = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=sample_source_transcript.content.id,
                title="Cached Fluid",
                text="Cached fluid prose body.",
            ),
        )
        fresh_gaps = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=sample_source_transcript.content.id,
                title="Fresh Gaps",
                text="Expanded fresh gap filler prose body with deeper analysis.",
            ),
        )
        fresh_long = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=sample_source_transcript.content.id,
                title="Fresh Long",
                text="Multi-secular longitudinal expansion.\n\n### Extra Info\n\n1. Archival note.",
            ),
        )
        fresh_wide = StageTranscript(
            channel=sample_source_transcript.channel,
            provenance=sample_source_transcript.provenance,
            content=Content(
                id=sample_source_transcript.content.id,
                title="Fresh Wide",
                text="Synchronic horizontal expansion.\n\n### Extra Info\n\n1. Comparative note.",
            ),
        )
        mock_vault.get_stage_transcript.side_effect = [cached_fluid, None, None, None]
        mock_runner.execute_stage.side_effect = [fresh_gaps, fresh_long, fresh_wide]

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            telemetry_port=telemetry,
            stage_runner=mock_runner,
        )
        with caplog.at_level("INFO"):
            res = pipeline.execute(
                sample_source_transcript, expansion_max_passes=2, force_reprocess=False
            )

        assert res.success is True
        assert any(
            record.getMessage() == "Reusing cached fluid_prose for content_id 'c1234567'"
            for record in caplog.records
        )
        output_payload = telemetry.spans[0].outputs[0]
        assert output_payload["stages_reused_from_cache"] == ["fluid_prose"]
        assert output_payload["cache_hit_count"] == 1
        assert output_payload["cache_hit_ratio"] == round(1 / 4, 3)
        assert output_payload["force_reprocess"] is False
        assert output_payload["expansion_max_passes"] == 2

    def test_execute_with_minimal_metadata_and_defaults(self) -> None:
        raw_bare = StageTranscript(
            channel=Channel(name="BareChannel", id=None),
            provenance=MediaProvenance(url="", description=""),
            content=Content(
                id=ContentId("c999"),
                title="Bare Title",
                text="Raw bare text without provenance",
            ),
        )

        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        telemetry = InMemoryTelemetryPort()
        mock_runner = MagicMock(spec=PipelineStageRunner)

        class BareFluid:
            text = "Bare fluid output"

        mock_runner.execute_stage.return_value = BareFluid()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=telemetry,
        )

        res = pipeline.execute(raw_bare, user=None, batch_id="  str_batch_id  ")
        assert res.success is True

        spec = telemetry.spans[0].session_spec
        assert spec is not None
        assert spec.user_id == UserIdentity.anonymous()
        assert spec.channel_id == ""
        assert spec.expansion_max_passes is None
        assert spec.batch_id == "str_batch_id"
        assert "max_passes" not in mock_runner.execute_stage.call_args_list[-1].kwargs
        assert spec.video_url is None
        assert spec.publication_date is None

    def test_execute_expansion_ratio_when_source_has_single_word(self) -> None:
        raw_one_word = StageTranscript(
            channel=Channel(name=ChannelName("OneWord")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=ContentId("c1word"), title="T", text="Word"),
        )
        mock_runner = MagicMock(spec=PipelineStageRunner)

        multi_word = StageTranscript(
            channel=raw_one_word.channel,
            provenance=raw_one_word.provenance,
            content=Content(
                id=ContentId("c1word"),
                title="T",
                text="One two three four five six seven eight nine ten",
            ),
        )

        mock_runner.execute_stage.return_value = multi_word
        telemetry = InMemoryTelemetryPort()

        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=mock_runner,
            telemetry_port=telemetry,
        )

        pipeline.execute(raw_one_word)
        payload = telemetry.spans[0].outputs[0]
        # 10 synth words / max(1 raw word, 1) == 10.0
        assert payload["expansion_ratio"] == 10.0

    def test_execute_fluid_without_title_falls_back_to_content_title(self) -> None:
        raw = StageTranscript(
            channel=Channel(name=ChannelName("TitleChan")),
            provenance=MediaProvenance.create(url=""),
            content=Content(
                id=ContentId("c_fallback_title"),
                title="Original Content Title",
                text="Some raw body text.",
            ),
        )
        mock_runner = MagicMock(spec=PipelineStageRunner)

        fluid_obj = StageTranscript(
            channel=raw.channel,
            provenance=raw.provenance,
            content=Content(
                id=raw.content.id,
                title="",
                text="Synthesized body text without title attribute.",
            ),
        )

        mock_runner.execute_stage.return_value = fluid_obj
        telemetry = InMemoryTelemetryPort()

        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=mock_runner,
            telemetry_port=telemetry,
        )

        pipeline.execute(raw)
        payload = telemetry.spans[0].outputs[0]
        assert payload["content_title"] == "Original Content Title"

    def test_execute_title_and_synthesized_text_fallback_precedence(self) -> None:
        """Verify root output title and text fall back from gaps -> fluid -> raw -> empty string."""
        raw = StageTranscript(
            channel=Channel(name=ChannelName("PrecedenceChan")),
            provenance=MediaProvenance.create(url=""),
            content=Content(
                id=ContentId("c_prec_01"),
                title="Raw Title",
                text="Raw body words.",
            ),
        )
        fluid = StageTranscript(
            channel=raw.channel,
            provenance=raw.provenance,
            content=Content(
                id=raw.content.id,
                title="Fluid Title Only",
                text="Fluid synthesized body text.",
            ),
        )

        class BareGaps:
            pass

        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.side_effect = [fluid, BareGaps(), BareGaps(), BareGaps()]
        telemetry = InMemoryTelemetryPort()
        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=mock_runner,
            telemetry_port=telemetry,
        )

        pipeline.execute(raw, force_reprocess=True)
        payload = telemetry.spans[0].outputs[0]
        assert payload["content_title"] == "Fluid Title Only"
        assert payload["synthesized_characters"] == len("Fluid synthesized body text.")
        assert payload["synthesized_words"] == 4

        raw_untitled = StageTranscript(
            channel=Channel(name=ChannelName("PrecedenceChan")),
            provenance=MediaProvenance.create(url=""),
            content=Content(
                id=ContentId("c_prec_02"),
                title="",
                text="Raw untitled text.",
            ),
        )
        mock_runner.execute_stage.side_effect = [BareGaps(), BareGaps(), BareGaps(), BareGaps()]
        pipeline.execute(raw_untitled, force_reprocess=True)
        untitled_payload = telemetry.spans[1].outputs[0]
        assert isinstance(untitled_payload, dict)
        assert untitled_payload["content_title"] == ""
        assert untitled_payload["synthesized_characters"] == 0
        assert untitled_payload["synthesized_words"] == 0

    def test_execute_idempotent_skip_when_in_ledger_and_not_force_reprocess(
        self, sample_source_transcript: StageTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_ledger.is_processed.return_value = True

        telemetry = InMemoryTelemetryPort()
        mock_m = MagicMock(spec=MetricsPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        fluid_mock = MagicMock(spec=StageTranscript)
        gaps_mock = MagicMock(spec=StageTranscript)
        long_mock = MagicMock(spec=StageTranscript)
        wide_mock = MagicMock(spec=StageTranscript)
        mock_vault.get_stage_transcript.side_effect = [
            fluid_mock,
            gaps_mock,
            long_mock,
            wide_mock,
        ]
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            ledger_port=mock_ledger,
            telemetry_port=telemetry,
            metrics_port=mock_m,
        )

        res = pipeline.execute(sample_source_transcript, force_reprocess=False)

        assert res.already_processed is True
        assert res.success is True
        assert res.content_id == sample_source_transcript.content.id
        assert res.source_transcript is sample_source_transcript
        assert res.stage_artifacts[StageName.FLUID_PROSE] is fluid_mock
        assert res.stage_artifacts[StageName.GAP_FILLER] is gaps_mock
        assert res.stage_artifacts[StageName.LONG_EXPANDER] is long_mock
        assert res.stage_artifacts[StageName.WIDE_EXPANDER] is wide_mock
        assert res.final_transcript is wide_mock
        assert res.synthesized_notes == ()
        assert res.reconciled_mocs == ()
        assert isinstance(res.synthesized_notes, tuple)
        assert isinstance(res.reconciled_mocs, tuple)
        mock_runner.execute_stage.assert_not_called()
        assert mock_vault.get_stage_transcript.call_count == 4
        mock_vault.get_stage_transcript.assert_any_call(
            StageName.FLUID_PROSE, sample_source_transcript.content.id
        )
        mock_vault.get_stage_transcript.assert_any_call(
            StageName.GAP_FILLER, sample_source_transcript.content.id
        )
        mock_vault.get_stage_transcript.assert_any_call(
            StageName.LONG_EXPANDER, sample_source_transcript.content.id
        )
        mock_vault.get_stage_transcript.assert_any_call(
            StageName.WIDE_EXPANDER, sample_source_transcript.content.id
        )

        assert telemetry.spans[0].outputs == [
            {
                "status": "SKIPPED_IDEMPOTENT",
                "reason": "Existing content already processed",
                "content_id": "c1234567",
            }
        ]
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": "UC_econ101",
                "status": "skipped_idempotent",
                "modality": "transcript",
            },
        )

    def test_execute_idempotent_skip_when_channel_id_is_none(self) -> None:
        raw_no_chid = StageTranscript(
            channel=Channel(name="NoChIdChan", id=None),
            provenance=MediaProvenance.create(url=""),
            content=Content(
                id=ContentId("c_no_chid"), title="T", text="Text for no chid transcript"
            ),
        )
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_ledger.is_processed.return_value = True
        mock_m = MagicMock(spec=MetricsPort)

        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=MagicMock(spec=PipelineStageRunner),
            ledger_port=mock_ledger,
            metrics_port=mock_m,
        )

        res = pipeline.execute(raw_no_chid)
        assert res.already_processed is True
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": "",
                "status": "skipped_idempotent",
                "modality": "transcript",
            },
        )

    def test_execute_bypasses_idempotent_skip_when_force_reprocess_is_true(
        self, sample_source_transcript: StageTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_ledger.is_processed.return_value = True

        mock_t = MagicMock(spec=TelemetryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.return_value = MagicMock(text="New fluid body")

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            ledger_port=mock_ledger,
            telemetry_port=mock_t,
        )

        res = pipeline.execute(sample_source_transcript, force_reprocess=True)
        assert res.already_processed is False
        assert res.success is True
        assert mock_runner.execute_stage.call_count == 4

    def test_execute_stage_failure_propagates_exception(
        self, sample_source_transcript: StageTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.side_effect = RuntimeError("Stage execution died")

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=mock_t,
        )

        with pytest.raises(RuntimeError, match="Stage execution died"):
            pipeline.execute(sample_source_transcript)

    def test_default_parameter_signatures_and_contracts(self) -> None:
        sig_exec = inspect.signature(CresmoPipeline.execute)
        assert sig_exec.parameters["expansion_max_passes"].default is None
        assert sig_exec.parameters["force_reprocess"].default is False

        sig_vid = inspect.signature(CresmoPipeline.run_for_video)
        assert sig_vid.parameters["expansion_max_passes"].default is None
        assert sig_vid.parameters["force_reprocess"].default is False

        sig_file = inspect.signature(CresmoPipeline.run_for_text_file)
        assert sig_file.parameters["expansion_max_passes"].default is None
        assert sig_file.parameters["force_reprocess"].default is False


class TestCresmoPipelineRunForSources:
    """Verifies run_for_video and run_for_text_file wrappers."""

    def test_run_for_video_success(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        sample_raw = MagicMock(spec=StageTranscript)
        sample_raw.content = Content(
            id=ContentId("v123"), title="Vid Title", text="Transcript text"
        )
        sample_raw.channel = Channel(name="ChanVid", id=None)
        sample_raw.provenance = MediaProvenance(
            url="https://youtube.com/watch?v=v123", description=""
        )

        pipeline.ingest_raw_transcript.execute = MagicMock(return_value=sample_raw)

        with (
            patch.object(pipeline, "warmup") as mock_warmup,
            patch.object(pipeline, "execute", return_value=MagicMock(success=True)) as mock_exec,
        ):
            res = pipeline.run_for_video(
                video_url="https://youtube.com/watch?v=v123",
                expansion_max_passes=2,
                force_reprocess=True,
                user=UserIdentity.worker(),
                batch_id="batch_vid",
            )
            mock_warmup.assert_called_once()
            pipeline.ingest_raw_transcript.execute.assert_called_once_with(
                video_url="https://youtube.com/watch?v=v123"
            )
            mock_exec.assert_called_once_with(
                raw=sample_raw,
                expansion_max_passes=2,
                force_reprocess=True,
                user=UserIdentity.worker(),
                batch_id="batch_vid",
            )
            assert res == mock_exec.return_value

    def test_run_for_video_default_parameters(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        sample_raw = MagicMock(spec=StageTranscript)
        pipeline.ingest_raw_transcript.execute = MagicMock(return_value=sample_raw)

        with (
            patch.object(pipeline, "warmup") as mock_warmup,
            patch.object(pipeline, "execute", return_value=MagicMock(success=True)) as mock_exec,
        ):
            pipeline.run_for_video("https://youtube.com/watch?v=defaults")
            mock_warmup.assert_called_once()
            mock_exec.assert_called_once_with(
                raw=sample_raw,
                expansion_max_passes=None,
                force_reprocess=False,
                user=None,
                batch_id=None,
            )

    def test_run_for_video_ingestion_failure_raises_domain_error(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )
        pipeline.ingest_raw_transcript.execute = MagicMock(return_value=None)

        with pytest.raises(
            CresmoDomainError,
            match=r"^Ingestion failed to retrieve transcript for: https://youtube\.com/watch\?v=fail$",
        ):
            pipeline.run_for_video("https://youtube.com/watch?v=fail")

    def test_run_for_text_file_rejects_internal_system_artifacts(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        invalid_path = Path("/vault/_index.json")
        with pytest.raises(
            CresmoDomainError,
            match=r"^File '_index\.json' is an internal Cresmo artifact or system index and cannot be processed as a transcript\.$",
        ):
            pipeline.run_for_text_file(invalid_path)

    def test_run_for_text_file_success(self, tmp_path: Path) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        file_path = tmp_path / "valid_transcript.md"
        file_path.write_text("Hello transcript text body", encoding="utf-8")

        mock_raw = MagicMock(spec=StageTranscript)
        mock_result = MagicMock(spec=PipelineResult)

        with (
            patch(
                "cresmo.application.pipeline.coordinator.load_transcript_from_file",
                return_value=mock_raw,
            ) as mock_load,
            patch(
                "cresmo.application.pipeline.coordinator.ensure_transcript_saved",
            ) as mock_ensure,
            patch.object(pipeline, "warmup") as mock_warmup,
            patch.object(pipeline, "execute", return_value=mock_result) as mock_exec,
        ):
            user = UserIdentity.worker()
            res = pipeline.run_for_text_file(
                file_path=file_path,
                expansion_max_passes=3,
                force_reprocess=False,
                user=user,
                batch_id="text_batch",
            )
            mock_warmup.assert_called_once()
            mock_load.assert_called_once_with(file_path, taxonomy_port=pipeline.taxonomy_port)
            mock_ensure.assert_called_once_with(
                mock_vault,
                file_path,
                mock_raw,
                target_dir=mock_vault.resolve_stage_dir.return_value,
            )
            mock_exec.assert_called_once_with(
                raw=mock_raw,
                expansion_max_passes=3,
                force_reprocess=False,
                user=user,
                batch_id="text_batch",
            )
            assert res == mock_result

    def test_run_for_text_file_default_parameters(self, tmp_path: Path) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        file_path = tmp_path / "defaults.md"
        file_path.write_text("Default file body", encoding="utf-8")
        mock_raw = MagicMock(spec=StageTranscript)

        with (
            patch(
                "cresmo.application.pipeline.coordinator.load_transcript_from_file",
                return_value=mock_raw,
            ),
            patch("cresmo.application.pipeline.coordinator.ensure_transcript_saved"),
            patch.object(pipeline, "warmup"),
            patch.object(pipeline, "execute", return_value=MagicMock(success=True)) as mock_exec,
        ):
            pipeline.run_for_text_file(file_path=file_path)
            mock_exec.assert_called_once_with(
                raw=mock_raw,
                expansion_max_passes=None,
                force_reprocess=False,
                user=None,
                batch_id=None,
            )

    def test_pipeline_fluid_prose_checkpoint_skips_stage_runner(self) -> None:
        """Verify pipeline reuses all cached StageTranscripts when force_reprocess is False per ADR-043."""
        cid = ContentId("vid_cached_fluid")
        raw = StageTranscript(
            channel=Channel(name=ChannelName("Channel Test")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=cid, title="T", text="Verbatim spoken text."),
        )
        cached_fluid = StageTranscript(
            channel=Channel(name=ChannelName("Channel Test")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=cid, title="T", text="## Cached Detranscribed Prose"),
        )
        cached_gaps = MagicMock(spec=StageTranscript)
        cached_long = MagicMock(spec=StageTranscript)
        cached_wide = MagicMock(spec=StageTranscript)
        stage_cache = {
            "fluid_prose": cached_fluid,
            "gap_filler": cached_gaps,
            "long_expander": cached_long,
            "wide_expander": cached_wide,
        }
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_vault.get_stage_transcript.side_effect = lambda stage, _cid: stage_cache.get(stage)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        result = pipeline.execute(raw, force_reprocess=False)

        assert result.success is True
        assert result.stage_artifacts[StageName.FLUID_PROSE] == cached_fluid
        assert result.stage_artifacts[StageName.GAP_FILLER] == cached_gaps
        assert result.stage_artifacts[StageName.LONG_EXPANDER] == cached_long
        assert result.final_transcript == cached_wide
        mock_runner.execute_stage.assert_not_called()

    def test_pipeline_cached_fluid_only_executes_expansion_stages(self) -> None:
        """Verify pipeline reuses cached fluid and runs gap_filler, long_expander, wide_expander sequentially."""
        cid = ContentId("vid_cached_fluid_only")
        raw = StageTranscript(
            channel=Channel(name=ChannelName("Channel Test")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=cid, title="T", text="Verbatim spoken text."),
        )
        cached_fluid = StageTranscript(
            channel=Channel(name=ChannelName("Channel Test")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=cid, title="T", text="## Cached Detranscribed Prose"),
        )
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_vault.get_stage_transcript.side_effect = lambda stage, cid: (
            cached_fluid if stage == "fluid_prose" else None
        )
        gaps_out = MagicMock(spec=StageTranscript)
        long_out = MagicMock(spec=StageTranscript)
        wide_out = MagicMock(spec=StageTranscript)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.side_effect = [gaps_out, long_out, wide_out]

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        result = pipeline.execute(raw, force_reprocess=False)

        assert result.success is True
        assert result.stage_artifacts[StageName.FLUID_PROSE] == cached_fluid
        assert result.stage_artifacts[StageName.GAP_FILLER] is gaps_out
        assert result.stage_artifacts[StageName.LONG_EXPANDER] is long_out
        assert result.final_transcript is wide_out
        assert mock_runner.execute_stage.call_count == 3
        first_call = mock_runner.execute_stage.call_args_list[0]
        assert first_call[0][0] == "gap_filler"
        assert first_call[1]["source"] == cached_fluid
        second_call = mock_runner.execute_stage.call_args_list[1]
        assert second_call[0][0] == "long_expander"
        assert second_call[1]["source"] is gaps_out
        third_call = mock_runner.execute_stage.call_args_list[2]
        assert third_call[0][0] == "wide_expander"
        assert third_call[1]["source"] is long_out

    def test_execute_flushes_telemetry_after_root_session_span_closes(self) -> None:
        """Verify CresmoPipeline.execute flushes closed root session span cleanly on success and failure."""
        cid = ContentId("vid_root_flush")
        raw = StageTranscript(
            channel=Channel(name=ChannelName("Channel Test")),
            provenance=MediaProvenance.create(url=""),
            content=Content(id=cid, title="T", text="Verbatim spoken text."),
        )
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_vault.get_stage_transcript.return_value = None
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.return_value = MagicMock(text="Stage output")
        telemetry = InMemoryTelemetryPort()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=telemetry,
        )

        result = pipeline.execute(raw, force_reprocess=True)
        assert result.success is True
        assert telemetry.spans[0].session_spec is not None
        assert telemetry.spans[0].session_spec.force_reprocess is True
        assert telemetry.spans[0].session_spec.batch_id is None
        assert telemetry.lifecycle_events == [
            "session_enter:cresmo.pipeline",
            "session_exit:cresmo.pipeline",
            "flush",
        ]

        telemetry.lifecycle_events.clear()
        mock_runner.execute_stage.side_effect = RuntimeError("pipeline boom")
        with pytest.raises(RuntimeError, match="pipeline boom"):
            pipeline.execute(raw, force_reprocess=True)
        assert telemetry.lifecycle_events == [
            "session_enter:cresmo.pipeline",
            "session_exit:cresmo.pipeline",
            "flush",
        ]
