"""Hermetic unit tests for Hexagonal Text Embedding Infrastructure Adapters.

Conforms to:
    - ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §4 (Infrastructure Embedding Adapters)
"""

from __future__ import annotations

import json
import logging
import math
import urllib.error
import urllib.request
from collections.abc import Sequence
from email.message import Message
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
import structlog.testing
from google.genai import errors

from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.domain.exceptions import EmbeddingInfrastructureError
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
from cresmo.infrastructure.adapters.embeddings.tfidf_embedding_adapter import TfidfEmbeddingAdapter
from cresmo.infrastructure.adapters.llm.gemini_pool import (
    CredentialPoolExhaustedError,
    GeminiCredentialPool,
)


def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Compute local cosine similarity without relying on unimplemented domain stubs."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(vec_a, vec_b, strict=True)) / (norm_a * norm_b)


class _FakeEmbeddingPort(TextEmbeddingPort):
    """Deterministic in-memory TextEmbeddingPort double for resilient fallback tests."""

    def __init__(
        self,
        name: str,
        *,
        vectors: list[list[float]] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._name = name
        self._vectors = vectors
        self._error = error
        self.calls: list[list[str]] = []

    @property
    def provider_name(self) -> str:
        return self._name

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        if self._error is not None:
            raise self._error
        if self._vectors is not None:
            return [list(v) for v in self._vectors]
        return [[float(idx + 1), 0.0] for idx in range(len(texts))]


class TestGeminiEmbeddingAdapter:
    """Hermetic unit tests for GeminiEmbeddingAdapter."""

    def test_provider_name_is_gemini(self) -> None:
        adapter = GeminiEmbeddingAdapter(api_key="test-key")
        assert adapter.provider_name == "gemini"

    def test_embed_batch_empty_input_returns_empty_without_calling_client_or_pool(self) -> None:
        mock_client = MagicMock()
        mock_pool = MagicMock(spec=GeminiCredentialPool)

        client_adapter = GeminiEmbeddingAdapter(genai_client=mock_client)
        pool_adapter = GeminiEmbeddingAdapter(credential_pool=mock_pool)

        assert client_adapter.embed_batch([]) == []
        assert pool_adapter.embed_batch([]) == []
        mock_client.models.embed_content.assert_not_called()
        mock_pool.execute_with_failover.assert_not_called()

    def test_embed_batch_calls_genai_client_with_semantic_similarity_config(self) -> None:
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = SimpleNamespace(
            embeddings=[
                SimpleNamespace(values=[0.1, 0.2, 0.3]),
                SimpleNamespace(values=[0.4, 0.5, 0.6]),
            ]
        )

        adapter = GeminiEmbeddingAdapter(genai_client=mock_client)
        result = adapter.embed_batch(["alpha", "beta"])

        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_client.models.embed_content.assert_called_once()
        kwargs = mock_client.models.embed_content.call_args.kwargs
        assert kwargs["model"] == DEFAULT_GEMINI_EMBEDDING_MODEL == "gemini-embedding-001"
        assert kwargs["contents"] == ["alpha", "beta"]
        config = kwargs["config"]
        assert config.task_type == "SEMANTIC_SIMILARITY"
        assert config.output_dimensionality == DEFAULT_GEMINI_EMBEDDING_DIMENSIONS == 768

    def test_embed_batch_uses_credential_pool_execute_with_failover(self) -> None:
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = SimpleNamespace(
            embeddings=[SimpleNamespace(values=[0.25, 0.75])]
        )
        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda _key: mock_client,
        )

        adapter = GeminiEmbeddingAdapter(credential_pool=pool)
        result = adapter.embed_batch(["unit one"])

        assert result == [[0.25, 0.75]]
        mock_client.models.embed_content.assert_called_once()

    def test_embed_batch_chunks_105_texts_into_100_and_5_preserving_order(self) -> None:
        texts = [f"semantic paragraph {idx}" for idx in range(105)]
        observed_chunks: list[list[str]] = []

        def _fake_embed_content(
            *,
            model: str,
            contents: list[str],
            config: Any,
        ) -> SimpleNamespace:
            assert model == "gemini-embedding-001"
            assert config.task_type == "SEMANTIC_SIMILARITY"
            assert config.output_dimensionality == 768
            observed_chunks.append(list(contents))
            embeddings = []
            for item in contents:
                item_idx = int(item.rsplit(" ", maxsplit=1)[1])
                embeddings.append(SimpleNamespace(values=[float(item_idx), float(item_idx) + 0.5]))
            return SimpleNamespace(embeddings=embeddings)

        mock_client = MagicMock()
        mock_client.models.embed_content.side_effect = _fake_embed_content

        adapter = GeminiEmbeddingAdapter(genai_client=mock_client)
        result = adapter.embed_batch(texts)

        assert mock_client.models.embed_content.call_count == 2
        assert [len(chunk) for chunk in observed_chunks] == [100, 5]
        assert observed_chunks[0] == texts[:100]
        assert observed_chunks[1] == texts[100:]
        assert result == [[float(i), float(i) + 0.5] for i in range(105)]

    def test_embed_batch_missing_credentials_raises_embedding_infrastructure_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        with pytest.raises(EmbeddingInfrastructureError):
            adapter = GeminiEmbeddingAdapter()
            adapter.embed_batch(["missing credentials unit"])

    @pytest.mark.parametrize(
        "fake_embeddings",
        [
            [],
            None,
            [SimpleNamespace(values=[0.1, 0.2])],
            [SimpleNamespace(values=[]), SimpleNamespace(values=[0.3, 0.4])],
        ],
    )
    def test_embed_batch_empty_or_mismatched_embeddings_raises_embedding_infrastructure_error(
        self,
        fake_embeddings: list[SimpleNamespace] | None,
    ) -> None:
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = SimpleNamespace(embeddings=fake_embeddings)

        adapter = GeminiEmbeddingAdapter(genai_client=mock_client)
        with pytest.raises(EmbeddingInfrastructureError):
            adapter.embed_batch(["first unit", "second unit"])

    def test_embed_batch_api_error_raises_embedding_infrastructure_error(self) -> None:
        mock_client = MagicMock()
        mock_client.models.embed_content.side_effect = errors.APIError(
            code=500,
            response_json={"error": {"message": "internal server error"}},
        )

        adapter = GeminiEmbeddingAdapter(genai_client=mock_client)
        with pytest.raises(EmbeddingInfrastructureError):
            adapter.embed_batch(["failing unit"])

    def test_embed_batch_pool_exhausted_raises_embedding_infrastructure_error(self) -> None:
        mock_pool = MagicMock(spec=GeminiCredentialPool)
        mock_pool.execute_with_failover.side_effect = CredentialPoolExhaustedError(
            retry_after_seconds=12.0
        )

        adapter = GeminiEmbeddingAdapter(credential_pool=mock_pool)
        with pytest.raises(EmbeddingInfrastructureError):
            adapter.embed_batch(["rate limited unit"])


class TestOllamaEmbeddingAdapter:
    """Hermetic unit tests for OllamaEmbeddingAdapter."""

    def test_provider_name_is_ollama(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        assert adapter.provider_name == "ollama"

    def test_embed_batch_empty_input_returns_empty_without_http_calls(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        with (
            patch("urllib.request.urlopen") as mock_urlopen,
            patch.object(httpx.Client, "post") as mock_httpx_client_post,
            patch("httpx.post") as mock_httpx_post,
        ):
            assert adapter.embed_batch([]) == []
            mock_urlopen.assert_not_called()
            mock_httpx_client_post.assert_not_called()
            mock_httpx_post.assert_not_called()

    def test_embed_batch_posts_expected_payload_and_extracts_embeddings(self) -> None:
        expected_vectors = [[0.11, 0.22], [0.33, 0.44]]
        response_payload = {"embeddings": expected_vectors}
        adapter = OllamaEmbeddingAdapter(
            base_url="http://localhost:11434/",
            model=DEFAULT_OLLAMA_EMBEDDING_MODEL,
            timeout_seconds=15.0,
        )

        mock_urllib_resp = MagicMock()
        mock_urllib_resp.status = 200
        mock_urllib_resp.read.return_value = json.dumps(response_payload).encode("utf-8")
        mock_urllib_resp.__enter__.return_value = mock_urllib_resp

        mock_httpx_resp = MagicMock()
        mock_httpx_resp.status_code = 200
        mock_httpx_resp.raise_for_status.return_value = None
        mock_httpx_resp.json.return_value = response_payload

        with (
            patch("urllib.request.urlopen", return_value=mock_urllib_resp) as mock_urlopen,
            patch.object(
                httpx.Client, "post", return_value=mock_httpx_resp
            ) as mock_httpx_client_post,
            patch("httpx.post", return_value=mock_httpx_resp) as mock_httpx_post,
        ):
            result = adapter.embed_batch(["first unit", "second unit"])

        assert result == expected_vectors
        transport_calls = (
            int(mock_urlopen.called)
            + int(mock_httpx_client_post.called)
            + int(mock_httpx_post.called)
        )
        assert transport_calls == 1

        if mock_urlopen.called:
            req = mock_urlopen.call_args.args[0]
            assert isinstance(req, urllib.request.Request)
            assert req.full_url == "http://localhost:11434/api/embed"
            assert req.get_method() == "POST"
            assert isinstance(req.data, bytes)
            body = json.loads(req.data.decode("utf-8"))
        else:
            active_mock = (
                mock_httpx_client_post if mock_httpx_client_post.called else mock_httpx_post
            )
            call = active_mock.call_args
            url = call.kwargs.get("url") or call.args[0]
            assert url == "http://localhost:11434/api/embed"
            body = call.kwargs["json"]

        assert body == {
            "model": "nomic-embed-text",
            "input": ["first unit", "second unit"],
        }

    def test_embed_batch_connection_error_raises_embedding_infrastructure_error(self) -> None:
        adapter = OllamaEmbeddingAdapter(base_url="http://localhost:11434")

        with (
            patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError("Connection refused"),
            ),
            patch.object(
                httpx.Client,
                "post",
                side_effect=httpx.ConnectError("Connection refused"),
            ),
            patch(
                "httpx.post",
                side_effect=httpx.ConnectError("Connection refused"),
            ),
            pytest.raises(EmbeddingInfrastructureError),
        ):
            adapter.embed_batch(["some unit"])

    def test_embed_batch_http_status_error_raises_embedding_infrastructure_error(self) -> None:
        adapter = OllamaEmbeddingAdapter(base_url="http://localhost:11434")
        httpx_error = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=httpx.Request("POST", "http://localhost:11434/api/embed"),
            response=httpx.Response(500),
        )
        mock_httpx_resp = MagicMock()
        mock_httpx_resp.status_code = 500
        mock_httpx_resp.raise_for_status.side_effect = httpx_error

        with (
            patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.HTTPError(
                    url="http://localhost:11434/api/embed",
                    code=500,
                    msg="Internal Server Error",
                    hdrs=Message(),
                    fp=None,
                ),
            ),
            patch.object(httpx.Client, "post", return_value=mock_httpx_resp),
            patch("httpx.post", return_value=mock_httpx_resp),
            pytest.raises(EmbeddingInfrastructureError),
        ):
            adapter.embed_batch(["some unit"])

    def test_embed_batch_mismatched_embedding_count_raises_embedding_infrastructure_error(
        self,
    ) -> None:
        adapter = OllamaEmbeddingAdapter(base_url="http://localhost:11434")
        bad_payload = {"embeddings": [[0.1, 0.2]]}

        mock_urllib_resp = MagicMock()
        mock_urllib_resp.status = 200
        mock_urllib_resp.read.return_value = json.dumps(bad_payload).encode("utf-8")
        mock_urllib_resp.__enter__.return_value = mock_urllib_resp

        mock_httpx_resp = MagicMock()
        mock_httpx_resp.status_code = 200
        mock_httpx_resp.raise_for_status.return_value = None
        mock_httpx_resp.json.return_value = bad_payload

        with (
            patch("urllib.request.urlopen", return_value=mock_urllib_resp),
            patch.object(httpx.Client, "post", return_value=mock_httpx_resp),
            patch("httpx.post", return_value=mock_httpx_resp),
            pytest.raises(EmbeddingInfrastructureError),
        ):
            adapter.embed_batch(["first unit", "second unit"])


class TestTfidfEmbeddingAdapter:
    """Hermetic unit tests for local TfidfEmbeddingAdapter."""

    def test_provider_name_is_tfidf(self) -> None:
        adapter = TfidfEmbeddingAdapter()
        assert adapter.provider_name == "tfidf"

    def test_embed_batch_empty_input_returns_empty(self) -> None:
        adapter = TfidfEmbeddingAdapter()
        assert adapter.embed_batch([]) == []

    @pytest.mark.parametrize(
        ("base", "paraphrase", "unrelated"),
        [
            (
                "A circulacao das elites descreve como minorias governantes sao substituidas por novas contra-elites.",
                "Na teoria da circulacao das elites, minorias governantes acabam substituidas por contra-elites emergentes.",
                "Protocolos de compressao sem perda reduzem entropia em fluxos binarios de telemetria industrial.",
            ),
            (
                "Monetary expansion lowers borrowing costs and stimulates capital investment across industrial sectors.",
                "Expansionary monetary policy reduces borrowing costs and encourages industrial capital investment.",
                "Photosynthetic chlorophyll absorbs red wavelengths inside chloroplast thylakoid membranes.",
            ),
        ],
    )
    def test_embed_batch_l2_normalized_vectors_rank_paraphrase_above_unrelated(
        self,
        base: str,
        paraphrase: str,
        unrelated: str,
    ) -> None:
        adapter = TfidfEmbeddingAdapter()
        vectors = adapter.embed_batch([base, paraphrase, unrelated])

        assert len(vectors) == 3
        dims = {len(vec) for vec in vectors}
        assert len(dims) == 1
        assert next(iter(dims)) > 0

        for vec in vectors:
            norm = math.sqrt(sum(val * val for val in vec))
            assert math.isclose(norm, 1.0, rel_tol=1e-6)

        paraphrase_sim = _cosine_similarity(vectors[0], vectors[1])
        unrelated_sim = _cosine_similarity(vectors[0], vectors[2])
        assert paraphrase_sim > unrelated_sim

    def test_embed_batch_punctuation_only_vocabulary_degrades_to_zero_vectors(self) -> None:
        adapter = TfidfEmbeddingAdapter()
        vectors = adapter.embed_batch(["...", "!!!"])

        assert len(vectors) == 2
        dims = {len(vec) for vec in vectors}
        assert len(dims) == 1
        assert all(val == 0.0 for vec in vectors for val in vec)


class TestResilientEmbeddingAdapter:
    """Hermetic unit tests for ResilientEmbeddingAdapter."""

    def test_provider_name_and_initial_last_provider_name_match_primary(self) -> None:
        primary = _FakeEmbeddingPort("gemini")
        adapter = ResilientEmbeddingAdapter(primary=primary)

        assert adapter.provider_name == "gemini"
        assert adapter.last_provider_name == "gemini"

    def test_embed_batch_empty_input_returns_empty_without_calling_ports(self) -> None:
        primary = _FakeEmbeddingPort("gemini")
        fallback = _FakeEmbeddingPort("tfidf")
        adapter = ResilientEmbeddingAdapter(primary=primary, fallback=fallback)

        assert adapter.embed_batch([]) == []
        assert primary.calls == []
        assert fallback.calls == []

    def test_embed_batch_primary_success_sets_last_provider_name(self) -> None:
        expected = [[0.9, 0.1], [0.2, 0.8]]
        primary = _FakeEmbeddingPort("ollama", vectors=expected)
        fallback = _FakeEmbeddingPort("tfidf", vectors=[[0.0, 1.0], [1.0, 0.0]])
        adapter = ResilientEmbeddingAdapter(primary=primary, fallback=fallback)

        result = adapter.embed_batch(["first", "second"])

        assert result == expected
        assert adapter.last_provider_name == "ollama"
        assert primary.calls == [["first", "second"]]
        assert fallback.calls == []

    def test_embed_batch_primary_failure_logs_warning_and_falls_back_to_default_tfidf(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        primary = _FakeEmbeddingPort(
            "gemini",
            error=EmbeddingInfrastructureError("Gemini embedding quota exhausted"),
        )
        adapter = ResilientEmbeddingAdapter(primary=primary)

        texts = [
            "Sovereign fiscal deficits shift intertemporal tax burdens.",
            "Unrelated geological stratigraphy of Precambrian basalt formations.",
        ]

        with (
            caplog.at_level(logging.WARNING),
            structlog.testing.capture_logs() as captured_struct_logs,
        ):
            result = adapter.embed_batch(texts)

        assert len(result) == 2
        assert len(result[0]) == len(result[1]) > 0
        assert adapter.last_provider_name == "tfidf_fallback"
        logged_warning = any(record.levelno >= logging.WARNING for record in caplog.records) or any(
            entry.get("log_level") == "warning" for entry in captured_struct_logs
        )
        assert logged_warning is True

    def test_embed_batch_primary_failure_uses_custom_fallback_provider_suffix(self) -> None:
        primary = _FakeEmbeddingPort(
            "gemini",
            error=EmbeddingInfrastructureError("Upstream 503"),
        )
        fallback = _FakeEmbeddingPort("ollama", vectors=[[0.5, 0.5]])
        adapter = ResilientEmbeddingAdapter(primary=primary, fallback=fallback)

        result = adapter.embed_batch(["single unit"])

        assert result == [[0.5, 0.5]]
        assert fallback.calls == [["single unit"]]
        assert adapter.last_provider_name == "ollama_fallback"

    def test_embed_batch_primary_mismatched_vector_count_triggers_fallback(self) -> None:
        primary = _FakeEmbeddingPort("gemini", vectors=[[1.0, 0.0]])  # Only 1 vector for 2 inputs
        fallback = _FakeEmbeddingPort("tfidf", vectors=[[0.2, 0.8], [0.8, 0.2]])
        adapter = ResilientEmbeddingAdapter(primary=primary, fallback=fallback)

        result = adapter.embed_batch(["first unit", "second unit"])

        assert result == [[0.2, 0.8], [0.8, 0.2]]
        assert fallback.calls == [["first unit", "second unit"]]
        assert adapter.last_provider_name == "tfidf_fallback"
