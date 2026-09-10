"""Unit tests for GeminiLLMAdapter with Langfuse telemetry.

Ensures proper delegation to google-genai client and Langfuse span observation.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter


class TestGeminiLLMAdapter:
    """Hermetic unit tests for GeminiLLMAdapter."""

    def test_transform_delegates_to_genai_client(self) -> None:
        # Mock Google GenAI response
        mock_response = MagicMock()
        mock_response.text = "Generated analytical synthesis content."
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 150
        mock_response.usage_metadata.candidates_token_count = 80

        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        mock_langfuse = MagicMock()

        adapter = GeminiLLMAdapter(
            api_key="test-api-key",
            model_name="gemini-2.5-flash",
            genai_client=mock_genai_client,
            langfuse_client=mock_langfuse,
        )

        result = adapter.transform(
            prompt="Analyze the circulation of elites.",
            system_instruction="Act as a political scientist.",
            temperature=0.2,
            trace_id="test-trace-123",
        )

        assert result == "Generated analytical synthesis content."
        mock_genai_client.models.generate_content.assert_called_once()
        call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert call_kwargs["contents"] == "Analyze the circulation of elites."
        assert call_kwargs["config"].temperature == 0.2
        assert call_kwargs["config"].system_instruction == "Act as a political scientist."
