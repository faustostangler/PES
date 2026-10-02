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

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)

logger = logging.getLogger(__name__)


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
    ) -> None:
        """Initialize Ollama judge adapter.

        Args:
            http_client: HTTP client instance (defaults to httpx.Client).
            base_url: Ollama API server base URL.
            model: Model variant running on Ollama.
            timeout_seconds: HTTP request timeout duration.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds
        self._client = http_client or httpx.Client(timeout=timeout_seconds)

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using local Ollama model."""
        start_time = time.perf_counter()
        criteria_names = [c.value for c in context.required_criteria]

        system_instruction = (
            "You are a rigorous Quality Evaluation Judge. Evaluate the candidate text against the source text. "
            "Output ONLY valid JSON with keys: criteria (array of {criterion, score, passed, reasoning}), "
            "overall_score (0.0-1.0), and passed (boolean)."
        )

        user_prompt = (
            f"Stage: {context.stage_name}\n"
            f"Required Criteria: {json.dumps(criteria_names)}\n\n"
            f"--- SOURCE ---\n{context.raw_text}\n\n"
            f"--- CANDIDATE ---\n{context.candidate_text}\n\n"
            "Evaluate and return JSON:"
        )

        try:
            payload = {
                "model": self._model,
                "prompt": user_prompt,
                "system": system_instruction,
                "format": "json",
                "stream": False,
            }
            resp = self._client.post(f"{self._base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
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
                passed_val = bool(item.get("passed", score_val >= 0.8))
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
        overall_passed = bool(parsed.get("passed", overall_score >= 0.8))

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="ollama",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )
