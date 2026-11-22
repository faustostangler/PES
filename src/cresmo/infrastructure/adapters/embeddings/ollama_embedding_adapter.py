"""Local Ollama Text Embedding Infrastructure Adapter.

Implements ``TextEmbeddingPort`` against the local Ollama ``/api/embed`` endpoint
for zero-egress semantic convergence evaluation.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §4 (OllamaEmbeddingAdapter)
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any, Final

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.domain.exceptions import EmbeddingInfrastructureError

DEFAULT_OLLAMA_EMBEDDING_MODEL: Final[str] = "nomic-embed-text"


class OllamaEmbeddingAdapter(TextEmbeddingPort):
    """Infrastructure adapter generating local text embeddings via Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = DEFAULT_OLLAMA_EMBEDDING_MODEL,
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize the local Ollama embedding adapter.

        Args:
            base_url: Root URL of the local Ollama daemon.
            model: Ollama embedding model identifier.
            timeout_seconds: HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        """Return canonical provider identifier ('ollama')."""
        return "ollama"

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embedding vectors for a sequence of text units via Ollama.

        Args:
            texts: Ordered sequence of text units to embed.

        Returns:
            list[list[float]]: Embedding vectors aligned to the input order.

        Raises:
            EmbeddingInfrastructureError: If Ollama is unreachable, returns an HTTP error,
                or returns malformed/mismatched embeddings.
        """
        text_list = list(texts)
        if not text_list:
            return []

        endpoint = f"{self.base_url}/api/embed"
        request_body = json.dumps({"model": self.model, "input": text_list}).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                payload: Any = json.loads(raw_body)
        except urllib.error.HTTPError as exc:
            raise EmbeddingInfrastructureError(
                f"Ollama HTTP {exc.code} during embedding request at {endpoint}: {exc.reason}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise EmbeddingInfrastructureError(
                f"Ollama embedding request failed at {endpoint}: {exc}"
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise EmbeddingInfrastructureError(
                f"Ollama returned invalid JSON from {endpoint}: {exc}"
            ) from exc
        except Exception as exc:
            raise EmbeddingInfrastructureError(
                f"Unexpected error calling Ollama embeddings at {endpoint}: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise EmbeddingInfrastructureError(
                f"Ollama embedding response at {endpoint} must be a JSON object."
            )

        raw_embeddings = payload.get("embeddings")
        if not isinstance(raw_embeddings, list) or len(raw_embeddings) != len(text_list):
            actual_count = len(raw_embeddings) if isinstance(raw_embeddings, list) else 0
            raise EmbeddingInfrastructureError(
                f"Ollama returned {actual_count} embeddings for {len(text_list)} input texts."
            )

        vectors: list[list[float]] = []
        for idx, vec in enumerate(raw_embeddings):
            if not isinstance(vec, Sequence) or isinstance(vec, (str, bytes)) or not vec:
                raise EmbeddingInfrastructureError(
                    f"Ollama returned invalid embedding vector at index {idx}."
                )
            try:
                vectors.append([float(v) for v in vec])
            except (TypeError, ValueError) as exc:
                raise EmbeddingInfrastructureError(
                    f"Ollama returned non-numeric embedding values at index {idx}: {exc}"
                ) from exc

        return vectors
