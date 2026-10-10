"""Unit tests for IndexRawTranscriptsUseCase.

Verifies single-transcript indexing, idempotency skipping, paratactic parsing,
dual output persistence (_canal.md and brain.csv), channel batching, and error resilience,
now enhanced with LLM-as-a-judge synthesis verification, sizing heuristics, and configurable loops.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from cresmo.application.use_cases.index_raw_transcripts import (
    IndexRawTranscriptsUseCase,
    is_valid_synthesis_paragraph,
    parse_judge_boolean,
)
from cresmo.domain.entities import FluidTranscript, SourceTranscript
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import ChannelName, ContentId
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from tests.doubles.mock_adapters import InMemoryVaultAdapter, MockLLMAdapter

_SAMPLE_VALID_SYNTHESIS = (
    "Minorias burocráticas governam as instituições políticas centrais. "
    "A decadência dos governantes precipita a substituição por novas contra-elites "
    "organizadas em estruturas institucionais complexas e altamente resilientes."
)


class TestIndexRawTranscriptsUseCase:
    """Hermetic unit tests for IndexRawTranscriptsUseCase."""

    def test_index_single_transcript_success(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Circulação de Elites",
                "true",
                "Resumo conceitual da teoria das elites e oligarquias organizadas.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid11111111"),
            channel_name=ChannelName("Political Theory"),
            title="Vilfredo Pareto and Elites",
            body="A teoria sociológica de Vilfredo Pareto enfatiza a inevitabilidade das oligarquias.",
            source_url="https://youtube.com/watch?v=vid11111111",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.video_id == ContentId("vid11111111")
        assert entry.title == "Vilfredo Pareto and Elites"
        assert entry.key_concept == "Circulação de Elites"
        assert "Minorias burocráticas governam" in entry.synthesis
        assert entry.channel_name == "Political Theory"
        assert entry.summary == "Resumo conceitual da teoria das elites e oligarquias organizadas."
        assert (
            entry.excerpt
            == "A teoria sociológica de Vilfredo Pareto enfatiza a inevitabilidade das oligarquias."
        )

        # 6 sequential passes executed: Concepts -> Concepts Judge -> Summary -> Summary Judge -> Synthesis -> Synthesis Judge
        assert len(llm.call_history) == 6
        assert llm.call_history[0]["trace_id"] == "vid11111111_concepts"
        assert llm.call_history[0]["temperature"] == 0.2
        assert llm.call_history[0]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[0]["user_id"] == "anonymous"
        assert llm.call_history[1]["trace_id"] == "vid11111111_concepts_judge"
        assert llm.call_history[1]["temperature"] == 0.0
        assert llm.call_history[1]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[1]["user_id"] == "anonymous"
        assert llm.call_history[2]["trace_id"] == "vid11111111_summary"
        assert llm.call_history[2]["temperature"] == 0.2
        assert llm.call_history[2]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[2]["user_id"] == "anonymous"
        assert llm.call_history[3]["trace_id"] == "vid11111111_summary_judge"
        assert llm.call_history[3]["temperature"] == 0.0
        assert llm.call_history[3]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[3]["user_id"] == "anonymous"
        assert llm.call_history[4]["trace_id"] == "vid11111111_synthesis"
        assert llm.call_history[4]["temperature"] == 0.2
        assert llm.call_history[4]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[4]["user_id"] == "anonymous"
        assert llm.call_history[5]["trace_id"] == "vid11111111_synthesis_judge"
        assert llm.call_history[5]["temperature"] == 0.0
        assert llm.call_history[5]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[5]["user_id"] == "anonymous"

        # Verify dual persistence: _canal.md index AND brain.csv
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1
        assert vault.channel_raw_indexes["Political Theory"][0] == entry
        assert len(vault.brain_csv_entries) == 1
        assert vault.brain_csv_entries[0] == entry

        # Verify exact log formatting on completion
        expected_log = f"[IndexRaw] Indexed '{entry.video_id}' | {entry.channel_name} | '{entry.key_concept}'"
        assert any(
            r.levelno == logging.INFO and r.getMessage() == expected_log
            for r in caplog.records
        )

    def test_index_single_transcript_idempotent_skip(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=["Conceito", "true", "Resumo.", "true", _SAMPLE_VALID_SYNTHESIS, "true"]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid11111111"),
            channel_name=ChannelName("Political Theory"),
            title="Vilfredo Pareto and Elites",
            body="Body text...",
        )

        # Index once
        entry1 = use_case.execute(transcript)
        assert entry1 is not None
        assert len(llm.call_history) == 6

        # Index again without force - should skip and return None (0 additional calls)
        entry2 = use_case.execute(transcript)
        assert entry2 is None
        assert len(llm.call_history) == 6
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1

        expected_skip_log = (
            f"[IndexRaw] Skipping already indexed transcript '{transcript.content.id.value}' for channel '{transcript.channel.name}'."
        )
        assert any(
            r.levelno == logging.INFO and r.getMessage() == expected_skip_log
            for r in caplog.records
        )

    def test_index_single_transcript_handles_legacy_comma_format(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Teoria dos Jogos, Equilíbrios de Nash",
                "true",
                "Resumo sobre equilíbrio de Nash e estratégias interdependentes.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid22222222"),
            channel_name=ChannelName("Economics"),
            title="Nash Equilibrium",
            body="Jogo não-cooperativo...",
        )

        entry = use_case.execute(transcript)
        assert entry is not None
        assert entry.key_concept == "Teoria dos Jogos, Equilíbrios de Nash"
        assert "Minorias burocráticas governam" in entry.synthesis

    def test_index_single_transcript_resilient_to_llm_failure(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.WARNING)
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = RuntimeError("Ollama connection failed")
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=mock_llm,
            prompt_provider=prompt_provider,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid33333333"),
            channel_name=ChannelName("Tech Channel"),
            title="AI Systems",
            body="AI body...",
        )

        # Should not raise exception, logs warning and returns None
        entry = use_case.execute(transcript)
        assert entry is None
        assert len(vault.channel_raw_indexes) == 0

        expected_warn_log = (
            f"[IndexRaw] Skipped '{transcript.content.id}' ({transcript.channel.name}) due to inference error: Ollama connection failed"
        )
        matching_warns = [
            r for r in caplog.records
            if r.levelno == logging.WARNING and r.getMessage() == expected_warn_log
        ]
        assert len(matching_warns) == 1
        warn_rec = matching_warns[0]
        assert warn_rec.exc_info is not None
        assert isinstance(warn_rec.exc_info, tuple)
        assert len(warn_rec.exc_info) == 3
        assert isinstance(warn_rec.exc_info[1], RuntimeError)

    def test_index_raw_rejects_raw_transcript(self) -> None:
        """ADR-028: IndexRawTranscriptsUseCase strictly rejects SourceTranscript."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter()
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
        )
        raw = SourceTranscript(
            content_id=ContentId("vidraw001"),
            channel_name=ChannelName("Canal Teste"),
            title="Video Raw",
            body="Raw spoken text with verbal noise.",
        )
        with pytest.raises(
            DomainValidationError,
            match="IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: SourceTranscript",
        ):
            use_case.execute(raw)  # type: ignore[arg-type]

        with pytest.raises(
            DomainValidationError,
            match="IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: int",
        ):
            use_case.execute(12345)  # type: ignore[arg-type]

    def test_self_healing_rewrite_loop_triggered_when_forbidden_prefix_returned(self) -> None:
        """Verify that when LLM returns forbidden prefix on concepts, a rewrite is requested."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Key concepts: Circulação de Elites",
                "Circulação de Elites, Teoria das Elites",
                "true",
                "Resumo sobre Pareto e teoria das elites.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
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

        transcript = FluidTranscript(
            content_id=ContentId("vid44444444"),
            channel_name=ChannelName("Political Theory"),
            title="Vilfredo Pareto and Elites",
            body="A teoria sociológica de Vilfredo Pareto...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Circulação de Elites, Teoria das Elites"
        # 1 bad concepts + 1 rewrite + 1 concepts judge + 1 summary + 1 summary judge + 1 synthesis + 1 synthesis judge = 7 calls
        assert len(llm.call_history) == 7
        assert llm.call_history[0]["trace_id"] == "vid44444444_concepts"
        assert llm.call_history[1]["trace_id"] == "vid44444444_concepts_rewrite_1"
        assert llm.call_history[2]["trace_id"] == "vid44444444_concepts_judge_retry_1"
        assert llm.call_history[2]["temperature"] == 0.0
        assert llm.call_history[3]["trace_id"] == "vid44444444_summary"
        assert llm.call_history[4]["trace_id"] == "vid44444444_summary_judge"
        assert llm.call_history[4]["temperature"] == 0.0
        assert llm.call_history[5]["trace_id"] == "vid44444444_synthesis"
        assert llm.call_history[6]["trace_id"] == "vid44444444_synthesis_judge"

    def test_self_healing_rewrite_loop_exhausts_retries_and_defensively_cleans(self) -> None:
        """Verify that when LLM keeps returning forbidden prefix, retries stop at max_rewrites and cleans."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Resumo teórico...",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid55555555"),
            channel_name=ChannelName("Theory"),
            title="Theoretical Notes",
            body="Conteúdo...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        # Defensively cleaned even though rewrite loop exhausted
        assert entry.key_concept == "Conceito Teórico"
        # 1 initial concept + 2 rewrites + 1 summary + 1 summary judge + 1 synthesis + 1 synthesis judge = 7 calls
        assert len(llm.call_history) == 7
        assert llm.call_history[0]["trace_id"] == "vid55555555_concepts"
        assert llm.call_history[1]["trace_id"] == "vid55555555_concepts_rewrite_1"
        assert llm.call_history[2]["trace_id"] == "vid55555555_concepts_rewrite_2"
        assert llm.call_history[3]["trace_id"] == "vid55555555_summary"
        assert llm.call_history[4]["trace_id"] == "vid55555555_summary_judge"
        assert llm.call_history[5]["trace_id"] == "vid55555555_synthesis"
        assert llm.call_history[6]["trace_id"] == "vid55555555_synthesis_judge"

    def test_summary_judge_triggers_regeneration_on_false(self) -> None:
        """Verify that when summary judge returns false, summary is regenerated and re-judged."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Fiel",
                "true",
                "Resumo superficial com alucinação.",
                "false",
                "Resumo rigoroso e conceitualmente fiel.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid77777777"),
            channel_name=ChannelName("Philosophy"),
            title="Concept Analysis",
            body="Detailed text on philosophy...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Fiel"
        assert len(llm.call_history) == 8
        assert llm.call_history[0]["trace_id"] == "vid77777777_concepts"
        assert llm.call_history[1]["trace_id"] == "vid77777777_concepts_judge"
        assert llm.call_history[2]["trace_id"] == "vid77777777_summary"
        assert llm.call_history[3]["trace_id"] == "vid77777777_summary_judge"
        assert llm.call_history[4]["trace_id"] == "vid77777777_summary_retry_1"
        assert llm.call_history[5]["trace_id"] == "vid77777777_summary_judge_retry_1"
        assert llm.call_history[6]["trace_id"] == "vid77777777_synthesis"
        assert llm.call_history[7]["trace_id"] == "vid77777777_synthesis_judge"

    def test_concepts_judge_triggers_rewrite_on_false(self) -> None:
        """Verify that when concepts pass regex but judge returns false, rewrite is triggered."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Desconexo",
                "false",
                "Conceito Conexo, Teoria Central",
                "true",
                "Resumo fiel do conteúdo.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid88888888"),
            channel_name=ChannelName("Sociology"),
            title="Social Dynamics",
            body="Sociology transcript body...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Conexo, Teoria Central"
        assert len(llm.call_history) == 8
        assert llm.call_history[0]["trace_id"] == "vid88888888_concepts"
        assert llm.call_history[1]["trace_id"] == "vid88888888_concepts_judge"
        assert llm.call_history[2]["trace_id"] == "vid88888888_concepts_rewrite_1"
        assert llm.call_history[3]["trace_id"] == "vid88888888_concepts_judge_retry_1"
        assert llm.call_history[4]["trace_id"] == "vid88888888_summary"
        assert llm.call_history[5]["trace_id"] == "vid88888888_summary_judge"
        assert llm.call_history[6]["trace_id"] == "vid88888888_synthesis"
        assert llm.call_history[7]["trace_id"] == "vid88888888_synthesis_judge"

    def test_synthesis_judge_triggers_regeneration_on_false(self) -> None:
        """Verify that when synthesis judge returns false, synthesis is regenerated and re-judged."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Sólido",
                "true",
                "Resumo bem estruturado.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "false",  # Initial synthesis judged false (e.g. slight factual hallucination)
                "Minorias políticas burocráticas governam as instituições com base em normas estritas e transparentes. As contra-elites organizadas substituem a liderança decadente e reconfiguram as decisões estruturais.",
                "true",  # Regenerated synthesis judged true
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid99999999"),
            channel_name=ChannelName("Political Theory"),
            title="Pareto Dynamics",
            body="Sociological dynamics...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Sólido"
        assert "Minorias políticas burocráticas governam" in entry.synthesis
        # 1 concepts + 1 concepts_judge + 1 summary + 1 summary_judge + 1 synthesis + 1 synthesis_judge (false) + 1 retry + 1 retry_judge (true) = 8 calls
        assert len(llm.call_history) == 8
        assert llm.call_history[4]["trace_id"] == "vid99999999_synthesis"
        assert llm.call_history[5]["trace_id"] == "vid99999999_synthesis_judge"
        assert llm.call_history[5]["temperature"] == 0.0
        assert llm.call_history[6]["trace_id"] == "vid99999999_synthesis_retry_1"
        assert llm.call_history[7]["trace_id"] == "vid99999999_synthesis_judge_retry_1"
        assert llm.call_history[7]["temperature"] == 0.0

    def test_synthesis_size_invalidation_triggers_retry(self) -> None:
        """Verify that when synthesis fails sizing heuristic (e.g. too few words), judge is skipped and retry triggered."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito",
                "true",
                "Resumo completo.",
                "true",
                "Texto curto demais.",  # 3 words -> fails min_words heuristic
                _SAMPLE_VALID_SYNTHESIS,  # Valid size
                "true",  # Judge confirms
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vidsize123"),
            channel_name=ChannelName("General"),
            title="Size Validation Test",
            body="Body content...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.synthesis == _SAMPLE_VALID_SYNTHESIS
        # 1 concepts + 1 judge + 1 summary + 1 judge + 1 short_syn (no judge!) + 1 retry_syn + 1 judge = 7 calls
        assert len(llm.call_history) == 7
        assert llm.call_history[4]["trace_id"] == "vidsize123_synthesis"
        assert llm.call_history[5]["trace_id"] == "vidsize123_synthesis_retry_1"
        assert llm.call_history[6]["trace_id"] == "vidsize123_synthesis_judge_retry_1"

    def test_infinite_retry_loop_when_max_rewrites_is_zero(self) -> None:
        """Verify that max_rewrites=0 allows unconstrained retries without aborting early."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Central",
                "true",
                "Resumo inicial.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "false",  # Attempt 0 fails judge
                _SAMPLE_VALID_SYNTHESIS,
                "false",  # Attempt 1 fails judge
                _SAMPLE_VALID_SYNTHESIS,
                "false",  # Attempt 2 fails judge
                _SAMPLE_VALID_SYNTHESIS,
                "false",  # Attempt 3 fails judge (> 3 attempts!)
                _SAMPLE_VALID_SYNTHESIS,
                "true",  # Attempt 4 succeeds
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=llm,
            prompt_provider=prompt_provider,
            max_rewrites=0,  # Unbounded / infinite loop mode
        )

        transcript = FluidTranscript(
            content_id=ContentId("vidinfinite"),
            channel_name=ChannelName("Perseverance"),
            title="Infinite Retries",
            body="Infinite attempt body...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Central"
        # 1 concepts + 1 judge + 1 summary + 1 judge + 5 synthesis calls + 5 judge calls = 14 calls
        assert len(llm.call_history) == 14
        assert llm.call_history[-2]["trace_id"] == "vidinfinite_synthesis_retry_4"
        assert llm.call_history[-1]["trace_id"] == "vidinfinite_synthesis_judge_retry_4"

    def test_is_valid_synthesis_paragraph_heuristic(self) -> None:
        """Verify the standalone synthesis paragraph heuristic function."""
        # Empty text
        assert not is_valid_synthesis_paragraph("")
        assert not is_valid_synthesis_paragraph("   ")

        # Forbidden prefix
        assert not is_valid_synthesis_paragraph("Síntese: " + _SAMPLE_VALID_SYNTHESIS)
        assert not is_valid_synthesis_paragraph("Key concepts: " + _SAMPLE_VALID_SYNTHESIS)

        # Markdown bullet list
        assert not is_valid_synthesis_paragraph(
            "- Ponto 1\n- Ponto 2 com palavras suficientes para atingir o tamanho"
        )

        # Multiple paragraphs separated by blank line
        assert not is_valid_synthesis_paragraph(
            "Parágrafo um de texto com muitas palavras.\n\nParágrafo dois também com muitas palavras."
        )

        # Too short (< 20 words)
        assert not is_valid_synthesis_paragraph("Apenas algumas palavras aqui.")

        # Valid single paragraph
        assert is_valid_synthesis_paragraph(_SAMPLE_VALID_SYNTHESIS)

    def test_index_single_transcript_passes_configured_temperature(self) -> None:
        """Verify that configured temperature is passed to generative transformations and 0.0 to judges."""
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = [
            "Conceito",
            "true",
            "Resumo explicativo.",
            "true",
            _SAMPLE_VALID_SYNTHESIS,
            "true",
        ]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_repo=vault,
            llm=mock_llm,
            prompt_provider=prompt_provider,
            temperature=0.35,
            language="Português do Brasil",
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid66666666"),
            channel_name=ChannelName("Science"),
            title="Physics",
            body="Physics transcript...",
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert mock_llm.transform.call_count == 6
        calls = mock_llm.transform.call_args_list
        # Generative passes use configured temperature (0.35): Pass 1 concepts, Pass 2 summary, Pass 3 synthesis
        assert calls[0][1]["temperature"] == 0.35
        assert calls[2][1]["temperature"] == 0.35
        assert calls[4][1]["temperature"] == 0.35
        # Judge passes use deterministic temperature (0.0): Pass 1 concepts judge, Pass 2 summary judge, Pass 3 synthesis judge
        assert calls[1][1]["temperature"] == 0.0
        assert calls[3][1]["temperature"] == 0.0
        assert calls[5][1]["temperature"] == 0.0

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

    def test_distiller_delegates_to_llm_judge_port_when_provided(self) -> None:
        """Verify LLMTranscriptDistiller delegates 100% to LlmJudgePort when injected (ADR-029)."""
        from cresmo.application.ports import LlmJudgePort
        from cresmo.application.use_cases.indexing.distiller import LLMTranscriptDistiller
        from cresmo.domain.value_objects import JudgeEvaluation

        mock_llm = MagicMock()
        mock_llm.transform.return_value = "Conceito Extraído"
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.return_value = JudgeEvaluation(
            target_stage="raw_indexing_concepts",
            passed=True,
            overall_score=0.92,
            criteria_scores=(),
            provider="gemini",
        )
        prompt_provider = JsonPromptProvider()

        distiller = LLMTranscriptDistiller(
            llm_indexing_port=mock_llm,
            prompt_provider=prompt_provider,
            llm_judge_port=mock_judge,
            max_rewrites=1,
        )

        result = distiller.extract_concepts(
            video_id=ContentId("vid_test_1"),
            title="Video Title",
            text="Video transcript body",
            channel_name=ChannelName("Channel"),
        )
        assert result == "Conceito Extraído"
        mock_judge.evaluate.assert_called_once()
        ctx = mock_judge.evaluate.call_args[0][0]
        assert ctx.stage_name == "raw_indexing_concepts"

    def test_init_defaults_and_attributes(self) -> None:
        """Verify default configuration attributes and alias properties."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter()
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )
        assert use_case.vault_port is vault
        assert use_case.vault_repo is vault
        assert use_case.llm_indexing_port is llm
        assert use_case.llm is llm
        assert use_case.prompt_provider is prompt_provider
        assert use_case.max_chars == 0
        assert use_case.temperature == 0.2
        assert use_case.language == "Português do Brasil"
        assert use_case.max_rewrites == 3
        assert use_case.llm_judge_port is None
        assert use_case._distiller.max_rewrites == 3
        assert use_case._distiller.language == "Português do Brasil"
        assert use_case._distiller.llm_judge_port is None

        mock_judge = MagicMock()
        use_case_with_judge = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            llm_judge_port=mock_judge,
            language="English",
        )
        assert use_case_with_judge.llm_judge_port is mock_judge
        assert use_case_with_judge.language == "English"
        assert use_case_with_judge._distiller.llm_judge_port is mock_judge
        assert use_case_with_judge._distiller.language == "English"

    def test_init_raises_value_error_on_missing_required_ports(self) -> None:
        """Verify fail-fast validation on required ports and prompt provider."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter()
        prompt_provider = JsonPromptProvider()

        with pytest.raises(ValueError) as exc1:
            IndexRawTranscriptsUseCase(
                vault_port=None,
                vault_repo=None,
                llm_indexing_port=llm,
                prompt_provider=prompt_provider,
            )
        assert str(exc1.value) == "vault_port is required."

        with pytest.raises(ValueError) as exc2:
            IndexRawTranscriptsUseCase(
                vault_port=vault,
                llm_indexing_port=None,
                llm=None,
                prompt_provider=prompt_provider,
            )
        assert str(exc2.value) == "llm_indexing_port is required."

        with pytest.raises(ValueError) as exc3:
            IndexRawTranscriptsUseCase(
                vault_port=vault,
                llm_indexing_port=llm,
                prompt_provider=None,
            )
        assert str(exc3.value) == "prompt_provider is required."

    def test_warmup_passes_timeout_seconds(self) -> None:
        """Verify warmup contract forwards timeout_seconds."""
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=mock_llm,
            prompt_provider=prompt_provider,
        )
        use_case.warmup(timeout_seconds=42.0)
        mock_llm.warmup.assert_called_once_with(timeout_seconds=42.0)

    def test_index_single_transcript_excerpt_slicing_and_fallback_title(self) -> None:
        """Verify max_chars excerpt slicing and fallback to video_id when title is empty."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Concept",
                "true",
                "Summary.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_chars=1,
        )

        transcript = FluidTranscript(
            content_id=ContentId("vid_notitle_99"),
            channel_name=ChannelName("3blue1brown"),
            title="",
            body="Long body text...",
        )

        entry = use_case.execute(transcript)
        assert entry is not None
        assert entry.title == "vid_notitle_99"
        assert entry.excerpt == "L"

    def test_execute_forwards_all_arguments_to_distiller(self) -> None:
        """Verify execute forwards all VOs, metadata, and user identity to distiller."""
        from cresmo.domain.entities import UserIdentity
        from cresmo.domain.value_objects import ChannelId

        vault = InMemoryVaultAdapter()
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=MockLLMAdapter(),
            prompt_provider=prompt_provider,
        )

        mock_distiller = MagicMock()
        mock_distiller.extract_concepts.return_value = "Concept Alpha"
        mock_distiller.extract_summary.return_value = "Summary Beta"
        mock_distiller.extract_synthesis.return_value = "Synthesis Gamma"
        use_case._distiller = mock_distiller

        user = UserIdentity("custom_user_123")
        transcript = FluidTranscript(
            content_id=ContentId("vid_args_1"),
            channel_name=ChannelName("TestChannel"),
            channel_id=ChannelId("chan_id_1"),
            title="Title Test",
            body="Body Test",
        )

        entry = use_case.execute(transcript, user=user)
        assert entry is not None
        assert entry.key_concept == "Concept Alpha"
        assert entry.summary == "Summary Beta"
        assert entry.synthesis == "Synthesis Gamma"

        mock_distiller.extract_concepts.assert_called_once_with(
            video_id=ContentId("vid_args_1"),
            title="Title Test",
            text="Body Test",
            channel_name=ChannelName("TestChannel"),
            channel_id=ChannelId("chan_id_1"),
            user=user,
        )
        mock_distiller.extract_summary.assert_called_once_with(
            video_id=ContentId("vid_args_1"),
            title="Title Test",
            text="Body Test",
            channel_name=ChannelName("TestChannel"),
            channel_id=ChannelId("chan_id_1"),
            user=user,
        )
        mock_distiller.extract_synthesis.assert_called_once_with(
            video_id=ContentId("vid_args_1"),
            title="Title Test",
            excerpt="Body Test",
            summary="Summary Beta",
            channel_name=ChannelName("TestChannel"),
            channel_id=ChannelId("chan_id_1"),
            user=user,
        )

    def test_category_explicit_vs_classified_taxonomy(self) -> None:
        """Verify explicit category preservation and deterministic fallback taxonomy."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Concept",
                "true",
                "Summary.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
                "Concept",
                "true",
                "Summary.",
                "true",
                _SAMPLE_VALID_SYNTHESIS,
                "true",
            ]
        )
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )

        # Case A: explicit category with whitespace
        transcript_explicit = FluidTranscript(
            content_id=ContentId("vid_cat_1"),
            channel_name=ChannelName("Generic"),
            channel_category="  Epistemology  ",
            title="Title",
            body="Body",
        )
        entry_explicit = use_case.execute(transcript_explicit)
        assert entry_explicit is not None
        assert entry_explicit.channel_category == "Epistemology"

        # Case B: empty category -> auto-classify by channel name
        transcript_classified = FluidTranscript(
            content_id=ContentId("vid_cat_2"),
            channel_name=ChannelName("3blue1brown"),
            channel_category="",
            title="Title",
            body="Body",
        )
        entry_classified = use_case.execute(transcript_classified)
        assert entry_classified is not None
        assert entry_classified.channel_category == "engineering"
