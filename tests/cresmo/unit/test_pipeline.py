"""Unit test for Cresmo end-to-end 7-stage Pipeline Orchestration.

Verifies complete causal flow across all incremental integer stages:
Stage 1 (Raw Transcript / Priority Text) -> Stage 2 (Gap Filler) -> Stage 3 (Expander)
-> Stage 4 (Inventory) -> Stage 5 (Batch) -> Stage 6 (MOC) -> Stage 7 (Dedupe).
Tests run_for_video, run_for_text_file, and run_for_manifest.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

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
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider


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

    def test_pipeline_init_defaults_and_custom_options(self) -> None:
        # Default initialization
        pipeline_default = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
        )
        assert isinstance(pipeline_default.prompt_provider, JsonPromptProvider)
        assert pipeline_default.synthesize_atomic_batch.batch_size == 5

        # Custom initialization
        custom_pp = MagicMock()
        pipeline_custom = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            batch_size=9,
            prompt_provider=custom_pp,
        )
        assert pipeline_custom.prompt_provider is custom_pp
        assert pipeline_custom.synthesize_atomic_batch.batch_size == 9
        assert pipeline_custom.fill_gaps_fluid_prose.prompt_provider is custom_pp

    def test_run_for_video_gap_filler_passes_and_idempotency_attributes(self) -> None:
        cid = ContentId("videoPassTest1")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
        )
        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        # Explicit gap_filler_passes = 2 (Stage 2 sets passes=2, Stage 3 increments to 3)
        res = pipeline.run_for_video(
            "https://youtube.com/watch?v=videoPassTest1", gap_filler_passes=2
        )
        assert res.success is True
        comp = vault.get_enriched_compendium(cid)
        assert comp is not None
        assert comp.pass_count == 3

        # Second run without force_reprocess returns exact idempotency attributes
        res_cached = pipeline.run_for_video(
            "https://youtube.com/watch?v=videoPassTest1", force_reprocess=False
        )
        assert res_cached.content_id == cid
        assert res_cached.synthesized_notes == ()
        assert res_cached.reconciled_mocs == ()
        assert res_cached.duplicates_unified == 0
        assert res_cached.already_processed is True
        assert res_cached.success is True

    def test_run_for_text_file_content_id_derivation_boundaries(self, tmp_path: Path) -> None:
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=InMemoryVaultAdapter(),
            ledger_port=InMemoryLedgerAdapter(),
        )

        # Boundary: clean stem length exactly 8
        f8 = tmp_path / "exact008.txt"
        f8.write_text("Text content for length 8 boundary.", encoding="utf-8")
        res8 = pipeline.run_for_text_file(f8)
        assert res8.content_id.value == "exact008"

        # Boundary: clean stem length exactly 64
        name64 = "a" * 64
        f64 = tmp_path / f"{name64}.txt"
        f64.write_text("Text content for length 64 boundary.", encoding="utf-8")
        res64 = pipeline.run_for_text_file(f64)
        assert res64.content_id.value == name64

        # Boundary: clean stem length 65 (triggers fallback)
        name65 = "b" * 65
        f65 = tmp_path / f"{name65}.txt"
        f65.write_text("Text content for length 65 boundary.", encoding="utf-8")
        res65 = pipeline.run_for_text_file(f65)
        assert res65.content_id.value.startswith("b" * 24 + "_")
        assert len(res65.content_id.value) == 24 + 1 + 16

        # Boundary: non-alphanumeric stem (empty clean stem -> prefix is 'text')
        f_symbols = tmp_path / "###$$$%%%.txt"
        f_symbols.write_text("Text content for non-alphanumeric stem.", encoding="utf-8")
        res_sym = pipeline.run_for_text_file(f_symbols)
        assert res_sym.content_id.value.startswith("text_")
        assert len(res_sym.content_id.value) == 4 + 1 + 16

        # Hyphens and underscores preserved in stem
        f_hyph = tmp_path / "hyphen-and_under.txt"
        f_hyph.write_text("Text content with hyphens and underscores.", encoding="utf-8")
        res_hyph = pipeline.run_for_text_file(f_hyph)
        assert res_hyph.content_id.value == "hyphen-and_under"

    def test_run_for_text_file_passes_and_idempotency_attributes(self, tmp_path: Path) -> None:
        text_file = tmp_path / "pass_count_test.txt"
        text_file.write_text("Detailed text for pass count verification.", encoding="utf-8")

        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        res = pipeline.run_for_text_file(text_file, gap_filler_passes=4)
        assert res.success is True
        comp = vault.get_enriched_compendium(res.content_id)
        assert comp is not None
        assert comp.pass_count == 5

        # Idempotent re-run
        res_idem = pipeline.run_for_text_file(text_file, force_reprocess=False)
        assert res_idem.content_id == res.content_id
        assert res_idem.synthesized_notes == ()
        assert res_idem.reconciled_mocs == ()
        assert res_idem.duplicates_unified == 0
        assert res_idem.already_processed is True
        assert res_idem.success is True

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
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(),
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
        )

        res_var = pipeline.run_for_text_file(f_var)
        assert res_var.success is True
        raw = vault.get_raw_transcript(res_var.content_id)
        assert raw is not None
        assert raw.title == "Alternative Title"
        assert raw.channel_name == "Alternative Channel"
        assert raw.channel_category == "sociology"
        assert raw.channel_id == "alt_id_1"
        assert raw.source_url == "https://example.org/alt"
        assert raw.video_description == "Alternative description text"

        # Malformed YAML frontmatter (syntax error) is safely tolerated
        f_bad_yaml = tmp_path / "bad_yaml.md"
        f_bad_yaml.write_text(
            "---\n[unclosed_yaml_sequence: {broken\n---\nBody content surviving bad YAML syntax.",
            encoding="utf-8",
        )
        res_bad = pipeline.run_for_text_file(f_bad_yaml)
        assert res_bad.success is True
        raw_bad = vault.get_raw_transcript(res_bad.content_id)
        assert raw_bad is not None
        assert "Body content surviving bad YAML" in raw_bad.body

        # Unclosed frontmatter (no closing ---) is treated directly as body
        f_no_close = tmp_path / "no_close.md"
        f_no_close.write_text(
            "---\ntitle: Unclosed without closing delimiter\nJust plain body text.",
            encoding="utf-8",
        )
        res_no_close = pipeline.run_for_text_file(f_no_close)
        assert res_no_close.success is True
        raw_no_close = vault.get_raw_transcript(res_no_close.content_id)
        assert raw_no_close is not None
        assert "Just plain body text." in raw_no_close.body

    def test_run_for_manifest_parameters_passthrough(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest_params.txt"
        manifest.write_text(
            "https://youtube.com/watch?v=paramVid123\n",
            encoding="utf-8",
        )

        cid = ContentId("paramVid123")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw transcript for manifest param test.",
        )
        vault = InMemoryVaultAdapter()
        ledger = InMemoryLedgerAdapter()
        pipeline = CresmoPipeline(
            media_ingestion_port=MockMediaIngestionPort(canned_transcript=canned_raw),
            llm_port=SmartMockLLMAdapter(),
            vault_port=vault,
            ledger_port=ledger,
        )

        # Run with gap_filler_passes = 2 (Stage 2 sets passes=2, Stage 3 increments to 3)
        results = pipeline.run_for_manifest(manifest, gap_filler_passes=2)
        assert len(results) == 1
        assert results[0].success is True
        comp = vault.get_enriched_compendium(cid)
        assert comp is not None
        assert comp.pass_count == 3

        # Second run without force_reprocess is skipped as already processed
        results_cached = pipeline.run_for_manifest(manifest, force_reprocess=False)
        assert results_cached[0].already_processed is True

        # Third run with force_reprocess = True executes
        results_force = pipeline.run_for_manifest(manifest, force_reprocess=True)
        assert results_force[0].already_processed is False
        assert results_force[0].success is True
