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
LONG_UNIT_WORD_CUTOFF: Final[int] = 120
SLIDING_WINDOW_SENTENCES: Final[int] = 3
SLIDING_WINDOW_OVERLAP: Final[int] = 1

_BLANK_LINE_SPLIT_PATTERN = re.compile(r"\n\s*\n")
_HEADING_LINE_PATTERN = re.compile(r"^\s*#{1,6}\s+")
_NUMBERED_ITEM_LINE_PATTERN = re.compile(r"^\s*\d+\.\s+")
_SENTENCE_END_CANDIDATE_PATTERN = re.compile(r"[.!?]+[\"'”’)\]]*\s+")
_WORD_TOKEN_PATTERN = re.compile(r"\w+")

_TITLE_ABBREVIATIONS: Final[frozenset[str]] = frozenset(
    {
        "a.c",
        "aprox",
        "ca",
        "cf",
        "d",
        "d.c",
        "dr",
        "dra",
        "e.g",
        "i.e",
        "núm",
        "pág",
        "págs",
        "pp",
        "prof",
        "profa",
        "s",
        "séc",
        "sr",
        "sra",
        "srs",
        "sras",
        "st",
        "sta",
        "sto",
        "v.g",
        "vol",
        "vols",
    }
)
_NUMBERED_REF_ABBREVIATIONS: Final[frozenset[str]] = frozenset(
    {"art", "cap", "fig", "n", "no", "p", "sec", "tab"}
)


def _tokenize_words(text: str) -> list[str]:
    """Extract normalized lowercase alphanumeric word tokens from text."""
    return _WORD_TOKEN_PATTERN.findall(text.lower())


def _build_ngram_shingles(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    """Build contiguous word n-gram shingles, or a single tuple when shorter than n."""
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def segment_semantic_units(
    text: str,
    *,
    long_unit_word_cutoff: int = LONG_UNIT_WORD_CUTOFF,
    sliding_window_sentences: int = SLIDING_WINDOW_SENTENCES,
    sliding_window_overlap: int = SLIDING_WINDOW_OVERLAP,
) -> tuple[str, ...]:
    """Segment markdown compendia into discrete paragraph, item, and window semantic units.

    Units exceeding ``long_unit_word_cutoff`` words are conditionally sub-chunked
    into overlapping sentence sliding windows to avoid intra-paragraph embedding dilution.

    Args:
        text: Markdown compendium text containing main body and optional '### Extra Info'.
        long_unit_word_cutoff: Word-count threshold above which a unit is sub-chunked.
        sliding_window_sentences: Number of sentences per sliding window.
        sliding_window_overlap: Number of overlapping sentences between consecutive windows.

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
        for unit in _split_kept_block_lines(kept_lines):
            units.extend(
                _apply_long_unit_sliding_window(
                    unit,
                    word_cutoff=long_unit_word_cutoff,
                    window_sentences=sliding_window_sentences,
                    window_overlap=sliding_window_overlap,
                )
            )

    return tuple(units)


def _apply_long_unit_sliding_window(
    unit: str,
    *,
    word_cutoff: int = LONG_UNIT_WORD_CUTOFF,
    window_sentences: int = SLIDING_WINDOW_SENTENCES,
    window_overlap: int = SLIDING_WINDOW_OVERLAP,
) -> list[str]:
    """Slice units exceeding word_cutoff words into overlapping sentence windows."""
    if len(_tokenize_words(unit)) <= word_cutoff:
        return [unit]

    sentences = _split_sentences(unit)
    if len(sentences) <= window_sentences:
        return [unit]

    stride = window_sentences - window_overlap
    windows: list[str] = []
    start = 0
    while True:
        end = start + window_sentences
        windows.append(" ".join(sentences[start:end]))
        if end >= len(sentences):
            return windows
        start += stride


def _split_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into trimmed sentences while guarding abbreviations and markers."""
    stripped = paragraph.strip()
    sentences: list[str] = []
    start_idx = 0
    for match in _SENTENCE_END_CANDIDATE_PATTERN.finditer(stripped):
        if not _is_sentence_boundary(stripped, match.start(), match.end()):
            continue
        sentences.append(stripped[start_idx : match.end()].strip())
        start_idx = match.end()

    sentences.append(stripped[start_idx:].strip())
    return sentences


def _is_sentence_boundary(text: str, boundary_start: int, boundary_end: int) -> bool:
    """Return True when punctuation and whitespace at boundary delimit a new sentence."""
    after = text[boundary_end:].lstrip("*_\"'“‘([")
    if not after:
        return False

    if text[boundary_start] in ("!", "?"):
        return True

    if after[0].islower():
        return False

    prefix_text = text[:boundary_start].strip()
    cleaned_prefix = prefix_text.rstrip(".")
    if not cleaned_prefix or cleaned_prefix.isdigit():
        return False

    lower_stem = prefix_text.rsplit(maxsplit=1)[-1].lstrip("*_\"'“‘([").lower()
    if lower_stem in _TITLE_ABBREVIATIONS:
        return False

    return not (lower_stem in _NUMBERED_REF_ABBREVIATIONS and after[0].isdigit())


def _split_kept_block_lines(kept_lines: list[str]) -> list[str]:
    """Split a heading-free block into semantic units, isolating numbered list items."""
    if not kept_lines:
        return []

    split_units: list[str] = []
    current_unit_lines: list[str] = []
    for line in kept_lines:
        if _NUMBERED_ITEM_LINE_PATTERN.match(line) and current_unit_lines:
            split_units.append("\n".join(current_unit_lines))
            current_unit_lines = [line]
        else:
            current_unit_lines.append(line)

    split_units.append("\n".join(current_unit_lines))
    return split_units


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
) -> tuple[int, float]:
    """Evaluate unit-level MaxSim novelty of current vectors against baseline vectors.

    Args:
        baseline_vectors: Embedding vectors representing baseline semantic units.
        current_vectors: Embedding vectors representing candidate semantic units.
        similarity_threshold: Minimum cosine similarity required to consider a unit covered.

    Returns:
        tuple[int, float]: Tuple of (novel_count, max_novelty).
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
        return (0, 0.0)
    if not baseline_vectors:
        return (len(current_vectors), 1.0)

    novel_count = 0
    max_novelty = 0.0

    for curr_vec in current_vectors:
        max_sim = max(cosine_similarity(curr_vec, base_vec) for base_vec in baseline_vectors)
        novelty = min(1.0, max(0.0, 1.0 - max_sim))
        if max_sim < similarity_threshold:
            novel_count += 1
        max_novelty = max(max_novelty, novelty)

    return (novel_count, max_novelty)


def evaluate_lexical_convergence(
    baseline_text: str,
    current_text: str,
    thresholds: SaturationThresholds | None = None,
    pass_index: int = 2,
    *,
    lexical_jaccard: float | None = None,
    word_delta_ratio: float | None = None,
    current_unit_count: int | None = None,
) -> SaturationVerdict | None:
    """Evaluate Tier 1 sentinel and lexical convergence gates before semantic embedding.

    Args:
        baseline_text: Reference baseline text from source or prior pass.
        current_text: Candidate text produced by the current pass.
        thresholds: Saturation threshold configuration; defaults to SaturationThresholds().
        pass_index: One-based pass index being evaluated.
        lexical_jaccard: Optional precomputed n-gram Jaccard similarity.
        word_delta_ratio: Optional precomputed relative word-count delta ratio.
        current_unit_count: Optional precomputed semantic unit count for current_text.

    Returns:
        SaturationVerdict | None: Saturation verdict if Tier 1 short-circuits, else None.
    """
    active_thresholds = thresholds if thresholds is not None else SaturationThresholds()
    is_sentinel = is_explicit_stop_sentinel(current_text, pass_index=pass_index)
    resolved_jaccard = (
        compute_ngram_jaccard(baseline_text, current_text)
        if lexical_jaccard is None
        else lexical_jaccard
    )
    resolved_word_delta = (
        compute_word_delta_ratio(baseline_text, current_text)
        if word_delta_ratio is None
        else word_delta_ratio
    )
    total_paragraphs = (
        len(
            segment_semantic_units(
                current_text,
                long_unit_word_cutoff=active_thresholds.long_unit_word_cutoff,
                sliding_window_sentences=active_thresholds.sliding_window_sentences,
                sliding_window_overlap=active_thresholds.sliding_window_overlap,
            )
        )
        if current_unit_count is None
        else current_unit_count
    )

    if is_sentinel:
        return SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.EXPLICIT_SENTINEL,
            lexical_jaccard=resolved_jaccard,
            word_delta_ratio=resolved_word_delta,
            max_novelty=0.0,
            novel_paragraphs=0,
            total_paragraphs=total_paragraphs,
            preserve_baseline=True,
            provider="sentinel",
        )

    if (
        resolved_jaccard >= active_thresholds.lexical_identity_threshold
        and resolved_word_delta <= active_thresholds.max_lexical_word_delta
    ):
        return SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.LEXICAL_IDENTITY,
            lexical_jaccard=resolved_jaccard,
            word_delta_ratio=resolved_word_delta,
            max_novelty=0.0,
            novel_paragraphs=0,
            total_paragraphs=total_paragraphs,
            preserve_baseline=False,
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
    novel_paragraphs, max_novelty = compute_maxsim_novelty(
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
            preserve_baseline=False,
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
