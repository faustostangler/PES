"""TypeSafe AI (System One Jev) Decision-Model Evaluator Adapter.

Conforms to:
    - ADR-029: Unified QualityJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: Quality Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from cresmo.application.ports.quality_judge_port import QualityJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)

logger = logging.getLogger(__name__)


class TypeSafeJudgeAdapter(QualityJudgePort):
    """Quality judge adapter utilizing TypeSafe AI (System One Jev) Decision Models."""

    def __init__(
        self,
        http_client: Any | None = None,
        api_key: str = "",
        model: str = "jev-latest",
        base_url: str = "https://api.typesafe.ai/v1",
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize TypeSafe AI judge adapter.

        Args:
            http_client: HTTP client instance (defaults to httpx.Client).
            api_key: TypeSafe AI authentication bearer token.
            model: Model identifier (e.g. 'jev-latest').
            base_url: API endpoint URL.
            timeout_seconds: HTTP timeout duration.
        """
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._client = http_client or httpx.Client(timeout=timeout_seconds)

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using TypeSafe System One Jev."""
        start_time = time.perf_counter()

        questions_payload: dict[str, Any] = {}
        for criterion in context.required_criteria:
            if criterion == JudgeCriterion.ORALITY_REMOVAL:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Are all oralities, verbal crutches, and conversational filler words purged from the candidate text?"
                    ),
                }
            elif criterion == JudgeCriterion.NER_PRESERVATION:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Are all proper names, entities, and technical terms accurately preserved and correctly spelled?"
                    ),
                }
            elif criterion == JudgeCriterion.STRUCTURAL_COMPLIANCE:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Is the candidate text continuous Markdown prose without forbidden tables or stray sections?"
                    ),
                }
            elif criterion == JudgeCriterion.SEMANTIC_FAITHFULNESS:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "How faithfully does the candidate text represent the facts and arguments of the source text?"
                    ),
                    "criteria": [
                        "significant distortions or fabrications",
                        "minor discrepancies or omissions",
                        "completely faithful and grounded",
                    ],
                }
            elif criterion == JudgeCriterion.INVENTORY_COHERENCE:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": "How coherent, complete, and well-structured is the atomic entity inventory?",
                    "criteria": [
                        "incomplete or incoherent",
                        "partially coherent with gaps",
                        "fully coherent and complete",
                    ],
                }
            elif criterion == JudgeCriterion.INDEX_SYNTHESIS_QUALITY:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": "How precise, dense, and paratactic is the raw catalog index entry?",
                    "criteria": [
                        "insufficient density or accuracy",
                        "acceptable density",
                        "exemplary paratactic synthesis",
                    ],
                }

        state_payload = {
            "source_raw": context.raw_text,
            "candidate_output": context.candidate_text,
            "stage": context.stage_name,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._model,
            "state": state_payload,
            "questions": questions_payload,
        }

        try:
            resp = self._client.post(
                f"{self._base_url}/system-one",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("TypeSafeJudgeAdapter evaluation request failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        nouls = data.get("nouls", {})
        scores = data.get("scores", {})

        criteria_scores_list: list[CriterionScore] = []
        for criterion in context.required_criteria:
            c_name = criterion.value
            score_val = 0.0
            confidence_val: float | None = None
            passed_val = False

            if c_name in nouls:
                noul_item = nouls[c_name]
                score_val = float(noul_item.get("noul", 0.0))
                passed_val = score_val >= 0.8
            elif c_name in scores:
                score_item = scores[c_name]
                score_val = float(score_item.get("score", 0.0))
                confidence_val = score_item.get("confidence")
                if confidence_val is not None:
                    confidence_val = float(confidence_val)
                passed_val = score_val >= 0.8
            else:
                score_val = 0.5
                passed_val = False

            score_val = max(0.0, min(1.0, score_val))
            if confidence_val is not None:
                confidence_val = max(0.0, min(1.0, confidence_val))

            criteria_scores_list.append(
                CriterionScore(
                    criterion=criterion,
                    score=score_val,
                    passed=passed_val,
                    confidence=confidence_val,
                    reasoning=f"System One Jev evaluation for {c_name}",
                )
            )

        if criteria_scores_list:
            overall_score = sum(c.score for c in criteria_scores_list) / len(criteria_scores_list)
        else:
            overall_score = 1.0

        overall_passed = (
            all(c.passed for c in criteria_scores_list) if criteria_scores_list else True
        )

        return JudgeEvaluation(
            target_stage=context.stage_name,
            passed=overall_passed,
            overall_score=overall_score,
            criteria_scores=tuple(criteria_scores_list),
            provider="typesafe",
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )
