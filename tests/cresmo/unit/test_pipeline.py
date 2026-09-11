"""Unit test for Cresmo end-to-end 6-stage Pipeline Orchestration.

Verifies complete causal flow across all 6 incremental integer stages:
Stage 1 (Raw Transcript) -> Stage 2 (Gap Filler) -> Stage 3 (Expander)
-> Stage 4 (Inventory) -> Stage 5 (Batch) -> Stage 6 (MOC).
"""

from __future__ import annotations

from cresmo.application.pipeline import CresmoPipeline, PipelineResult
from cresmo.domain.entities import RawTranscript
from cresmo.domain.value_objects import ContentId
from cresmo.infrastructure.adapters.mock_adapters import (
    InMemoryLedgerAdapter,
    InMemoryVaultAdapter,
    MockLLMAdapter,
    MockMediaIngestionPort,
)


class TestCresmoPipelineOrchestration:
    """Hermetic unit tests for the 6-stage pipeline orchestration."""

    def test_pipeline_full_cycle_success(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        canned_raw = RawTranscript(
            content_id=cid,
            channel_name="Political Theory",
            body="Raw spoken audio transcript regarding Vilfredo Pareto and elites.",
        )

        gap_filler_llm = (
            "# Teoria das Elites\n\n"
            "A teoria da circulação das elites postula que minorias organizadas governam maiorias.\n\n"
            "## Informações Complementares\n\n"
            "Análise sociológica e precursores históricos."
        )
        expander_llm = (
            "Texto expandido com longa duração e dinâmica axial sincrônica.\n\n"
            "## Informações Complementares\n\n"
            "Matrizes históricas aprofundadas."
        )
        inventory_llm = '[{"title": "Vilfredo Pareto", "type": "entity"}]'
        batch_llm = (
            '[{"title": "Vilfredo Pareto", "type": "entity", '
            '"definition": "Sociólogo e economista italiano formulador do conceito de circulação das elites.", '
            '"direct_relations": ["Teoria das Elites"], '
            '"causal_matrix": {"cause": "Heterogeneidade social", "effect": "Substituição cíclica de lideranças"}}]'
        )
        moc_llm = (
            '[{"title": "MOC Teoria Politica", "theme": "Ciência Política", '
            '"overview": "Mapeamento das teorias de liderança.", '
            '"associated_notes": ["Vilfredo Pareto"]}]'
        )

        mock_llm = MockLLMAdapter(
            responses=[
                gap_filler_llm,  # Gap Filler
                expander_llm,  # Longitudinal Expander
                expander_llm,  # Synchronic Expander
                inventory_llm,  # Inventory Discovery
                batch_llm,  # Batched Synthesis
                moc_llm,  # MOC Reconciliation
            ]
        )
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
        assert ledger_port.is_processed(cid) is True
