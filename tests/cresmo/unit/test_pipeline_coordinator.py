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

from cresmo.application.pipeline import (
    CresmoPipeline,
    PipelineResult,
    PipelineStageRunner,
)
from cresmo.application.pipeline.coordinator import (
    _extract_fluid_text,
    _extract_source_text,
)
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PromptProviderPort,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    SourceTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import (
    BatchId,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
    RawIndexEntry,
)


class TestTextExtractionHelpers:
    """Verifies _extract_source_text and _extract_fluid_text helper ladders."""

    def test_extract_source_text_shapes(self) -> None:
        # Content body shape (SourceTranscript triad)
        raw_content = MagicMock()
        raw_content.content.body = "Content body text"
        assert _extract_source_text(raw_content) == "Content body text"

        # Content without body attribute (AttributeError if default omitted in getattr)
        raw_content_no_body = MagicMock(content=object(), body="Fallback from raw.body")
        assert _extract_source_text(raw_content_no_body) == "Fallback from raw.body"

        # Content without body, fallback to raw.body
        raw_body = MagicMock(spec=["body"])
        raw_body.body = "Raw body text"
        assert _extract_source_text(raw_body) == "Raw body text"

        # Raw without body, fallback to raw.text
        raw_text = MagicMock(spec=["text"])
        raw_text.text = "Raw text only"
        assert _extract_source_text(raw_text) == "Raw text only"

        # Empty fallbacks
        assert _extract_source_text(MagicMock(spec=[])) == ""
        assert _extract_source_text(None) == ""

    def test_extract_fluid_text_shapes(self) -> None:
        # Body shape
        fluid_body = MagicMock(spec=["body"])
        fluid_body.body = "Fluid body prose"
        assert _extract_fluid_text(fluid_body) == "Fluid body prose"

        # Text shape
        fluid_text = MagicMock(spec=["text"])
        fluid_text.text = "Fluid text prose"
        assert _extract_fluid_text(fluid_text) == "Fluid text prose"

        # Empty fallbacks
        assert _extract_fluid_text(MagicMock(spec=[])) == ""
        assert _extract_fluid_text(None) == ""


class TestCresmoPipelineInitializationAndProperties:
    """Verifies constructor dependency wiring, defaults, and accessor properties."""

    def test_init_raises_when_vault_port_is_none(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        with pytest.raises(ValueError, match=r"^vault_port must be provided$"):
            CresmoPipeline(media_ingestion_port=mock_ingestion, vault_port=None)  # type: ignore[arg-type]

    def test_init_raises_when_no_stage_runner_and_no_llm_synthesis_port(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)

        with pytest.raises(
            ValueError, match=r"^Either stage_runner or llm_synthesis_port must be provided$"
        ):
            CresmoPipeline(
                media_ingestion_port=mock_ingestion,
                vault_port=mock_vault,
                stage_runner=None,
                llm_synthesis_port=None,
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

        assert pipeline.stage_runner is runner
        assert pipeline.telemetry_port is mock_t
        assert pipeline.metrics_port is mock_m
        assert pipeline.stage_factory is mock_factory
        assert pipeline.llm_synthesis_port is mock_llm
        assert pipeline.llm_judge is mock_judge
        assert pipeline.prompt_provider is mock_prompt
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

    def test_init_constructing_stage_runner_from_dependencies(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_llm_synth = MagicMock(spec=LLMTransformationPort)
        mock_llm_index = MagicMock(spec=LLMTransformationPort)
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_prompt = MagicMock(spec=PromptProviderPort)
        mock_synth = MagicMock(spec=CritiqueSynthesizerPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)

        settings = DefaultPipelineSettings(judge_blocking=True, judge_max_attempts=4)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            telemetry_port=mock_t,
            metrics_port=mock_m,
            llm_synthesis_port=mock_llm_synth,
            llm_indexing_port=mock_llm_index,
            prompt_provider=mock_prompt,
            llm_judge_port=mock_judge,
            critique_synthesizer=mock_synth,
            ledger_port=mock_ledger,
            settings=settings,
            batch_size=10,
        )

        assert pipeline.telemetry_port is mock_t
        assert pipeline.metrics_port is mock_m
        assert pipeline.llm_indexing_port is mock_llm_index
        assert pipeline.batch_size == 10
        assert pipeline.stage_runner.judge_blocking is True
        assert pipeline.stage_runner.judge_max_attempts == 4
        assert pipeline.stage_runner.prompt_provider is mock_prompt
        assert pipeline.stage_runner.llm_transformation_port is mock_llm_synth
        assert pipeline.stage_runner.llm_judge is mock_judge
        assert pipeline.stage_runner.critique_synthesizer is mock_synth
        assert pipeline.stage_runner.ledger_port is mock_ledger
        assert pipeline.stage_factory is not None
        assert pipeline.stage_factory.settings is settings
        assert pipeline.stage_runner.stage_factory is not None
        assert pipeline.stage_runner.stage_factory.settings is settings

    def test_init_constructing_stage_runner_with_default_prompt_provider_noop(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_llm_synth = MagicMock(spec=LLMTransformationPort)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            llm_synthesis_port=mock_llm_synth,
            prompt_provider=None,
        )

        assert isinstance(pipeline.stage_runner.prompt_provider, NoOpPromptProviderPort)

    def test_init_constructing_stage_runner_settings_fallbacks_when_attributes_missing(
        self,
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_llm_synth = MagicMock(spec=LLMTransformationPort)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            llm_synthesis_port=mock_llm_synth,
            settings=object(),  # Has neither judge_blocking nor judge_max_attempts
        )
        assert pipeline.stage_runner.judge_blocking is False
        assert pipeline.stage_runner.judge_max_attempts == 1


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
    def sample_source_transcript(self) -> SourceTranscript:
        return SourceTranscript(
            content_id=ContentId("c1234567"),
            channel_name=ChannelName("Economics & Society"),
            channel=Channel(name="Economics & Society", id=ChannelId("UC_econ101")),
            content=Content(
                id=ContentId("c1234567"),
                title="Vilfredo Pareto and Circulation of Elites",
                body="Raw spoken audio transcript discussing Pareto optimal states and elite rotation.",
            ),
            provenance=MediaProvenance(
                url="https://youtube.com/watch?v=1234567",
                description="Lecture video",
                publication_date=datetime(2024, 5, 20, 10, 30, tzinfo=UTC),
            ),
        )

    def test_execute_happy_path_produces_full_result_and_telemetry(
        self, sample_source_transcript: SourceTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        class FluidOutput:
            title = "Polished Pareto Essay"
            body = (
                "Synthesized Pareto prose text with higher conceptual density and no verbal noise."
            )

        mock_runner.execute_stage.return_value = FluidOutput()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=mock_t,
            metrics_port=mock_m,
        )

        user = UserIdentity.worker()
        raw_idx = MagicMock(spec=RawIndexEntry)
        batch = BatchId.generate()

        res = pipeline.execute(
            sample_source_transcript,
            gap_filler_passes=3,
            force_reprocess=False,
            user=user,
            entry=raw_idx,
            batch_id=batch,
        )

        assert res.success is True
        assert res.content_id == ContentId("c1234567")
        assert res.source_transcript is sample_source_transcript
        assert res.fluid_transcript is mock_runner.execute_stage.return_value
        assert res.index_entry is raw_idx

        # Verify start_pipeline_session metadata
        mock_t.start_pipeline_session.assert_called_once()
        sess_call = mock_t.start_pipeline_session.call_args[1]
        assert sess_call["user_id"] == user
        assert sess_call["channel_tenant_id"] == sample_source_transcript.channel.tenant_key
        assert sess_call["trace_name"] == "cresmo.synthesis_pipeline"
        meta = sess_call["metadata"]
        assert meta["source"] == "transcript"
        assert meta["channel_id"] == "UC_econ101"
        assert meta["channel_name"] == "Economics & Society"
        assert meta["content_id"] == "c1234567"
        assert meta["content_title"] == "Vilfredo Pareto and Circulation of Elites"
        assert meta["raw_characters"] == len(sample_source_transcript.content.body)
        assert meta["raw_words"] == len(sample_source_transcript.content.body.split())
        assert meta["gap_filler_passes"] == 3
        assert meta["batch_id"] == batch.value
        assert meta["video_url"] == "https://youtube.com/watch?v=1234567"
        assert meta["publication_date"] == "2024-05-20"

        # Verify execute_stage call
        mock_runner.execute_stage.assert_called_once()
        stage_args = mock_runner.execute_stage.call_args
        assert stage_args[0][0] == "fluid_prose"
        assert stage_args[1]["source"] is sample_source_transcript
        assert stage_args[1]["context"].content.id == ContentId("c1234567")
        assert stage_args[1]["context"].user_identity == user

        # Verify record_session_output with all canonical fields
        mock_t.record_session_output.assert_called_once()
        output_payload = mock_t.record_session_output.call_args[0][0]
        assert output_payload["status"] == "COMPLETED"
        assert output_payload["stage"] == "fluid_prose"
        assert output_payload["stages_completed"] == ["fluid_prose"]
        assert output_payload["content_title"] == "Polished Pareto Essay"
        raw_words = len(sample_source_transcript.content.body.split())
        synth_words = len(FluidOutput.body.split())
        assert output_payload["word_count"] == synth_words
        assert output_payload["char_count"] == len(FluidOutput.body)
        assert output_payload["source_words"] == raw_words
        assert output_payload["synthesized_words"] == synth_words
        assert output_payload["expansion_ratio"] == round(synth_words / max(raw_words, 1), 3)
        assert output_payload["source_characters"] == len(sample_source_transcript.content.body)
        assert output_payload["synthesized_characters"] == len(FluidOutput.body)

    def test_execute_with_minimal_metadata_and_defaults(self) -> None:
        raw_bare = SourceTranscript(
            content_id=ContentId("c999"),
            channel_name=ChannelName("BareChannel"),
            channel=Channel(name="BareChannel", id=None),
            content=Content(
                id=ContentId("c999"),
                title="Bare Title",
                body="Raw bare text without provenance",
            ),
            provenance=MediaProvenance(url="", description=""),
        )

        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_t = MagicMock(spec=TelemetryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        class BareFluid:
            text = "Bare fluid output"

        mock_runner.execute_stage.return_value = BareFluid()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            telemetry_port=mock_t,
        )

        res = pipeline.execute(raw_bare, user=None, batch_id="  str_batch_id  ")
        assert res.success is True

        sess_call = mock_t.start_pipeline_session.call_args[1]
        assert sess_call["user_id"] == UserIdentity.anonymous()
        meta = sess_call["metadata"]
        assert meta["channel_id"] == ""
        assert meta["gap_filler_passes"] == 3
        assert meta["batch_id"] == "str_batch_id"
        assert "video_url" not in meta
        assert "publication_date" not in meta

    def test_execute_expansion_ratio_when_source_has_single_word(self) -> None:
        raw_one_word = SourceTranscript(
            content_id=ContentId("c1word"),
            channel_name=ChannelName("OneWord"),
            body="Word",
        )
        mock_runner = MagicMock(spec=PipelineStageRunner)

        class MultiWordFluid:
            body = "One two three four five six seven eight nine ten"

        mock_runner.execute_stage.return_value = MultiWordFluid()
        mock_t = MagicMock(spec=TelemetryPort)

        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=mock_runner,
            telemetry_port=mock_t,
        )

        pipeline.execute(raw_one_word)
        payload = mock_t.record_session_output.call_args[0][0]
        # 10 synth words / max(1 raw word, 1) == 10.0
        assert payload["expansion_ratio"] == 10.0

    def test_execute_fluid_without_title_falls_back_to_content_title(self) -> None:
        raw = SourceTranscript(
            content_id=ContentId("c_fallback_title"),
            channel_name=ChannelName("TitleChan"),
            title="Original Content Title",
            body="Some raw body text.",
        )
        mock_runner = MagicMock(spec=PipelineStageRunner)

        class TitlelessFluid:
            body = "Synthesized body text without title attribute."

        mock_runner.execute_stage.return_value = TitlelessFluid()
        mock_t = MagicMock(spec=TelemetryPort)

        pipeline = CresmoPipeline(
            media_ingestion_port=MagicMock(spec=MediaIngestionPort),
            vault_port=MagicMock(spec=VaultRepositoryPort),
            stage_runner=mock_runner,
            telemetry_port=mock_t,
        )

        pipeline.execute(raw)
        payload = mock_t.record_session_output.call_args[0][0]
        assert payload["content_title"] == "Original Content Title"

    def test_execute_idempotent_skip_when_in_ledger_and_not_force_reprocess(
        self, sample_source_transcript: SourceTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_ledger.is_processed.return_value = True

        mock_t = MagicMock(spec=TelemetryPort)
        mock_m = MagicMock(spec=MetricsPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        compendium_mock = MagicMock()
        mock_vault.get_enriched_compendium.return_value = compendium_mock
        raw_idx = MagicMock(spec=RawIndexEntry)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
            ledger_port=mock_ledger,
            telemetry_port=mock_t,
            metrics_port=mock_m,
        )

        res = pipeline.execute(sample_source_transcript, force_reprocess=False, entry=raw_idx)

        assert res.already_processed is True
        assert res.success is True
        assert res.content_id == sample_source_transcript.content.id
        assert res.source_transcript is sample_source_transcript
        assert res.index_entry is raw_idx
        assert res.compendium is compendium_mock
        assert res.synthesized_notes == ()
        assert res.reconciled_mocs == ()
        assert isinstance(res.synthesized_notes, tuple)
        assert isinstance(res.reconciled_mocs, tuple)
        mock_runner.execute_stage.assert_not_called()

        mock_t.record_session_output.assert_called_once_with(
            {
                "status": "SKIPPED_IDEMPOTENT",
                "reason": "Existing content already processed",
                "content_id": "c1234567",
            }
        )
        mock_m.increment_counter.assert_called_once_with(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": "UC_econ101",
                "channel_name": "Economics & Society",
                "content_id": "c1234567",
                "status": "skipped_idempotent",
                "modality": "transcript",
            },
        )

    def test_execute_idempotent_skip_when_channel_id_is_none(self) -> None:
        raw_no_chid = SourceTranscript(
            content_id=ContentId("c_no_chid"),
            channel_name=ChannelName("NoChIdChan"),
            channel=Channel(name="NoChIdChan", id=None),
            body="Text for no chid transcript",
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
                "channel_name": "NoChIdChan",
                "content_id": "c_no_chid",
                "status": "skipped_idempotent",
                "modality": "transcript",
            },
        )

    def test_execute_bypasses_idempotent_skip_when_force_reprocess_is_true(
        self, sample_source_transcript: SourceTranscript
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_ledger = MagicMock(spec=LedgerRepositoryPort)
        mock_ledger.is_processed.return_value = True

        mock_t = MagicMock(spec=TelemetryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)
        mock_runner.execute_stage.return_value = MagicMock(body="New fluid body")

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
        mock_runner.execute_stage.assert_called_once()

    def test_execute_stage_failure_propagates_exception(
        self, sample_source_transcript: SourceTranscript
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
        assert sig_exec.parameters["gap_filler_passes"].default == 3
        assert sig_exec.parameters["force_reprocess"].default is False

        sig_vid = inspect.signature(CresmoPipeline.run_for_video)
        assert sig_vid.parameters["gap_filler_passes"].default == 3
        assert sig_vid.parameters["force_reprocess"].default is False

        sig_file = inspect.signature(CresmoPipeline.run_for_text_file)
        assert sig_file.parameters["gap_filler_passes"].default == 3
        assert sig_file.parameters["force_reprocess"].default is False

        sig_man = inspect.signature(CresmoPipeline.run_for_manifest)
        assert sig_man.parameters["gap_filler_passes"].default == 1
        assert sig_man.parameters["force_reprocess"].default is False


class TestCresmoPipelineRunForSources:
    """Verifies run_for_video, run_for_text_file, and run_for_manifest wrappers."""

    def test_run_for_video_success(self) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        sample_raw = MagicMock(spec=SourceTranscript)
        sample_raw.content = Content(id=ContentId("v123"), title="Vid Title")
        sample_raw.channel = Channel(name="ChanVid", id=None)
        sample_raw.body = "Transcript text"
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
                gap_filler_passes=2,
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
                gap_filler_passes=2,
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

        sample_raw = MagicMock(spec=SourceTranscript)
        pipeline.ingest_raw_transcript.execute = MagicMock(return_value=sample_raw)

        with (
            patch.object(pipeline, "warmup") as mock_warmup,
            patch.object(pipeline, "execute", return_value=MagicMock(success=True)) as mock_exec,
        ):
            pipeline.run_for_video("https://youtube.com/watch?v=defaults")
            mock_warmup.assert_called_once()
            mock_exec.assert_called_once_with(
                raw=sample_raw,
                gap_filler_passes=3,
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

        mock_raw = MagicMock(spec=SourceTranscript)
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
                gap_filler_passes=3,
                force_reprocess=False,
                user=user,
                batch_id="text_batch",
            )
            mock_warmup.assert_called_once()
            mock_load.assert_called_once_with(file_path)
            mock_ensure.assert_called_once_with(
                mock_vault,
                file_path,
                mock_raw,
                target_dir=pipeline.settings.raw_dir,
            )
            mock_exec.assert_called_once_with(
                raw=mock_raw,
                gap_filler_passes=3,
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
        mock_raw = MagicMock(spec=SourceTranscript)

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
                gap_filler_passes=3,
                force_reprocess=False,
                user=None,
                batch_id=None,
            )

    def test_run_for_manifest_sequences_all_urls_and_propagates_parameters(
        self, tmp_path: Path
    ) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        manifest_file = tmp_path / "manifest.txt"
        manifest_file.write_text(
            "https://youtube.com/watch?v=1\nhttps://youtube.com/watch?v=2\n", encoding="utf-8"
        )

        user = UserIdentity.worker()
        batch = BatchId.generate()
        res1 = MagicMock(spec=PipelineResult)
        res2 = MagicMock(spec=PipelineResult)

        with (
            patch(
                "cresmo.application.pipeline.coordinator.load_manifest_urls",
                return_value=["https://youtube.com/watch?v=1", "https://youtube.com/watch?v=2"],
            ),
            patch.object(pipeline, "run_for_video", side_effect=[res1, res2]) as mock_run_video,
        ):
            results = pipeline.run_for_manifest(
                manifest_path=manifest_file,
                gap_filler_passes=2,
                force_reprocess=True,
                user=user,
                batch_id=batch,
            )
            assert results == [res1, res2]
            assert mock_run_video.call_count == 2
            mock_run_video.assert_any_call(
                video_url="https://youtube.com/watch?v=1",
                gap_filler_passes=2,
                force_reprocess=True,
                user=user,
                batch_id=batch,
            )
            mock_run_video.assert_any_call(
                video_url="https://youtube.com/watch?v=2",
                gap_filler_passes=2,
                force_reprocess=True,
                user=user,
                batch_id=batch,
            )

    def test_run_for_manifest_generates_batch_id_when_none(self, tmp_path: Path) -> None:
        mock_ingestion = MagicMock(spec=MediaIngestionPort)
        mock_vault = MagicMock(spec=VaultRepositoryPort)
        mock_runner = MagicMock(spec=PipelineStageRunner)

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            vault_port=mock_vault,
            stage_runner=mock_runner,
        )

        manifest_file = tmp_path / "manifest.txt"
        manifest_file.write_text("https://youtube.com/watch?v=1\n", encoding="utf-8")

        res1 = MagicMock(spec=PipelineResult)

        with (
            patch(
                "cresmo.application.pipeline.coordinator.load_manifest_urls",
                return_value=["https://youtube.com/watch?v=1"],
            ),
            patch.object(pipeline, "run_for_video", return_value=res1) as mock_run_video,
        ):
            results = pipeline.run_for_manifest(manifest_path=manifest_file, batch_id=None)
            assert results == [res1]
            mock_run_video.assert_called_once()
            call_kwargs = mock_run_video.call_args[1]
            assert call_kwargs["gap_filler_passes"] == 1
            assert call_kwargs["force_reprocess"] is False
            assert call_kwargs["user"] is None
            assert isinstance(call_kwargs["batch_id"], BatchId)
