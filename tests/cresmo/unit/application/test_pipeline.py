"""Unit test for Cresmo end-to-end Pipeline Orchestration.

Verifies complete causal flow across all incremental synthesis steps:
Raw Transcript / Priority Text -> Gap Filler -> Expander
-> Inventory -> Batch -> MOC -> Deduplication.
Tests run_for_video, run_for_text_file, and run_for_manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.models import PipelineDependencies, PipelineResult
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import (
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PromptProviderPort,
)
from cresmo.domain.entities import StageTranscript
from cresmo.domain.exceptions import CresmoDomainError, StageQuarantinedError
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    ChatPrompt,
    Content,
    ContentId,
    LedgerEntry,
    MediaProvenance,
    PipelineStatus,
    RawIndexEntry,
    StageExecutionPolicy,
)
from tests.doubles.mock_adapters import (
    InMemoryLedgerAdapter,
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


def _make_pipeline(
    *,
    media_ingestion_port: Any,
    vault_port: Any,
    llm_synthesis_port: Any,
    ledger_port: Any | None = None,
    prompt_provider: PromptProviderPort | None = None,
) -> CresmoPipeline:
    runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            llm_transformation_port=llm_synthesis_port,
            prompt_provider=prompt_provider or NoOpPromptProviderPort(),
            stage_factory=StageFactory(policy=StageExecutionPolicy()),
        )
    )
    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        vault_port=vault_port,
        stage_runner=runner,
        ledger_port=ledger_port,
    )


class SmartMockLLMAdapter(MockLLMAdapter):
    """Context-aware mock LLM adapter returning valid stage outputs based on prompt intent."""

    def transform(
        self,
        prompt: Any,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        sys_str = prompt.system_prompt if isinstance(prompt, ChatPrompt) else system_prompt
        prompt_text = prompt.messages[-1].content if isinstance(prompt, ChatPrompt) else str(prompt)
        self.call_history.append(
            {
                "prompt": prompt,
                "system_prompt": sys_str,
                "temperature": temperature,
                "trace_id": trace_id,
                "session_id": session_id,
                "user_id": user_id,
            }
        )
        if trace_id and "judge" in trace_id:
            return "true"
        if trace_id and "concepts" in trace_id:
            return "Circulação de Elites"
        if trace_id and "summary" in trace_id:
            return "Resumo da teoria das elites."
        if trace_id and "synthesis" in trace_id:
            return (
                "Minorias burocráticas governam as instituições políticas centrais. "
                "A decadência dos governantes precipita a substituição por novas contra-elites "
                "organizadas em estruturas institucionais complexas e altamente resilientes."
            )
        if trace_id and "atomic_batch" in trace_id:
            return (
                '[{"title": "Vilfredo Pareto", "type": "entity", '
                '"definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.", '
                '"direct_relations": ["Teoria das Elites"], '
                '"causal_matrix": {"cause": "Heterogeneidade social", "effect": "Substituição cíclica de lideranças"}}]'
            )
        combined = f"{sys_str or ''} {prompt_text}".lower()
        if "atomic inventory" in combined or (trace_id and "inventory" in trace_id):
            return '[{"title": "Vilfredo Pareto", "type": "entity"}]'
        if "target entities to synthesize" in combined or "targets_json" in combined:
            return (
                '[{"title": "Vilfredo Pareto", "type": "entity", '
                '"definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.", '
                '"direct_relations": ["Teoria das Elites"], '
                '"causal_matrix": {"cause": "Heterogeneidade social", "effect": "Substituição cíclica de lideranças"}}]'
            )
        if (
            "moc manager" in combined
            or "maps of content" in combined
            or "cresmo-moc-manager" in combined
            or (trace_id and "mocs" in trace_id)
        ):
            return (
                '[{"title": "MOC Teoria Politica", "theme": "Ciência Política", '
                '"overview": "Mapeamento das teorias de liderança.", '
                '"associated_notes": ["Vilfredo Pareto"]}]'
            )
        return (
            "# Teoria das Elites\n\n"
            "A teoria da circulação das elites postula que minorias organizadas governam maiorias.\n\n"
            "### Extra Info\n\n"
            "Análise sociológica e precursores históricos."
        )


class TestCresmoPipelineOrchestration:
    """Hermetic unit tests for the pipeline orchestration."""

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_pipeline_full_cycle_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = StageTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
        )

        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
        )

        result: PipelineResult = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")

        assert result.already_processed is False
        assert result.content_id == cid
        assert result.source_transcript is canned_raw
        assert result.index_entry is not None
        assert result.index_entry.video_id == cid
        assert result.final_transcript is not None
        assert result.final_transcript.content_id == cid
        assert result.inventory is not None
        assert len(result.inventory.items) == 1
        assert result.dedup_report is not None
        assert ledger_port.is_processed(cid) is True

    def test_pipeline_stage1_fluid_prose_execution(self) -> None:
        """Verify CresmoPipeline Stage 1 executes with StageTranscript via StageConfig."""
        cid = ContentId("vid_stage1_iso")
        canned_source = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_stage1_iso"),
            content=Content(
                id=cid,
                title="Political Theory",
                text="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
            ),
        )

        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_source)
        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()

        pipeline = _make_pipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
        )

        result: PipelineResult = pipeline.run_for_video(
            "https://youtube.com/watch?v=vid_stage1_iso"
        )

        from cresmo.domain.stage_registry import StageName

        assert result.already_processed is False
        assert result.content_id == cid
        assert result.source_transcript is canned_source
        fluid_res = result.stage_artifacts.get(StageName.FLUID_PROSE)
        assert fluid_res is not None
        assert isinstance(fluid_res, StageTranscript)
        assert fluid_res.content.id == cid
        assert "A teoria da circulação das elites postula" in fluid_res.content.text

    def test_run_for_video_ingestion_failure_raises_domain_error(self) -> None:
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=None)
        pipeline = _make_pipeline(
            media_ingestion_port=mock_ingestion,
            llm_synthesis_port=mock_llm,
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        with pytest.raises(
            CresmoDomainError,
            match=r"Ingestion failed to retrieve transcript for: https://youtube\.com/watch\?v=failed",
        ):
            pipeline.run_for_video("https://youtube.com/watch?v=failed")

    def test_run_for_video_idempotent_skip_when_already_processed(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(id=cid, title="Political Theory", text="Some text"),
        )
        ledger = InMemoryLedgerAdapter()
        ledger.save_entry(
            LedgerEntry(
                content_id=cid,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Political Theory",
                channel_name=ChannelName("Political Theory"),
                status=PipelineStatus.COMPLETED,
            )
        )

        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert res.already_processed is True

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_video_force_reprocess_bypasses_ledger(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(id=cid, title="Political Theory", text="Some text"),
        )
        ledger = InMemoryLedgerAdapter()
        ledger.save_entry(
            LedgerEntry(
                content_id=cid,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Political Theory",
                channel_name=ChannelName("Political Theory"),
                status=PipelineStatus.COMPLETED,
            )
        )

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_video(
            "https://youtube.com/watch?v=dQw4w9WgXcQ", force_reprocess=True
        )
        assert res.already_processed is False

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_video_resumes_when_expanded_compendium_exists(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(id=cid, title="Political Theory", text="Raw transcript"),
        )
        vault = InMemoryVaultAdapter()
        compendium = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            content=Content(
                id=cid,
                title="Pre-existing Title",
                text="Pre-existing expanded compendium\n\n### Extra Info\n\nComplementary information",
            ),
            pass_count=3,
        )
        vault.save_stage_transcript("gap_filler", compendium)

        llm = SmartMockLLMAdapter()

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=llm,
            vault_port=vault,
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert res.already_processed is False
        # All calls share the unified video session_id (1 fluid prose + 6 indexing + 4 downstream synthesis = 11)
        video_session_calls = [
            c for c in llm.call_history if c.get("session_id") == "Political Theory:dQw4w9WgXcQ"
        ]
        assert len(video_session_calls) == 11
        # Gap filler and expansion were skipped because compendium was pre-saved
        assert not any("_gap_fill_pass_" in c.get("trace_id", "") for c in video_session_calls)
        assert not any("_longitudinal" in c.get("trace_id", "") for c in video_session_calls)

    # =========================================================================
    # Tests for run_for_text_file
    # =========================================================================

    def test_run_for_text_file_missing_raises_error(self, tmp_path: Path) -> None:
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        missing = tmp_path / "non_existent.md"
        with pytest.raises(CresmoDomainError, match=r"Transcript file not found:"):
            pipeline.run_for_text_file(missing)

    def test_run_for_text_file_empty_raises_error(self, tmp_path: Path) -> None:
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        empty_file = tmp_path / "empty_transcript.txt"
        empty_file.write_text("   \n\t  ", encoding="utf-8")
        with pytest.raises(CresmoDomainError, match=r"Transcript file is empty:"):
            pipeline.run_for_text_file(empty_file)

    def test_run_for_text_file_rejects_internal_system_artifacts(self, tmp_path: Path) -> None:
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        canal_file = tmp_path / "_canal.md"
        canal_file.write_text("# Channel Index", encoding="utf-8")
        with pytest.raises(CresmoDomainError, match=r"internal Cresmo artifact or system index"):
            pipeline.run_for_text_file(canal_file)

        brain_file = tmp_path / "brain.csv"
        brain_file.write_text("channel,title\n", encoding="utf-8")
        with pytest.raises(CresmoDomainError, match=r"internal Cresmo artifact or system index"):
            pipeline.run_for_text_file(brain_file)

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_text_file_plain_text_full_cycle(self, tmp_path: Path) -> None:
        chan_dir = tmp_path / "political_science"
        chan_dir.mkdir(parents=True)
        text_file = chan_dir / "pareto_elites_analysis.txt"
        text_file.write_text(
            "This is a detailed textual treatise about Vilfredo Pareto and the circulation of elites.",
            encoding="utf-8",
        )

        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.already_processed is False
        assert res.content_id.value == "pareto_elites_analysis"
        assert ledger.is_processed(res.content_id) is True
        assert vault.get_stage_transcript("raw", res.content_id) is not None

    def test_run_for_text_file_frontmatter_metadata_parsing(self, tmp_path: Path) -> None:
        text_file = tmp_path / "custom_doc_file.md"
        content = (
            "---\n"
            "video_title: 'Discurso sobre a Servidão Voluntária'\n"
            "channel_name: 'Filosofia Política'\n"
            "channel_id: 'chan_philo_123'\n"
            "channel_category: 'philosophy'\n"
            "url: 'https://example.org/etienne'\n"
            "video_description: 'Análise de La Boétie'\n"
            "---\n"
            "Corpo do texto sobre a servidão voluntária e legitimidade do poder."
        )
        text_file.write_text(content, encoding="utf-8")

        vault = InMemoryVaultAdapter()
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.already_processed is False
        raw = vault.get_stage_transcript("raw", res.content_id)
        assert raw is not None
        assert raw.content.title == "Discurso sobre a Servidão Voluntária"
        assert raw.channel.name == "Filosofia Política"
        assert raw.channel.id == ChannelId("chan_philo_123")
        assert raw.channel.category == "philosophy"
        assert raw.provenance.url == "https://example.org/etienne"
        assert raw.provenance.description == "Análise de La Boétie"
        assert "Corpo do texto sobre a servidão voluntária" in raw.content.text

    def test_run_for_text_file_skips_save_when_already_in_raw_lake(self, tmp_path: Path) -> None:
        """Verify that files residing inside raw_dir lake are not redundantly re-saved to disk."""
        raw_lake_dir = tmp_path / "raw"
        chan_dir = raw_lake_dir / "economics"
        chan_dir.mkdir(parents=True)
        raw_file = chan_dir / "austrian_business_cycle.md"
        raw_file.write_text(
            "An analytical treatise on capital structure and credit expansion.",
            encoding="utf-8",
        )

        vault = InMemoryVaultAdapter(data_dir=tmp_path)
        vault.save_stage_transcript = MagicMock(wraps=vault.save_stage_transcript)  # type: ignore[method-assign]

        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_text_file(raw_file)
        assert res.already_processed is False
        # Assert raw stage persistence was bypassed to prevent redundant disk I/O
        raw_calls = [
            c
            for c in vault.save_stage_transcript.call_args_list
            if c.args and (c.args[0] == "raw" or getattr(c.args[0], "value", None) == "raw")
        ]
        assert len(raw_calls) == 0

        # For an external file outside raw_dir, verify it IS saved into raw lake
        ext_dir = tmp_path / "priority_texts"
        ext_dir.mkdir(parents=True)
        ext_file = ext_dir / "external_article.txt"
        ext_file.write_text("External article content.", encoding="utf-8")

        result_external = pipeline.run_for_text_file(ext_file)
        assert result_external.already_processed is False
        external_raw_calls = [
            c
            for c in vault.save_stage_transcript.call_args_list
            if c.args and (c.args[0] == "raw" or getattr(c.args[0], "value", None) == "raw")
        ]
        assert len(external_raw_calls) == 1

    def test_run_for_text_file_short_stem_fallback_hash(self, tmp_path: Path) -> None:
        short_file = tmp_path / "ab.txt"
        short_file.write_text("Valid non-empty body content for short stem file.", encoding="utf-8")

        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_text_file(short_file)
        assert res.already_processed is False
        assert res.content_id.value.startswith("ab_")
        assert len(res.content_id.value) >= 8

    def test_run_for_text_file_idempotent_skip_when_in_ledger(self, tmp_path: Path) -> None:
        text_file = tmp_path / "idempotent_doc_file.txt"
        text_file.write_text("Some text for idempotency check.", encoding="utf-8")

        cid = ContentId("idempotent_doc_file")
        ledger = InMemoryLedgerAdapter()
        ledger.save_entry(
            LedgerEntry(
                content_id=cid,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Political Theory",
                channel_name=ChannelName("Political Theory"),
                status=PipelineStatus.COMPLETED,
            )
        )

        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.already_processed is True

    def test_run_for_text_file_force_reprocess_bypasses_ledger(self, tmp_path: Path) -> None:
        text_file = tmp_path / "force_reprocess_file.txt"
        text_file.write_text("Text content for force reprocess.", encoding="utf-8")

        cid = ContentId("force_reprocess_file")
        ledger = InMemoryLedgerAdapter()
        ledger.save_entry(
            LedgerEntry(
                content_id=cid,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Political Theory",
                channel_name=ChannelName("Political Theory"),
                status=PipelineStatus.COMPLETED,
            )
        )

        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file, force_reprocess=True)
        assert res.already_processed is False

    def test_pipeline_init_with_directly_injected_stage_runner(self) -> None:
        """Verify CresmoPipeline accepts a directly injected PipelineStageRunner instance."""
        mock_llm = SmartMockLLMAdapter()
        deps = PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            prompt_provider=NoOpPromptProviderPort(),
            llm_transformation_port=mock_llm,
        )
        stage_runner = PipelineStageRunner(dependencies=deps)

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            vault_port=InMemoryVaultAdapter(),
            stage_runner=stage_runner,
        )

        assert pipeline.stage_runner is stage_runner
        assert pipeline.telemetry_port is stage_runner.telemetry_port
        assert pipeline.metrics_port is stage_runner.metrics_port
        assert pipeline.stage_runner.llm_transformation_port is mock_llm

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_video_expansion_passes_and_idempotency_attributes(self) -> None:
        cid = ContentId("videoPassTest1")
        canned_raw = StageTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
        )
        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        # Explicit expansion_max_passes = 2 (fluid prose sets passes=2, expansion increments to 3)
        res = pipeline.run_for_video(
            "https://youtube.com/watch?v=videoPassTest1", expansion_max_passes=2
        )
        assert res.already_processed is False
        comp = vault.get_stage_transcript("gap_filler", cid)
        assert comp is not None
        assert comp.pass_count == 3

        # Second run without force_reprocess returns exact idempotency attributes
        result_cached = pipeline.run_for_video(
            "https://youtube.com/watch?v=videoPassTest1", force_reprocess=False
        )
        assert result_cached.content_id == cid
        assert result_cached.already_processed is True

    def test_run_for_text_file_content_id_derivation_boundaries(self, tmp_path: Path) -> None:
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        # Boundary: clean stem length exactly 8
        f8 = tmp_path / "exact008.txt"
        f8.write_text("Text content for length 8 boundary.", encoding="utf-8")
        result_exact_8 = pipeline.run_for_text_file(f8)
        assert result_exact_8.content_id.value == "exact008"

        # Boundary: clean stem length exactly 64
        name64 = "a" * 64
        f64 = tmp_path / f"{name64}.txt"
        f64.write_text("Text content for length 64 boundary.", encoding="utf-8")
        result_exact_64 = pipeline.run_for_text_file(f64)
        assert result_exact_64.content_id.value == name64

        # Boundary: clean stem length 65 (triggers fallback)
        name65 = "b" * 65
        f65 = tmp_path / f"{name65}.txt"
        f65.write_text("Text content for length 65 boundary.", encoding="utf-8")
        result_long_65 = pipeline.run_for_text_file(f65)
        assert result_long_65.content_id.value.startswith("b" * 24 + "_")
        assert len(result_long_65.content_id.value) == 24 + 1 + 16

        # Boundary: non-alphanumeric stem (empty clean stem -> prefix is 'text')
        f_symbols = tmp_path / "###$$$%%%.txt"
        f_symbols.write_text("Text content for non-alphanumeric stem.", encoding="utf-8")
        result_symbols = pipeline.run_for_text_file(f_symbols)
        assert result_symbols.content_id.value.startswith("text_")
        assert len(result_symbols.content_id.value) == 4 + 1 + 16

        # Hyphens and underscores preserved in stem
        f_hyph = tmp_path / "hyphen-and_under.txt"
        f_hyph.write_text("Text content with hyphens and underscores.", encoding="utf-8")
        result_hyphenated = pipeline.run_for_text_file(f_hyph)
        assert result_hyphenated.content_id.value == "hyphen-and_under"

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_text_file_passes_and_idempotency_attributes(self, tmp_path: Path) -> None:
        text_file = tmp_path / "pass_count_test.txt"
        text_file.write_text("Detailed text for pass count verification.", encoding="utf-8")

        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file, expansion_max_passes=4)
        assert res.already_processed is False
        comp = vault.get_stage_transcript("gap_filler", res.content_id)
        assert comp is not None
        assert comp.pass_count == 5

        # Idempotent re-run
        result_idempotent = pipeline.run_for_text_file(text_file, force_reprocess=False)
        assert result_idempotent.content_id == res.content_id
        assert result_idempotent.already_processed is True

    def test_run_for_text_file_frontmatter_field_variants_and_malformed_tolerance(
        self, tmp_path: Path
    ) -> None:
        # Variant keys: 'title', 'channel', 'domain'
        f_var = tmp_path / "variant_fm.md"
        f_var.write_text(
            "---\n"
            "title: 'Alternative Title'\n"
            "channel: 'Alternative Channel'\n"
            "domain: 'sociology'\n"
            "channel_id: 'alt_id_1'\n"
            "url: 'https://example.org/alt'\n"
            "video_description: 'Alternative description text'\n"
            "---\n"
            "Body content under variant frontmatter keys.",
            encoding="utf-8",
        )

        vault = InMemoryVaultAdapter()
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
        )

        result_variant = pipeline.run_for_text_file(f_var)
        assert result_variant.already_processed is False
        raw = vault.get_stage_transcript("raw", result_variant.content_id)
        assert raw is not None
        assert raw.content.title == "Alternative Title"
        assert raw.channel.name == "Alternative Channel"
        assert raw.channel.category == "sociology"
        assert raw.channel.id == ChannelId("alt_id_1")
        assert raw.provenance.url == "https://example.org/alt"
        assert raw.provenance.description == "Alternative description text"

        # Malformed YAML frontmatter (syntax error) is safely tolerated
        f_bad_yaml = tmp_path / "bad_yaml.md"
        f_bad_yaml.write_text(
            "---\n[unclosed_yaml_sequence: {broken\n---\nBody content surviving bad YAML syntax.",
            encoding="utf-8",
        )
        result_bad = pipeline.run_for_text_file(f_bad_yaml)
        assert result_bad.already_processed is False
        raw_bad = vault.get_stage_transcript("raw", result_bad.content_id)
        assert raw_bad is not None
        assert "Body content surviving bad YAML" in raw_bad.content.text

        # Unclosed frontmatter (no closing ---) is treated directly as body
        f_no_close = tmp_path / "no_close.md"
        f_no_close.write_text(
            "---\ntitle: Unclosed without closing delimiter\nJust plain body text.",
            encoding="utf-8",
        )
        result_no_close = pipeline.run_for_text_file(f_no_close)
        assert result_no_close.already_processed is False
        raw_no_close = vault.get_stage_transcript("raw", result_no_close.content_id)
        assert raw_no_close is not None
        assert "Just plain body text." in raw_no_close.content.text

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_run_for_manifest_parameters_passthrough(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest_params.txt"
        manifest.write_text(
            "https://youtube.com/watch?v=paramVid123\n",
            encoding="utf-8",
        )

        cid = ContentId("paramVid123")
        canned_raw = StageTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Raw transcript for manifest param test.",
        )
        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        # Run with expansion_max_passes = 2 (fluid prose sets passes=2, expansion increments to 3)
        results = pipeline.run_for_manifest(manifest, expansion_max_passes=2)
        assert len(results) == 1
        assert results[0].already_processed is False
        comp = vault.get_stage_transcript("gap_filler", cid)
        assert comp is not None
        assert comp.pass_count == 3

        # Second run without force_reprocess is skipped as already processed
        results_cached = pipeline.run_for_manifest(manifest, force_reprocess=False)
        assert results_cached[0].already_processed is True

        # Third run with force_reprocess = True executes
        results_force = pipeline.run_for_manifest(manifest, force_reprocess=True)
        assert results_force[0].already_processed is False

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_pipeline_run_passes_raw_index_entry_to_synthesize(self) -> None:
        cid = ContentId("entryPass123")
        canned_raw = StageTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Raw transcript body containing substantial philosophical concepts.",
        )
        vault = InMemoryVaultAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
        )

        res = pipeline.run_for_video("https://youtube.com/watch?v=entryPass123")

        assert res.already_processed is False
        assert res.index_entry is not None
        assert isinstance(res.index_entry, RawIndexEntry)
        assert res.index_entry.video_id == cid
        assert res.index_entry.channel_name == ChannelName("Political Theory")
        assert res.index_entry.summary != ""
        assert res.index_entry.excerpt != ""

    def test_pipeline_execute_skips_raw_indexing_when_already_processed_in_ledger(self) -> None:
        """Verify that execute() evaluates ledger idempotency before raw indexing."""
        cid = ContentId("idempotentVideo123")
        canned_raw = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=idempotentVideo123"),
            content=Content(id=cid, title="Political Theory", text="Raw transcript content."),
        )
        ledger = InMemoryLedgerAdapter()
        ledger.save_entry(
            LedgerEntry(
                content_id=cid,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Political Theory",
                channel_name=ChannelName("Political Theory"),
                status=PipelineStatus.COMPLETED,
            )
        )

        vault = InMemoryVaultAdapter()
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        stage_executed = False
        orig_execute = pipeline.stage_runner.execute_stage

        def spy_stage_execute(*args: Any, **kwargs: Any) -> Any:
            nonlocal stage_executed
            stage_executed = True
            return orig_execute(*args, **kwargs)

        pipeline.stage_runner.execute_stage = spy_stage_execute  # type: ignore[assignment,method-assign]
        res = pipeline.execute(raw=canned_raw, force_reprocess=False)

        assert res.already_processed is True
        assert not stage_executed

    def test_execute_persists_unified_ledger_lifecycle(self) -> None:
        cid = ContentId("unifiedLedger01")
        raw = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="file:///tmp/local.txt"),
            content=Content(id=cid, title="", text="Raw transcript body."),
        )
        ledger = InMemoryLedgerAdapter()
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.execute(raw=raw)
        assert res.already_processed is False
        assert ledger.is_processed(cid) is True
        entry = ledger.get_entry(cid)
        assert entry is not None
        assert entry.status == PipelineStatus.COMPLETED
        assert entry.media_url == "https://cresmo.internal/content/unifiedLedger01"

    def test_execute_records_failed_and_preserves_quarantined_in_ledger(self) -> None:
        cid_fail = ContentId("unifiedFail001")
        raw_fail = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=unifiedFail001"),
            content=Content(id=cid_fail, title="Fail Video", text="Raw transcript body."),
        )
        ledger = InMemoryLedgerAdapter()
        pipeline = _make_pipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        def boom(*_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("transient LLM outage")

        pipeline.stage_runner.execute_stage = boom  # type: ignore[assignment,method-assign]
        with pytest.raises(RuntimeError, match="transient LLM outage"):
            pipeline.execute(raw=raw_fail)
        failed_entry = ledger.get_entry(cid_fail)
        assert failed_entry is not None
        assert failed_entry.status == PipelineStatus.FAILED_TRANSFORMATION
        assert failed_entry.error_message == "transient LLM outage"

        cid_quar = ContentId("unifiedQuar001")
        raw_quar = StageTranscript(
            channel=Channel(name="Political Theory"),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=unifiedQuar001"),
            content=Content(id=cid_quar, title="Quar Video", text="Raw transcript body."),
        )

        def quarantine_hit(*_args: Any, **_kwargs: Any) -> Any:
            ledger.save_entry(
                LedgerEntry(
                    content_id=cid_quar,
                    media_url="https://youtube.com/watch?v=unifiedQuar001",
                    title="Quar Video",
                    channel_name=ChannelName("Political Theory"),
                    status=PipelineStatus.QUARANTINED,
                )
            )
            raise StageQuarantinedError(
                stage_name="fluid_prose",
                content_id=cid_quar.value,
                attempts=1,
                critique="crit",
                overall_score=0.4,
            )

        pipeline.stage_runner.execute_stage = quarantine_hit  # type: ignore[assignment,method-assign]
        with pytest.raises(StageQuarantinedError):
            pipeline.execute(raw=raw_quar)
        quar_entry = ledger.get_entry(cid_quar)
        assert quar_entry is not None
        assert quar_entry.status == PipelineStatus.QUARANTINED

    @pytest.mark.skip(
        reason="Downstream stages 2-8 quarantined pending StageConfig refactoring per ADR-031"
    )
    def test_pipeline_execute_handles_raw_indexing_failure_gracefully(self) -> None:
        """Verify that execute() logs a warning and proceeds when raw indexing fails (fatal=False)."""
        cid = ContentId("failIndex123")
        canned_raw = StageTranscript(
            content_id=cid,
            channel_name=ChannelName("Political Theory"),
            body="Raw transcript content for graceful degradation check.",
        )
        vault = InMemoryVaultAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_synthesis_port=SmartMockLLMAdapter(),
            vault_port=vault,
        )

        def failing_index_execute(
            transcript: StageTranscript,
            force: bool = False,
            user: Any = None,
        ) -> RawIndexEntry | None:
            raise RuntimeError("Disk write failed during raw indexing")

        pipeline.index_raw.execute = failing_index_execute  # type: ignore[assignment,method-assign]
        from cresmo.domain.stage_registry import StageName

        res = pipeline.execute(raw=canned_raw)

        assert res.already_processed is False
        assert res.index_entry is None
        assert res.stage_artifacts[StageName.FLUID_PROSE] is not None
        assert res.final_transcript is not None
