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

    # Valid extreme boundaries (including positive int lower bound 1 and overlap=0)
    boundary = SaturationThresholds(
        lexical_identity_threshold=1.0,
        max_lexical_word_delta=0.0,
        semantic_similarity_threshold=1.0,
        max_novel_paragraphs_for_saturation=0,
        long_unit_word_cutoff=1,
        sliding_window_sentences=1,
        sliding_window_overlap=0,
    )
    assert boundary.max_lexical_word_delta == 0.0
    assert boundary.long_unit_word_cutoff == 1
    assert boundary.sliding_window_sentences == 1
    assert boundary.sliding_window_overlap == 0

    # Invalid lexical_identity_threshold: (0.0, 1.0], finite, non-bool
    for bad_val, expected_msg in (
        (0.0, "lexical_identity_threshold must be within (0.0, 1.0], got 0.0."),
        (-0.1, "lexical_identity_threshold must be within (0.0, 1.0], got -0.1."),
        (1.01, "lexical_identity_threshold must be within (0.0, 1.0], got 1.01."),
        (math.nan, "lexical_identity_threshold must be finite, got nan."),
        (math.inf, "lexical_identity_threshold must be finite, got inf."),
        (-math.inf, "lexical_identity_threshold must be finite, got -inf."),
        (True, "lexical_identity_threshold must be a finite float, got True."),
        (False, "lexical_identity_threshold must be a finite float, got False."),
    ):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(lexical_identity_threshold=cast(float, bad_val))
        assert exc_info.value.args[0] == expected_msg

    # Invalid max_lexical_word_delta: [0.0, 1.0], finite, non-bool
    for bad_val, expected_msg in (
        (-0.01, "max_lexical_word_delta must be within [0.0, 1.0], got -0.01."),
        (1.01, "max_lexical_word_delta must be within [0.0, 1.0], got 1.01."),
        (math.nan, "max_lexical_word_delta must be finite, got nan."),
        (math.inf, "max_lexical_word_delta must be finite, got inf."),
        (-math.inf, "max_lexical_word_delta must be finite, got -inf."),
        (True, "max_lexical_word_delta must be a finite float, got True."),
        (False, "max_lexical_word_delta must be a finite float, got False."),
    ):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(max_lexical_word_delta=cast(float, bad_val))
        assert exc_info.value.args[0] == expected_msg

    # Invalid semantic_similarity_threshold: (0.0, 1.0], finite, non-bool
    for bad_val, expected_msg in (
        (0.0, "semantic_similarity_threshold must be within (0.0, 1.0], got 0.0."),
        (-0.5, "semantic_similarity_threshold must be within (0.0, 1.0], got -0.5."),
        (1.01, "semantic_similarity_threshold must be within (0.0, 1.0], got 1.01."),
        (math.nan, "semantic_similarity_threshold must be finite, got nan."),
        (math.inf, "semantic_similarity_threshold must be finite, got inf."),
        (-math.inf, "semantic_similarity_threshold must be finite, got -inf."),
        (True, "semantic_similarity_threshold must be a finite float, got True."),
        (False, "semantic_similarity_threshold must be a finite float, got False."),
    ):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(semantic_similarity_threshold=cast(float, bad_val))
        assert exc_info.value.args[0] == expected_msg

    # Invalid max_novel_paragraphs_for_saturation: non-bool int >= 0
    for bad_count in (-1, True, False, 1.5):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(max_novel_paragraphs_for_saturation=cast(int, bad_count))
        assert (
            exc_info.value.args[0]
            == f"max_novel_paragraphs_for_saturation must be a non-negative integer, got {bad_count!r}."
        )

    # Invalid long_unit_word_cutoff, sliding_window_sentences, sliding_window_overlap
    for bad_cutoff in (0, -1, True, False, 1.5):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(long_unit_word_cutoff=cast(int, bad_cutoff))
        assert (
            exc_info.value.args[0]
            == f"long_unit_word_cutoff must be a positive integer, got {bad_cutoff!r}."
        )
    for bad_win in (0, -2, True, 2.5):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(sliding_window_sentences=cast(int, bad_win))
        assert (
            exc_info.value.args[0]
            == f"sliding_window_sentences must be a positive integer, got {bad_win!r}."
        )
    for bad_overlap in (-1, True, 1.5):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationThresholds(sliding_window_overlap=cast(int, bad_overlap))
        assert (
            exc_info.value.args[0]
            == f"sliding_window_overlap must be a non-negative integer, got {bad_overlap!r}."
        )

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
        expected_non_sat = (
            f"Non-saturated reason '{non_sat_reason.value}' requires "
            "is_saturated=False and preserve_baseline=False."
        )
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationVerdict(
                is_saturated=True,
                reason=non_sat_reason,
                lexical_jaccard=0.5,
                word_delta_ratio=0.1,
            )
        assert exc_info.value.args[0] == expected_non_sat
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationVerdict(
                is_saturated=False,
                reason=non_sat_reason,
                lexical_jaccard=0.5,
                word_delta_ratio=0.1,
                preserve_baseline=True,
            )
        assert exc_info.value.args[0] == expected_non_sat

    # Saturated reasons must have is_saturated=True
    for sat_reason in (
        SaturationReason.EXPLICIT_SENTINEL,
        SaturationReason.LEXICAL_IDENTITY,
        SaturationReason.SEMANTIC_PLATEAU,
    ):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationVerdict(
                is_saturated=False,
                reason=sat_reason,
                lexical_jaccard=0.95,
                word_delta_ratio=0.01,
            )
        assert (
            exc_info.value.args[0]
            == f"Saturated reason '{sat_reason.value}' requires is_saturated=True."
        )

    # Scalar range and count invariants
    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=1.2,
            word_delta_ratio=0.0,
        )
    assert exc_info.value.args[0] == "lexical_jaccard must be within [0.0, 1.0], got 1.2."

    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=0.5,
            word_delta_ratio=math.nan,
        )
    assert exc_info.value.args[0] == "word_delta_ratio must be finite, got nan."

    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=True,
            reason=SaturationReason.SEMANTIC_PLATEAU,
            lexical_jaccard=0.5,
            word_delta_ratio=0.0,
            max_novelty=-0.1,
        )
    assert exc_info.value.args[0] == "max_novelty must be within [0.0, 1.0], got -0.1."

    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.2,
            word_delta_ratio=0.1,
            novel_paragraphs=3,
            total_paragraphs=2,
        )
    assert exc_info.value.args[0] == "novel_paragraphs (3) cannot exceed total_paragraphs (2)."

    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.2,
            word_delta_ratio=0.1,
            novel_paragraphs=cast(int, True),
            total_paragraphs=2,
        )
    assert exc_info.value.args[0] == "novel_paragraphs must be a non-negative integer, got True."

    with pytest.raises(DomainValidationError) as exc_info:
        SaturationVerdict(
            is_saturated=False,
            reason=SaturationReason.NOVEL_CONTENT,
            lexical_jaccard=0.2,
            word_delta_ratio=0.1,
            novel_paragraphs=0,
            total_paragraphs=-1,
        )
    assert exc_info.value.args[0] == "total_paragraphs must be a non-negative integer, got -1."

    for bad_verdict_kwargs, expected_msg in (
        (
            {"is_saturated": "yes", "reason": SaturationReason.NOVEL_CONTENT},
            "is_saturated must be a bool, got 'yes'.",
        ),
        (
            {"is_saturated": False, "reason": SaturationReason.NOVEL_CONTENT, "preserve_baseline": 1},
            "preserve_baseline must be a bool, got 1.",
        ),
        (
            {"is_saturated": False, "reason": "novel_content"},
            "reason must be a SaturationReason, got 'novel_content'.",
        ),
        (
            {"is_saturated": False, "reason": SaturationReason.NOVEL_CONTENT, "provider": 123},
            "provider must be a str, got 123.",
        ),
    ):
        with pytest.raises(DomainValidationError) as exc_info:
            SaturationVerdict(
                lexical_jaccard=0.2,
                word_delta_ratio=0.1,
                **cast(dict[str, Any], bad_verdict_kwargs),
            )
        assert exc_info.value.args[0] == expected_msg

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

    # > 120 words concentrated in <= 3 long baroque sentences remains 1 intact unit (even with newlines)
    baroque_3 = "\n".join(_make_sentence(f"z{i}_", 41) for i in range(3))
    assert segment_semantic_units(baroque_3) == (baroque_3,)

    # 7 sentences (> 120 words) MUST advance across 3 overlapping windows [0..2], [2..4], [4..6]
    seven = [_make_sentence(f"w{i}_", 20) for i in range(7)]
    long_7 = " ".join(seven)
    assert segment_semantic_units(long_7) == (
        f"{seven[0]} {seven[1]} {seven[2]}",
        f"{seven[2]} {seven[3]} {seven[4]}",
        f"{seven[4]} {seven[5]} {seven[6]}",
    )

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
    with pytest.raises(DomainValidationError) as exc_info:
        SaturationThresholds(long_unit_word_cutoff=0)
    assert exc_info.value.args[0] == "long_unit_word_cutoff must be a positive integer, got 0."
    with pytest.raises(DomainValidationError) as exc_info:
        SaturationThresholds(sliding_window_sentences=0)
    assert exc_info.value.args[0] == "sliding_window_sentences must be a positive integer, got 0."
    with pytest.raises(DomainValidationError) as exc_info:
        SaturationThresholds(sliding_window_sentences=3, sliding_window_overlap=3)
    assert (
        exc_info.value.args[0]
        == "sliding_window_overlap (3) must be less than sliding_window_sentences (3)."
    )


def test_segment_semantic_units_crlf_cr_and_multiline_blocks() -> None:
    # Single CRLF inside a paragraph stays one unit; double CR splits blocks
    assert segment_semantic_units("Line one\r\nLine two") == ("Line one\nLine two",)
    assert segment_semantic_units("Para one\r\rPara two") == ("Para one", "Para two")

    # Multi-line prose before numbered item and multi-line numbered item preserve '\n' joins
    block = "First line\nSecond line\n1. Item line one\nItem line two"
    assert segment_semantic_units(block) == (
        "First line\nSecond line",
        "1. Item line one\nItem line two",
    )


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

    # 3 sentences + trailing '. (' must remain 1 unit (not 4 sentences)
    pad40 = " ".join(f"ctx{i}" for i in range(42))
    trailing_paren = f"Um {pad40}. Dois {pad40}. Tres {pad40}. ("
    assert len(segment_semantic_units(trailing_paren)) == 1

    # 3 sentences + trailing '. X' MUST split into 4 sentences -> 2 windows
    trailing_x = f"Um {pad40}. Dois {pad40}. Tres {pad40}. X"
    assert len(segment_semantic_units(trailing_x)) == 2

    # Wrapped lowercase continuation after period must NOT split
    wrapped_lower = f"Um {pad40}. *continuacao* {pad40}. Dois {pad40}. Tres {pad40}."
    assert len(segment_semantic_units(wrapped_lower)) == 1

    # Exclamation and question marks followed by lowercase MUST split
    bang_q_lower = f"Prof. Silva {pad40}! quem diria {pad40}? talvez {pad40}. Fim {pad40}."
    assert len(segment_semantic_units(bang_q_lower)) == 2

    # Single-letter 'X.' prefix MUST split (not treated as empty prefix)
    prefix_x = f"X. Um {pad40}. Dois {pad40}. Tres {pad40}."
    assert len(segment_semantic_units(prefix_x)) == 2

    # Leading abbreviation with no prior spaces and wrapped abbreviation must NOT split
    leading_abbr = f"Dr. Um {pad40}. Veja *Dr. Silva* {pad40}. Dois {pad40}."
    assert len(segment_semantic_units(leading_abbr)) == 1

    # Non-abbreviation 'Xst.' MUST split
    non_abbr_xst = f"Xst. Um {pad40}. Dois {pad40}. Tres {pad40}."
    assert len(segment_semantic_units(non_abbr_xst)) == 2


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
        with pytest.raises(DomainValidationError) as exc_info:
            is_explicit_stop_sentinel("<NO_NEW_GAPS/>", pass_index=bad_pass)
        assert exc_info.value.args[0] == f"pass_index must be an integer >= 1, got {bad_pass!r}."


def test_compute_ngram_jaccard_and_word_delta_ratio() -> None:
    # Empty boundaries
    assert compute_ngram_jaccard("", "") == 1.0
    assert compute_ngram_jaccard("   ", "") == 1.0
    assert compute_ngram_jaccard("", "non empty prose") == 0.0
    assert compute_ngram_jaccard("non empty prose", "") == 0.0

    # Identical and disjoint cases (including Unicode lowercase preservation: groß != gross)
    assert compute_ngram_jaccard("Alpha Beta Gamma Delta", "alpha beta, gamma delta.") == 1.0
    assert compute_ngram_jaccard("groß", "gross") == 0.0
    assert compute_ngram_jaccard("one two three four", "five six seven eight") == 0.0

    # Default n=3 partial 3-gram overlap
    assert compute_ngram_jaccard("one two three four", "one two three five") == pytest.approx(
        1.0 / 3.0
    )

    # Boundary n=1 unigrams
    assert compute_ngram_jaccard("alpha beta", "alpha gamma", n=1) == pytest.approx(1.0 / 3.0)

    # Short sequences (< n tokens) form single tuple shingle
    assert compute_ngram_jaccard("alpha beta", "alpha beta", n=3) == 1.0
    assert compute_ngram_jaccard("alpha beta", "alpha gamma", n=3) == 0.0

    for bad_n in (0, -2, True, False):
        with pytest.raises(DomainValidationError) as exc_info:
            compute_ngram_jaccard("a b c", "a b c", n=bad_n)
        assert exc_info.value.args[0] == f"n must be an integer >= 1, got {bad_n!r}."

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
    with pytest.raises(ValueError) as val_exc:
        cosine_similarity([1.0, 0.0], [1.0])
    assert val_exc.value.args[0] == "Vector length mismatch: 2 != 1"

    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [0.0, 0.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [2.0, 4.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)
    # Non-unit non-collinear vectors distinguish dot/(norm_a*norm_b) from dot*(norm_a*norm_b) and dot/(norm_a/norm_b)
    assert cosine_similarity([1.0, 1.0], [2.0, 0.0]) == pytest.approx(1.0 / math.sqrt(2.0))
    # IEEE 754 overshoot clamping at exact [-1.0, 1.0]
    assert cosine_similarity([3.0, 3.0], [3.0, 3.0]) == 1.0
    assert cosine_similarity([3.0, 3.0], [-3.0, -3.0]) == -1.0

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

    # Multiple novel vectors and opposite-vector novelty clamping to 1.0
    multi_novel_count, multi_max_nov = compute_maxsim_novelty(
        [[1.0, 0.0]],
        [[0.0, 1.0], [-1.0, 0.0]],
        similarity_threshold=1.0,
    )
    assert multi_novel_count == 2
    assert multi_max_nov == 1.0

    # Exact similarity_threshold boundary (max_sim == similarity_threshold is covered, not novel)
    exact_count, exact_max_nov = compute_maxsim_novelty(
        [[1.0, 0.0]],
        [[0.8, 0.6]],
        similarity_threshold=0.8,
    )
    assert exact_count == 0
    assert exact_max_nov == pytest.approx(0.2)

    # All current units covered above 0.88 threshold
    covered_count, covered_max_nov = compute_maxsim_novelty(
        [[1.0, 0.0], [0.0, 1.0]],
        [[1.0, 0.0], [0.99, 0.1]],
        similarity_threshold=0.88,
    )
    assert covered_count == 0
    assert 0.0 <= covered_max_nov < 0.02

    for bad_thresh in (0.0, -0.2, 1.05, math.nan, True, "0.8"):
        with pytest.raises(DomainValidationError) as exc_info:
            compute_maxsim_novelty(
                [[1.0, 0.0]],
                [[1.0, 0.0]],
                similarity_threshold=cast(float, bad_thresh),
            )
        assert (
            exc_info.value.args[0]
            == f"similarity_threshold must be a finite float in (0.0, 1.0], got {bad_thresh!r}."
        )


def test_evaluate_lexical_convergence_gates() -> None:
    baseline = "## Topic\n\nCentral banks regulate monetary aggregates across credit cycles."

    # Sentinel short-circuits on pass >= 2
    sentinel_verdict = evaluate_lexical_convergence(
        baseline,
        "  <NO_NEW_GAPS/>  ",
        pass_index=2,
        current_unit_count=3,
    )
    assert sentinel_verdict is not None
    assert sentinel_verdict.is_saturated is True
    assert sentinel_verdict.reason is SaturationReason.EXPLICIT_SENTINEL
    assert sentinel_verdict.max_novelty == 0.0
    assert sentinel_verdict.novel_paragraphs == 0
    assert sentinel_verdict.preserve_baseline is True
    assert sentinel_verdict.provider == "sentinel"
    assert sentinel_verdict.total_paragraphs == 3

    # Pass 1 ignores sentinel and returns None when lexically distinct from baseline
    assert evaluate_lexical_convergence(baseline, "<NO_NEW_GAPS/>", pass_index=1) is None

    # Identical text triggers LEXICAL_IDENTITY short-circuit
    lexical_verdict = evaluate_lexical_convergence(baseline, baseline, pass_index=2)
    assert lexical_verdict is not None
    assert lexical_verdict.is_saturated is True
    assert lexical_verdict.reason is SaturationReason.LEXICAL_IDENTITY
    assert lexical_verdict.lexical_jaccard == pytest.approx(1.0)
    assert lexical_verdict.word_delta_ratio == pytest.approx(0.0)
    assert lexical_verdict.max_novelty == 0.0
    assert lexical_verdict.novel_paragraphs == 0
    assert lexical_verdict.preserve_baseline is False
    assert lexical_verdict.provider == "lexical"
    assert lexical_verdict.total_paragraphs == 1

    # Exact inclusive threshold boundaries (>= lexical_identity_threshold and <= max_lexical_word_delta)
    boundary_verdict = evaluate_lexical_convergence(
        baseline,
        baseline,
        thresholds=SaturationThresholds(
            lexical_identity_threshold=0.95,
            max_lexical_word_delta=0.03,
        ),
        lexical_jaccard=0.95,
        word_delta_ratio=0.03,
    )
    assert boundary_verdict is not None
    assert boundary_verdict.reason is SaturationReason.LEXICAL_IDENTITY

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

    # Fractional max_novelty (< 1.0) and custom semantic_similarity_threshold forwarding
    strict_semantic = SaturationThresholds(
        semantic_similarity_threshold=0.95,
        max_novel_paragraphs_for_saturation=0,
    )
    novel_verdict = evaluate_semantic_convergence(
        [[1.0, 0.0]],
        [[1.0, 0.0], [0.8, 0.6]],
        thresholds=strict_semantic,
        lexical_jaccard=0.30,
        word_delta_ratio=0.25,
        provider="tfidf_fallback",
    )
    assert novel_verdict.is_saturated is False
    assert novel_verdict.reason is SaturationReason.NOVEL_CONTENT
    assert novel_verdict.preserve_baseline is False
    assert novel_verdict.novel_paragraphs == 1
    assert novel_verdict.total_paragraphs == 2
    assert novel_verdict.max_novelty == pytest.approx(0.2)
    assert novel_verdict.provider == "tfidf_fallback"

    # Verify default keyword arguments (lexical_jaccard=0.0, word_delta_ratio=0.0, provider='semantic')
    default_verdict = evaluate_semantic_convergence(
        [[1.0, 0.0]],
        [[0.9, math.sqrt(1.0 - 0.81)]],
        thresholds=strict_semantic,
    )
    assert default_verdict.is_saturated is False
    assert default_verdict.reason is SaturationReason.NOVEL_CONTENT
    assert default_verdict.lexical_jaccard == 0.0
    assert default_verdict.word_delta_ratio == 0.0
    assert default_verdict.provider == "semantic"

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
