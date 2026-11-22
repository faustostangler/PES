"""Application orchestration service for two-tier hybrid pass saturation evaluation.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §3.2 (HybridSaturationEvaluator)
"""

from __future__ import annotations

import structlog

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.domain.exceptions import EmbeddingInfrastructureError
from cresmo.domain.services.convergence_evaluator import (
    compute_ngram_jaccard,
    compute_word_delta_ratio,
    evaluate_lexical_convergence,
    evaluate_semantic_convergence,
    segment_semantic_units,
)
from cresmo.domain.value_objects.convergence import (
    ConvergenceMode,
    SaturationReason,
    SaturationThresholds,
    SaturationVerdict,
    never_saturate,
)

logger = structlog.get_logger(__name__)


def _resolve_provider_name(port: TextEmbeddingPort) -> str:
    """Resolve active provider attribution, honoring resilient fallback wrappers."""
    raw_last_provider = getattr(port, "last_provider_name", None)
    if isinstance(raw_last_provider, str) and raw_last_provider:
        return raw_last_provider
    return port.provider_name


def _build_novel_verdict(
    *,
    lexical_jaccard: float,
    word_delta_ratio: float,
    unit_count: int,
    provider: str,
) -> SaturationVerdict:
    """Build a non-saturated NOVEL_CONTENT verdict when semantic comparison is bypassed or degraded."""
    return SaturationVerdict(
        is_saturated=False,
        reason=SaturationReason.NOVEL_CONTENT,
        lexical_jaccard=lexical_jaccard,
        word_delta_ratio=word_delta_ratio,
        max_novelty=1.0,
        novel_paragraphs=unit_count,
        total_paragraphs=unit_count,
        preserve_baseline=False,
        provider=provider,
    )


class HybridSaturationEvaluator:
    """Orchestrates two-tier lexical and unit-level MaxSim semantic convergence evaluation.

    Satisfies the Domain ``SaturationPolicy`` callable contract while keeping embedding
    infrastructure decoupled behind ``TextEmbeddingPort``.
    """

    def __init__(
        self,
        embedding_port: TextEmbeddingPort | None = None,
        thresholds: SaturationThresholds | None = None,
        mode: ConvergenceMode = ConvergenceMode.HYBRID_SEMANTIC,
    ) -> None:
        """Initialize the hybrid saturation evaluator.

        Args:
            embedding_port: Optional text embedding adapter port for Tier 2 semantic scoring.
            thresholds: Optional lexical and semantic convergence thresholds.
            mode: Convergence mode governing whether hybrid checks execute or stay disabled.
        """
        self.embedding_port = embedding_port
        self.thresholds = thresholds or SaturationThresholds()
        self.mode = mode

    def evaluate(
        self,
        baseline_text: str,
        current_text: str,
        pass_index: int = 1,
    ) -> SaturationVerdict:
        """Evaluate pass convergence using Tier 1 lexical gates and Tier 2 MaxSim semantics.

        Args:
            baseline_text: Reference baseline text from source or prior pass.
            current_text: Candidate text produced during the current pass.
            pass_index: One-based pass index being evaluated.

        Returns:
            SaturationVerdict: Structured convergence outcome with scalar metrics and baseline flags.
        """
        if self.mode is ConvergenceMode.NONE:
            return never_saturate(baseline_text, current_text, pass_index)

        lexical_verdict = evaluate_lexical_convergence(
            baseline_text,
            current_text,
            thresholds=self.thresholds,
            pass_index=pass_index,
        )
        if lexical_verdict is not None:
            return lexical_verdict

        lexical_jaccard = compute_ngram_jaccard(baseline_text, current_text)
        word_delta_ratio = compute_word_delta_ratio(baseline_text, current_text)
        baseline_units = segment_semantic_units(baseline_text)
        current_units = segment_semantic_units(current_text)

        if not current_units:
            return SaturationVerdict(
                is_saturated=True,
                reason=SaturationReason.SEMANTIC_PLATEAU,
                lexical_jaccard=lexical_jaccard,
                word_delta_ratio=word_delta_ratio,
                max_novelty=0.0,
                novel_paragraphs=0,
                total_paragraphs=0,
                preserve_baseline=False,
                provider="lexical",
            )

        if not baseline_units:
            return _build_novel_verdict(
                lexical_jaccard=lexical_jaccard,
                word_delta_ratio=word_delta_ratio,
                unit_count=len(current_units),
                provider="lexical",
            )

        if self.embedding_port is None:
            return _build_novel_verdict(
                lexical_jaccard=lexical_jaccard,
                word_delta_ratio=word_delta_ratio,
                unit_count=len(current_units),
                provider="none",
            )

        combined_units = [*baseline_units, *current_units]
        try:
            vectors = self.embedding_port.embed_batch(combined_units)
        except EmbeddingInfrastructureError as exc:
            logger.warning(
                "Embedding port failed during saturation check; degrading to NOVEL_CONTENT.",
                provider=self.embedding_port.provider_name,
                error=str(exc),
            )
            return _build_novel_verdict(
                lexical_jaccard=lexical_jaccard,
                word_delta_ratio=word_delta_ratio,
                unit_count=len(current_units),
                provider="degraded",
            )

        if len(vectors) != len(combined_units):
            logger.warning(
                "Embedding port returned mismatched vector count; degrading to NOVEL_CONTENT.",
                provider=_resolve_provider_name(self.embedding_port),
                expected=len(combined_units),
                actual=len(vectors),
            )
            return _build_novel_verdict(
                lexical_jaccard=lexical_jaccard,
                word_delta_ratio=word_delta_ratio,
                unit_count=len(current_units),
                provider="degraded",
            )

        split_idx = len(baseline_units)
        baseline_vectors = vectors[:split_idx]
        current_vectors = vectors[split_idx:]
        provider = _resolve_provider_name(self.embedding_port)

        return evaluate_semantic_convergence(
            baseline_vectors,
            current_vectors,
            thresholds=self.thresholds,
            lexical_jaccard=lexical_jaccard,
            word_delta_ratio=word_delta_ratio,
            provider=provider,
        )

    def __call__(
        self,
        baseline_text: str,
        current_text: str,
        pass_index: int = 1,
    ) -> SaturationVerdict:
        """Invoke convergence evaluation directly via the SaturationPolicy callable contract.

        Args:
            baseline_text: Reference baseline text from source or prior pass.
            current_text: Candidate text produced during the current pass.
            pass_index: One-based pass index being evaluated.

        Returns:
            SaturationVerdict: Structured convergence outcome with scalar metrics and baseline flags.
        """
        return self.evaluate(baseline_text, current_text, pass_index)
