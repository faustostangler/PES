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
    assert verdict.preserve_baseline is True
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
        "O controle fiscal das rotas comerciais financiou a defesa das fronteiras marítimas.\n\n"
        "### Extra Info\n\n"
        "1. A Casa da Índia centralizava registros aduaneiros e contratos de navegação."
    )
    current = (
        "## Bloco Dois\n\n"
        "A arrecadação tributária sobre o comércio oceânico sustentou a proteção portuária.\n\n"
        "### Extra Info\n\n"
        "1. O órgão régio lisboeta supervisionava tarifas marítimas e licenças mercantis."
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
    assert verdict.preserve_baseline is True
    assert verdict.provider == "gemini"


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
    assert identity_verdict.preserve_baseline is True

    distinct_current = (
        "## Capítulo\n\n"
        "A expansão marítima reorganizou a arrecadação aduaneira e financiou armadas permanentes."
    )
    degraded_verdict = evaluator.evaluate(baseline, distinct_current, pass_index=2)
    assert degraded_verdict.is_saturated is False
    assert degraded_verdict.reason is SaturationReason.NOVEL_CONTENT
    assert degraded_verdict.preserve_baseline is False


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
