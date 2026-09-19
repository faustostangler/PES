"""Unit tests for OllamaLLMAdapter.

Verifies local Ollama HTTP REST communication, payload formatting, error handling,
actionable warnings when Ollama is offline, and availability healthcheck.
"""

from __future__ import annotations

import json
import time
import urllib.error
from email.message import Message
from typing import Any
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

    def test_transform_uses_configured_default_temperature(self) -> None:
        """Verify that default_temperature passed in constructor is used when temperature is None."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            default_temperature=0.35,
        )

        mock_response_data = {
            "response": "Clean output",
            "done": True,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.transform("Some prompt", temperature=None)

            req = mock_urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert body["options"]["temperature"] == 0.35

    def test_transform_emits_langfuse_generation_telemetry(self) -> None:
        """Verify that OllamaLLMAdapter passes token counts and metrics to Langfuse client."""
        mock_langfuse = MagicMock()
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            langfuse_client=mock_langfuse,
        )

        mock_response_data = {
            "response": "Observed output",
            "done": True,
            "prompt_eval_count": 50,
            "eval_count": 120,
            "total_duration": 450_000_000,
            "eval_duration": 400_000_000,
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            result = adapter.transform(
                "Telemetry test prompt",
                trace_id="cresmo-trace-1",
                session_id="session-42",
            )

            assert result == "Observed output"
            mock_langfuse.update_current_generation.assert_called_once()
            call_kwargs = mock_langfuse.update_current_generation.call_args[1]
            assert call_kwargs["usage_details"] == {
                "input": 50,
                "output": 120,
                "total": 170,
            }
            assert call_kwargs["metadata"]["total_duration_ms"] == 450.0
            assert call_kwargs["metadata"]["trace_id"] == "cresmo-trace-1"
            assert call_kwargs["metadata"]["session_id"] == "session-42"

    def test_transform_omits_num_predict_when_zero_or_negative(self) -> None:
        """Verify that when num_predict is 0 (default), num_predict is omitted from options."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            num_predict=0,
        )
        mock_response_data = {"response": "Clean output", "done": True}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.transform("Test prompt")
            req = mock_urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert "num_predict" not in body["options"]

    def test_transform_includes_num_predict_when_positive(self) -> None:
        """Verify that when num_predict > 0, it is explicitly included in options."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            num_predict=500,
        )
        mock_response_data = {"response": "Clean output", "done": True}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.transform("Test prompt")
            req = mock_urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert body["options"]["num_predict"] == 500

    def test_warmup_success(self) -> None:
        """Verify that warmup asynchronously sends model and keep_alive to /api/generate."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            keep_alive="2h",
            warmup_timeout_seconds=120.0,
        )

        mock_response_data = {
            "model": "qwen2.5:7b",
            "done": True,
            "done_reason": "load",
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.warmup()
            assert adapter.wait_for_warmup() is True
            assert adapter.is_warmed_up is True

            req = mock_urlopen.call_args[0][0]
            assert req.full_url == "http://localhost:11434/api/generate"
            body = json.loads(req.data.decode("utf-8"))
            assert body["model"] == "qwen2.5:7b"
            assert body["keep_alive"] == "2h"
            assert "prompt" not in body

    def test_warmup_model_not_found_raises_actionable_error(self) -> None:
        """Verify that warmup failure on missing model raises LLMInfrastructureError with pull command."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="nonexistent:model",
        )

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://localhost:11434/api/generate",
                code=404,
                msg="Not Found",
                hdrs=Message(),
                fp=None,
            )

            adapter.warmup()
            with pytest.raises(LLMInfrastructureError, match="ollama pull"):
                adapter.wait_for_warmup()

    def test_warmup_timeout_raises_actionable_error(self) -> None:
        """Verify that warmup timeout raises LLMInfrastructureError."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            warmup_timeout_seconds=5.0,
        )

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError("Socket timed out")

            adapter.warmup()
            with pytest.raises(LLMInfrastructureError, match="timed out loading model"):
                adapter.wait_for_warmup()

    def test_transform_propagates_keep_alive(self) -> None:
        """Verify that transform includes configured keep_alive in every generate request."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            keep_alive="1h",
        )
        adapter._is_warmed_up = True  # Pre-mark warmed up to test transform payload directly

        mock_response_data = {"response": "Output with keepalive", "done": True}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.transform("Test keepalive prompt")
            req = mock_urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert body["keep_alive"] == "1h"

    def test_async_warmup_and_rendezvous_barrier_success(self) -> None:
        """Verify non-blocking early background warmup and lazy rendezvous barrier synchronization."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )
        assert adapter.is_warmed_up is False

        mock_response_data = {"done": True, "done_reason": "load"}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            adapter.warmup()
            assert adapter._warmup_thread is not None

            # Rendezvous barrier blocks until thread completes and returns True
            assert adapter.wait_for_warmup() is True
            assert adapter.is_warmed_up is True

            # Subsequent wait_for_warmup returns immediately without re-invoking urlopen
            mock_urlopen.reset_mock()
            assert adapter.wait_for_warmup() is True
            mock_urlopen.assert_not_called()

    def test_warmup_concurrent_calls_prevent_duplicate_threads(self) -> None:
        """Verify multiple calls to warmup() do not spawn duplicate threads or cause race conditions."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )
        mock_response_data = {"done": True, "done_reason": "load"}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            # Dispatch twice
            adapter.warmup()
            initial_thread = adapter._warmup_thread
            adapter.warmup()
            assert adapter._warmup_thread is initial_thread

            assert adapter.wait_for_warmup() is True
            assert adapter.is_warmed_up is True

            # Calling warmup after completion is a no-op
            adapter.warmup()
            assert adapter.is_warmed_up is True

    def test_wait_for_warmup_reraises_background_exception(self) -> None:
        """Verify that an exception raised in background warmup is re-raised at rendezvous barrier."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="nonexistent:model",
        )

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://localhost:11434/api/generate",
                code=404,
                msg="Not Found",
                hdrs=Message(),
                fp=None,
            )

            adapter.warmup()
            with pytest.raises(LLMInfrastructureError, match="ollama pull"):
                adapter.wait_for_warmup()

    def test_transform_rendezvous_barrier_triggers_warmup_when_cold(self) -> None:
        """Verify that transform automatically invokes rendezvous barrier when adapter is cold."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )
        assert adapter.is_warmed_up is False

        mock_preload_data = {"done": True, "done_reason": "load"}
        mock_gen_data = {"response": "Transformed text", "done": True}

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_preload_resp = MagicMock()
            mock_preload_resp.status = 200
            mock_preload_resp.read.return_value = json.dumps(mock_preload_data).encode("utf-8")
            mock_preload_resp.__enter__.return_value = mock_preload_resp

            mock_gen_resp = MagicMock()
            mock_gen_resp.status = 200
            mock_gen_resp.read.return_value = json.dumps(mock_gen_data).encode("utf-8")
            mock_gen_resp.__enter__.return_value = mock_gen_resp

            mock_urlopen.side_effect = [mock_preload_resp, mock_gen_resp]

            result = adapter.transform("Hello from cold start")
            assert result == "Transformed text"
            assert adapter.is_warmed_up is True
            assert mock_urlopen.call_count == 2

    def test_concurrent_threads_waiting_at_rendezvous_barrier(self) -> None:
        """Verify multiple concurrent threads block cleanly at barrier with zero race conditions."""
        import concurrent.futures

        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )

        mock_preload_data = {"done": True, "done_reason": "load"}

        def _delayed_urlopen(*_args: Any, **_kwargs: Any) -> MagicMock:
            time.sleep(0.05)  # Simulate network/VRAM load time
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_preload_data).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=_delayed_urlopen) as mock_urlopen:
            adapter.warmup()

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(adapter.wait_for_warmup) for _ in range(5)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            assert all(results)
            assert adapter.is_warmed_up is True
            assert mock_urlopen.call_count == 1
