"""Unit tests for OllamaLLMAdapter.

Verifies local Ollama HTTP REST communication, payload formatting, error handling,
actionable warnings when Ollama is offline, and availability healthcheck.
"""

from __future__ import annotations

import json
import urllib.error
from email.message import Message
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.exceptions import LLMInfrastructureError
from cresmo.infrastructure.adapters.ollama_llm_adapter import OllamaLLMAdapter


class TestOllamaLLMAdapter:
    """Hermetic unit tests for OllamaLLMAdapter."""

    def test_transform_success(self) -> None:
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            timeout_seconds=10.0,
        )

        mock_response_data = {
            "response": "Circulação de Elites\nMinorias governam a sociedade e são ciclicamente substituídas por novas contra-elites.",
            "done": True,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            result = adapter.transform(
                prompt="Video Title: Pareto\nTranscript...",
                system_instruction="Act as a domain expert.",
                temperature=0.2,
            )

            assert "Circulação de Elites" in result
            assert mock_urlopen.called
            req = mock_urlopen.call_args[0][0]
            assert req.full_url == "http://localhost:11434/api/generate"
            assert req.headers["Content-type"] == "application/json"
            body = json.loads(req.data.decode("utf-8"))
            assert body["model"] == "qwen2.5:7b"
            assert body["prompt"] == "Video Title: Pareto\nTranscript..."
            assert body["system"] == "Act as a domain expert."
            assert body["options"]["temperature"] == 0.2

    def test_transform_connection_refused_raises_actionable_error(self) -> None:
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            with pytest.raises(LLMInfrastructureError, match="ollama serve"):
                adapter.transform("Some prompt")

    def test_transform_http_error_raises_llm_infrastructure_error(self) -> None:
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="nonexistent:model",
        )

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://localhost:11434/api/generate",
                code=404,
                msg="model 'nonexistent:model' not found",
                hdrs=Message(),
                fp=None,
            )

            with pytest.raises(LLMInfrastructureError, match="404"):
                adapter.transform("Some prompt")

    def test_is_available_returns_true_on_success(self) -> None:
        adapter = OllamaLLMAdapter(base_url="http://localhost:11434")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            assert adapter.is_available() is True

    def test_is_available_returns_false_on_connection_error(self) -> None:
        adapter = OllamaLLMAdapter(base_url="http://localhost:11434")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            assert adapter.is_available() is False
