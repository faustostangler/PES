"""Unit tests for GeminiLLMAdapter with Langfuse telemetry.

Ensures proper delegation to google-genai client, transient error classification,
retry behavior, fallback model execution, and Langfuse span observation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from cresmo.infrastructure.adapters.gemini_adapter import (
    GeminiLLMAdapter,
    _is_transient_genai_error,
)


class TestTransientErrorClassification:
    """Tests for _is_transient_genai_error covering API error codes and transient strings."""

    @pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
    def test_transient_api_error_codes_return_true(self, code: int) -> None:
        err = errors.APIError(code=code, response_json={})
        assert _is_transient_genai_error(err) is True

    @pytest.mark.parametrize("code", [400, 401, 403, 404, 499])
    def test_non_transient_api_error_codes_return_false(self, code: int) -> None:
        err = errors.APIError(code=code, response_json={})
        assert _is_transient_genai_error(err) is False

    @pytest.mark.parametrize(
        "msg",
        [
            "Error 503: Backend service unavailable",
            "Error 429: Too Many Requests",
            "Status UNAVAILABLE from upstream gRPC",
            "ResourceExhausted: Quota limit reached",
            "Server is currently under high demand",
            "Exceeded rate limit for model",
            "Connection reset by peer during read",
        ],
    )
    def test_transient_error_substrings_return_true(self, msg: str) -> None:
        err = RuntimeError(msg)
        assert _is_transient_genai_error(err) is True

    @pytest.mark.parametrize(
        "msg",
        [
            "400 Bad Request: malformed prompt",
            "401 Unauthorized: invalid API key",
            "403 PermissionDenied",
            "404 Model not found",
            "SyntaxError: invalid syntax",
        ],
    )
    def test_non_transient_error_substrings_return_false(self, msg: str) -> None:
        err = RuntimeError(msg)
        assert _is_transient_genai_error(err) is False

    def test_arbitrary_exception_returns_false(self) -> None:
        err = ValueError("Invalid operation argument")
        assert _is_transient_genai_error(err) is False


class TestGeminiLLMAdapter:
    """Hermetic unit tests for GeminiLLMAdapter."""

    def test_transform_delegates_to_genai_client(self) -> None:
        mock_response = MagicMock()
        mock_response.text = "Generated analytical synthesis content."
        mock_response.usage_metadata = MagicMock(prompt_token_count=150, candidates_token_count=80)

        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_langfuse = MagicMock()

        adapter = GeminiLLMAdapter(
            api_key="test-api-key",
            model_name="gemini-2.5-flash",
            max_output_tokens=4096,
            genai_client=mock_genai_client,
            langfuse_client=mock_langfuse,
        )

        result = adapter.transform(
            prompt="Analyze the circulation of elites.",
            system_instruction="Act as a political scientist.",
            temperature=0.7,
            trace_id="test-trace-123",
            session_id="session-456",
            user_id="user-789",
        )

        assert result == "Generated analytical synthesis content."
        mock_genai_client.models.generate_content.assert_called_once()
        call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert call_kwargs["contents"] == "Analyze the circulation of elites."
        assert call_kwargs["config"].temperature == 0.7
        assert call_kwargs["config"].max_output_tokens == 4096
        assert call_kwargs["config"].system_instruction == "Act as a political scientist."
        assert call_kwargs["config"].automatic_function_calling.disable is True

        # Verify Langfuse generation metadata update
        mock_langfuse.update_current_generation.assert_called_once_with(
            name="test-trace-123",
            model="gemini-2.5-flash",
            output="Generated analytical synthesis content.",
            usage_details={"input": 150, "output": 80, "total": 230},
            metadata={
                "provider": "gemini",
                "temperature": 0.7,
                "trace_id": "test-trace-123",
                "session_id": "session-456",
                "user_id": "user-789",
            },
        )

    def test_transform_uses_default_temperature_when_none(self) -> None:
        mock_response = MagicMock(text="Default temp text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            langfuse_client=None,
        )
        adapter.transform(prompt="Default test")

        call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert call_kwargs["config"].temperature == 0.2

    def test_transform_emits_full_telemetry_metadata(self) -> None:
        mock_response = MagicMock(text="Output with telemetry", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_langfuse = MagicMock()
        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            langfuse_client=mock_langfuse,
        )

        adapter.transform(
            prompt="Test prompt",
            trace_id="vid123_concepts",
            session_id="raw_index_Philosophy",
            user_id="Philosophy",
        )

        mock_langfuse.update_current_generation.assert_called_once_with(
            name="vid123_concepts",
            model="gemini-3.5-flash-lite",
            output="Output with telemetry",
            usage_details={"input": 2, "output": 3, "total": 5},
            metadata={
                "provider": "gemini",
                "temperature": 0.2,
                "trace_id": "vid123_concepts",
                "session_id": "raw_index_Philosophy",
                "user_id": "Philosophy",
            },
        )

    def test_transform_retries_on_transient_error(self) -> None:
        mock_response = MagicMock(text="Success after retry", usage_metadata=None)
        mock_genai_client = MagicMock()
        # Fail first with transient 503, then succeed
        mock_genai_client.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE: high demand"),
            mock_response,
        ]

        adapter = GeminiLLMAdapter(
            model_name="gemini-2.5-flash",
            genai_client=mock_genai_client,
            langfuse_client=None,
        )

        result = adapter.transform(prompt="Test retry")
        assert result == "Success after retry"
        assert mock_genai_client.models.generate_content.call_count == 2

    def test_transform_falls_back_to_secondary_model_on_failure(self) -> None:
        mock_fallback_response = MagicMock(text="Fallback model response", usage_metadata=None)
        mock_genai_client = MagicMock()
        # Primary fails with non-retryable error, fallback succeeds
        mock_genai_client.models.generate_content.side_effect = [
            ValueError("Primary model failure"),
            mock_fallback_response,
        ]

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.1-flash-lite",
            genai_client=mock_genai_client,
            langfuse_client=None,
        )

        result = adapter.transform(prompt="Test fallback")
        assert result == "Fallback model response"
        assert mock_genai_client.models.generate_content.call_count == 2
        first_call = mock_genai_client.models.generate_content.call_args_list[0][1]
        second_call = mock_genai_client.models.generate_content.call_args_list[1][1]
        assert first_call["model"] == "gemini-3.5-flash-lite"
        assert second_call["model"] == "gemini-3.1-flash-lite"

    def test_transform_reraises_when_no_fallback_configured(self) -> None:
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.side_effect = ValueError("Fatal model error")

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name=None,
            genai_client=mock_genai_client,
            langfuse_client=None,
        )

        with pytest.raises(ValueError, match="Fatal model error"):
            adapter.transform(prompt="Test no fallback")

    def test_transform_reraises_when_fallback_same_as_primary(self) -> None:
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.side_effect = ValueError("Same model error")

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.5-flash-lite",
            genai_client=mock_genai_client,
            langfuse_client=None,
        )

        with pytest.raises(ValueError, match="Same model error"):
            adapter.transform(prompt="Test same fallback")

    def test_transform_token_fallback_when_usage_metadata_none(self) -> None:
        mock_response = MagicMock(text="Three words text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_langfuse = MagicMock()
        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            langfuse_client=mock_langfuse,
        )

        adapter.transform(prompt="One two three four five")

        mock_langfuse.update_current_generation.assert_called_once_with(
            name="gemini_generation",
            model="gemini-3.5-flash-lite",
            output="Three words text",
            usage_details={"input": 5, "output": 3, "total": 8},
            metadata={"provider": "gemini", "temperature": 0.2},
        )

    def test_transform_handles_langfuse_telemetry_exception_gracefully(self) -> None:
        mock_response = MagicMock(text="Output text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_langfuse = MagicMock()
        mock_langfuse.update_current_generation.side_effect = RuntimeError("Telemetry crash")

        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            langfuse_client=mock_langfuse,
        )

        # Should not raise exception
        result = adapter.transform(prompt="Test telemetry error")
        assert result == "Output text"

    def test_init_without_langfuse_or_env(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            adapter = GeminiLLMAdapter(
                genai_client=MagicMock(),
                langfuse_client=None,
            )
            assert adapter._langfuse is None

    def test_init_creates_genai_client_when_none(self) -> None:
        with patch("google.genai.Client") as mock_client_cls:
            adapter = GeminiLLMAdapter(
                api_key="secret-key",
                genai_client=None,
                langfuse_client=None,
            )
            mock_client_cls.assert_called_once_with(api_key="secret-key")
            assert adapter._client == mock_client_cls.return_value
