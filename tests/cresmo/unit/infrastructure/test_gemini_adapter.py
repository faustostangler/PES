"""Unit tests for GeminiLLMAdapter with injected Hexagonal TelemetryPort.

Ensures proper delegation to google-genai client, transient error classification,
retry behavior, fallback model execution, and TelemetryPort generation spans (ADR-065, ADR-070).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors, types

from cresmo.application.ports import (
    NoOpTelemetryPort,
    SpanKind,
    active_telemetry_pass,
    active_telemetry_stage,
)
from cresmo.domain.value_objects.prompt import ChatPrompt
from cresmo.infrastructure.adapters.llm.gemini_adapter import (
    GeminiLLMAdapter,
    _is_transient_genai_error,
)
from cresmo.infrastructure.adapters.llm.gemini_common import (
    build_thinking_config,
    resolve_effective_thinking_level,
)
from tests.doubles.telemetry_fake import InMemoryTelemetryPort


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

    def test_api_error_without_code_attribute_returns_false(self) -> None:
        class DummyAPIError(errors.APIError):
            def __init__(self) -> None:
                pass

        err = DummyAPIError()
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

    @pytest.mark.parametrize(
        "msg",
        [
            "504 DEADLINE_EXCEEDED",
            "Error 504: Deadline expired",
        ],
    )
    def test_transient_504_deadline_exceeded_patterns_return_true(self, msg: str) -> None:
        """Verify 504 DEADLINE_EXCEEDED and deadline expired errors are classified as transient."""
        assert _is_transient_genai_error(RuntimeError(msg)) is True


class TestGeminiLLMAdapter:
    """Hermetic unit tests for GeminiLLMAdapter."""

    def test_transform_delegates_to_genai_client(self) -> None:
        mock_response = MagicMock()
        mock_response.text = "Generated analytical synthesis content."
        mock_response.usage_metadata = MagicMock(prompt_token_count=150, candidates_token_count=80)

        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(
            api_key="test-api-key",
            model_name="gemini-2.5-flash",
            max_output_tokens=4096,
            genai_client=mock_genai_client,
            telemetry_port=telemetry,
        )

        result = adapter.transform(
            prompt=ChatPrompt.from_system_and_user(
                system="Act as a political scientist.",
                user="Analyze the circulation of elites.",
            ),
            temperature=0.7,
            trace_id="test-trace-123",
            session_id="session-456",
            user_id="user-789",
        )

        assert result == "Generated analytical synthesis content."
        assert telemetry.flush_count == 0
        mock_genai_client.models.generate_content.assert_called_once()
        call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert len(call_kwargs["contents"]) == 1
        assert call_kwargs["contents"][0].role == "user"
        assert call_kwargs["contents"][0].parts[0].text == "Analyze the circulation of elites."
        assert call_kwargs["config"].temperature is None
        assert call_kwargs["config"].thinking_config is not None
        assert call_kwargs["config"].thinking_config.thinking_level == types.ThinkingLevel.LOW
        assert call_kwargs["config"].max_output_tokens == 4096
        assert call_kwargs["config"].system_instruction == "Act as a political scientist."
        assert call_kwargs["config"].automatic_function_calling.disable is True

    def test_transform_applies_thinking_level_and_omits_deprecated_temperature(self) -> None:
        mock_response = MagicMock(text="Low thinking text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            genai_client=mock_genai_client,
        )
        adapter.transform(prompt=ChatPrompt.single_turn("Default test"))

        default_call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert default_call_kwargs["config"].temperature is None
        assert default_call_kwargs["config"].thinking_config is not None
        assert (
            default_call_kwargs["config"].thinking_config.thinking_level == types.ThinkingLevel.LOW
        )

        adapter.transform(
            prompt=ChatPrompt.single_turn("Minimal test"),
            thinking_level="minimal",
        )
        override_call_kwargs = mock_genai_client.models.generate_content.call_args[1]
        assert override_call_kwargs["config"].temperature is None
        assert override_call_kwargs["config"].thinking_config is not None
        assert (
            override_call_kwargs["config"].thinking_config.thinking_level
            == types.ThinkingLevel.MINIMAL
        )

    def test_transform_emits_full_telemetry_metadata(self) -> None:
        mock_response = MagicMock(text="Output with telemetry", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            telemetry_port=telemetry,
        )

        adapter.transform(
            prompt=ChatPrompt.single_turn("Test prompt"),
            trace_id="vid123_concepts",
            session_id="raw_index_Philosophy",
            user_id="Philosophy",
        )

        assert len(telemetry.spans) == 1
        gen_span = telemetry.spans[0]
        assert gen_span.name == "cresmo.llm.generate"
        assert gen_span.kind is SpanKind.GENERATION
        assert gen_span.attributes["gen_ai.system"] == "google"
        assert gen_span.attributes["gen_ai.request.model"] == "gemini-3.5-flash-lite"
        assert gen_span.attributes["gen_ai.usage.input_tokens"] == 2
        assert gen_span.attributes["gen_ai.usage.output_tokens"] == 3
        assert gen_span.attributes["langfuse.session.id"] == "raw_index_Philosophy"
        assert gen_span.attributes["langfuse.user.id"] == "Philosophy"
        assert gen_span.attributes["cresmo.trace_id"] == "vid123_concepts"
        assert gen_span.attributes["cresmo.thinking_level"] == "low"
        assert "cresmo.temperature" not in gen_span.attributes
        assert gen_span.outputs == ["Output with telemetry"]

    def test_transform_emits_reasoning_tokens_from_usage_metadata(self) -> None:
        mock_response = MagicMock(
            text="Output with thinking usage",
            usage_metadata=MagicMock(
                prompt_token_count=120,
                candidates_token_count=45,
                thoughts_token_count=64,
            ),
        )
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(genai_client=mock_genai_client, telemetry_port=telemetry)
        adapter.transform(prompt=ChatPrompt.single_turn("Reasoned prompt"))

        attrs = telemetry.spans[0].attributes
        assert attrs["gen_ai.usage.input_tokens"] == 120
        assert attrs["gen_ai.usage.output_tokens"] == 45
        assert attrs["gen_ai.usage.reasoning_tokens"] == 64
        assert attrs["cresmo.thinking_level"] == "low"

    def test_transform_retries_on_transient_error(self) -> None:
        mock_response = MagicMock(text="Success after retry", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE: high demand"),
            mock_response,
        ]

        adapter = GeminiLLMAdapter(
            model_name="gemini-2.5-flash",
            genai_client=mock_genai_client,
        )

        result = adapter.transform(prompt=ChatPrompt.single_turn("Test retry"))
        assert result == "Success after retry"
        assert mock_genai_client.models.generate_content.call_count == 2

    def test_transform_falls_back_to_secondary_model_on_failure(self) -> None:
        mock_fallback_response = MagicMock(text="Fallback model response", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.side_effect = [
            ValueError("Primary model failure"),
            mock_fallback_response,
        ]

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.1-flash-lite",
            genai_client=mock_genai_client,
        )

        result = adapter.transform(prompt=ChatPrompt.single_turn("Test fallback"))
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
        )

        with pytest.raises(ValueError, match="Fatal model error"):
            adapter.transform(prompt=ChatPrompt.single_turn("Test no fallback"))

    def test_transform_reraises_when_fallback_same_as_primary(self) -> None:
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.side_effect = ValueError("Same model error")

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.5-flash-lite",
            genai_client=mock_genai_client,
        )

        with pytest.raises(ValueError, match="Same model error"):
            adapter.transform(prompt=ChatPrompt.single_turn("Test same fallback"))

    def test_transform_token_fallback_when_usage_metadata_none(self) -> None:
        mock_response = MagicMock(text="Three words text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(
            genai_client=mock_genai_client,
            telemetry_port=telemetry,
        )
        adapter.transform(prompt=ChatPrompt.single_turn("One two three four five"))

        attrs = telemetry.spans[0].attributes
        assert attrs["gen_ai.usage.input_tokens"] == 5
        assert attrs["gen_ai.usage.output_tokens"] == 3

    def test_transform_works_with_default_noop_telemetry_port(self) -> None:
        mock_response = MagicMock(text="Output text", usage_metadata=None)
        mock_genai_client = MagicMock()
        mock_genai_client.models.generate_content.return_value = mock_response

        adapter = GeminiLLMAdapter(genai_client=mock_genai_client)
        assert isinstance(adapter._telemetry, NoOpTelemetryPort)
        assert adapter.transform(prompt=ChatPrompt.single_turn("NoOp test")) == "Output text"

    def test_init_creates_genai_client_when_none(self) -> None:
        with patch("google.genai.Client") as mock_client_cls:
            adapter = GeminiLLMAdapter(
                api_key="secret-key",
                genai_client=None,
            )
            mock_client_cls.assert_called_once()
            call_kwargs = mock_client_cls.call_args.kwargs
            assert call_kwargs["api_key"] == "secret-key"
            assert call_kwargs["http_options"].timeout == 300000
            assert adapter._client == mock_client_cls.return_value

    def test_default_initialization_attributes(self) -> None:
        mock_client = MagicMock()
        adapter = GeminiLLMAdapter(genai_client=mock_client)
        assert adapter.model_name == "gemini-3.5-flash-lite"
        assert adapter.fallback_model_name == "gemini-3.6-flash"
        assert adapter.max_output_tokens == 32_768
        assert adapter.thinking_level == "low"
        assert not hasattr(adapter, "default_temperature")

    def test_transient_api_error_all_codes_individually(self) -> None:
        for c in (429, 500, 502, 503, 504):
            err = errors.APIError(code=c, response_json={})
            assert _is_transient_genai_error(err) is True

    def test_transform_switches_to_fallback_model_on_exception(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Fallback output"
        mock_client.models.generate_content.side_effect = [
            RuntimeError("Primary model failed"),
            mock_response,
        ]

        adapter = GeminiLLMAdapter(
            genai_client=mock_client,
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.1-flash-lite",
        )

        res = adapter.transform(ChatPrompt.single_turn("trigger fallback"))
        assert res == "Fallback output"
        assert mock_client.models.generate_content.call_count == 2
        calls = mock_client.models.generate_content.call_args_list
        assert calls[0].kwargs["model"] == "gemini-3.5-flash-lite"
        assert calls[1].kwargs["model"] == "gemini-3.1-flash-lite"

    def test_transform_rotates_api_key_on_429(self) -> None:
        from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

        client1 = MagicMock(name="client-1")
        client2 = MagicMock(name="client-2")
        client1.models.generate_content.side_effect = RuntimeError(
            "ResourceExhausted: 429 Quota exceeded. Please retry in 3600s."
        )
        mock_resp = MagicMock(text="Success from secondary key", usage_metadata=None)
        client2.models.generate_content.return_value = mock_resp

        clients = {"k1": client1, "k2": client2}
        pool = GeminiCredentialPool(keys=["k1", "k2"], client_factory=lambda k: clients[k])

        adapter = GeminiLLMAdapter(credential_pool=pool)
        result = adapter.transform(ChatPrompt.single_turn("Testing 429 failover"))

        assert result == "Success from secondary key"
        assert client1.models.generate_content.call_count == 1
        assert client2.models.generate_content.call_count == 1
        assert pool.lease()[0] == "k2"

    def test_transform_does_not_rotate_key_on_503(self) -> None:
        from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

        client1 = MagicMock(name="client-1")
        client2 = MagicMock(name="client-2")
        mock_resp = MagicMock(text="Recovered from 503", usage_metadata=None)
        client1.models.generate_content.side_effect = [
            RuntimeError("503 UNAVAILABLE: high demand"),
            mock_resp,
        ]

        clients = {"k1": client1, "k2": client2}
        pool = GeminiCredentialPool(keys=["k1", "k2"], client_factory=lambda k: clients[k])

        adapter = GeminiLLMAdapter(credential_pool=pool)
        result = adapter.transform(ChatPrompt.single_turn("Testing 503 retention"))

        assert result == "Recovered from 503"
        assert client1.models.generate_content.call_count == 2
        assert client2.models.generate_content.call_count == 0
        assert pool.lease()[0] == "k1"

    def test_init_normalizes_gemini_provider_prefix_on_models(self) -> None:
        """Verify ACL strips leading 'gemini:' provider prefix from primary and fallback models."""
        mock_response = MagicMock(text="Normalized output", usage_metadata=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        adapter = GeminiLLMAdapter(
            model_name="gemini:gemini-3.8-flash",
            fallback_model_name="gemini:gemini-3.8-flash",
            genai_client=mock_client,
        )

        assert adapter.model_name == "gemini-3.8-flash"
        assert adapter.fallback_model_name == "gemini-3.8-flash"

        result = adapter.transform(prompt=ChatPrompt.single_turn("Normalize model name"))
        assert result == "Normalized output"
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.8-flash"

    def test_transform_fallback_recomputes_thinking_config_for_fallback_model(self) -> None:
        """Verify fallback call clamps thinking_level appropriately for the fallback model."""
        mock_fallback_response = MagicMock(text="Fallback clamped", usage_metadata=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            ValueError("Primary failed"),
            mock_fallback_response,
        ]

        adapter = GeminiLLMAdapter(
            model_name="gemini-4-hydrogen",
            fallback_model_name="gemini-3.6-flash",
            thinking_level="xhigh",
            genai_client=mock_client,
        )
        result = adapter.transform(prompt=ChatPrompt.single_turn("Fallback clamping test"))
        assert result == "Fallback clamped"
        assert mock_client.models.generate_content.call_count == 2
        fallback_kwargs = mock_client.models.generate_content.call_args_list[1].kwargs
        assert fallback_kwargs["model"] == "gemini-3.6-flash"
        assert fallback_kwargs["config"].thinking_config is not None
        assert fallback_kwargs["config"].thinking_config.thinking_level == types.ThinkingLevel.HIGH


class TestThinkingLevelClamping:
    """Hermetic unit tests for model-aware thinking_level resolution and ThinkingConfig building."""

    @pytest.mark.parametrize(
        ("model", "requested", "expected"),
        [
            ("gemini-3.5-flash-lite", "minimal", "minimal"),
            ("gemini-3.5-flash-lite", "low", "low"),
            ("gemini-3.5-flash-lite", "medium", "medium"),
            ("gemini-3.5-flash-lite", "high", "high"),
            ("gemini-3.5-flash-lite", "xhigh", "high"),
            ("gemini-3.8-flash", "minimal", "low"),
            ("gemini-3.8-flash", "low", "low"),
            ("gemini-3.8-flash", "xhigh", "high"),
            ("gemini-4-hydrogen", "minimal", "low"),
            ("gemini-4-hydrogen", "xhigh", "xhigh"),
            ("gemma-4-31b-it", "low", "minimal"),
            ("gemma-4-31b-it", "minimal", "minimal"),
            ("gemma-4-31b-it", "medium", "high"),
            ("gemma-4-31b-it", "high", "high"),
            ("gemma-4-26b-a4b-it", "low", "minimal"),
            ("gemma-4-26b-a4b-it", "high", "high"),
            ("gemini-2.5-flash", "minimal", "low"),
            ("gemini-2.5-flash", "low", "low"),
            ("gemini-3.5-flash-lite", None, None),
        ],
    )
    def test_resolve_effective_thinking_level(
        self, model: str, requested: str | None, expected: str | None
    ) -> None:
        assert resolve_effective_thinking_level(model, requested) == expected

    def test_build_thinking_config_returns_none_when_unset(self) -> None:
        assert build_thinking_config("gemini-3.5-flash-lite", None) is None

    def test_build_thinking_config_maps_gemma_low_to_minimal(self) -> None:
        cfg = build_thinking_config("gemma-4-31b-it", "low")
        assert cfg is not None
        assert cfg.thinking_level == types.ThinkingLevel.MINIMAL

    def test_build_thinking_config_supports_xhigh_for_gemini_4_hydrogen(self) -> None:
        cfg = build_thinking_config("gemini-4-hydrogen", "xhigh")
        assert cfg is not None
        assert str(cfg.thinking_level).lower().endswith("xhigh")


class TestAdr065StageScopedGenerationTelemetry:
    """Verify dynamic stage-scoped generation and fallback observation naming via TelemetryPort."""

    def test_transform_emits_stage_scoped_and_standalone_generation_names(self) -> None:
        mock_response = MagicMock(text="Stage output", usage_metadata=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(genai_client=mock_client, telemetry_port=telemetry)

        assert adapter.transform(ChatPrompt.single_turn("Standalone call")) == "Stage output"
        with active_telemetry_stage("fluid_prose"):
            assert adapter.transform(ChatPrompt.single_turn("In-stage call")) == "Stage output"

        assert [s.name for s in telemetry.spans] == [
            "cresmo.llm.generate",
            "cresmo.fluid_prose.generate",
        ]
        assert all(s.kind is SpanKind.GENERATION for s in telemetry.spans)

    def test_transform_fallback_emits_separate_fallback_observation(self) -> None:
        mock_fallback_response = MagicMock(text="Recovered by fallback", usage_metadata=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            ValueError("Primary failed"),
            mock_fallback_response,
            ValueError("Primary failed standalone"),
            mock_fallback_response,
        ]
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.6-flash",
            genai_client=mock_client,
            telemetry_port=telemetry,
        )

        with active_telemetry_stage("fluid_prose"):
            assert (
                adapter.transform(ChatPrompt.single_turn("Stage fallback"))
                == "Recovered by fallback"
            )
        assert (
            adapter.transform(ChatPrompt.single_turn("Standalone fallback"))
            == "Recovered by fallback"
        )

        assert [s.name for s in telemetry.spans] == [
            "cresmo.fluid_prose.generate",
            "cresmo.fluid_prose.generate_fallback",
            "cresmo.llm.generate",
            "cresmo.llm.generate_fallback",
        ]
        assert len(telemetry.spans[0].errors) == 1
        assert len(telemetry.spans[1].errors) == 0
        assert len(telemetry.spans[2].errors) == 1
        assert len(telemetry.spans[3].errors) == 0

    def test_transform_does_not_failover_model_when_credential_pool_exhausted(self) -> None:
        from cresmo.infrastructure.adapters.llm.gemini_pool import (
            CredentialPoolExhaustedError,
            GeminiCredentialPool,
        )

        client1 = MagicMock()
        client1.models.generate_content.side_effect = RuntimeError(
            "429 RESOURCE_EXHAUSTED: retry in 60s"
        )
        pool = GeminiCredentialPool(keys=["k1"], client_factory=lambda _: client1)
        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.6-flash",
            credential_pool=pool,
        )

        with pytest.raises(CredentialPoolExhaustedError):
            adapter.transform(ChatPrompt.single_turn("Quota exhausted"))

        assert client1.models.generate_content.call_count == 1
        assert client1.models.generate_content.call_args.kwargs["model"] == "gemini-3.5-flash-lite"

    def test_transform_and_fallback_include_active_pass_number(self) -> None:
        mock_fallback_response = MagicMock(text="Pass 2 fallback output", usage_metadata=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            ValueError("Primary failed on pass 2"),
            mock_fallback_response,
        ]
        telemetry = InMemoryTelemetryPort()

        adapter = GeminiLLMAdapter(
            model_name="gemini-3.5-flash-lite",
            fallback_model_name="gemini-3.6-flash",
            genai_client=mock_client,
            telemetry_port=telemetry,
        )

        with active_telemetry_stage("gap_filler"), active_telemetry_pass(2):
            assert (
                adapter.transform(ChatPrompt.single_turn("Pass 2 prompt"))
                == "Pass 2 fallback output"
            )

        assert [s.name for s in telemetry.spans] == [
            "cresmo.gap_filler.generate.pass_2",
            "cresmo.gap_filler.generate_fallback.pass_2",
        ]
        assert telemetry.spans[1].attributes["cresmo.pass_num"] == 2
