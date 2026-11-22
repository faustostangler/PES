"""Pure Domain mathematical convergence evaluation for multi-pass synthesis.

Pure Python standard library only. Zero external ML, HTTP, or SDK dependencies.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §2.3 (Domain Convergence Evaluator)
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from typing import Final

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.convergence import (
    SaturationReason,
    SaturationThresholds,
    SaturationVerdict,
)

NO_NEW_GAPS_SENTINEL: Final[str] = "<NO_NEW_GAPS/>"

_BLANK_LINE_SPLIT_PATTERN = re.compile(r"\n\s*\n")
_HEADING_LINE_PATTERN = re.compile(r"^\s*#{1,6}\s+")
_WORD_TOKEN_PATTERN = re.compile(r"\w+")


def _tokenize_words(text: str) -> list[str]:
    """Extract normalized lowercase alphanumeric word tokens from text."""
    return _WORD_TOKEN_PATTERN.findall(text.lower())


def _build_ngram_shingles(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    """Build contiguous word n-gram shingles, or a single tuple when shorter than n."""
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def segment_semantic_units(text: str) -> tuple[str, ...]:
    """Segment markdown compendia into discrete paragraph and numbered semantic units.

    Args:
        text: Markdown compendium text containing main body and optional '### Extra Info'.

    Returns:
        tuple[str, ...]: Ordered semantic units with markdown headings and stop sentinels excluded.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return ()

    units: list[str] = []
    for raw_block in _BLANK_LINE_SPLIT_PATTERN.split(normalized):
        block = raw_block.strip()
        if not block:
            continue

        kept_lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
            and not _HEADING_LINE_PATTERN.match(line)
            and line.strip() != NO_NEW_GAPS_SENTINEL
        ]
        cleaned = "\n".join(kept_lines).strip()
        if cleaned and cleaned != NO_NEW_GAPS_SENTINEL:
            units.append(cleaned)

    return tuple(units)


def is_explicit_stop_sentinel(text: str, pass_index: int = 2) -> bool:
    """Detect whether text emits the explicit saturation stop sentinel for eligible passes.

    Args:
        text: Candidate output text from a refinement pass.
        pass_index: One-based pass index being evaluated.

    Returns:
        bool: True when pass_index > 1 and the stop sentinel token is present.
    """
    if isinstance(pass_index, bool) or not isinstance(pass_index, int) or pass_index < 1:
        raise DomainValidationError(f"pass_index must be an integer >= 1, got {pass_index!r}.")
    if pass_index == 1:
        return False
    return text.strip() == NO_NEW_GAPS_SENTINEL


def compute_ngram_jaccard(baseline_text: str, current_text: str, n: int = 3) -> float:
    """Compute word n-gram Jaccard similarity between baseline and current text.

    Args:
        baseline_text: Reference baseline text.
        current_text: Candidate current pass text.
        n: Contiguous word shingle size (must be >= 1).

    Returns:
        float: Jaccard similarity coefficient bounded in [0.0, 1.0].
    """
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise DomainValidationError(f"n must be an integer >= 1, got {n!r}.")

    base_tokens = _tokenize_words(baseline_text)
    curr_tokens = _tokenize_words(current_text)

    if not base_tokens and not curr_tokens:
        return 1.0
    if not base_tokens or not curr_tokens:
        return 0.0

    base_shingles = _build_ngram_shingles(base_tokens, n)
    curr_shingles = _build_ngram_shingles(curr_tokens, n)
    union = base_shingles | curr_shingles
    return len(base_shingles & curr_shingles) / len(union)


def compute_word_delta_ratio(baseline_text: str, current_text: str) -> float:
    """Compute relative word-count delta ratio between baseline and current text.

    Args:
        baseline_text: Reference baseline text.
        current_text: Candidate current pass text.

    Returns:
        float: Relative word-count variation bounded in [0.0, 1.0].
    """
    n_base = len(_tokenize_words(baseline_text))
    n_curr = len(_tokenize_words(current_text))
    if n_base == 0 and n_curr == 0:
        return 0.0
    return abs(n_curr - n_base) / max(n_curr, n_base)


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Compute cosine similarity between two numeric vectors using pure stdlib math.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector of matching dimensionality.

    Returns:
        float: Cosine similarity bounded in [-1.0, 1.0], or 0.0 when either norm is zero.
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector length mismatch: {len(vec_a)} != {len(vec_b)}")
    if not vec_a:
        return 0.0

    dot = math.fsum(a * b for a, b in zip(vec_a, vec_b, strict=True))
    norm_a = math.sqrt(math.fsum(a * a for a in vec_a))
    norm_b = math.sqrt(math.fsum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def compute_maxsim_novelty(
    baseline_vectors: Sequence[Sequence[float]],
    current_vectors: Sequence[Sequence[float]],
    similarity_threshold: float = 0.88,
) -> tuple[int, float, float]:
    """Evaluate unit-level MaxSim novelty of current vectors against baseline vectors.

    Args:
        baseline_vectors: Embedding vectors representing baseline semantic units.
        current_vectors: Embedding vectors representing candidate semantic units.
        similarity_threshold: Minimum cosine similarity required to consider a unit covered.

    Returns:
        tuple[int, float, float]: Tuple of (novel_count, max_novelty, mean_max_similarity).
    """
    if (
        isinstance(similarity_threshold, bool)
        or not isinstance(similarity_threshold, (int, float))
        or not math.isfinite(similarity_threshold)
        or not (0.0 < similarity_threshold <= 1.0)
    ):
        raise DomainValidationError(
            f"similarity_threshold must be a finite float in (0.0, 1.0], got {similarity_threshold!r}."
        )

    if not current_vectors:
        return (0, 0.0, 1.0)
    if not baseline_vectors:
        return (len(current_vectors), 1.0, 0.0)

    novel_count = 0
    max_novelty = 0.0
    max_similarities: list[float] = []

    for curr_vec in current_vectors:
        max_sim = max(cosine_similarity(curr_vec, base_vec) for base_vec in baseline_vectors)
        novelty = min(1.0, max(0.0, 1.0 - max_sim))
        if max_sim < similarity_threshold:
            novel_count += 1
        max_novelty = max(max_novelty, novelty)
        max_similarities.append(max_sim)

    mean_max_similarity = math.fsum(max_similarities) / len(max_similarities)
    return (novel_count, max_novelty, mean_max_similarity)


def evaluate_lexical_convergence(
    baseline_text: str,
    current_text: str,
    thresholds: SaturationThresholds | None = None,
    pass_index: int = 2,
) -> SaturationVerdict | None:
    """Evaluate Tier 1 sentinel and lexical convergence gates before semantic embedding.

    Args:
        baseline_text: Reference baseline text from source or prior pass.
        current_text: Candidate text produced by the current pass.
        thresholds: Saturation threshold configuration; defaults to SaturationThresholds().
        pass_index: One-based pass index being evaluated.

    Returns:
        SaturationVerdict | None: Saturation verdict if Tier 1 short-circuits, else None.
    """
    active_thresholds = thresholds if thresholds is not None else SaturationThresholds()
    is_sentinel = is_explicit_stop_sentinel(current_text, pass_index=pass_index)
    lexical_jaccard = compute_ngram_jaccard(baseline_text, current_text)
    word_delta_ratio = compute_word_delta_ratio(baseline_text, current_text)
    total_paragraphs = len(segment_semantic_units(current_text))

    if is_sentinel:
        return SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.EXPLICIT_SENTINEL,
            lexical_jaccard=lexical_jaccard,
            word_delta_ratio=word_delta_ratio,
            max_novelty=0.0,
            novel_paragraphs=0,
            total_paragraphs=total_paragraphs,
            preserve_baseline=True,
            provider="sentinel",
        )

    if (
        lexical_jaccard >= active_thresholds.lexical_identity_threshold
        and word_delta_ratio <= active_thresholds.max_lexical_word_delta
    ):
        return SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.LEXICAL_IDENTITY,
            lexical_jaccard=lexical_jaccard,
            word_delta_ratio=word_delta_ratio,
            max_novelty=0.0,
            novel_paragraphs=0,
            total_paragraphs=total_paragraphs,
            preserve_baseline=True,
            provider="lexical",
        )

    return None


def evaluate_semantic_convergence(
    baseline_vectors: Sequence[Sequence[float]],
    current_vectors: Sequence[Sequence[float]],
    thresholds: SaturationThresholds | None = None,
    *,
    lexical_jaccard: float = 0.0,
    word_delta_ratio: float = 0.0,
    provider: str = "semantic",
) -> SaturationVerdict:
    """Evaluate Tier 2 unit-level MaxSim semantic convergence from precomputed embeddings.

    Args:
        baseline_vectors: Embedding vectors for baseline semantic units.
        current_vectors: Embedding vectors for current candidate semantic units.
        thresholds: Saturation threshold configuration; defaults to SaturationThresholds().
        lexical_jaccard: Precomputed Tier 1 n-gram Jaccard similarity.
        word_delta_ratio: Precomputed Tier 1 relative word-count delta ratio.
        provider: Active embedding provider identifier for verdict attribution.

    Returns:
        SaturationVerdict: Structured semantic plateau or novel content verdict.
    """
    active_thresholds = thresholds if thresholds is not None else SaturationThresholds()
    novel_paragraphs, max_novelty, _ = compute_maxsim_novelty(
        baseline_vectors,
        current_vectors,
        similarity_threshold=active_thresholds.semantic_similarity_threshold,
    )
    total_paragraphs = len(current_vectors)

    if novel_paragraphs <= active_thresholds.max_novel_paragraphs_for_saturation:
        return SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=lexical_jaccard,
            word_delta_ratio=word_delta_ratio,
            max_novelty=max_novelty,
            novel_paragraphs=novel_paragraphs,
            total_paragraphs=total_paragraphs,
            preserve_baseline=True,
            provider=provider,
        )

    return SaturationVerdict(
        is_saturated=False,
        reason=SaturationReason.NOVEL_CONTENT,
        lexical_jaccard=lexical_jaccard,
        word_delta_ratio=word_delta_ratio,
        max_novelty=max_novelty,
        novel_paragraphs=novel_paragraphs,
        total_paragraphs=total_paragraphs,
        preserve_baseline=False,
        provider=provider,
    )
