"""Gemini LLM-as-a-Judge Adapter for Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from google import genai
from google.genai import errors, types
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    MessageRole,
    PromptKey,
)
from cresmo.infrastructure.adapters.gemini_pool import (
    GeminiCredentialPool,
    is_quota_exhausted_error,
)
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
from cresmo.infrastructure.config import (
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    DEFAULT_JUDGE_TEMPERATURE,
)

logger = logging.getLogger(__name__)

DEFAULT_PASS_THRESHOLD: float = DEFAULT_JUDGE_PASS_THRESHOLD
DEFAULT_MODEL: str = DEFAULT_JUDGE_GEMINI_MODEL
DEFAULT_TEMPERATURE: float = DEFAULT_JUDGE_TEMPERATURE


def _clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def _is_transient_genai_error(exc: BaseException) -> bool:
    """Determine if a Gemini API exception represents a temporary, retryable condition (e.g. 429)."""
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
            "RESOURCE_EXHAUSTED",
            "high demand",
            "rate limit",
            "quota",
            "Connection reset",
        )
    )


def _is_transient_cluster_error(exc: BaseException) -> bool:
    """Determine if an exception represents a retryable 5xx or cluster network condition.

    CRITICAL INVARIANT (ADR-041 §2.3):
    HTTP 429 (quota exhaustion) is NOT retried here because it must immediately trigger
    credential rotation via GeminiCredentialPool.
    """
    if is_quota_exhausted_error(exc):
        return False
    return _is_transient_genai_error(exc)


@retry(
    retry=retry_if_exception(_is_transient_cluster_error),
    wait=wait_random_exponential(min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _generate_content_with_retry(
    client: Any,
    model: str,
    contents: Any,
    config: Any,
) -> Any:
    """Generate content with automatic exponential backoff for transient cluster errors (5xx)."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )


class GeminiJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing Google Gemini API with structured outputs."""

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt_provider: PromptProviderPort | None = None,
        credential_pool: GeminiCredentialPool | None = None,
        api_keys: list[str] | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            temperature: Sampling temperature for deterministic generation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
            credential_pool: Optional injected GeminiCredentialPool for quota rotation.
            api_keys: Optional list of raw API keys to initialize credential pool.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._pass_threshold = pass_threshold
        self._temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

        # Initialize credential pool if configured
        self._pool: GeminiCredentialPool | None = None
        if credential_pool is not None:
            self._pool = credential_pool
        elif api_keys is not None and len(api_keys) > 0:
            self._pool = GeminiCredentialPool(keys=api_keys)
        elif client is not None:
            self._pool = GeminiCredentialPool(
                keys=["mock-key"],
                client_factory=lambda _: client,
            )
        elif api_key:
            parts = [p.strip() for p in api_key.split(",") if p.strip()]
            self._pool = GeminiCredentialPool(keys=parts if parts else [api_key])

    @property
    def client(self) -> Any:
        """Lazy-instantiate the Google GenAI client."""
        if self._pool is not None:
            return self._pool.lease()[1]
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "Gemini API key must be provided explicitly via api_key or client. "
                    "Bypassing Pydantic Settings via direct os.getenv is prohibited (ADR-026 Rule 9)."
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        prompt_key = (
            PromptKey.JUDGE_GAP_FILLER
            if context.stage_name == "gap_filler"
            else PromptKey.LLM_JUDGE
        )
        chat_prompt = self._prompt_provider.get_prompt(
            prompt_key,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=self._temperature,
                system_instruction=chat_prompt.system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            contents = [
                types.Content(
                    role="model" if m.role == MessageRole.ASSISTANT else "user",
                    parts=[types.Part.from_text(text=m.content)],
                )
                for m in chat_prompt.messages
            ]

            def _do_generate(active_client: Any) -> Any:
                return _generate_content_with_retry(
                    client=active_client,
                    model=self._model,
                    contents=contents,
                    config=config,
                )

            if self._pool is not None:
                response = self._pool.execute_with_failover(_do_generate)
            else:
                response = _do_generate(self.client)

            raw_response_text = response.text or "{}"
        except Exception as exc:
            # Re-raise to trigger resilient composite failover
            logger.warning("GeminiJudgeAdapter invocation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_response_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Gemini judge response as JSON: %s", raw_response_text)
            raise ValueError(f"Gemini judge returned non-JSON output: {raw_response_text}") from err

        criteria_scores_list: list[CriterionScore] = []
        for item in parsed.get("criteria", []):
            try:
                crit_enum = JudgeCriterion(item["criterion"])
                score_val = max(0.0, min(1.0, float(item["score"])))
                passed_val = bool(item.get("passed", score_val >= self._pass_threshold))
                criteria_scores_list.append(
                    CriterionScore(
                        criterion=crit_enum,
                        score=score_val,
                        passed=passed_val,
                        reasoning=str(item.get("reasoning", "")),
                    )
                )
            except (ValueError, KeyError) as parse_item_err:
                logger.debug("Skipping unparseable judge criterion item: %s", parse_item_err)

        return JudgeEvaluation.create_with_composite_verdict(
            target_stage=context.stage_name,
            criteria_scores=criteria_scores_list,
            provider="gemini",
            pass_threshold=self._pass_threshold,
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold

    @property
    def temperature(self) -> float:
        """Return the sampling temperature."""
        return self._temperature

    @property
    def model(self) -> str:
        """Return the model identifier."""
        return self._model


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_PASS_THRESHOLD",
    "DEFAULT_TEMPERATURE",
    "GeminiJudgeAdapter",
]
