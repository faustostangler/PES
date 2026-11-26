"""Pipeline orchestration, stage budgets, and saturation convergence settings.

Conforms to:
    - ADR-066: Hybrid Semantic Pass Saturation & Sliding Window Sub-Chunking
    - ADR-073: Sequential Conveyor Integration of Long and Wide Expander Stages
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cresmo.domain.value_objects import DEFAULT_LANGUAGE, SaturationThresholds
from cresmo.domain.value_objects.convergence import (
    DEFAULT_LEXICAL_IDENTITY_THRESHOLD,
    DEFAULT_LONG_UNIT_WORD_CUTOFF,
    DEFAULT_MAX_LEXICAL_WORD_DELTA,
    DEFAULT_MAX_NOVEL_PARAGRAPHS,
    DEFAULT_SEMANTIC_SIMILARITY_THRESHOLD,
    DEFAULT_SLIDING_WINDOW_OVERLAP,
    DEFAULT_SLIDING_WINDOW_SENTENCES,
)
from cresmo.domain.value_objects.policies import (
    DEFAULT_COMPENDIUM_MAX_WORDS,
    DEFAULT_EXPANSION_MAX_PASSES,
    DEFAULT_LONG_EXPANDER_MAX_PASSES,
    MAX_STAGE_PASSES,
    MIN_COMPENDIUM_MAX_WORDS,
    MIN_STAGE_PASSES,
)

DEFAULT_RAW_INDEX_MAX_ATTEMPTS: Final[int] = 2
DEFAULT_ATOMIC_BATCH_SIZE: Final[int] = 5
DEFAULT_RAW_INDEX_MAX_CHARS: Final[int] = 0
_MIN_ATOMIC_BATCH_SIZE: Final[int] = 1
_MIN_UNIT_THRESHOLD_POSITIVE: Final[float] = 0.0
_MIN_UNIT_THRESHOLD_INCLUSIVE: Final[float] = 0.0
_MAX_UNIT_THRESHOLD: Final[float] = 1.0
_MIN_SLIDING_WINDOW_SENTENCES: Final[int] = 1
_MIN_LONG_UNIT_WORD_CUTOFF: Final[int] = 1
_MIN_ZERO_COUNT: Final[int] = 0


class StageBudgetsSettings(BaseModel):
    """Immutable per-stage pass and rewrite budget configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    expansion_max_passes: int = Field(
        default=DEFAULT_EXPANSION_MAX_PASSES,
        ge=MIN_STAGE_PASSES,
        le=MAX_STAGE_PASSES,
        description="Default multi-pass expansion budget before mechanical saturation.",
    )
    long_expander_max_passes: int = Field(
        default=DEFAULT_LONG_EXPANDER_MAX_PASSES,
        ge=MIN_STAGE_PASSES,
        le=MAX_STAGE_PASSES,
        description="Multi-pass longitudinal expansion budget before mechanical saturation.",
    )
    raw_index_max_attempts: int = Field(
        default=DEFAULT_RAW_INDEX_MAX_ATTEMPTS,
        ge=_MIN_ZERO_COUNT,
        description="Maximum LLM judge rewrite attempts for raw indexing (0 means unconstrained).",
    )


class SaturationSettings(BaseModel):
    """Immutable hybrid lexical/semantic saturation threshold settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lexical_threshold: float = Field(
        default=DEFAULT_LEXICAL_IDENTITY_THRESHOLD,
        gt=_MIN_UNIT_THRESHOLD_POSITIVE,
        le=_MAX_UNIT_THRESHOLD,
        description="Minimum n-gram Jaccard similarity required for Tier 1 lexical saturation.",
    )
    max_word_delta: float = Field(
        default=DEFAULT_MAX_LEXICAL_WORD_DELTA,
        ge=_MIN_UNIT_THRESHOLD_INCLUSIVE,
        le=_MAX_UNIT_THRESHOLD,
        description="Maximum relative word-count delta allowed for Tier 1 lexical saturation.",
    )
    semantic_threshold: float = Field(
        default=DEFAULT_SEMANTIC_SIMILARITY_THRESHOLD,
        gt=_MIN_UNIT_THRESHOLD_POSITIVE,
        le=_MAX_UNIT_THRESHOLD,
        description="Minimum cosine similarity threshold to consider a unit semantically covered.",
    )
    max_novel_paragraphs: int = Field(
        default=DEFAULT_MAX_NOVEL_PARAGRAPHS,
        ge=_MIN_ZERO_COUNT,
        description="Maximum novel semantic units tolerated while classifying a pass as saturated.",
    )
    long_unit_word_cutoff: int = Field(
        default=DEFAULT_LONG_UNIT_WORD_CUTOFF,
        ge=_MIN_LONG_UNIT_WORD_CUTOFF,
        description="Word-count cutoff above which long units are sub-chunked via sliding window.",
    )
    sliding_window_sentences: int = Field(
        default=DEFAULT_SLIDING_WINDOW_SENTENCES,
        ge=_MIN_SLIDING_WINDOW_SENTENCES,
        description="Sentence count per overlapping sliding window for long semantic units.",
    )
    sliding_window_overlap: int = Field(
        default=DEFAULT_SLIDING_WINDOW_OVERLAP,
        ge=_MIN_ZERO_COUNT,
        description="Overlapping sentence count between consecutive sliding windows (< window size).",
    )

    @model_validator(mode="after")
    def _validate_sliding_window(self) -> Self:
        """Ensure sliding window overlap is strictly less than window sentence size."""
        if self.sliding_window_overlap >= self.sliding_window_sentences:
            raise ValueError("sliding_window_overlap must be less than sliding_window_sentences.")
        return self

    def to_domain_thresholds(self) -> SaturationThresholds:
        """Translate infrastructure settings into pure domain SaturationThresholds."""
        return SaturationThresholds(
            lexical_identity_threshold=self.lexical_threshold,
            max_lexical_word_delta=self.max_word_delta,
            semantic_similarity_threshold=self.semantic_threshold,
            max_novel_paragraphs_for_saturation=self.max_novel_paragraphs,
            long_unit_word_cutoff=self.long_unit_word_cutoff,
            sliding_window_sentences=self.sliding_window_sentences,
            sliding_window_overlap=self.sliding_window_overlap,
        )


class PipelineSettings(BaseModel):
    """Composed pipeline execution, stage budgets, and saturation configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    language: str = Field(
        default=DEFAULT_LANGUAGE,
        description="Target generation language for synthesis, compendiums, and conceptual indexing.",
    )
    batch_size: int = Field(  # Consumed by SynthesizeAtomicBatchUseCase (re-wired post-refactor)
        default=DEFAULT_ATOMIC_BATCH_SIZE,
        ge=_MIN_ATOMIC_BATCH_SIZE,
        description="Batch size for Atomic Note synthesis.",
    )
    concat_max_words: int = Field(
        default=DEFAULT_COMPENDIUM_MAX_WORDS,
        ge=MIN_COMPENDIUM_MAX_WORDS,
        description="Maximum word limit per aggregated master document before sequential rollover.",
    )
    raw_index_max_chars: int = Field(
        default=DEFAULT_RAW_INDEX_MAX_CHARS,
        ge=_MIN_ZERO_COUNT,
        description="Maximum characters of transcript body passed to LLM for conceptual synthesis (0 = full text).",
    )
    stages: StageBudgetsSettings = Field(default_factory=StageBudgetsSettings)
    saturation: SaturationSettings = Field(default_factory=SaturationSettings)


__all__ = [
    "PipelineSettings",
    "SaturationSettings",
    "StageBudgetsSettings",
]
