"""Unit tests for IndexRawTranscriptsUseCase.

Verifies single-transcript indexing, idempotency skipping, paratactic parsing,
dual output persistence (_canal.md and brain.csv), channel batching, and error resilience,
now enhanced with LLM-as-a-judge synthesis verification, sizing heuristics, and configurable loops.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import ChannelTaxonomyPort, LlmJudgePort
from cresmo.application.use_cases.indexing.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.indexing.validators import (
    is_valid_synthesis_paragraph,
)
from cresmo.domain.entities import StageTranscript
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    Channel,
    ChannelName,
    Content,
    ContentId,
    JudgeEvaluation,
    MediaProvenance,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
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
                "Resumo conceitual da teoria das elites e oligarquias organizadas.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Political Theory")),
            provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid11111111"),
            content=Content(
                id=ContentId("vid11111111"),
                title="Vilfredo Pareto and Elites",
                text="A teoria sociológica de Vilfredo Pareto enfatiza a inevitabilidade das oligarquias.",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.video_id == ContentId("vid11111111")
        assert entry.title == "Vilfredo Pareto and Elites"
        assert entry.key_concept == "Circulação de Elites"
        assert "Minorias burocráticas governam" in entry.synthesis
        assert entry.channel_name == "Political Theory"

        # 3 sequential generative passes when no llm_judge_port is attached
        assert len(llm.call_history) == 3
        assert llm.call_history[0]["trace_id"] == "vid11111111_concepts"
        assert llm.call_history[0]["temperature"] == 0.2
        assert llm.call_history[0]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[0]["user_id"] == "anonymous"
        assert llm.call_history[1]["trace_id"] == "vid11111111_summary"
        assert llm.call_history[1]["temperature"] == 0.2
        assert llm.call_history[1]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[1]["user_id"] == "anonymous"
        assert llm.call_history[2]["trace_id"] == "vid11111111_synthesis"
        assert llm.call_history[2]["temperature"] == 0.2
        assert llm.call_history[2]["session_id"] == "Political Theory:vid11111111"
        assert llm.call_history[2]["user_id"] == "anonymous"

        # Verify dual persistence: _canal.md index AND brain.csv
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1
        assert vault.channel_raw_indexes["Political Theory"][0] == entry
        assert len(vault.brain_csv_entries) == 1
        assert vault.brain_csv_entries[0] == entry

        # Verify exact log formatting on completion
        expected_log = (
            f"[IndexRaw] Indexed '{entry.video_id}' | {entry.channel_name} | '{entry.key_concept}'"
        )
        assert any(
            r.levelno == logging.INFO and r.getMessage() == expected_log for r in caplog.records
        )

    def test_index_single_transcript_idempotent_skip(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=["Conceito", "Resumo.", _SAMPLE_VALID_SYNTHESIS]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Political Theory")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid11111111').value}"
            ),
            content=Content(
                id=ContentId("vid11111111"), title="Vilfredo Pareto and Elites", text="Body text..."
            ),
        )

        # Index once
        entry1 = use_case.execute(transcript)
        assert entry1 is not None
        assert len(llm.call_history) == 3

        # Index again without force - should skip and return None (0 additional calls)
        entry2 = use_case.execute(transcript)
        assert entry2 is None
        assert len(llm.call_history) == 3
        assert len(vault.channel_raw_indexes["Political Theory"]) == 1

        expected_skip_log = f"[IndexRaw] Skipping already indexed transcript '{transcript.content.id.value}' for channel '{transcript.channel.name}'."
        assert any(
            r.levelno == logging.INFO and r.getMessage() == expected_skip_log
            for r in caplog.records
        )

    def test_index_single_transcript_handles_legacy_comma_format(self) -> None:
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Teoria dos Jogos, Equilíbrios de Nash",
                "Resumo sobre equilíbrio de Nash e estratégias interdependentes.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Economics")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid22222222').value}"
            ),
            content=Content(
                id=ContentId("vid22222222"),
                title="Nash Equilibrium",
                text="Jogo não-cooperativo...",
            ),
        )

        entry = use_case.execute(transcript)
        assert entry is not None
        assert entry.key_concept == "Teoria dos Jogos, Equilíbrios de Nash"
        assert "Minorias burocráticas governam" in entry.synthesis

    def test_index_single_transcript_resilient_to_llm_failure(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.WARNING)
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = RuntimeError("Ollama connection failed")
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=mock_llm,
            prompt_provider=prompt_provider,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Tech Channel")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid33333333').value}"
            ),
            content=Content(id=ContentId("vid33333333"), title="AI Systems", text="AI body..."),
        )

        # Should not raise exception, logs warning and returns None
        entry = use_case.execute(transcript)
        assert entry is None
        assert len(vault.channel_raw_indexes) == 0

        expected_warn_log = f"[IndexRaw] Skipped '{transcript.content.id}' ({transcript.channel.name}) due to inference error: Ollama connection failed"
        matching_warns = [
            r
            for r in caplog.records
            if r.levelno == logging.WARNING and r.getMessage() == expected_warn_log
        ]
        assert len(matching_warns) == 1
        warn_rec = matching_warns[0]
        has_exc = (
            (warn_rec.exc_info is not None and isinstance(warn_rec.exc_info[1], RuntimeError))
            or getattr(warn_rec, "exception", None) is not None
            or "RuntimeError: Ollama connection failed" in caplog.text
        )
        assert has_exc

    def test_index_raw_rejects_raw_transcript(self) -> None:
        """ADR-028: IndexRawTranscriptsUseCase strictly rejects non-StageTranscript."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter()
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
        )
        with pytest.raises(
            DomainValidationError,
            match="IndexRawTranscriptsUseCase strictly requires StageTranscript, got: str",
        ):
            use_case.execute("invalid string")  # type: ignore[arg-type]

        with pytest.raises(
            DomainValidationError,
            match="IndexRawTranscriptsUseCase strictly requires StageTranscript, got: int",
        ):
            use_case.execute(12345)  # type: ignore[arg-type]

    def test_self_healing_rewrite_loop_triggered_when_forbidden_prefix_returned(self) -> None:
        """Verify that when LLM returns forbidden prefix on concepts, a rewrite is requested."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Key concepts: Circulação de Elites",
                "Circulação de Elites, Teoria das Elites",
                "Resumo sobre Pareto e teoria das elites.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            temperature=0.2,
            language="Português do Brasil",
            max_rewrites=3,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Political Theory")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid44444444').value}"
            ),
            content=Content(
                id=ContentId("vid44444444"),
                title="Vilfredo Pareto and Elites",
                text="A teoria sociológica de Vilfredo Pareto...",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Circulação de Elites, Teoria das Elites"
        assert len(llm.call_history) == 4
        assert llm.call_history[0]["trace_id"] == "vid44444444_concepts"
        assert llm.call_history[1]["trace_id"] == "vid44444444_concepts_rewrite_1"
        assert llm.call_history[2]["trace_id"] == "vid44444444_summary"
        assert llm.call_history[3]["trace_id"] == "vid44444444_synthesis"

    def test_self_healing_rewrite_loop_exhausts_retries_and_defensively_cleans(self) -> None:
        """Verify that when LLM keeps returning forbidden prefix, retries stop at max_rewrites and cleans."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Palavras-chave: Conceito Teórico",
                "Resumo teórico...",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Theory")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid55555555').value}"
            ),
            content=Content(
                id=ContentId("vid55555555"), title="Theoretical Notes", text="Conteúdo..."
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        # Defensively cleaned even though rewrite loop exhausted
        assert entry.key_concept == "Conceito Teórico"
        assert len(llm.call_history) == 5
        assert llm.call_history[0]["trace_id"] == "vid55555555_concepts"
        assert llm.call_history[1]["trace_id"] == "vid55555555_concepts_rewrite_1"
        assert llm.call_history[2]["trace_id"] == "vid55555555_concepts_rewrite_2"
        assert llm.call_history[3]["trace_id"] == "vid55555555_summary"
        assert llm.call_history[4]["trace_id"] == "vid55555555_synthesis"

    def test_summary_judge_triggers_regeneration_on_false(self) -> None:
        """Verify that when summary judge returns false, summary is regenerated and re-judged."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Fiel",
                "Resumo superficial com alucinação.",
                "Resumo rigoroso e conceitualmente fiel.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        pass_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="test",
        )
        fail_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=False,
            overall_score=0.3,
            criteria_scores=(),
            provider="test",
        )
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [pass_eval, fail_eval, pass_eval, pass_eval]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
            llm_judge_port=mock_judge,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Philosophy")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid77777777').value}"
            ),
            content=Content(
                id=ContentId("vid77777777"),
                title="Concept Analysis",
                text="Detailed text on philosophy...",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Fiel"
        assert len(llm.call_history) == 4
        assert mock_judge.evaluate.call_count == 4
        assert llm.call_history[0]["trace_id"] == "vid77777777_concepts"
        assert llm.call_history[1]["trace_id"] == "vid77777777_summary"
        assert llm.call_history[2]["trace_id"] == "vid77777777_summary_retry_1"
        assert llm.call_history[3]["trace_id"] == "vid77777777_synthesis"

    def test_concepts_judge_triggers_rewrite_on_false(self) -> None:
        """Verify that when concepts pass regex but judge returns false, rewrite is triggered."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Desconexo",
                "Conceito Conexo, Teoria Central",
                "Resumo fiel do conteúdo.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        pass_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="test",
        )
        fail_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=False,
            overall_score=0.3,
            criteria_scores=(),
            provider="test",
        )
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [fail_eval, pass_eval, pass_eval, pass_eval]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
            llm_judge_port=mock_judge,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Sociology")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid88888888').value}"
            ),
            content=Content(
                id=ContentId("vid88888888"),
                title="Social Dynamics",
                text="Sociology transcript body...",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Conexo, Teoria Central"
        assert len(llm.call_history) == 4
        assert mock_judge.evaluate.call_count == 4
        assert llm.call_history[0]["trace_id"] == "vid88888888_concepts"
        assert llm.call_history[1]["trace_id"] == "vid88888888_concepts_rewrite_1"
        assert llm.call_history[2]["trace_id"] == "vid88888888_summary"
        assert llm.call_history[3]["trace_id"] == "vid88888888_synthesis"

    def test_synthesis_judge_triggers_regeneration_on_false(self) -> None:
        """Verify that when synthesis judge returns false, synthesis is regenerated and re-judged."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Sólido",
                "Resumo bem estruturado.",
                _SAMPLE_VALID_SYNTHESIS,
                "Minorias políticas burocráticas governam as instituições com base em normas estritas e transparentes. As contra-elites organizadas substituem a liderança decadente e reconfiguram as decisões estruturais.",
            ]
        )
        pass_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="test",
        )
        fail_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=False,
            overall_score=0.3,
            criteria_scores=(),
            provider="test",
        )
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [pass_eval, pass_eval, fail_eval, pass_eval]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
            llm_judge_port=mock_judge,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Political Theory")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid99999999').value}"
            ),
            content=Content(
                id=ContentId("vid99999999"),
                title="Pareto Dynamics",
                text="Sociological dynamics...",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Sólido"
        assert "Minorias políticas burocráticas governam" in entry.synthesis
        assert len(llm.call_history) == 4
        assert mock_judge.evaluate.call_count == 4
        assert llm.call_history[2]["trace_id"] == "vid99999999_synthesis"
        assert llm.call_history[3]["trace_id"] == "vid99999999_synthesis_retry_1"
        assert mock_judge.evaluate.call_args_list[2][0][0].trace_id == "vid99999999_synthesis_judge"
        assert (
            mock_judge.evaluate.call_args_list[3][0][0].trace_id
            == "vid99999999_synthesis_judge_retry_1"
        )

    def test_synthesis_size_invalidation_triggers_retry(self) -> None:
        """Verify that when synthesis fails sizing heuristic (e.g. too few words), judge is skipped and retry triggered."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito",
                "Resumo completo.",
                "Texto curto demais.",  # 3 words -> fails min_words heuristic
                _SAMPLE_VALID_SYNTHESIS,  # Valid size
            ]
        )
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=2,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("General")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vidsize123').value}"
            ),
            content=Content(
                id=ContentId("vidsize123"), title="Size Validation Test", text="Body content..."
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.synthesis == _SAMPLE_VALID_SYNTHESIS
        assert len(llm.call_history) == 4
        assert llm.call_history[2]["trace_id"] == "vidsize123_synthesis"
        assert llm.call_history[3]["trace_id"] == "vidsize123_synthesis_retry_1"

    def test_infinite_retry_loop_when_max_rewrites_is_zero(self) -> None:
        """Verify that max_rewrites=0 allows unconstrained retries without aborting early."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Conceito Central",
                "Resumo inicial.",
                _SAMPLE_VALID_SYNTHESIS,
                _SAMPLE_VALID_SYNTHESIS,
                _SAMPLE_VALID_SYNTHESIS,
                _SAMPLE_VALID_SYNTHESIS,
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        pass_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="test",
        )
        fail_eval = JudgeEvaluation(
            target_stage="raw_index",
            passed=False,
            overall_score=0.3,
            criteria_scores=(),
            provider="test",
        )
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [
            pass_eval,
            pass_eval,
            fail_eval,
            fail_eval,
            fail_eval,
            fail_eval,
            pass_eval,
        ]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_rewrites=0,  # Unbounded / infinite loop mode
            llm_judge_port=mock_judge,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Perseverance")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vidinfinite').value}"
            ),
            content=Content(
                id=ContentId("vidinfinite"),
                title="Infinite Retries",
                text="Infinite attempt body...",
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert entry.key_concept == "Conceito Central"
        assert len(llm.call_history) == 7
        assert mock_judge.evaluate.call_count == 7
        assert llm.call_history[-1]["trace_id"] == "vidinfinite_synthesis_retry_4"
        assert (
            mock_judge.evaluate.call_args_list[-1][0][0].trace_id
            == "vidinfinite_synthesis_judge_retry_4"
        )

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
        """Verify that configured temperature is passed to generative transformations."""
        vault = InMemoryVaultAdapter()
        mock_llm = MagicMock()
        mock_llm.transform.side_effect = [
            "Conceito",
            "Resumo explicativo.",
            _SAMPLE_VALID_SYNTHESIS,
        ]
        prompt_provider = JsonPromptProvider()

        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=mock_llm,
            prompt_provider=prompt_provider,
            temperature=0.35,
            language="Português do Brasil",
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("Science")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid66666666').value}"
            ),
            content=Content(
                id=ContentId("vid66666666"), title="Physics", text="Physics transcript..."
            ),
        )

        entry = use_case.execute(transcript)

        assert entry is not None
        assert mock_llm.transform.call_count == 3
        calls = mock_llm.transform.call_args_list
        assert calls[0][1]["temperature"] == 0.35
        assert calls[1][1]["temperature"] == 0.35
        assert calls[2][1]["temperature"] == 0.35

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
        assert use_case.llm_indexing_port is llm
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
                llm_indexing_port=llm,
                prompt_provider=prompt_provider,
            )
        assert str(exc1.value) == "vault_port is required."

        with pytest.raises(ValueError) as exc2:
            IndexRawTranscriptsUseCase(
                vault_port=vault,
                llm_indexing_port=None,
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

    def test_index_single_transcript_excerpt_slicing_and_fallback_title(self) -> None:
        """Verify max_chars excerpt slicing and fallback to video_id when title is empty."""
        vault = InMemoryVaultAdapter()
        llm = MockLLMAdapter(
            responses=[
                "Concept",
                "Summary.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )
        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            max_chars=1,
        )

        transcript = StageTranscript(
            channel=Channel(name=ChannelName("3blue1brown")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid_notitle_99').value}"
            ),
            content=Content(id=ContentId("vid_notitle_99"), title="", text="Long body text..."),
        )

        entry = use_case.execute(transcript)
        assert entry is not None
        assert entry.title == "vid_notitle_99"
        assert "Long body" not in llm.call_history[0]["prompt"].messages[-1].content

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
        transcript = StageTranscript(
            channel=Channel(name=ChannelName("TestChannel"), id=ChannelId("chan_id_1")),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid_args_1').value}"
            ),
            content=Content(id=ContentId("vid_args_1"), title="Title Test", text="Body Test"),
        )

        entry = use_case.execute(transcript, user=user)
        assert entry is not None
        assert entry.key_concept == "Concept Alpha"
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
                "Summary.",
                _SAMPLE_VALID_SYNTHESIS,
                "Concept",
                "Summary.",
                _SAMPLE_VALID_SYNTHESIS,
            ]
        )

        class _StubTaxonomy(ChannelTaxonomyPort):
            def classify(self, channel_name: ChannelName | str) -> tuple[str, str]:
                if str(channel_name).lower() == "3blue1brown":
                    return "engineering", "perennial"
                return "uncategorized", "volatile"

        prompt_provider = JsonPromptProvider()
        use_case = IndexRawTranscriptsUseCase(
            vault_port=vault,
            llm_indexing_port=llm,
            prompt_provider=prompt_provider,
            taxonomy_port=_StubTaxonomy(),
        )

        # Case A: explicit category with whitespace
        transcript_explicit = StageTranscript(
            channel=Channel(name=ChannelName("Generic"), category="  Epistemology  "),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid_cat_1').value}"
            ),
            content=Content(id=ContentId("vid_cat_1"), title="Title", text="Body"),
        )
        entry_explicit = use_case.execute(transcript_explicit)
        assert entry_explicit is not None
        assert entry_explicit.channel_category == "Epistemology"

        # Case B: empty category -> auto-classify by channel name
        transcript_classified = StageTranscript(
            channel=Channel(name=ChannelName("3blue1brown"), category=""),
            provenance=MediaProvenance.create(
                url=f"https://youtube.com/watch?v={ContentId('vid_cat_2').value}"
            ),
            content=Content(id=ContentId("vid_cat_2"), title="Title", text="Body"),
        )
        entry_classified = use_case.execute(transcript_classified)
        assert entry_classified is not None
        assert entry_classified.channel_category == "engineering"
