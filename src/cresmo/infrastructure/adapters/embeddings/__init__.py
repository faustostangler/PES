"""Hexagonal Text Embedding Infrastructure Adapters Package."""

from __future__ import annotations

from cresmo.infrastructure.adapters.embeddings.gemini_embedding_adapter import (
    DEFAULT_GEMINI_EMBEDDING_DIMENSIONS,
    DEFAULT_GEMINI_EMBEDDING_MODEL,
    GeminiEmbeddingAdapter,
)
from cresmo.infrastructure.adapters.embeddings.ollama_embedding_adapter import (
    DEFAULT_OLLAMA_EMBEDDING_MODEL,
    OllamaEmbeddingAdapter,
)
from cresmo.infrastructure.adapters.embeddings.resilient_embedding_adapter import (
    ResilientEmbeddingAdapter,
)
from cresmo.infrastructure.adapters.embeddings.tfidf_embedding_adapter import (
    TfidfEmbeddingAdapter,
)

__all__ = [
    "DEFAULT_GEMINI_EMBEDDING_DIMENSIONS",
    "DEFAULT_GEMINI_EMBEDDING_MODEL",
    "DEFAULT_OLLAMA_EMBEDDING_MODEL",
    "GeminiEmbeddingAdapter",
    "OllamaEmbeddingAdapter",
    "ResilientEmbeddingAdapter",
    "TfidfEmbeddingAdapter",
]
