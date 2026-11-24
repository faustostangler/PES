"""Production LLM adapter integrating Google Gemini API with injected Hexagonal TelemetryPort.

Adheres to EVAL-001 rubrics and ADR-070 unified telemetry standards, capturing
generation spans, trace IDs, latency, token counts, thinking telemetry, and structured I/O
through TelemetryPort. Acts as an Anti-Corruption Layer (ACL) shielding the domain core
from vendor-specific types and transient HTTP 429/503 network anomalies.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-003: PES Production Architecture & Telemetry
    - ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature
    - ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
    - EVAL-001: LLM Synthesis Evaluation Rubrics
"""

from __future__ import annotations

from typing import Any

import structlog
from google.genai import types
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpTelemetryPort,
    SpanKind,
    TelemetryPort,
    resolve_llm_generation_span_name,
)
from cresmo.domain.value_objects import ChatPrompt, MessageRole
from cresmo.infrastructure.adapters.llm.gemini_common import (
    build_thinking_config,
    is_transient_cluster_error,
    is_transient_genai_error,
    log_gemini_retry_attempt,
    resolve_effective_thinking_level,
)
from cresmo.infrastructure.adapters.llm.gemini_pool import (
    CredentialPoolExhaustedError,
    GeminiCredentialPool,
    is_quota_exhausted_error,
)
from cresmo.infrastructure.adapters.telemetry.genai import build_genai_attributes
from cresmo.infrastructure.config import (
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
)

__all__ = ["GeminiLLMAdapter"]

logger = structlog.get_logger(__name__)

_is_transient_genai_error = is_transient_genai_error
_is_transient_cluster_error = is_transient_cluster_error


@retry(
    retry=retry_if_exception(_is_transient_cluster_error),
    wait=wait_random_exponential(min=2, max=20),
    stop=stop_after_attempt(3),
    before_sleep=log_gemini_retry_attempt,
    reraise=True,
)
def _generate_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Execute model content generation with bounded exponential backoff on transient errors.

    Args:
        client: Google GenAI client instance.
        model: Model identifier string.
        contents: Input prompt or payload.
        config: Generation configuration parameters.

    Returns:
        SDK generation response object.
    """
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )


class GeminiLLMAdapter(LLMTransformationPort):
    """Production LLM adapter with Google Gemini API and injected TelemetryPort.

    Implements LLMTransformationPort as an Anti-Corruption Layer (ACL), wrapping
    Google GenAI client calls with bounded retries, model failover, thinking_level
    control, and detailed token usage tracking recorded through TelemetryPort.

    Attributes:
        model_name: Primary Gemini model variant.
        fallback_model_name: Optional secondary model variant used if primary fails.
        max_output_tokens: Bounded token ceiling for model generation.
        thinking_level: Reasoning effort level applied to Gemini/Gemma generations.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_GEMINI_MODEL,
        fallback_model_name: str | None = DEFAULT_GEMINI_FALLBACK_MODEL,
        max_output_tokens: int = DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
        thinking_level: str | None = DEFAULT_GEMINI_THINKING_LEVEL,
        genai_client: Any | None = None,
        telemetry_port: TelemetryPort | None = None,
        credential_pool: GeminiCredentialPool | None = None,
        api_keys: list[str] | None = None,
        timeout_seconds: float = DEFAULT_GEMINI_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize GeminiLLMAdapter with model configuration and injected TelemetryPort.

        Args:
            api_key: Optional Gemini API key string. If None, SDK looks for GEMINI_API_KEY env.
            model_name: Default Gemini model variant for pipeline stages.
            fallback_model_name: Secondary model variant if primary hits demand spikes or fails.
            max_output_tokens: Maximum token output limit (thinking + response) per generation.
            thinking_level: Reasoning effort level ('minimal', 'low', 'medium', 'high', 'xhigh').
            genai_client: Optional injected GenAI client for testing.
            telemetry_port: Optional injected Hexagonal TelemetryPort (defaults to NoOpTelemetryPort).
            credential_pool: Optional injected GeminiCredentialPool for quota rotation.
            api_keys: Optional list of raw API keys to initialize credential pool.
            timeout_seconds: Socket and request timeout in seconds for GenAI HTTP calls.
        """
        # ACL boundary hygiene: strip optional provider routing prefix ("gemini:")
        self.model_name = model_name.removeprefix("gemini:")
        self.fallback_model_name = (
            fallback_model_name.removeprefix("gemini:") if fallback_model_name is not None else None
        )
        self.max_output_tokens = max_output_tokens
        self.thinking_level = thinking_level
        self.timeout_seconds = timeout_seconds
        self._telemetry: TelemetryPort = telemetry_port or NoOpTelemetryPort()

        if credential_pool is not None:
            self._pool = credential_pool
        elif api_keys is not None and len(api_keys) > 0:
            self._pool = GeminiCredentialPool(keys=api_keys, timeout=timeout_seconds)
        elif genai_client is not None:
            self._pool = GeminiCredentialPool(
                keys=["mock-key"],
                client_factory=lambda _: genai_client,
                timeout=timeout_seconds,
            )
        else:
            raw = api_key or ""
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            self._pool = GeminiCredentialPool(
                keys=parts if parts else [""], timeout=timeout_seconds
            )

    @property
    def _client(self) -> Any:
        """Active leased client from the credential pool."""
        return self._pool.lease()[1]

    def transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        thinking_level: str | None = None,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation contract with primary/fallback failover and TelemetryPort.

        Args:
            prompt: Domain ChatPrompt containing sequential messages and optional system instruction.
            temperature: Deprecated for Gemini 3.5+/4 (ignored; kept for port LSP parity).
            thinking_level: Optional reasoning effort override for this call.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text.
        """
        _ = temperature
        try:
            return self._run_model_generation(
                model=self.model_name,
                prompt=prompt,
                thinking_level=thinking_level,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
                fallback=False,
            )
        except Exception as exc:
            if (
                isinstance(exc, CredentialPoolExhaustedError)
                or is_quota_exhausted_error(exc)
                or not self.fallback_model_name
                or self.fallback_model_name == self.model_name
            ):
                raise
            logger.warning(
                "[GeminiLLMAdapter] Primary model '%s' failed (%s). Failing over to '%s'.",
                self.model_name,
                exc,
                self.fallback_model_name,
            )
            return self._run_model_generation(
                model=self.fallback_model_name,
                prompt=prompt,
                thinking_level=thinking_level,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
                fallback=True,
            )

    def _build_generation_config(
        self,
        model: str,
        system_prompt: str | None,
        thinking_level: str | None,
    ) -> types.GenerateContentConfig:
        """Construct GenerateContentConfig without deprecated sampling parameters."""
        return types.GenerateContentConfig(
            max_output_tokens=self.max_output_tokens,
            system_instruction=system_prompt,
            thinking_config=build_thinking_config(model=model, thinking_level=thinking_level),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    def _run_model_generation(
        self,
        *,
        model: str,
        prompt: ChatPrompt,
        thinking_level: str | None,
        trace_id: str | None,
        session_id: str | None,
        user_id: str | None,
        fallback: bool = False,
    ) -> str:
        """Build GenAI request, invoke credential pool with failover, and record generation span."""
        span_name = resolve_llm_generation_span_name(fallback=fallback)
        requested_thinking_level = self.thinking_level if thinking_level is None else thinking_level
        contents = [
            types.Content(
                role="model" if msg.role == MessageRole.ASSISTANT else "user",
                parts=[types.Part.from_text(text=msg.content)],
            )
            for msg in prompt.messages
        ]
        config = self._build_generation_config(
            model=model,
            system_prompt=prompt.system_prompt,
            thinking_level=requested_thinking_level,
        )

        with self._telemetry.start_span(span_name, kind=SpanKind.GENERATION) as span:
            span.set_input(prompt.to_dict_list())
            response = self._pool.execute_with_failover(
                lambda client: _generate_with_retry(
                    client=client,
                    model=model,
                    contents=contents,
                    config=config,
                )
            )
            response_text = response.text or ""

            usage_meta = getattr(response, "usage_metadata", None)
            total_prompt_words = sum(len(m.content.split()) for m in prompt.messages)
            prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or total_prompt_words
            candidate_tokens = getattr(usage_meta, "candidates_token_count", 0) or len(
                response_text.split()
            )
            raw_thoughts_tokens = getattr(usage_meta, "thoughts_token_count", None)
            thinking_tokens = raw_thoughts_tokens if isinstance(raw_thoughts_tokens, int) else None
            effective_thinking_level = resolve_effective_thinking_level(
                model=model,
                thinking_level=requested_thinking_level,
            )

            span.set_attributes(
                build_genai_attributes(
                    system="google",
                    model=model,
                    prompt_tokens=prompt_tokens,
                    candidate_tokens=candidate_tokens,
                    session_id=session_id,
                    user_id=user_id,
                    trace_id=trace_id,
                    max_tokens=self.max_output_tokens,
                    thinking_level=effective_thinking_level,
                    thinking_tokens=thinking_tokens,
                )
            )
            span.set_output(response_text)
            return response_text
