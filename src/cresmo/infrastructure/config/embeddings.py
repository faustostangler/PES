"""Vector embedding provider configuration for Cresmo.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation & Text Embedding Adapters
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cresmo.infrastructure.config.catalog import normalize_str_choice

DEFAULT_GEMINI_EMBEDDING_MODEL: Final[str] = "gemini-embedding-001"
DEFAULT_GEMINI_EMBEDDING_DIMENSIONS: Final[int] = 768
DEFAULT_OLLAMA_EMBEDDING_MODEL: Final[str] = "nomic-embed-text"


class EmbeddingSettings(BaseModel):
    """Immutable text embedding provider and model configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: Literal["gemini", "ollama", "tfidf"] = Field(
        default="gemini",
        description="Text embedding provider for hybrid semantic pass saturation ('gemini', 'ollama', 'tfidf').",
    )
    gemini_model: str = Field(
        default=DEFAULT_GEMINI_EMBEDDING_MODEL,
        description="Google Gemini model identifier used for text embeddings.",
    )
    gemini_dimensions: int = Field(
        default=DEFAULT_GEMINI_EMBEDDING_DIMENSIONS,
        ge=1,
        description="Output vector dimensionality requested from Gemini embeddings.",
    )
    ollama_model: str = Field(
        default=DEFAULT_OLLAMA_EMBEDDING_MODEL,
        description="Local Ollama model identifier used for text embeddings.",
    )

    @field_validator("provider", mode="before")
    @classmethod
    def _normalize_provider(cls, value: Any) -> Any:
        return normalize_str_choice(value)


__all__ = ["EmbeddingSettings"]
