"""Resilient Text Embedding Decorator with Automatic Offline Fallback.

Wraps a primary ``TextEmbeddingPort`` and falls back to a secondary port (typically
``TfidfEmbeddingAdapter``) upon ``EmbeddingInfrastructureError``.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §4 (ResilientEmbeddingAdapter)
"""

from __future__ import annotations

from collections.abc import Sequence

import structlog

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.infrastructure.adapters.embeddings.tfidf_embedding_adapter import (
    TfidfEmbeddingAdapter,
)

logger = structlog.get_logger(__name__)


class ResilientEmbeddingAdapter(TextEmbeddingPort):
    """Decorator wrapping a primary embedding port with automatic fallback handling."""

    def __init__(
        self,
        primary: TextEmbeddingPort,
        fallback: TextEmbeddingPort | None = None,
    ) -> None:
        """Initialize the resilient embedding wrapper.

        Args:
            primary: Primary embedding port attempted first for each batch.
            fallback: Optional fallback embedding port used when primary raises infrastructure errors.
        """
        self.primary = primary
        self.fallback: TextEmbeddingPort = (
            fallback if fallback is not None else TfidfEmbeddingAdapter()
        )
        self._last_provider_name: str = primary.provider_name

    @property
    def last_provider_name(self) -> str:
        """Return the provider identifier used by the most recent embedding batch call."""
        return self._last_provider_name

    @property
    def provider_name(self) -> str:
        """Return canonical provider identifier of the wrapped primary embedding adapter."""
        return self.primary.provider_name

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a sequence of texts using primary port with automatic fallback on failure.

        Args:
            texts: Ordered sequence of text units to embed.

        Returns:
            list[list[float]]: Embedding vectors aligned to the input order.
        """
        if not texts:
            return []

        try:
            vectors = self.primary.embed_batch(texts)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Primary embedding adapter failed; falling back to secondary provider.",
                primary_provider=self.primary.provider_name,
                fallback_provider=self.fallback.provider_name,
                error=str(exc),
            )
            self._last_provider_name = f"{self.fallback.provider_name}_fallback"
            return self.fallback.embed_batch(texts)

        self._last_provider_name = self.primary.provider_name
        return vectors
