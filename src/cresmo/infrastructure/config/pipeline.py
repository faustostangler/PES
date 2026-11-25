"""Pipeline orchestration, stage budgets, and saturation convergence settings.

Conforms to:
    - ADR-066: Hybrid Semantic Pass Saturation & Sliding Window Sub-Chunking
    - ADR-073: Sequential Conveyor Integration of Long and Wide Expander Stages
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cresmo.domain.value_objects import DEFAULT_LANGUAGE, SaturationThresholds


class StageBudgetsSettings(BaseModel):
    """Immutable per-stage pass and rewrite budget configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    expansion_max_passes: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Default multi-pass expansion budget before mechanical saturation.",
    )
    long_expander_max_passes: int = Field(
        default=7,
        ge=1,
        le=10,
        description="Multi-pass longitudinal expansion budget before mechanical saturation.",
    )
    raw_index_max_attempts: int = Field(
        default=2,
        ge=0,
        description="Maximum LLM judge rewrite attempts for raw indexing (0 means unconstrained).",
    )


class SaturationSettings(BaseModel):
    """Immutable hybrid lexical/semantic saturation threshold settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lexical_threshold: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
        description="Minimum n-gram Jaccard similarity required for Tier 1 lexical saturation.",
    )
    max_word_delta: float = Field(
        default=0.03,
        ge=0.0,
        le=1.0,
        description="Maximum relative word-count delta allowed for Tier 1 lexical saturation.",
    )
    semantic_threshold: float = Field(
        default=0.88,
        gt=0.0,
        le=1.0,
        description="Minimum cosine similarity threshold to consider a unit semantically covered.",
    )
    max_novel_paragraphs: int = Field(
        default=0,
        ge=0,
        description="Maximum novel semantic units tolerated while classifying a pass as saturated.",
    )
    long_unit_word_cutoff: int = Field(
        default=120,
        ge=1,
        description="Word-count cutoff above which long units are sub-chunked via sliding window.",
    )
    sliding_window_sentences: int = Field(
        default=3,
        ge=1,
        description="Sentence count per overlapping sliding window for long semantic units.",
    )
    sliding_window_overlap: int = Field(
        default=1,
        ge=0,
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
        default=5,
        ge=1,
        description="Batch size for Atomic Note synthesis.",
    )
    concat_max_words: int = Field(
        default=500_000,
        ge=1,
        description="Maximum word limit per aggregated master document before sequential rollover.",
    )
    raw_index_max_chars: int = Field(
        default=0,
        ge=0,
        description="Maximum characters of transcript body passed to LLM for conceptual synthesis (0 = full text).",
    )
    stages: StageBudgetsSettings = Field(default_factory=StageBudgetsSettings)
    saturation: SaturationSettings = Field(default_factory=SaturationSettings)


__all__ = [
    "PipelineSettings",
    "SaturationSettings",
    "StageBudgetsSettings",
]
