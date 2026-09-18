"""Unit tests for IndexRawTranscriptsUseCase.

Verifies single-transcript indexing, idempotency skipping, paratactic parsing,
dual output persistence (_canal.md and brain.csv), channel batching, and error resilience.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.index_raw_transcripts import (
    IndexRawTranscriptsUseCase,
    parse_judge_boolean,
)
from cresmo.domain.entities import RawTranscript
from cresmo.domain.value_objects import ContentId
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from tests.doubles.mock_adapters import InMemoryVaultAdapter, MockLLMAdapter


class TestIndexRawTranscriptsUseCase:
    """Hermetic unit tests for IndexRawTranscriptsUseCase."""

    def test_index_single_transcript_success(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo conceitual da teoria das elites e oligarquias organizadas.",
                "true",
                "Circulação de Elites",
                "true",
                "Minorias burocráticas governam as instituições políticas. A decadência dos governantes precipita a substituição por novas contra-elites organizadas.",
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
            title="Vilfredo Pareto and Elites",
            body="A teoria sociológica de Vilfredo Pareto enfatiza a inevitabilidade das oligarquias.",
            source_url="https://youtube.com/watch?v=vid11111111",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert entry.video_id == ContentId("vid11111111")
        assert entry.key_concept == "Circulação de Elites"
        assert "Minorias burocráticas governam" in entry.synthesis
        assert entry.channel_name == "Political Theory"

        # 5 sequential passes executed: Summary -> Summary Judge -> Concepts -> Concepts Judge -> Synthesis
        assert len(llm.call_history) == 5
        assert llm.call_history[0]["trace_id"] == "vid11111111_summary"
        assert llm.call_history[0]["temperature"] == 0.2
        assert llm.call_history[1]["trace_id"] == "vid11111111_summary_judge"
        assert llm.call_history[1]["temperature"] == 0.0
        assert llm.call_history[2]["trace_id"] == "vid11111111_concepts"
        assert llm.call_history[2]["temperature"] == 0.2
        assert llm.call_history[3]["trace_id"] == "vid11111111_concepts_judge"
        assert llm.call_history[3]["temperature"] == 0.0
        assert llm.call_history[4]["trace_id"] == "vid11111111_synthesis"
        assert llm.call_history[4]["temperature"] == 0.2

        # Verify dual persistence: _canal.md index AND brain.csv
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1
        assert vault.channel_raw_indexes["Political Theory"][0] == entry
        assert len(vault.brain_csv_entries) == 1
        assert vault.brain_csv_entries[0] == entry

    def test_index_single_transcript_idempotent_skip(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(responses=["Resumo.", "true", "Conceito", "true", "Síntese."])
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid11111111"),
            channel_name="Political Theory",
            title="Vilfredo Pareto and Elites",
            body="Body text...",
        )

        # Index once
        entry1 = use_case.index_single_transcript(transcript)
        assert entry1 is not None
        assert len(llm.call_history) == 5

        # Index again without force - should skip and return None (0 additional calls)
        entry2 = use_case.index_single_transcript(transcript)
        assert entry2 is None
        assert len(llm.call_history) == 5
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1

    def test_index_single_transcript_handles_legacy_comma_format(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo sobre equilíbrio de Nash e estratégias interdependentes.",
                "true",
                "Teoria dos Jogos, Equilíbrios de Nash",
                "true",
                "Equilíbrios de Nash determinam estratégias ótimas em sistemas competitivos interdependentes.",
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
            title="Nash Equilibrium",
            body="Jogo não-cooperativo...",
        )

        entry = use_case.index_single_transcript(transcript)
        assert entry is not None
        assert entry.key_concept == "Teoria dos Jogos, Equilíbrios de Nash"
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
            title="AI Systems",
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
                "Resumo 1",
                "true",
                "Conceito Um",
                "true",
                "Síntese um.",
                "Resumo 2",
                "true",
                "Conceito Dois",
                "true",
                "Síntese dois.",
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
            title="Video 1",
            body="Conteúdo 1",
        )
        t2 = RawTranscript(
            content_id=ContentId("vid22222222"),
            channel_name="Canal Teste",
            title="Video 2",
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

    def test_self_healing_rewrite_loop_triggered_when_forbidden_prefix_returned(self) -> None:
        """Verify that when LLM returns forbidden prefix on concepts, a rewrite is requested."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo sobre Pareto e teoria das elites.",
                "true",
                "Key concepts: Circulação de Elites",
                "Circulação de Elites, Teoria das Elites",
                "true",
                "Minorias burocráticas governam as instituições políticas.",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            temperature=0.2,
            language="Português do Brasil",
            max_rewrites=3,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid44444444"),
            channel_name="Political Theory",
            title="Vilfredo Pareto and Elites",
            body="A teoria sociológica de Vilfredo Pareto...",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert entry.key_concept == "Circulação de Elites, Teoria das Elites"
        # 1 summary + 1 summary judge + 1 bad concepts + 1 rewrite + 1 concepts judge + 1 synthesis = 6 calls
        assert len(llm.call_history) == 6
        assert llm.call_history[0]["trace_id"] == "vid44444444_summary"
        assert llm.call_history[1]["trace_id"] == "vid44444444_summary_judge"
        assert llm.call_history[2]["trace_id"] == "vid44444444_concepts"
        assert llm.call_history[3]["trace_id"] == "vid44444444_concepts_rewrite_1"
        assert llm.call_history[4]["trace_id"] == "vid44444444_concepts_judge_retry_1"
        assert llm.call_history[4]["temperature"] == 0.0
        assert llm.call_history[5]["trace_id"] == "vid44444444_synthesis"

    def test_self_healing_rewrite_loop_exhausts_retries_and_defensively_cleans(self) -> None:
        """Verify that when LLM keeps returning forbidden prefix, retries stop at max_rewrites and cleans."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo teórico...",
                "true",
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Síntese analítica.",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid55555555"),
            channel_name="Theory",
            title="Theoretical Notes",
            body="Conteúdo...",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        # Defensively cleaned even though rewrite loop exhausted
        assert entry.key_concept == "Conceito Teórico"
        # 1 summary + 1 summary judge + 1 initial concept + 2 rewrites + 1 synthesis = 6 calls
        assert len(llm.call_history) == 6

    def test_summary_judge_triggers_regeneration_on_false(self) -> None:
        """Verify that when summary judge returns false, summary is regenerated and re-judged."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo superficial com alucinação.",
                "false",
                "Resumo rigoroso e conceitualmente fiel.",
                "true",
                "Conceito Fiel",
                "true",
                "Síntese paratática final.",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid77777777"),
            channel_name="Philosophy",
            title="Concept Analysis",
            body="Detailed text on philosophy...",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Fiel"
        assert len(llm.call_history) == 7
        assert llm.call_history[0]["trace_id"] == "vid77777777_summary"
        assert llm.call_history[1]["trace_id"] == "vid77777777_summary_judge"
        assert llm.call_history[2]["trace_id"] == "vid77777777_summary_retry_1"
        assert llm.call_history[3]["trace_id"] == "vid77777777_summary_judge_retry_1"
        assert llm.call_history[4]["trace_id"] == "vid77777777_concepts"
        assert llm.call_history[5]["trace_id"] == "vid77777777_concepts_judge"
        assert llm.call_history[6]["trace_id"] == "vid77777777_synthesis"

    def test_concepts_judge_triggers_rewrite_on_false(self) -> None:
        """Verify that when concepts pass regex but judge returns false, rewrite is triggered."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Resumo fiel do conteúdo.",
                "true",
                "Conceito Desconexo",
                "false",
                "Conceito Conexo, Teoria Central",
                "true",
                "Síntese estruturada.",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = RawTranscript(
            content_id=ContentId("vid88888888"),
            channel_name="Sociology",
            title="Social Dynamics",
            body="Sociology transcript body...",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Conexo, Teoria Central"
        assert len(llm.call_history) == 7
        assert llm.call_history[2]["trace_id"] == "vid88888888_concepts"
        assert llm.call_history[3]["trace_id"] == "vid88888888_concepts_judge"
        assert llm.call_history[4]["trace_id"] == "vid88888888_concepts_rewrite_1"
        assert llm.call_history[5]["trace_id"] == "vid88888888_concepts_judge_retry_1"
        assert llm.call_history[6]["trace_id"] == "vid88888888_synthesis"

    def test_index_single_transcript_passes_configured_temperature(self) -> None:
        """Verify that configured temperature is passed to generative transformations and 0.0 to judges."""
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = [
            "Resumo explicativo.",
            "true",
            "Conceito",
            "true",
            "Síntese paratática explicativa.",
        ]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=mock_llm,
            prompt_provider=prompt_provider,
            temperature=0.35,
            language="Português do Brasil",
        )

        transcript = RawTranscript(
            content_id=ContentId("vid66666666"),
            channel_name="Science",
            title="Physics",
            body="Physics transcript...",
        )

        entry = use_case.index_single_transcript(transcript)

        assert entry is not None
        assert mock_llm.transform.call_count == 5
        calls = mock_llm.transform.call_args_list
        # Generative passes use configured temperature (0.35)
        assert calls[0][1]["temperature"] == 0.35
        assert calls[2][1]["temperature"] == 0.35
        assert calls[4][1]["temperature"] == 0.35
        # Judge passes use deterministic temperature (0.0)
        assert calls[1][1]["temperature"] == 0.0
        assert calls[3][1]["temperature"] == 0.0

    def test_parse_judge_boolean_edge_cases(self) -> None:
        """Verify deterministic parsing of judge true/false outputs."""
        assert parse_judge_boolean("true") is True
        assert parse_judge_boolean("True") is True
        assert parse_judge_boolean("TRUE.") is True
        assert parse_judge_boolean("true\n") is True
        assert parse_judge_boolean("```\ntrue\n```") is True
        assert parse_judge_boolean("```json\ntrue\n```") is True
        assert parse_judge_boolean("true - compliant with all guidelines") is True

        assert parse_judge_boolean("false") is False
        assert parse_judge_boolean("False") is False
        assert parse_judge_boolean("FALSE.") is False
        assert parse_judge_boolean("```\nfalse\n```") is False
        assert parse_judge_boolean("") is False
        assert parse_judge_boolean("unclear") is False
        assert parse_judge_boolean("no") is False
