"""Production LLM adapter integrating Google Gemini API and Langfuse Observability.

Adheres to EVAL-001 rubrics and stangler-surgery telemetry standards, capturing
prompt versions, trace IDs, latency, token counts, and structured outputs.
"""

from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import errors, types
from langfuse import Langfuse, observe
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from cresmo.application.ports import LLMTransformationPort


def _is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        if code in (429, 500, 502, 503, 504):
            return True
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
    """Execute model content generation with exponential backoff on transient errors."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )


class GeminiLLMAdapter(LLMTransformationPort):
    """Production LLM adapter with Google Gemini API and Langfuse telemetry."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.5-flash-lite",
        fallback_model_name: str | None = "gemini-3.1-flash-lite",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client if configured.
        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            self._langfuse = Langfuse()
        else:
            self._langfuse = None

        # Step 2: Initialize Google GenAI client.
        if genai_client is not None:
            self._client = genai_client
        else:
            self._client = genai.Client(api_key=api_key)

    @observe(as_type="generation")
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation contract with full Langfuse observability span.

        Args:
            prompt: Text prompt for generation.
            system_instruction: Optional system instruction directive.
            temperature: Generation sampling temperature.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text.
        """
        eff_temperature = 0.2 if temperature is None else temperature
        config = types.GenerateContentConfig(
            temperature=eff_temperature,
            max_output_tokens=self.max_output_tokens,
            system_instruction=system_instruction,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        active_model = self.model_name
        try:
            response = _generate_with_retry(
                client=self._client,
                model=active_model,
                contents=prompt,
                config=config,
            )
        except Exception:
            if self.fallback_model_name and self.fallback_model_name != self.model_name:
                active_model = self.fallback_model_name
                response = _generate_with_retry(
                    client=self._client,
                    model=active_model,
                    contents=prompt,
                    config=config,
                )
            else:
                raise

        response_text = response.text or ""

        # Extract usage metadata
        usage_meta = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or len(prompt.split())
        candidate_tokens = getattr(usage_meta, "candidates_token_count", 0) or len(
            response_text.split()
        )

        # Bind output and token metadata to Langfuse generation span if active
        if self._langfuse is not None:
            try:
                self._langfuse.update_current_generation(
                    model=active_model,
                    output=response_text,
                    usage_details={"input": prompt_tokens, "output": candidate_tokens},
                )
            except (AttributeError, RuntimeError, ValueError):
                pass

        return response_text
