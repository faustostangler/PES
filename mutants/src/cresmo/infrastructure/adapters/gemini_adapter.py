"""Production LLM adapter integrating Google Gemini API and Langfuse Observability.

Adheres to EVAL-001 rubrics and stangler-surgery telemetry standards, capturing
prompt versions, trace IDs, latency, token counts, and structured outputs. Acts
as an Anti-Corruption Layer (ACL) shielding the domain core from vendor-specific
types and transient HTTP 429/503 network anomalies.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-003: PES Production Architecture & Telemetry
    - EVAL-001: LLM Synthesis Evaluation Rubrics
"""

from __future__ import annotations

import logging
import os
from typing import Any

from google import genai
from google.genai import errors, types
from langfuse import Langfuse, observe
from opentelemetry import trace
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from cresmo.application.ports import LLMTransformationPort
from cresmo.domain.value_objects import ChatPrompt, MessageRole
from cresmo.infrastructure.adapters.opentelemetry_adapter import annotate_llm_span

__all__ = ["GeminiLLMAdapter", "trace"]

logger = logging.getLogger(__name__)


def _is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition.

    Args:
        exc: Raised base exception to inspect.

    Returns:
        True if the exception corresponds to an HTTP 429, 5xx, or transient network error;
        False otherwise.
    """
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in (429, 500, 502, 503, 504)
    msg = str(exc)
    return any(
        pattern in msg
        for pattern in (
            "503",
            "429",
            "UNAVAILABLE",
            "ResourceExhausted",
            "high demand",
            "rate limit",
            "Connection reset",
        )
    )


@retry(
    retry=retry_if_exception(_is_transient_genai_error),
    wait=wait_random_exponential(min=2, max=20),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _generate_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Execute model content generation with exponential backoff on transient errors.

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
    """Production LLM adapter with Google Gemini API and Langfuse telemetry.

    Implements LLMTransformationPort as an Anti-Corruption Layer (ACL), wrapping
    Google GenAI client calls with exponential retries, model failover, and
    detailed token usage tracking sent to Langfuse.

    Attributes:
        model_name: Primary Gemini model variant.
        fallback_model_name: Optional secondary model variant used if primary fails.
        max_output_tokens: Bounded token ceiling for model generation.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
        default_temperature: float = 0.2,
    ) -> None:
        """Initialize GeminiLLMAdapter with model configuration and telemetry clients.

        Args:
            api_key: Optional Gemini API key string. If None, SDK looks for GEMINI_API_KEY env.
            model_name: Default Gemini model variant for pipeline stages.
            fallback_model_name: Secondary model variant if primary hits quota or demand spikes.
            max_output_tokens: Maximum token output limit per generation.
            genai_client: Optional injected GenAI client for testing.
            langfuse_client: Optional injected Langfuse client for testing.
            default_temperature: Default generation sampling temperature when not overridden.
        """
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens
        self.default_temperature = default_temperature

        # Step 1: Initialize Langfuse client if configured
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    def transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation contract with immediate Langfuse telemetry synchronization.

        Args:
            prompt: Domain ChatPrompt containing sequential messages and optional system instruction.
            temperature: Generation sampling temperature.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text.
        """
        response_text = self._execute_transform(
            prompt=prompt,
            temperature=temperature,
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
        )

        client = self._langfuse
        if client is None:
            try:
                from langfuse import get_client

                client = get_client()
            except Exception:  # noqa: BLE001
                client = None

        if client is not None:
            try:
                client.flush()
            except Exception as exc:  # noqa: BLE001
                logger.debug("[GeminiLLMAdapter] Langfuse flush skipped: %s", exc)

        return response_text

    # Trace level 3: cresmo.llm.generate
    @observe(name="cresmo.llm.generate", as_type="generation")
    def _execute_transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Internal worker executing model generation within an active Langfuse generation observation."""
        effective_temperature = self.default_temperature if temperature is None else temperature
        config = types.GenerateContentConfig(
            temperature=effective_temperature,
            max_output_tokens=self.max_output_tokens,
            system_instruction=prompt.system_instruction,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        contents: list[types.Content] = []
        for msg in prompt.messages:
            role = "model" if msg.role == MessageRole.ASSISTANT else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)],
                )
            )

        active_model = self.model_name
        try:
            response = _generate_with_retry(
                client=self._client,
                model=active_model,
                contents=contents,
                config=config,
            )
        except Exception:
            if self.fallback_model_name and self.fallback_model_name != self.model_name:
                active_model = self.fallback_model_name
                response = _generate_with_retry(
                    client=self._client,
                    model=active_model,
                    contents=contents,
                    config=config,
                )
            else:
                raise

        response_text = response.text or ""

        # Extract usage metadata
        usage_meta = getattr(response, "usage_metadata", None)
        total_prompt_words = sum(len(m.content.split()) for m in prompt.messages)
        prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or total_prompt_words
        candidate_tokens = getattr(usage_meta, "candidates_token_count", 0) or len(
            response_text.split()
        )

        # OpenTelemetry GenAI Semantic Conventions & Langfuse span decoration
        annotate_llm_span(
            system="google",
            model=active_model,
            prompt_tokens=prompt_tokens,
            candidate_tokens=candidate_tokens,
            session_id=session_id,
            user_id=user_id,
            trace_id=trace_id,
            temperature=effective_temperature,
            max_tokens=self.max_output_tokens,
        )

        return response_text
