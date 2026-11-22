"""Google Gemini Text Embedding Infrastructure Adapter.

Implements ``TextEmbeddingPort`` behind an Anti-Corruption Layer using Google GenAI
embeddings and ``GeminiCredentialPool`` quota rotation.

Conforms to:
    - ADR-041: Gemini Credential Pool and Quota Failover
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §4 (GeminiEmbeddingAdapter)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.domain.exceptions import EmbeddingInfrastructureError
from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

DEFAULT_GEMINI_EMBEDDING_MODEL: Final[str] = "gemini-embedding-001"
DEFAULT_GEMINI_EMBEDDING_DIMENSIONS: Final[int] = 768
GEMINI_EMBED_MAX_BATCH_SIZE: Final[int] = 100


class GeminiEmbeddingAdapter(TextEmbeddingPort):
    """Infrastructure adapter generating semantic text embeddings via Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_GEMINI_EMBEDDING_MODEL,
        dimensions: int = DEFAULT_GEMINI_EMBEDDING_DIMENSIONS,
        genai_client: Any | None = None,
        credential_pool: GeminiCredentialPool | None = None,
        api_keys: list[str] | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize the Gemini embedding adapter configuration.

        Args:
            api_key: Optional single Gemini API key.
            model_name: Gemini embedding model identifier.
            dimensions: Output embedding dimensionality.
            genai_client: Optional injected Google GenAI client for deterministic testing.
            credential_pool: Optional shared GeminiCredentialPool for quota rotation.
            api_keys: Optional list of API keys when constructing an internal pool.
            timeout_seconds: Request timeout in seconds.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.dimensions = dimensions
        self.genai_client = genai_client
        self.credential_pool = credential_pool
        self.api_keys = api_keys
        self.timeout_seconds = timeout_seconds
        self._pool: GeminiCredentialPool | None = credential_pool

    @property
    def provider_name(self) -> str:
        """Return canonical provider identifier ('gemini')."""
        return "gemini"

    def _resolve_pool(self) -> GeminiCredentialPool:
        """Resolve or lazily instantiate the credential pool from configured API keys."""
        if self._pool is not None:
            return self._pool

        raw_keys = self.api_keys if self.api_keys else ([self.api_key] if self.api_key else [])
        cleaned_keys = [key.strip() for key in raw_keys if key and key.strip()]
        if not cleaned_keys:
            raise EmbeddingInfrastructureError(
                "GeminiEmbeddingAdapter requires genai_client, credential_pool, api_keys, or api_key."
            )

        self._pool = GeminiCredentialPool(keys=cleaned_keys, timeout=self.timeout_seconds)
        return self._pool

    def _embed_chunk(self, client: Any, chunk: list[str], config: Any) -> list[list[float]]:
        """Invoke embed_content for a single chunk and validate returned vectors."""
        response = client.models.embed_content(
            model=self.model_name,
            contents=chunk,
            config=config,
        )
        embeddings = getattr(response, "embeddings", None)
        if embeddings is None or len(embeddings) != len(chunk):
            actual_count = 0 if embeddings is None else len(embeddings)
            raise EmbeddingInfrastructureError(
                f"Gemini returned {actual_count} embeddings for {len(chunk)} input texts."
            )

        vectors: list[list[float]] = []
        for idx, item in enumerate(embeddings):
            values = getattr(item, "values", None)
            if not values:
                raise EmbeddingInfrastructureError(
                    f"Gemini returned an empty embedding vector at batch index {idx}."
                )
            vectors.append([float(v) for v in values])
        return vectors

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embedding vectors for a sequence of text units via Google Gemini.

        Args:
            texts: Ordered sequence of text units to embed.

        Returns:
            list[list[float]]: Embedding vectors aligned to the input order.

        Raises:
            EmbeddingInfrastructureError: If credentials are missing or the Gemini API fails.
        """
        text_list = list(texts)
        if not text_list:
            return []

        from google.genai import types

        config = types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=self.dimensions,
        )

        results: list[list[float]] = []
        try:
            for start in range(0, len(text_list), GEMINI_EMBED_MAX_BATCH_SIZE):
                chunk = text_list[start : start + GEMINI_EMBED_MAX_BATCH_SIZE]
                if self.genai_client is not None:
                    results.extend(self._embed_chunk(self.genai_client, chunk, config))
                else:
                    pool = self._resolve_pool()

                    def _run_chunk(
                        client: Any,
                        batch: list[str] = chunk,
                    ) -> list[list[float]]:
                        return self._embed_chunk(client, batch, config)

                    results.extend(pool.execute_with_failover(_run_chunk))
        except EmbeddingInfrastructureError:
            raise
        except Exception as exc:
            raise EmbeddingInfrastructureError(
                f"Gemini embedding request failed for model '{self.model_name}': {exc}"
            ) from exc

        return results
