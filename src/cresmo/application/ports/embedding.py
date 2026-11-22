"""Hexagonal Application Port for Text Vector Embeddings.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §3.1 (TextEmbeddingPort)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class TextEmbeddingPort(ABC):
    """Abstract port generating dense or sparse vector embeddings for text unit sequences."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Canonical identifier of the active embedding backend (e.g., 'gemini', 'ollama', 'tfidf')."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one embedding vector per input string preserving input order.

        Args:
            texts: Ordered sequence of text units to embed.

        Returns:
            list[list[float]]: One embedding vector per input string.
        """
        raise NotImplementedError
