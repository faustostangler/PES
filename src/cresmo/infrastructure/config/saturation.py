"""Semantic saturation and embedding threshold settings for Cresmo.

Conforms to:
    - ADR-066: Hybrid Semantic Pass Saturation & Sliding Window Sub-Chunking
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cresmo.infrastructure.config.catalog import _normalize_str_choice


class SaturationSettings(BaseSettings):
    """Embedding provider and hybrid lexical/semantic saturation settings."""

    model_config = SettingsConfigDict(extra="ignore")

    embedding_provider: Literal["gemini", "ollama", "tfidf"] = Field(
        default="gemini",
        validation_alias=AliasChoices("embedding_provider", "CRESMO_EMBEDDING_PROVIDER"),
        description="Text embedding provider for hybrid semantic pass saturation ('gemini', 'ollama', or 'tfidf').",
    )
    gemini_embedding_model: str = Field(
        default="gemini-embedding-001",
        validation_alias=AliasChoices("gemini_embedding_model", "CRESMO_GEMINI_EMBEDDING_MODEL"),
        description="Google Gemini model identifier used for text embeddings.",
    )
    gemini_embedding_dimensions: int = Field(
        default=768,
        ge=1,
        validation_alias=AliasChoices(
            "gemini_embedding_dimensions", "CRESMO_GEMINI_EMBEDDING_DIMENSIONS"
        ),
        description="Output vector dimensionality requested from Gemini embeddings.",
    )
    ollama_embedding_model: str = Field(
        default="nomic-embed-text",
        validation_alias=AliasChoices("ollama_embedding_model", "CRESMO_OLLAMA_EMBEDDING_MODEL"),
        description="Local Ollama model identifier used for text embeddings.",
    )
    saturation_lexical_threshold: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "saturation_lexical_threshold", "CRESMO_SATURATION_LEXICAL_THRESHOLD"
        ),
        description="Minimum n-gram Jaccard similarity required for Tier 1 lexical saturation.",
    )
    saturation_max_word_delta: float = Field(
        default=0.03,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "saturation_max_word_delta", "CRESMO_SATURATION_MAX_WORD_DELTA"
        ),
        description="Maximum relative word-count delta allowed for Tier 1 lexical saturation.",
    )
    saturation_semantic_threshold: float = Field(
        default=0.88,
        gt=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "saturation_semantic_threshold", "CRESMO_SATURATION_SEMANTIC_THRESHOLD"
        ),
        description="Minimum cosine similarity threshold to consider a unit semantically covered.",
    )
    saturation_max_novel_paragraphs: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices(
            "saturation_max_novel_paragraphs", "CRESMO_SATURATION_MAX_NOVEL_PARAGRAPHS"
        ),
        description="Maximum novel semantic units tolerated while classifying a pass as saturated.",
    )
    saturation_long_unit_word_cutoff: int = Field(
        default=120,
        ge=1,
        validation_alias=AliasChoices(
            "saturation_long_unit_word_cutoff", "CRESMO_SATURATION_LONG_UNIT_WORD_CUTOFF"
        ),
        description="Word-count cutoff above which long units are sub-chunked via sliding window.",
    )
    saturation_sliding_window_sentences: int = Field(
        default=3,
        ge=1,
        validation_alias=AliasChoices(
            "saturation_sliding_window_sentences", "CRESMO_SATURATION_SLIDING_WINDOW_SENTENCES"
        ),
        description="Sentence count per overlapping sliding window for long semantic units.",
    )
    saturation_sliding_window_overlap: int = Field(
        default=1,
        ge=0,
        validation_alias=AliasChoices(
            "saturation_sliding_window_overlap", "CRESMO_SATURATION_SLIDING_WINDOW_OVERLAP"
        ),
        description="Overlapping sentence count between consecutive sliding windows (must be < window size).",
    )

    @model_validator(mode="after")
    def _validate_saturation_sliding_window(self) -> Self:
        """Ensure sliding window overlap is strictly less than window sentence size."""
        if self.saturation_sliding_window_overlap >= self.saturation_sliding_window_sentences:
            raise ValueError(
                "saturation_sliding_window_overlap must be less than "
                "saturation_sliding_window_sentences."
            )
        return self

    @field_validator("embedding_provider", mode="before")
    @classmethod
    def _normalize_embedding_provider(cls, value: Any) -> Any:
        """Normalize embedding provider string by stripping whitespace and lowercasing."""
        return _normalize_str_choice(value)


__all__ = ["SaturationSettings"]
