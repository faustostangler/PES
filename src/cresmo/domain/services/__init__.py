"""Domain services package for Cresmo knowledge synthesis pipelines."""

from __future__ import annotations

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
from cresmo.domain.services.prose_syntax_guard import (
    extract_extra_info_section,
    validate_expanded_prose_syntax,
    validate_fluid_prose_syntax,
)
from cresmo.domain.services.stage_post_processor import post_process_expanded_transcript

__all__ = [
    "NO_NEW_GAPS_SENTINEL",
    "compute_maxsim_novelty",
    "compute_ngram_jaccard",
    "compute_word_delta_ratio",
    "cosine_similarity",
    "evaluate_lexical_convergence",
    "evaluate_semantic_convergence",
    "extract_extra_info_section",
    "is_explicit_stop_sentinel",
    "post_process_expanded_transcript",
    "segment_semantic_units",
    "validate_expanded_prose_syntax",
    "validate_fluid_prose_syntax",
]
