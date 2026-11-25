"""Gemini LLM-as-a-Judge Adapter for Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from typing import Any

import structlog
from google.genai import types

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    ChatPrompt,
    EvaluationContext,
    JudgeEvaluation,
    MessageRole,
)
from cresmo.infrastructure.adapters.judges.criterion_parser import JudgeResponseOutputSchema
from cresmo.infrastructure.adapters.judges.prompt_judge_runner import evaluate_prompt_judge
from cresmo.infrastructure.adapters.llm.gemini_common import (
    build_thinking_config,
    execute_with_model_failover,
    generate_content_with_retry,
)
from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.config import (
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
)

logger = structlog.get_logger(__name__)


class GeminiJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing Google Gemini API with structured outputs."""

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_JUDGE_GEMINI_MODEL,
        fallback_model: str | None = DEFAULT_GEMINI_FALLBACK_MODEL,
        pass_threshold: float = DEFAULT_JUDGE_PASS_THRESHOLD,
        thinking_level: str | None = DEFAULT_GEMINI_THINKING_LEVEL,
        max_output_tokens: int = DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
        prompt_provider: PromptProviderPort | None = None,
        credential_pool: GeminiCredentialPool | None = None,
        api_keys: list[str] | None = None,
        timeout_seconds: float = DEFAULT_GEMINI_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            fallback_model: Secondary Gemini model name used if primary fails after retries.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            thinking_level: Reasoning effort level ('minimal', 'low', 'medium', 'high', 'xhigh').
            max_output_tokens: Bounded token ceiling (thinking + JSON output).
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
            credential_pool: Optional injected GeminiCredentialPool for quota rotation.
            api_keys: Optional list of raw API keys to initialize credential pool.
            timeout_seconds: Socket and request timeout in seconds for GenAI HTTP calls.
        """
        # ACL boundary hygiene: strip optional provider routing prefix ("gemini:")
        self._model = model.removeprefix("gemini:")
        self._fallback_model = (
            fallback_model.removeprefix("gemini:") if fallback_model is not None else None
        )
        self._pass_threshold = pass_threshold
        self._thinking_level = thinking_level
        self._max_output_tokens = max_output_tokens
        self._prompt_provider = prompt_provider or JsonPromptProvider()

        # Initialize credential pool if configured
        self._pool: GeminiCredentialPool | None = None
        if credential_pool is not None:
            self._pool = credential_pool
        elif api_keys is not None and len(api_keys) > 0:
            self._pool = GeminiCredentialPool(keys=api_keys, timeout=timeout_seconds)
        elif client is not None:
            self._pool = GeminiCredentialPool(
                keys=["mock-key"],
                client_factory=lambda _: client,
                timeout=timeout_seconds,
            )
        elif api_key:
            parts = [p.strip() for p in api_key.split(",") if p.strip()]
            self._pool = GeminiCredentialPool(
                keys=parts if parts else [api_key], timeout=timeout_seconds
            )

    @property
    def client(self) -> Any:
        """Return an active leased Google GenAI client from the credential pool."""
        if self._pool is not None:
            return self._pool.lease()[1]
        raise ValueError(
            "Gemini API key must be provided explicitly via api_key or client. "
            "Bypassing Pydantic Settings via direct os.getenv is prohibited (ADR-026 Rule 9)."
        )

    def _invoke_gemini(self, chat_prompt: ChatPrompt) -> str:
        contents = [
            types.Content(
                role="model" if m.role == MessageRole.ASSISTANT else "user",
                parts=[types.Part.from_text(text=m.content)],
            )
            for m in chat_prompt.messages
        ]
        return execute_with_model_failover(
            primary_model=self._model,
            fallback_model=self._fallback_model,
            adapter_label="GeminiJudgeAdapter",
            operation=lambda target_model, _is_fallback: self._invoke_model(
                model=target_model,
                system_instruction=chat_prompt.system_prompt,
                contents=contents,
            ),
        )

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        return evaluate_prompt_judge(
            context=context,
            prompt_provider=self._prompt_provider,
            pass_threshold=self._pass_threshold,
            provider_name="gemini",
            invoke_llm=self._invoke_gemini,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold

    @property
    def thinking_level(self) -> str | None:
        """Return the configured thinking effort level."""
        return self._thinking_level

    @property
    def max_output_tokens(self) -> int:
        """Return the configured max output tokens ceiling."""
        return self._max_output_tokens

    def _invoke_model(
        self,
        *,
        model: str,
        system_instruction: str | None,
        contents: list[types.Content],
    ) -> str:
        """Build model-specific config and invoke GenAI with credential pool failover."""
        config = types.GenerateContentConfig(
            max_output_tokens=self._max_output_tokens,
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=JudgeResponseOutputSchema,
            thinking_config=build_thinking_config(
                model=model,
                thinking_level=self._thinking_level,
            ),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        def _do_generate(active_client: Any) -> Any:
            return generate_content_with_retry(
                client=active_client,
                model=model,
                contents=contents,
                config=config,
            )

        if self._pool is not None:
            response = self._pool.execute_with_failover(_do_generate)
        else:
            response = _do_generate(self.client)
        return str(response.text or "{}")

    @property
    def model(self) -> str:
        """Return the model identifier."""
        return self._model

    @property
    def fallback_model(self) -> str | None:
        """Return the secondary fallback model identifier, if configured."""
        return self._fallback_model


__all__ = [
    "GeminiJudgeAdapter",
]
