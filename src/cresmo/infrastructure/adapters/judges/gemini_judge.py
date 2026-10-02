"""Gemini LLM-as-a-Judge Adapter for Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

from google import genai
from google.genai import types

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    PromptKey,
)

logger = logging.getLogger(__name__)


def _clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


class GeminiJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing Google Gemini API with structured outputs."""

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str = "gemini-3.5-flash-lite",
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize the Gemini judge adapter.

        Args:
            client: Pre-configured Google GenAI client instance.
            api_key: Google Gemini API key string.
            model: Gemini model name for evaluation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._model = model
        self._api_key = api_key
        self._client = client
        self._prompt_provider = prompt_provider

    @property
    def client(self) -> Any:
        """Lazy-instantiate the Google GenAI client."""
        if self._client is None:
            resolved_key = self._api_key or os.getenv("GEMINI_API_KEY", "")
            self._client = genai.Client(api_key=resolved_key)
        return self._client

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text across requested criteria."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        provider = self._prompt_provider
        if provider is None:
            from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

            provider = JsonPromptProvider()
            self._prompt_provider = provider

        system_instruction, user_prompt = provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            config = types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=system_instruction,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=config,
            )
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
                passed_val = bool(item.get("passed", score_val >= 0.8))
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

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= 0.8))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="gemini",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )
