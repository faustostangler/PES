"""Unit tests for HybridSaturationEvaluator application orchestration service (ADR-066, SPEC-066)."""

from __future__ import annotations

from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.application.services.hybrid_saturation import HybridSaturationEvaluator
from cresmo.domain.services.convergence_evaluator import NO_NEW_GAPS_SENTINEL
from cresmo.domain.value_objects.convergence import (
    ConvergenceMode,
    SaturationReason,
    SaturationThresholds,
)


class _ResilientStubEmbeddingPort(TextEmbeddingPort):
    """Stub resilient port exposing last_provider_name alongside provider_name."""

    def __init__(self, vectors: list[list[float]]) -> None:
        self._vectors = vectors
        self.calls: list[list[str]] = []
        self.last_provider_name = "tfidf_fallback"

    @property
    def provider_name(self) -> str:
        return "gemini"

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return self._vectors


def test_pass2_explicit_sentinel_saturates_preserving_baseline_without_embedding() -> None:
    """Verify Pass 2+ with <NO_NEW_GAPS/> saturates via Layer 1 sentinel without calling embed_batch."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    baseline = "## Contexto\n\nTexto base consolidado sobre a fundação do condado."
    verdict = evaluator.evaluate(baseline, NO_NEW_GAPS_SENTINEL, pass_index=2)

    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.EXPLICIT_SENTINEL
    assert verdict.preserve_baseline is True
    mock_port.embed_batch.assert_not_called()

    callable_verdict = evaluator(baseline, f"  {NO_NEW_GAPS_SENTINEL}\n", 2)
    assert callable_verdict.is_saturated is True
    assert callable_verdict.reason is SaturationReason.EXPLICIT_SENTINEL
    assert callable_verdict.preserve_baseline is True
    mock_port.embed_batch.assert_not_called()


def test_pass1_explicit_sentinel_is_not_short_circuited_as_sentinel() -> None:
    """Verify Pass 1 forbids explicit sentinel short-circuiting even if token appears."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    baseline = "## Origens\n\nPrimeiro parágrafo histórico sobre instituições ibéricas."
    verdict = evaluator.evaluate(baseline, NO_NEW_GAPS_SENTINEL, pass_index=1)

    assert verdict.reason is not SaturationReason.EXPLICIT_SENTINEL


def test_lexical_identity_saturates_without_embedding() -> None:
    """Verify identical or near-identical passes short-circuit at Layer 1 lexical identity."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    text = (
        "## Formação Territorial\n\n"
        "A consolidação política do território portucalense resultou de alianças feudais, "
        "pressões militares fronteiriças e concessões régias outorgadas em 1096.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** exerceu autoridade militar na fronteira ocidental."
    )
    verdict = evaluator.evaluate(text, text, pass_index=2)

    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.LEXICAL_IDENTITY
    assert verdict.preserve_baseline is False
    assert verdict.lexical_jaccard == pytest.approx(1.0)
    assert verdict.word_delta_ratio == pytest.approx(0.0)
    mock_port.embed_batch.assert_not_called()


def test_semantic_plateau_calls_embed_batch_once_and_records_provider() -> None:
    """Verify Layer 2 calls embed_batch once with combined units and detects SEMANTIC_PLATEAU."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    mock_port.embed_batch.return_value = [
        [1.0, 0.0],
        [0.0, 1.0],
        [0.99, 0.14],
        [0.14, 0.99],
    ]
    evaluator = HybridSaturationEvaluator(
        embedding_port=mock_port,
        thresholds=SaturationThresholds(semantic_similarity_threshold=0.88),
    )

    baseline = (
        "## Bloco Um\n\n"
        "O controle fiscal das rotas comerciais no reino medieval financiou a defesa das fronteiras.\n\n"
        "### Extra Info\n\n"
        "1. A Casa da Índia centralizava registros aduaneiros e contratos de navegação."
    )
    current = (
        "## Bloco Dois\n\n"
        "A arrecadação tributária sobre o comércio oceânico no reino medieval sustentou portos.\n\n"
        "### Extra Info\n\n"
        "1. O órgão régio lisboeta supervisionava tarifas marítimas, contratos mercantis e licenças."
    )

    verdict = evaluator.evaluate(baseline, current, pass_index=2)

    mock_port.embed_batch.assert_called_once()
    batched_texts = mock_port.embed_batch.call_args.args[0]
    assert len(batched_texts) == 4
    assert "rotas comerciais" in batched_texts[0]
    assert "Casa da Índia" in batched_texts[1]
    assert "comércio oceânico" in batched_texts[2]
    assert "órgão régio lisboeta" in batched_texts[3]

    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert verdict.novel_paragraphs == 0
    assert verdict.total_paragraphs == 2
    assert verdict.preserve_baseline is False
    assert verdict.provider == "gemini"
    assert verdict.lexical_jaccard > 0.0
    assert verdict.word_delta_ratio > 0.0


def test_novel_content_calls_embed_batch_once_and_continues() -> None:
    """Verify Layer 2 returns NOVEL_CONTENT when candidate units introduce dissimilar semantics."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "ollama"
    mock_port.embed_batch.return_value = [
        [1.0, 0.0],
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    evaluator = HybridSaturationEvaluator(
        embedding_port=mock_port,
        thresholds=SaturationThresholds(semantic_similarity_threshold=0.88),
    )

    baseline = (
        "## Bloco Um\n\n"
        "O tratado comercial reduziu tarifas portuárias entre Lisboa e Antuérpia.\n\n"
        "### Extra Info\n\n"
        "1. Feitorias régias operavam como entrepostos diplomáticos."
    )
    current = (
        "## Bloco Dois\n\n"
        "O acordo mercantil diminuiu impostos alfandegários entre portos atlânticos.\n\n"
        "### Extra Info\n\n"
        "1. A reforma monetária de 1570 redefiniu a cunhagem de prata nas casas da moeda."
    )

    verdict = evaluator.evaluate(baseline, current, pass_index=2)

    mock_port.embed_batch.assert_called_once()
    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.novel_paragraphs == 1
    assert verdict.total_paragraphs == 2
    assert verdict.preserve_baseline is False
    assert verdict.max_novelty == pytest.approx(1.0)
    assert verdict.provider == "ollama"


def test_resilient_wrapper_last_provider_name_attribution() -> None:
    """Verify verdict.provider prefers last_provider_name when exposed by resilient wrapper."""
    stub_port = _ResilientStubEmbeddingPort(
        vectors=[
            [1.0, 0.0],
            [0.99, 0.14],
        ]
    )
    evaluator = HybridSaturationEvaluator(embedding_port=stub_port)

    baseline = "## Título\n\nPrimeiro argumento estrutural sobre crédito público."
    current = "## Título\n\nSegundo parágrafo explicando a mesma dívida soberana medieval."
    verdict = evaluator.evaluate(baseline, current, pass_index=2)

    assert len(stub_port.calls) == 1
    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert verdict.provider == "tfidf_fallback"


def test_none_embedding_port_preserves_layer1_and_degrades_layer2_to_novel_content() -> None:
    """Verify embedding_port=None runs Layer 1 checks and degrades Layer 2 to NOVEL_CONTENT."""
    evaluator = HybridSaturationEvaluator(embedding_port=None)

    baseline = "## Capítulo\n\nAnálise inicial sobre instituições tributárias do reino."
    sentinel_verdict = evaluator.evaluate(baseline, NO_NEW_GAPS_SENTINEL, pass_index=2)
    assert sentinel_verdict.is_saturated is True
    assert sentinel_verdict.reason is SaturationReason.EXPLICIT_SENTINEL
    assert sentinel_verdict.preserve_baseline is True

    identity_verdict = evaluator.evaluate(baseline, baseline, pass_index=2)
    assert identity_verdict.is_saturated is True
    assert identity_verdict.reason is SaturationReason.LEXICAL_IDENTITY
    assert identity_verdict.preserve_baseline is False

    distinct_current = (
        "## Capítulo\n\n"
        "A expansão marítima reorganizou a arrecadação aduaneira e financiou armadas permanentes."
    )
    degraded_verdict = evaluator.evaluate(baseline, distinct_current, pass_index=2)
    assert degraded_verdict.is_saturated is False
    assert degraded_verdict.reason is SaturationReason.NOVEL_CONTENT
    assert degraded_verdict.preserve_baseline is False
    assert degraded_verdict.provider == "none"


def test_mode_none_returns_disabled_verdict_without_embedding() -> None:
    """Verify ConvergenceMode.NONE immediately returns disabled verdict without embedding calls."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    evaluator = HybridSaturationEvaluator(
        embedding_port=mock_port,
        mode=ConvergenceMode.NONE,
    )

    text = "## Título\n\nParágrafo idêntico."
    verdict_sentinel = evaluator.evaluate(text, NO_NEW_GAPS_SENTINEL, pass_index=2)
    verdict_identical = evaluator.evaluate(text, text, pass_index=2)

    for verdict in (verdict_sentinel, verdict_identical):
        assert verdict.is_saturated is False
        assert verdict.reason is SaturationReason.DISABLED
        assert verdict.preserve_baseline is False
        assert verdict.provider == "disabled"

    mock_port.embed_batch.assert_not_called()


def test_empty_baseline_with_non_empty_current_returns_novel_content_without_embedding() -> None:
    """Verify heading-only baseline with populated candidate returns NOVEL_CONTENT, not plateau."""
    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    verdict = evaluator.evaluate(
        "## Only Heading",
        "## Main\n\nNew substantive paragraph.\n\n### Extra Info\n\n1. Detail one.\n2. Detail two.",
        pass_index=1,
    )

    mock_port.embed_batch.assert_not_called()
    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.novel_paragraphs == 3
    assert verdict.total_paragraphs == 3
    assert verdict.preserve_baseline is False
    assert verdict.provider == "lexical"


def test_long_paragraph_intra_paragraph_addition_detected_with_tfidf() -> None:
    """Verify >120-word paragraphs expose novel intra-paragraph additions instead of diluting."""
    from cresmo.infrastructure.adapters.embeddings.tfidf_embedding_adapter import (
        TfidfEmbeddingAdapter,
    )

    baseline = (
        "O Condado Portucalense emergiu como senhorio fronteiriço durante a reconquista ibérica "
        "no século XI, articulando milícias locais, alianças nobiliárquicas franco-leonesas e "
        "governança patrimonial em torno de Guimarães e Braga. "
        "As disputas sucessórias após a morte de Henrique da Borgonha intensificaram o atrito "
        "entre a regência de Teresa de Leão, apoiada pela casa galega de Trava, e os barões "
        "portucalenses liderados por Afonso Henriques e Egas Moniz. "
        "A vitória militar na Batalha de São Mamede reordenou a hierarquia aristocrática no "
        "noroeste peninsular, permitindo a consolidação administrativa do território e a "
        "projeção diplomática junto às cortes vizinhas. "
        "Em paralelo, os concelhos rurais obtiveram cartas de foral que asseguravam "
        "recrutamento militar permanente, tributação regular e autonomia jurídica perante os "
        "senhores feudais da região meridional."
    )
    added_sentence = (
        "Posteriormente, a arquitetura hidráulica das levadas madeirenses revolucionou a "
        "agroindústria açucareira atlântica, conectando engenhos coloniais a mercados flamengos "
        "de refino e crédito mercantil."
    )
    current = f"{baseline} {added_sentence}"

    evaluator = HybridSaturationEvaluator(embedding_port=TfidfEmbeddingAdapter())
    verdict = evaluator.evaluate(baseline, current, pass_index=2)

    assert len(baseline.split()) > 120
    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.novel_paragraphs >= 1
    assert verdict.total_paragraphs >= 2


def test_embedding_infrastructure_error_degrades_gracefully_to_novel_content() -> None:
    """Verify EmbeddingInfrastructureError from embed_batch degrades cleanly without crashing."""
    import structlog.testing

    from cresmo.domain.exceptions import EmbeddingInfrastructureError

    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    mock_port.embed_batch.side_effect = EmbeddingInfrastructureError("Upstream 503 unavailable")
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    baseline = "## Contexto\n\nPrimeiro parágrafo consolidado sobre tributação medieval."
    current = "## Contexto\n\nSegundo parágrafo sobre navegações atlânticas e feitorias régias."

    with structlog.testing.capture_logs() as captured_logs:
        verdict = evaluator.evaluate(baseline, current, pass_index=2)

    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.preserve_baseline is False
    assert verdict.provider == "degraded"
    assert verdict.novel_paragraphs == 1
    assert verdict.total_paragraphs == 1
    warning_entry = next(entry for entry in captured_logs if entry.get("log_level") == "warning")
    assert (
        warning_entry.get("event")
        == "Embedding port failed during saturation check; degrading to NOVEL_CONTENT."
    )
    assert warning_entry.get("provider") == "gemini"
    assert warning_entry.get("error") == "Upstream 503 unavailable"


def test_mismatched_embedding_vector_count_degrades_gracefully() -> None:
    """Verify mismatched embed_batch output length degrades cleanly instead of slicing corrupt vectors."""
    import structlog.testing

    mock_port = MagicMock(spec=TextEmbeddingPort)
    mock_port.provider_name = "gemini"
    mock_port.embed_batch.return_value = [[1.0, 0.0]]  # Expected 2 vectors
    evaluator = HybridSaturationEvaluator(embedding_port=mock_port)

    with structlog.testing.capture_logs() as captured_logs:
        verdict = evaluator.evaluate(
            "## A\n\nPrimeiro parágrafo sobre finanças públicas.",
            "## B\n\nSegundo parágrafo completamente distinto sobre arquitetura naval.",
            pass_index=2,
        )

    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.preserve_baseline is False
    assert verdict.provider == "degraded"
    assert verdict.novel_paragraphs == 1
    assert verdict.total_paragraphs == 1
    warning_entry = next(entry for entry in captured_logs if entry.get("log_level") == "warning")
    assert (
        warning_entry.get("event")
        == "Embedding port returned mismatched vector count; degrading to NOVEL_CONTENT."
    )
    assert warning_entry.get("provider") == "gemini"
    assert warning_entry.get("expected") == 2
    assert warning_entry.get("actual") == 1


def test_none_embedding_port_with_empty_current_returns_semantic_plateau() -> None:
    """Verify heading-only current_text still returns SEMANTIC_PLATEAU even when embedding_port is None."""
    evaluator = HybridSaturationEvaluator(embedding_port=None)

    verdict = evaluator.evaluate(
        "## A\n\nParágrafo original consolidado.",
        "## Apenas Título",
        pass_index=2,
    )

    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert verdict.max_novelty == pytest.approx(0.0)
    assert verdict.preserve_baseline is False
    assert verdict.novel_paragraphs == 0
    assert verdict.total_paragraphs == 0
    assert verdict.provider == "lexical"


def test_default_pass_index_is_one_for_evaluate_and_callable() -> None:
    """Verify omitted pass_index defaults to 1 so explicit stop sentinel is not triggered on Pass 1."""
    evaluator = HybridSaturationEvaluator(embedding_port=None)
    baseline = "## Origens\n\nParágrafo histórico inicial sobre instituições fiscais."

    verdict_eval = evaluator.evaluate(baseline, NO_NEW_GAPS_SENTINEL)
    verdict_call = evaluator(baseline, NO_NEW_GAPS_SENTINEL)

    assert verdict_eval.reason is not SaturationReason.EXPLICIT_SENTINEL
    assert verdict_call.reason is not SaturationReason.EXPLICIT_SENTINEL


def test_custom_thresholds_govern_lexical_segmentation_and_semantic_gates() -> None:
    """Verify SaturationThresholds are forwarded to lexical, unit-segmentation, and semantic evaluators."""
    # 1. Custom lexical thresholds trigger LEXICAL_IDENTITY below default 0.95/0.03
    lexical_eval = HybridSaturationEvaluator(
        embedding_port=None,
        thresholds=SaturationThresholds(
            lexical_identity_threshold=0.45,
            max_lexical_word_delta=0.25,
        ),
    )
    lex_verdict = lexical_eval.evaluate(
        "O controle fiscal das rotas comerciais no reino medieval financiou navios.",
        "O controle fiscal das rotas comerciais no reino medieval sustentou armadas.",
        pass_index=2,
    )
    assert lex_verdict.is_saturated is True
    assert lex_verdict.reason is SaturationReason.LEXICAL_IDENTITY

    # 2. Custom long_unit_word_cutoff / sliding_window_* split both baseline and current into 3 windows each
    mock_seg_port = MagicMock(spec=TextEmbeddingPort)
    mock_seg_port.provider_name = "gemini"
    mock_seg_port.embed_batch.return_value = [
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ]
    seg_eval = HybridSaturationEvaluator(
        embedding_port=mock_seg_port,
        thresholds=SaturationThresholds(
            long_unit_word_cutoff=6,
            sliding_window_sentences=2,
            sliding_window_overlap=0,
        ),
    )
    five_sent_base = (
        "Alpha sentence one. Beta sentence two. Gamma sentence three. "
        "Delta sentence four. Epsilon sentence five."
    )
    five_sent_curr = (
        "Zeta clause one. Eta clause two. Theta clause three. "
        "Iota clause four. Kappa clause five."
    )
    seg_verdict = seg_eval.evaluate(five_sent_base, five_sent_curr, pass_index=2)
    assert len(mock_seg_port.embed_batch.call_args.args[0]) == 6
    assert seg_verdict.total_paragraphs == 3

    # 3. Custom semantic_similarity_threshold=0.99 treats 0.95 cosine similarity as NOVEL_CONTENT
    mock_sem_port = MagicMock(spec=TextEmbeddingPort)
    mock_sem_port.provider_name = "gemini"
    mock_sem_port.embed_batch.return_value = [
        [1.0, 0.0],
        [0.95, 0.3122499],
    ]
    sem_eval = HybridSaturationEvaluator(
        embedding_port=mock_sem_port,
        thresholds=SaturationThresholds(semantic_similarity_threshold=0.99),
    )
    sem_verdict = sem_eval.evaluate(
        "## A\n\nPrimeiro argumento fiscal medieval.",
        "## B\n\nSegundo argumento marítimo atlântico.",
        pass_index=2,
    )
    assert sem_verdict.is_saturated is False
    assert sem_verdict.reason is SaturationReason.NOVEL_CONTENT


def test_empty_last_provider_name_falls_back_to_port_provider_name() -> None:
    """Verify empty last_provider_name falls back to embedding_port.provider_name."""
    stub_port = _ResilientStubEmbeddingPort(vectors=[[1.0, 0.0], [1.0, 0.0]])
    stub_port.last_provider_name = ""
    evaluator = HybridSaturationEvaluator(embedding_port=stub_port)

    verdict = evaluator.evaluate(
        "## A\n\nPrimeiro texto sobre crédito régio.",
        "## B\n\nSegundo texto sobre tesouro público.",
        pass_index=2,
    )
    assert verdict.provider == "gemini"
