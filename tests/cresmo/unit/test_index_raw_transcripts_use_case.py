"""Unit tests for IndexRawTranscriptsUseCase.

Verifies single-transcript indexing, idempotency skipping, paratactic parsing,
dual output persistence (_canal.md and brain.csv), channel batching, and error resilience.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.domain.entities import RawTranscript
from cresmo.domain.value_objects import ContentId, NoteTitle
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from tests.doubles.mock_adapters import InMemoryVaultAdapter, MockLLMAdapter


class TestIndexRawTranscriptsUseCase:
    """Hermetic unit tests for IndexRawTranscriptsUseCase."""

    def test_index_single_transcript_success(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Circulação de Elites\nMinorias burocráticas governam as instituições políticas. A decadência dos governantes precipita a substituição por novas contra-elites organizadas."
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid11111111"),
            channel_name="Political Theory",
            title=NoteTitle("Vilfredo Pareto and Elites"),
            body="A teoria sociológica de Vilfredo Pareto enfatiza a inevitabilidade das oligarquias.",
            source_url="https://youtube.com/watch?v=vid11111111",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert entry.video_id == ContentId("vid11111111")
        assert entry.key_concept == "Circulação de Elites"
        assert "Minorias burocráticas governam" in entry.synthesis
        assert entry.channel_name == "Political Theory"

        # Verify dual persistence: _canal.md index AND brain.csv
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1
        assert vault.channel_raw_indexes["Political Theory"][0] == entry
        assert len(vault.brain_csv_entries) == 1
        assert vault.brain_csv_entries[0] == entry

    def test_index_single_transcript_idempotent_skip(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(responses=["Conceito\nSíntese."])
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid11111111"),
            channel_name="Political Theory",
            title=NoteTitle("Vilfredo Pareto and Elites"),
            body="Body text...",
        )

        # Index once
        entry1 = use_case.index_single_transcript(transcript)
        assert entry1 is not None

        # Index again without force - should skip and return None
        entry2 = use_case.index_single_transcript(transcript)
        assert entry2 is None
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1

    def test_index_single_transcript_handles_legacy_comma_format(self) -> None:
        vault = InMemoryVaultAdapter()
        # LLM returns single line with comma: "<Concept>, <Synthesis>"
        llm = MockLLMAdapter(
            responses=[
                "Teoria dos Jogos, Equilíbrios de Nash determinam estratégias ótimas em sistemas competitivos interdependentes."
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid22222222"),
            channel_name="Economics",
            title=NoteTitle("Nash Equilibrium"),
            body="Jogo não-cooperativo...",
        )

        entry = use_case.index_single_transcript(transcript)
        assert entry is not None
        assert entry.key_concept == "Teoria dos Jogos"
        assert "Equilíbrios de Nash determinam" in entry.synthesis

    def test_index_single_transcript_resilient_to_llm_failure(self) -> None:
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = RuntimeError("Ollama connection failed")
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=mock_llm,
            prompt_provider=prompt_provider,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid33333333"),
            channel_name="Tech Channel",
            title=NoteTitle("AI Systems"),
            body="AI body...",
        )

        # Should not raise exception, logs warning and returns None
        entry = use_case.index_single_transcript(transcript)
        assert entry is None
        assert len(vault.channel_raw_indexes) == 0

    def test_index_channel_processes_all_unindexed_files(self, tmp_path: Path) -> None:
        from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter

        vault = ObsidianVaultAdapter(
            vault_dir=tmp_path / "vault",
            raw_dir=tmp_path / "raw",
            enriched_dir=tmp_path / "enriched",
        )
        llm = MockLLMAdapter(
            responses=[
                "Conceito Um\nSíntese um.",
                "Conceito Dois\nSíntese dois.",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        t1 = RawTranscript(
            content_id=ContentId("vid11111111"),
            channel_name="Canal Teste",
            title=NoteTitle("Video 1"),
            body="Conteúdo 1",
        )
        t2 = RawTranscript(
            content_id=ContentId("vid22222222"),
            channel_name="Canal Teste",
            title=NoteTitle("Video 2"),
            body="Conteúdo 2",
        )
        vault.save_raw_transcript(t1)
        vault.save_raw_transcript(t2)

        # Index channel
        entries = use_case.index_channel("Canal Teste")
        assert len(entries) == 2
        assert entries[0].key_concept == "Conceito Um"
        assert entries[1].key_concept == "Conceito Dois"

        # Calling again should skip already indexed
        entries_again = use_case.index_channel("Canal Teste")
        assert len(entries_again) == 0

