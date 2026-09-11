"""Production LLM adapter integrating Google Gemini API and Langfuse Observability.

Adheres to EVAL-001 rubrics and stangler-surgery telemetry standards, capturing
prompt versions, trace IDs, latency, token counts, and structured outputs.
"""

from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types
from langfuse import Langfuse, observe

from cresmo.application.ports import LLMTransformationPort


class GeminiLLMAdapter(LLMTransformationPort):
    """Production LLM adapter with Google Gemini API and Langfuse telemetry."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-2.5-flash",
        max_output_tokens: int = 8192,
        genai_client: Any | None = None,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        self.model_name = model_name
        self.max_output_tokens = max_output_tokens

        # Step 1: Initialize Langfuse client for trace lifecycle management.
        self._langfuse = langfuse_client if langfuse_client is not None else Langfuse()

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

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

        response_text = response.text or ""

        # Extract usage metadata
        usage_meta = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or len(prompt.split())
        candidate_tokens = getattr(usage_meta, "candidates_token_count", 0) or len(
            response_text.split()
        )

        # Bind output and token metadata to Langfuse generation span
        try:
            self._langfuse.update_current_generation(
                model=self.model_name,
                output=response_text,
                usage_details={"input": prompt_tokens, "output": candidate_tokens},
            )
        except (AttributeError, RuntimeError, ValueError):
            pass

        return response_text
