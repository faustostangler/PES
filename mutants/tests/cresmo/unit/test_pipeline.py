"""Unit test for Cresmo end-to-end 7-stage Pipeline Orchestration.

Verifies complete causal flow across all incremental integer stages:
Stage 1 (Raw Transcript / Priority Text) -> Stage 2 (Gap Filler) -> Stage 3 (Expander)
-> Stage 4 (Inventory) -> Stage 5 (Batch) -> Stage 6 (MOC) -> Stage 7 (Dedupe).
Tests run_for_video, run_for_text_file, and run_for_manifest.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cresmo.application.pipeline import CresmoPipeline, PipelineResult
from cresmo.domain.entities import EnrichedCompendium, RawTranscript
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId, NoteTitle
from cresmo.infrastructure.adapters.mock_adapters import (
    InMemoryLedgerAdapter,
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


class SmartMockLLMAdapter(MockLLMAdapter):
    """Context-aware mock LLM adapter returning valid stage outputs based on prompt intent."""

    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append(
            {
                "prompt": prompt,
                "system_instruction": system_instruction,
                "temperature": temperature,
            }
        )
        if "Atomic Inventory Specialist" in prompt or "atomic inventory" in prompt.lower():
            return '[{"title": "Vilfredo Pareto", "type": "entity"}]'
        if "Target Entities to Synthesize" in prompt or "targets_json" in prompt:
            return (
                '[{"title": "Vilfredo Pareto", "type": "entity", '
                '"definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.", '
                '"direct_relations": ["Teoria das Elites"], '
                '"causal_matrix": {"cause": "Heterogeneidade social", "effect": "Substituição cíclica de lideranças"}}]'
            )
        if (
            "MOC Manager" in prompt
            or "maps of content" in prompt.lower()
            or "cresmo-moc-manager" in prompt
        ):
            return (
                '[{"title": "MOC Teoria Politica", "theme": "Ciência Política", '
                '"overview": "Mapeamento das teorias de liderança.", '
                '"associated_notes": ["Vilfredo Pareto"]}]'
            )
        return (
            "# Teoria das Elites\n\n"
            "A teoria da circulação das elites postula que minorias organizadas governam maiorias.\n\n"
            "## Informações Complementares\n\n"
            "Análise sociológica e precursores históricos."
        )


class TestCresmoPipelineOrchestration:
    """Hermetic unit tests for the pipeline orchestration."""

    def test_pipeline_full_cycle_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
        )

        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=canned_raw)
        vault_port = InMemoryVaultAdapter()
        ledger_port = InMemoryLedgerAdapter()

        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_port=mock_llm,
            vault_port=vault_port,
            ledger_port=ledger_port,
        )

        result: PipelineResult = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")

        assert result.success is True
        assert result.content_id == cid
        assert len(result.synthesized_notes) == 1
        assert result.synthesized_notes[0].title.value == "Vilfredo Pareto"
        assert len(result.reconciled_mocs) == 1
        assert result.reconciled_mocs[0].title.value == "MOC Teoria Politica"
        assert result.duplicates_unified == 0
        assert ledger_port.is_processed(cid) is True

    def test_run_for_video_ingestion_failure_raises_domain_error(self) -> None:
        mock_llm = SmartMockLLMAdapter()
        mock_ingestion = MockMediaIngestionPort(canned_transcript=None)
        pipeline = CresmoPipeline(
            media_ingestion_port=mock_ingestion,
            llm_port=mock_llm,
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
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Some text",
        )
        ledger = InMemoryLedgerAdapter()
        ledger.mark_processed(cid)

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert res.already_processed is True
        assert res.success is True
        assert res.synthesized_notes == ()

    def test_run_for_video_force_reprocess_bypasses_ledger(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Some text",
        )
        ledger = InMemoryLedgerAdapter()
        ledger.mark_processed(cid)

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_video(
            "https://youtube.com/watch?v=dQw4w9WgXcQ", force_reprocess=True
        )
        assert res.already_processed is False
        assert res.success is True
        assert len(result_notes := res.synthesized_notes) == 1
        assert result_notes[0].title.value == "Vilfredo Pareto"

    def test_run_for_video_resumes_when_expanded_compendium_exists(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw transcript",
        )
        vault = InMemoryVaultAdapter()
        compendium = EnrichedCompendium(
            content_id=cid,
            channel_name="Political Theory",
            body="Pre-existing expanded compendium",
            complementary_info="Complementary information",
            title=NoteTitle("Pre-existing Title"),
            pass_count=3,
        )
        vault.save_enriched_compendium(compendium)

        llm = SmartMockLLMAdapter()

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=llm,
            vault_port=vault,
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert res.success is True
        assert len(res.synthesized_notes) == 1
        assert len(llm.call_history) == 3

    # =========================================================================
    # Tests for run_for_text_file
    # =========================================================================

    def test_run_for_text_file_missing_raises_error(self, tmp_path: Path) -> None:
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        missing = tmp_path / "non_existent.md"
        with pytest.raises(CresmoDomainError, match=r"Priority text file not found:"):
            pipeline.run_for_text_file(missing)

    def test_run_for_text_file_empty_raises_error(self, tmp_path: Path) -> None:
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        empty_file = tmp_path / "empty_transcript.txt"
        empty_file.write_text("   \n\t  ", encoding="utf-8")
        with pytest.raises(CresmoDomainError, match=r"Priority text file is empty:"):
            pipeline.run_for_text_file(empty_file)

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
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.success is True
        assert res.content_id.value == "pareto_elites_analysis"
        assert len(res.synthesized_notes) == 1
        assert res.synthesized_notes[0].title.value == "Vilfredo Pareto"
        assert ledger.is_processed(res.content_id) is True
        assert vault.get_raw_transcript(res.content_id) is not None

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
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.success is True
        raw = vault.get_raw_transcript(res.content_id)
        assert raw is not None
        assert raw.title == "Discurso sobre a Servidão Voluntária"
        assert raw.channel_name == "Filosofia Política"
        assert raw.channel_id == "chan_philo_123"
        assert raw.channel_category == "philosophy"
        assert raw.source_url == "https://example.org/etienne"
        assert raw.video_description == "Análise de La Boétie"
        assert "Corpo do texto sobre a servidão voluntária" in raw.body

    def test_run_for_text_file_short_stem_fallback_hash(self, tmp_path: Path) -> None:
        short_file = tmp_path / "ab.txt"
        short_file.write_text("Valid non-empty body content for short stem file.", encoding="utf-8")

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        res = pipeline.run_for_text_file(short_file)
        assert res.success is True
        assert res.content_id.value.startswith("ab_")
        assert len(res.content_id.value) >= 8

    def test_run_for_text_file_idempotent_skip_when_in_ledger(self, tmp_path: Path) -> None:
        text_file = tmp_path / "idempotent_doc_file.txt"
        text_file.write_text("Some text for idempotency check.", encoding="utf-8")

        cid = ContentId("idempotent_doc_file")
        ledger = InMemoryLedgerAdapter()
        ledger.mark_processed(cid)

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file)
        assert res.already_processed is True
        assert res.success is True

    def test_run_for_text_file_force_reprocess_bypasses_ledger(self, tmp_path: Path) -> None:
        text_file = tmp_path / "force_reprocess_file.txt"
        text_file.write_text("Text content for force reprocess.", encoding="utf-8")

        cid = ContentId("force_reprocess_file")
        ledger = InMemoryLedgerAdapter()
        ledger.mark_processed(cid)

        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file, force_reprocess=True)
        assert res.already_processed is False
        assert res.success is True

    # =========================================================================
    # Tests for run_for_manifest
    # =========================================================================

    def test_run_for_manifest_missing_raises_error(self, tmp_path: Path) -> None:
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        missing = tmp_path / "missing_playlist.txt"
        with pytest.raises(CresmoDomainError, match=r"Manifest file not found:"):
            pipeline.run_for_manifest(missing)

    def test_run_for_manifest_empty_returns_empty_list(self, tmp_path: Path) -> None:
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        empty_manifest = tmp_path / "empty_playlist.txt"
        empty_manifest.write_text("# Only comments\n\n   # Another comment\n", encoding="utf-8")

        results = pipeline.run_for_manifest(empty_manifest)
        assert results == []

    def test_run_for_manifest_processes_valid_urls_skipping_comments(self, tmp_path: Path) -> None:
        manifest = tmp_path / "valid_playlist.txt"
        manifest.write_text(
            "# Priority Playlist\n"
            "https://youtube.com/watch?v=dQw4w9WgXcQ\n"
            "\n"
            "# Secondary video\n"
            "https://youtube.com/watch?v=another12345\n",
            encoding="utf-8",
        )

        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw transcript content",
        )
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        results = pipeline.run_for_manifest(manifest)
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is True
