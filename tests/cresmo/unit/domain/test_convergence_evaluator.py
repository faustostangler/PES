"""Unit tests for Domain Convergence Value Objects and Convergence Evaluator.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: Sections 2.2 (Convergence Value Objects) and 2.3 (Domain Convergence Evaluator)
"""

from __future__ import annotations

import json
import math
from dataclasses import FrozenInstanceError
from enum import StrEnum
from typing import Any, cast

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.services.convergence_evaluator import (
    NO_NEW_GAPS_SENTINEL,
    compute_maxsim_novelty,
    compute_ngram_jaccard,
    compute_word_delta_ratio,
    cosine_similarity,
    evaluate_lexical_convergence,
    evaluate_semantic_convergence,
    is_explicit_stop_sentinel,
    segment_semantic_units,
)
from cresmo.domain.value_objects.convergence import (
    ConvergenceMode,
    SaturationPolicy,
    SaturationReason,
    SaturationThresholds,
    SaturationVerdict,
    never_saturate,
)


def test_convergence_enums_and_never_saturate_contract() -> None:
    assert issubclass(ConvergenceMode, StrEnum)
    assert ConvergenceMode.NONE.value == "none"
    assert ConvergenceMode.HYBRID_SEMANTIC.value == "hybrid_semantic"

    assert issubclass(SaturationReason, StrEnum)
    assert SaturationReason.DISABLED.value == "disabled"
    assert SaturationReason.EXPLICIT_SENTINEL.value == "explicit_sentinel"
    assert SaturationReason.LEXICAL_IDENTITY.value == "lexical_identity"
    assert SaturationReason.SEMANTIC_PLATEAU.value == "semantic_plateau"
    assert SaturationReason.NOVEL_CONTENT.value == "novel_content"

    policy: SaturationPolicy = never_saturate
    verdict = policy("baseline text", "current text", 1)
    assert verdict == SaturationVerdict(
        is_saturated=False,
        reason=SaturationReason.DISABLED,
        lexical_jaccard=0.0,
        word_delta_ratio=0.0,
        max_novelty=1.0,
        novel_paragraphs=0,
        total_paragraphs=0,
        preserve_baseline=False,
        provider="disabled",
    )
    assert verdict.reason is SaturationReason.DISABLED
    assert verdict.is_saturated is False
    assert verdict.provider == "disabled"


def test_saturation_thresholds_defaults_immutability_and_validation() -> None:
    defaults = SaturationThresholds()
    assert defaults.lexical_identity_threshold == 0.95
    assert defaults.max_lexical_word_delta == 0.03
    assert defaults.semantic_similarity_threshold == 0.88
    assert defaults.max_novel_paragraphs_for_saturation == 0

    with pytest.raises(FrozenInstanceError):
        cast(Any, defaults).semantic_similarity_threshold = 0.90

    # Valid extreme boundaries
    boundary = SaturationThresholds(
        lexical_identity_threshold=1.0,
        max_lexical_word_delta=0.0,
        semantic_similarity_threshold=1.0,
        max_novel_paragraphs_for_saturation=0,
    )
    assert boundary.max_lexical_word_delta == 0.0

    # Invalid lexical_identity_threshold: (0.0, 1.0], finite, non-bool
    for bad_val in (0.0, -0.1, 1.01, math.nan, math.inf, -math.inf, True, False):
        with pytest.raises(DomainValidationError):
            SaturationThresholds(lexical_identity_threshold=cast(float, bad_val))

    # Invalid max_lexical_word_delta: [0.0, 1.0], finite, non-bool
    for bad_val in (-0.01, 1.01, math.nan, math.inf, -math.inf, True, False):
        with pytest.raises(DomainValidationError):
            SaturationThresholds(max_lexical_word_delta=cast(float, bad_val))

    # Invalid semantic_similarity_threshold: (0.0, 1.0], finite, non-bool
    for bad_val in (0.0, -0.5, 1.01, math.nan, math.inf, -math.inf, True, False):
        with pytest.raises(DomainValidationError):
            SaturationThresholds(semantic_similarity_threshold=cast(float, bad_val))

    # Invalid max_novel_paragraphs_for_saturation: non-bool int >= 0
    for bad_count in (-1, True, False, 1.5):
        with pytest.raises(DomainValidationError):
            SaturationThresholds(max_novel_paragraphs_for_saturation=cast(int, bad_count))

    assert issubclass(DomainValidationError, ValueError)


def test_saturation_verdict_invariants_and_metadata_serialization() -> None:
    verdict = SaturationVerdict(
        is_saturated=False,
        reason=SaturationReason.NOVEL_CONTENT,
        lexical_jaccard=0.35,
        word_delta_ratio=0.12,
    )
    assert verdict.max_novelty == 1.0
    assert verdict.novel_paragraphs == 0
    assert verdict.total_paragraphs == 0
    assert verdict.preserve_baseline is False
    assert verdict.provider == ""

    with pytest.raises(FrozenInstanceError):
        cast(Any, verdict).is_saturated = True

    # Non-saturated reasons must not have is_saturated=True or preserve_baseline=True
    for non_sat_reason in (SaturationReason.DISABLED, SaturationReason.NOVEL_CONTENT):
        with pytest.raises(DomainValidationError):
            SaturationVerdict(
                is_saturated=True,
                reason=non_sat_reason,
                lexical_jaccard=0.5,
                word_delta_ratio=0.1,
            )
        with pytest.raises(DomainValidationError):
            SaturationVerdict(
                is_saturated=False,
                reason=non_sat_reason,
                lexical_jaccard=0.5,
                word_delta_ratio=0.1,
                preserve_baseline=True,
            )

    # Saturated reasons must have is_saturated=True
    for sat_reason in (
        SaturationReason.EXPLICIT_SENTINEL,
        SaturationReason.LEXICAL_IDENTITY,
        SaturationReason.SEMANTIC_PLATEAU,
    ):
        with pytest.raises(DomainValidationError):
            SaturationVerdict(
                is_saturated=False,
                reason=sat_reason,
                lexical_jaccard=0.95,
                word_delta_ratio=0.01,
            )

    # Scalar range and count invariants
    with pytest.raises(DomainValidationError):
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=1.2,
            word_delta_ratio=0.0,
        )
    with pytest.raises(DomainValidationError):
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=0.5,
            word_delta_ratio=math.nan,
        )
    with pytest.raises(DomainValidationError):
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=0.5,
            word_delta_ratio=0.0,
            max_novelty=-0.1,
        )
    with pytest.raises(DomainValidationError):
        SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.2,
            word_delta_ratio=0.1,
            novel_paragraphs=3,
            total_paragraphs=2,
        )
    with pytest.raises(DomainValidationError):
        SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.2,
            word_delta_ratio=0.1,
            novel_paragraphs=cast(int, True),
            total_paragraphs=2,
        )
    for bad_verdict_kwargs in (
        {"is_saturated": "yes", "reason": SaturationReason.NOVEL_CONTENT},
        {"is_saturated": False, "reason": SaturationReason.NOVEL_CONTENT, "preserve_baseline": 1},
        {"is_saturated": False, "reason": "novel_content"},
        {"is_saturated": False, "reason": SaturationReason.NOVEL_CONTENT, "provider": 123},
    ):
        with pytest.raises(DomainValidationError):
            SaturationVerdict(
                lexical_jaccard=0.2,
                word_delta_ratio=0.1,
                **cast(dict[str, Any], bad_verdict_kwargs),
            )

    plateau = SaturationVerdict(
        is_saturated=True,
        reason=SaturationReason.SEMANTIC_PLATEAU,
        lexical_jaccard=0.61,
        word_delta_ratio=0.04,
        max_novelty=0.08,
        novel_paragraphs=0,
        total_paragraphs=4,
        preserve_baseline=False,
        provider="gemini",
    )
    meta = plateau.to_metadata_dict()
    assert meta == {
        "is_saturated": True,
        "reason": "semantic_plateau",
        "lexical_jaccard": 0.61,
        "word_delta_ratio": 0.04,
        "max_novelty": 0.08,
        "novel_paragraphs": 0,
        "total_paragraphs": 4,
        "preserve_baseline": False,
        "provider": "gemini",
    }
    assert type(meta["reason"]) is str
    assert json.dumps(meta)


def test_segment_semantic_units_strips_headings_and_preserves_extra_info() -> None:
    assert segment_semantic_units("") == ()
    assert segment_semantic_units("   \n\n\t ") == ()
    assert segment_semantic_units("## Heading Only\n\n### Subheading") == ()
    assert segment_semantic_units(f"## Heading\n\n{NO_NEW_GAPS_SENTINEL}") == ()

    markdown = (
        "## Main Section\r\n\r\n"
        "First analytical paragraph about monetary expansion.\r\n\r\n"
        "### Subsection\r\n"
        "Second paragraph attached directly below heading.\r\n\r\n"
        "### Extra Info\r\n\r\n"
        "1. Contextual entity detail for central banks.\r\n\r\n"
        "2. Historical timeline anchor for Bretton Woods.\r\n\r\n"
        f"{NO_NEW_GAPS_SENTINEL}"
    )
    units = segment_semantic_units(markdown)
    assert isinstance(units, tuple)
    assert units == (
        "First analytical paragraph about monetary expansion.",
        "Second paragraph attached directly below heading.",
        "1. Contextual entity detail for central banks.",
        "2. Historical timeline anchor for Bretton Woods.",
    )

    # Single-newline numbered items in Extra Info MUST split into discrete semantic units
    single_newline_extra = (
        "## Main Section\n\n"
        "Main narrative paragraph.\n\n"
        "### Extra Info\n"
        "1. First single-newline extra info fact.\n"
        "2. Second single-newline extra info fact.\n"
        "3. Third single-newline extra info fact."
    )
    assert segment_semantic_units(single_newline_extra) == (
        "Main narrative paragraph.",
        "1. First single-newline extra info fact.",
        "2. Second single-newline extra info fact.",
        "3. Third single-newline extra info fact.",
    )


def _make_sentence(prefix: str, filler_words: int, ending: str = ".") -> str:
    """Build a deterministic sentence with exact total word count = 1 + filler_words."""
    body = " ".join(f"{prefix}{idx}" for idx in range(filler_words))
    return f"Sentence {body}{ending}" if body else f"Sentence{ending}"


def test_segment_semantic_units_long_paragraph_sliding_window_cutoff() -> None:
    # Exactly 120 words across 5 sentences (5 x 24 words) MUST remain 1 single unit (strict > 120)
    exact_120 = " ".join(_make_sentence(f"p{i}_", 23) for i in range(5))
    assert len(exact_120.split()) == 120
    assert segment_semantic_units(exact_120) == (exact_120,)

    # 121 words across 5 sentences MUST slice into 3-sentence windows with overlap=1 (stride=2)
    s0 = _make_sentence("a", 23)
    s1 = _make_sentence("b", 23)
    s2 = _make_sentence("c", 23)
    s3 = _make_sentence("d", 23)
    s4 = _make_sentence("e", 24)
    long_5 = f"{s0} {s1} {s2} {s3} {s4}"
    assert len(long_5.split()) == 121
    assert segment_semantic_units(long_5) == (
        f"{s0} {s1} {s2}",
        f"{s2} {s3} {s4}",
    )

    # 4 sentences (> 120 words) slices into [0,1,2] and [2,3] preserving 1-sentence overlap
    q0 = _make_sentence("q0_", 30)
    q1 = _make_sentence("q1_", 30)
    q2 = _make_sentence("q2_", 30)
    q3 = _make_sentence("q3_", 30)
    long_4 = f"{q0} {q1} {q2} {q3}"
    assert segment_semantic_units(long_4) == (
        f"{q0} {q1} {q2}",
        f"{q2} {q3}",
    )

    # > 120 words concentrated in <= 3 long baroque sentences remains 1 intact unit
    baroque_3 = " ".join(_make_sentence(f"z{i}_", 41) for i in range(3))
    assert segment_semantic_units(baroque_3) == (baroque_3,)

    # Custom configurable cutoff and sliding window parameters
    custom_units = segment_semantic_units(
        long_5,
        long_unit_word_cutoff=200,
    )
    assert custom_units == (long_5,)
    custom_win4 = segment_semantic_units(
        long_5,
        long_unit_word_cutoff=50,
        sliding_window_sentences=4,
        sliding_window_overlap=2,
    )
    assert custom_win4 == (
        f"{s0} {s1} {s2} {s3}",
        f"{s2} {s3} {s4}",
    )

    # SaturationThresholds sliding-window validation bounds
    with pytest.raises(DomainValidationError):
        SaturationThresholds(long_unit_word_cutoff=0)
    with pytest.raises(DomainValidationError):
        SaturationThresholds(sliding_window_sentences=0)
    with pytest.raises(DomainValidationError):
        SaturationThresholds(sliding_window_sentences=3, sliding_window_overlap=3)


def test_segment_semantic_units_sentence_boundary_guards_abbreviations_and_markers() -> None:
    padding = " ".join(f"contexto{i}" for i in range(30))
    padded_item = (
        f"1. ... D. Afonso Henriques governou no Séc. XII perto de Sto. Agostinho {padding}. "
        f"Em 1143 assinou tratados cf. p. 42 e Art. 5 com prata etc. e ouro {padding}! "
        f"_Afonso_ consolidou o reino em 1143. "
        f"**1179** trouxe reconhecimento papal com _Bula_ longa {padding}. ("
    )
    units = segment_semantic_units(f"### Extra Info\n{padded_item}")
    assert len(units) == 2
    assert units[0].startswith("1. ... D. Afonso Henriques governou no Séc. XII")
    assert "Sto. Agostinho" in units[0]
    assert "cf. p. 42 e Art. 5 com prata etc. e ouro" in units[0]
    assert units[0].endswith("_Afonso_ consolidou o reino em 1143.")
    assert units[1].startswith("_Afonso_ consolidou o reino em 1143.")
    assert "**1179** trouxe reconhecimento papal" in units[1]
    assert units[1].endswith(". (")

    ellipsis_prefix = f"... Prefácio {padding}. Segunda parte {padding}. Terceira parte {padding}. Quarta {padding}."
    ellipsis_units = segment_semantic_units(ellipsis_prefix)
    assert len(ellipsis_units) == 2
    assert ellipsis_units[0].startswith("... Prefácio")


def test_is_explicit_stop_sentinel_pass_index_and_validation() -> None:
    assert NO_NEW_GAPS_SENTINEL == "<NO_NEW_GAPS/>"

    # Pass 1 ALWAYS returns False to prevent zero-effort pass-1 termination
    assert is_explicit_stop_sentinel("<NO_NEW_GAPS/>", pass_index=1) is False
    assert is_explicit_stop_sentinel("  <NO_NEW_GAPS/>  ", pass_index=1) is False

    # Pass >= 2 returns True only when stripped text matches sentinel exactly
    assert is_explicit_stop_sentinel("<NO_NEW_GAPS/>") is True
    assert is_explicit_stop_sentinel("  <NO_NEW_GAPS/>  ", pass_index=2) is True
    assert is_explicit_stop_sentinel("\n\t<NO_NEW_GAPS/>\n", pass_index=3) is True
    assert (
        is_explicit_stop_sentinel("## Title\n\nExtra prose <NO_NEW_GAPS/>", pass_index=2) is False
    )
    assert is_explicit_stop_sentinel("## Title\n\nRegular prose.", pass_index=2) is False
    assert is_explicit_stop_sentinel("", pass_index=2) is False

    for bad_pass in (0, -1, True, False):
        with pytest.raises(DomainValidationError):
            is_explicit_stop_sentinel("<NO_NEW_GAPS/>", pass_index=bad_pass)


def test_compute_ngram_jaccard_and_word_delta_ratio() -> None:
    # Empty boundaries
    assert compute_ngram_jaccard("", "") == 1.0
    assert compute_ngram_jaccard("   ", "") == 1.0
    assert compute_ngram_jaccard("", "non empty prose") == 0.0
    assert compute_ngram_jaccard("non empty prose", "") == 0.0

    # Identical and disjoint cases
    assert compute_ngram_jaccard("Alpha Beta Gamma Delta", "alpha beta, gamma delta.") == 1.0
    assert compute_ngram_jaccard("one two three four", "five six seven eight") == 0.0

    # Partial 3-gram overlap: {("one","two","three"), ("two","three","four")} vs {("one","two","three"), ("two","three","five")}
    assert compute_ngram_jaccard("one two three four", "one two three five", n=3) == pytest.approx(
        1.0 / 3.0
    )

    # Short sequences (< n tokens) form single tuple shingle
    assert compute_ngram_jaccard("alpha beta", "alpha beta", n=3) == 1.0
    assert compute_ngram_jaccard("alpha beta", "alpha gamma", n=3) == 0.0

    for bad_n in (0, -2, True, False):
        with pytest.raises(DomainValidationError):
            compute_ngram_jaccard("a b c", "a b c", n=bad_n)

    # Word delta ratio
    assert compute_word_delta_ratio("", "") == 0.0
    assert compute_word_delta_ratio("alpha beta", "") == 1.0
    assert compute_word_delta_ratio("", "alpha beta") == 1.0
    assert compute_word_delta_ratio("one two three", "four five six") == 0.0
    assert compute_word_delta_ratio(
        "one two three four", "one two three four five"
    ) == pytest.approx(0.2)
    assert compute_word_delta_ratio("a b c d e f g h i j", "a b c d e f g h") == pytest.approx(0.2)


def test_cosine_similarity_and_compute_maxsim_novelty() -> None:
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 0.0], [1.0])

    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [0.0, 0.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [2.0, 4.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    # Empty vector boundary contracts for compute_maxsim_novelty
    assert compute_maxsim_novelty([[1.0, 0.0]], []) == (0, 0.0)
    assert compute_maxsim_novelty([], [[1.0, 0.0], [0.0, 1.0]]) == (2, 1.0)

    # Mixed novelty: one exact match (sim=1.0, nov=0.0) and one orthogonal unit (sim=0.0, nov=1.0)
    novel_count, max_novelty = compute_maxsim_novelty(
        [[1.0, 0.0]],
        [[1.0, 0.0], [0.0, 1.0]],
        similarity_threshold=0.88,
    )
    assert novel_count == 1
    assert max_novelty == pytest.approx(1.0)

    # All current units covered above 0.88 threshold
    covered_count, covered_max_nov = compute_maxsim_novelty(
        [[1.0, 0.0], [0.0, 1.0]],
        [[1.0, 0.0], [0.99, 0.1]],
        similarity_threshold=0.88,
    )
    assert covered_count == 0
    assert 0.0 <= covered_max_nov < 0.02

    for bad_thresh in (0.0, -0.2, 1.05, math.nan, True):
        with pytest.raises(DomainValidationError):
            compute_maxsim_novelty(
                [[1.0, 0.0]],
                [[1.0, 0.0]],
                similarity_threshold=cast(float, bad_thresh),
            )


def test_evaluate_lexical_convergence_gates() -> None:
    baseline = "## Topic\n\nCentral banks regulate monetary aggregates across credit cycles."

    # Sentinel short-circuits on pass >= 2
    sentinel_verdict = evaluate_lexical_convergence(baseline, "  <NO_NEW_GAPS/>  ", pass_index=2)
    assert sentinel_verdict is not None
    assert sentinel_verdict.is_saturated is True
    assert sentinel_verdict.reason is SaturationReason.EXPLICIT_SENTINEL
    assert sentinel_verdict.preserve_baseline is True
    assert sentinel_verdict.provider == "sentinel"
    assert sentinel_verdict.total_paragraphs == 0

    # Pass 1 ignores sentinel and returns None when lexically distinct from baseline
    assert evaluate_lexical_convergence(baseline, "<NO_NEW_GAPS/>", pass_index=1) is None

    # Identical text triggers LEXICAL_IDENTITY short-circuit
    lexical_verdict = evaluate_lexical_convergence(baseline, baseline, pass_index=2)
    assert lexical_verdict is not None
    assert lexical_verdict.is_saturated is True
    assert lexical_verdict.reason is SaturationReason.LEXICAL_IDENTITY
    assert lexical_verdict.lexical_jaccard == pytest.approx(1.0)
    assert lexical_verdict.word_delta_ratio == pytest.approx(0.0)
    assert lexical_verdict.preserve_baseline is False
    assert lexical_verdict.provider == "lexical"
    assert lexical_verdict.total_paragraphs == 1

    # High Jaccard but excessive word delta should NOT short-circuit
    strict_thresholds = SaturationThresholds(
        lexical_identity_threshold=0.5,
        max_lexical_word_delta=0.05,
    )
    expanded = (
        "## Topic\n\nCentral banks regulate monetary aggregates across credit cycles "
        "through open market operations and reserve requirements."
    )
    assert (
        evaluate_lexical_convergence(
            baseline,
            expanded,
            thresholds=strict_thresholds,
            pass_index=2,
        )
        is None
    )

    # Distinct content returns None to proceed to semantic layer
    distinct = "## Topic\n\nFiscal deficits alter sovereign yield curve slopes over decades."
    assert evaluate_lexical_convergence(baseline, distinct, pass_index=2) is None


def test_evaluate_semantic_convergence_plateau_and_novel_content() -> None:
    thresholds = SaturationThresholds(
        semantic_similarity_threshold=0.88,
        max_novel_paragraphs_for_saturation=0,
    )

    plateau_verdict = evaluate_semantic_convergence(
        [[1.0, 0.0], [0.0, 1.0]],
        [[1.0, 0.0], [0.0, 1.0]],
        thresholds=thresholds,
        lexical_jaccard=0.45,
        word_delta_ratio=0.02,
        provider="gemini",
    )
    assert plateau_verdict.is_saturated is True
    assert plateau_verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert plateau_verdict.preserve_baseline is False
    assert plateau_verdict.novel_paragraphs == 0
    assert plateau_verdict.total_paragraphs == 2
    assert plateau_verdict.max_novelty == pytest.approx(0.0)
    assert plateau_verdict.lexical_jaccard == 0.45
    assert plateau_verdict.word_delta_ratio == 0.02
    assert plateau_verdict.provider == "gemini"

    novel_verdict = evaluate_semantic_convergence(
        [[1.0, 0.0]],
        [[1.0, 0.0], [0.0, 1.0]],
        thresholds=thresholds,
        lexical_jaccard=0.30,
        word_delta_ratio=0.25,
        provider="tfidf_fallback",
    )
    assert novel_verdict.is_saturated is False
    assert novel_verdict.reason is SaturationReason.NOVEL_CONTENT
    assert novel_verdict.preserve_baseline is False
    assert novel_verdict.novel_paragraphs == 1
    assert novel_verdict.total_paragraphs == 2
    assert novel_verdict.max_novelty == pytest.approx(1.0)
    assert novel_verdict.provider == "tfidf_fallback"

    # Tolerance max_novel_paragraphs_for_saturation=1 saturates when novel_count == 1
    tolerant = SaturationThresholds(max_novel_paragraphs_for_saturation=1)
    tolerant_verdict = evaluate_semantic_convergence(
        [[1.0, 0.0]],
        [[1.0, 0.0], [0.0, 1.0]],
        thresholds=tolerant,
        provider="ollama",
    )
    assert tolerant_verdict.is_saturated is True
    assert tolerant_verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert tolerant_verdict.novel_paragraphs == 1
    assert tolerant_verdict.total_paragraphs == 2
    assert tolerant_verdict.preserve_baseline is False
    assert tolerant_verdict.provider == "ollama"
