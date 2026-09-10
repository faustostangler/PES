"""Unit and contract tests for Cresmo LLM Transformation Port and Adapters."""

from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError

from cresmo_llm import (
    CresmoLLMConfig,
    GeminiAPIAdapter,
    LLMTransformationPort,
    MockLLMAdapter,
)


def test_llm_transformation_port_is_abstract():
    """Verify that LLMTransformationPort cannot be instantiated directly without implementing transform."""
    with pytest.raises(TypeError):
        LLMTransformationPort()  # type: ignore[abstract]


def test_mock_llm_adapter_implements_port():
    """Verify MockLLMAdapter conforms to LLMTransformationPort contract and records calls."""
    adapter = MockLLMAdapter(canned_response="# Enriched Content\n\n## Informações Complementares\n- Grounding note")
    assert isinstance(adapter, LLMTransformationPort)

    result = adapter.transform(
        prompt="Process this transcript",
        system_instruction="You are Cresmo Expander",
    )

    assert "## Informações Complementares" in result
    assert len(adapter.call_history) == 1
    assert adapter.call_history[0]["prompt"] == "Process this transcript"
    assert adapter.call_history[0]["system_instruction"] == "You are Cresmo Expander"


def test_cresmo_llm_config_defaults():
    """Verify default configuration values adhere to SOTA KISS specifications."""
    config = CresmoLLMConfig(_env_file=None, gemini_api_key="test_api_key_123")
    assert config.gemini_api_key.get_secret_value() == "test_api_key_123"
    assert config.gemini_model == "gemini-3.5-flash"
    assert config.temperature == 0.7
    assert config.max_output_tokens == 65536
    assert config.request_timeout_seconds == 180.0


def test_cresmo_llm_config_fail_fast_missing_key():
    """Verify fail-fast validation when no API key is provided and none exists in env."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValidationError):
            CresmoLLMConfig(_env_file=None)


def test_gemini_api_adapter_calls_genai_client():
    """Verify GeminiAPIAdapter delegates prompt execution to google.genai client with proper configuration."""
    config = CresmoLLMConfig(
        gemini_api_key="AIzaSyDummyKeyForTestingPurposes",
        gemini_model="gemini-3.8-flash",
        temperature=0.5,
        enable_streaming=False,
    )

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "# Enriched Output\n\nEmpirical prose.\n\n## Informações Complementares\nDetails."
    mock_client.models.generate_content.return_value = mock_response

    adapter = GeminiAPIAdapter(config=config, client=mock_client)
    output = adapter.transform(
        prompt="Input raw text",
        system_instruction="System prompt directive",
    )

    assert output == mock_response.text
    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.8-flash"
    assert call_kwargs["contents"] == "Input raw text"
    assert call_kwargs["config"].system_instruction == "System prompt directive"
    assert call_kwargs["config"].temperature == 0.5


def test_gemini_api_adapter_retry_on_transient_failure():
    """Verify GeminiAPIAdapter retries on transient exceptions before returning successful response."""
    config = CresmoLLMConfig(
        gemini_api_key="AIzaSyDummyKeyForTestingPurposes",
        gemini_model="gemini-3.8-flash",
        enable_streaming=False,
    )

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "# Successful After Retry\n\n## Informações Complementares\nValid."

    # Fail once with connection error, then succeed
    mock_client.models.generate_content.side_effect = [
        ConnectionResetError("Transient network failure"),
        mock_response,
    ]

    adapter = GeminiAPIAdapter(config=config, client=mock_client)
    output = adapter.transform(prompt="Test prompt")

    assert output == mock_response.text
    assert mock_client.models.generate_content.call_count == 2


def test_gemini_api_adapter_streaming_mode():
    """Verify GeminiAPIAdapter delegates to generate_content_stream when enable_streaming=True."""
    config = CresmoLLMConfig(
        gemini_api_key="AIzaSyDummyKeyForTestingPurposes",
        gemini_model="gemini-3.8-flash",
        enable_streaming=True,
    )

    mock_client = MagicMock()
    chunk1 = MagicMock()
    chunk1.text = "Hello "
    chunk2 = MagicMock()
    chunk2.text = "World!"
    mock_client.models.generate_content_stream.return_value = [chunk1, chunk2]

    adapter = GeminiAPIAdapter(config=config, client=mock_client)
    output = adapter.transform(prompt="Stream test")

    assert output == "Hello World!"
    mock_client.models.generate_content_stream.assert_called_once()
