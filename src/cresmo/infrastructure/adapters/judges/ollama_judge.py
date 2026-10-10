"""Ollama Local LLM-as-a-Judge Adapter for Offline Fallback Quality Evaluation.

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

import httpx

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    PromptKey,
)
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
from cresmo.infrastructure.config import DEFAULT_JUDGE_PASS_THRESHOLD

logger = logging.getLogger(__name__)

DEFAULT_PASS_THRESHOLD: float = DEFAULT_JUDGE_PASS_THRESHOLD


def _clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


class OllamaJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing local Ollama instance for offline fallback evaluation."""

    def __init__(
        self,
        http_client: Any | None = None,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout_seconds: float = 120.0,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize Ollama judge adapter.

        Args:
            http_client: HTTP client instance (defaults to httpx.Client).
            base_url: Ollama API server base URL.
            model: Model variant running on Ollama.
            timeout_seconds: HTTP request timeout duration.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds
        self._pass_threshold = pass_threshold
        self._client = http_client or httpx.Client(timeout=timeout_seconds)
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using local Ollama model."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.LLM_JUDGE,
            stage_name=context.stage_name,
            criteria_json=json.dumps(criteria_names),
            source_text=context.raw_text,
            candidate_text=context.candidate_text,
        )

        try:
            payload = {
                "model": self._model,
                "messages": chat_prompt.to_dict_list(),
                "format": "json",
                "stream": False,
            }
            resp = self._client.post(f"{self._base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            msg_obj = data.get("message")
            if isinstance(msg_obj, dict):
                raw_text = msg_obj.get("content", "{}")
            else:
                raw_text = data.get("response", "{}")
        except Exception as exc:
            logger.warning("OllamaJudgeAdapter evaluation failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        try:
            parsed = json.loads(_clean_json_markdown(raw_text))
        except json.JSONDecodeError as err:
            logger.error("Failed to parse Ollama judge JSON output: %s", raw_text)
            raise ValueError(f"Ollama returned invalid JSON: {raw_text}") from err

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
            except (ValueError, KeyError) as parse_err:
                logger.debug("Skipping unparseable Ollama criterion item: %s", parse_err)

        overall_score = float(parsed.get("overall_score", 0.0))
        overall_score = max(0.0, min(1.0, overall_score))
        overall_passed = bool(parsed.get("passed", overall_score >= self._pass_threshold))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="ollama",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold

    @property
    def model(self) -> str:
        """Return the model identifier."""
        return self._model


__all__ = [
    "DEFAULT_PASS_THRESHOLD",
    "OllamaJudgeAdapter",
]
