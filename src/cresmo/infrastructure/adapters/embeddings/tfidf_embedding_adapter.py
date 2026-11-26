"""Offline TF-IDF Text Embedding Infrastructure Adapter.

Provides zero-network deterministic sparse vector embeddings using lazy scikit-learn imports
to preserve fast CLI startup times (ADR-053 / ADR-055).

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §4 (TfidfEmbeddingAdapter)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final

from cresmo.application.ports.embedding import TextEmbeddingPort

DEFAULT_TFIDF_NGRAM_RANGE: Final[tuple[int, int]] = (1, 2)
TFIDF_PROVIDER_NAME: Final[str] = "tfidf"
_TFIDF_NORM_L2: Final[str] = "l2"
_TFIDF_EMPTY_FALLBACK_VALUE: Final[float] = 0.0


class TfidfEmbeddingAdapter(TextEmbeddingPort):
    """Offline deterministic embedding adapter backed by TF-IDF vectorization."""

    def __init__(self, ngram_range: tuple[int, int] = DEFAULT_TFIDF_NGRAM_RANGE) -> None:
        """Initialize the TF-IDF embedding adapter.

        Args:
            ngram_range: Lower and upper boundary of n-gram extraction range.
        """
        self.ngram_range = ngram_range

    @property
    def provider_name(self) -> str:
        """Return canonical provider identifier ('tfidf')."""
        return TFIDF_PROVIDER_NAME

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Vectorize a sequence of text units locally using TF-IDF.

        Args:
            texts: Ordered sequence of text units to embed.

        Returns:
            list[list[float]]: Dense float vectors aligned to the input order.
        """
        text_list = list(texts)
        if not text_list:
            return []

        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]

        vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            sublinear_tf=True,
            norm=_TFIDF_NORM_L2,
        )
        try:
            matrix = vectorizer.fit_transform(text_list)
        except ValueError:
            # Empty vocabulary (e.g., punctuation-only or stopword-only units) degrades safely.
            return [[_TFIDF_EMPTY_FALLBACK_VALUE] for _ in text_list]

        raw_rows: list[list[Any]] = matrix.toarray().tolist()
        return [[float(x) for x in row] for row in raw_rows]
