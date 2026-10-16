"""Langfuse Telemetry Emission Decorator for LLM Judge Evaluations.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging
from typing import Any

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeEvaluation

logger = logging.getLogger(__name__)


class LangfuseJudgeDecorator(LlmJudgePort):
    """Decorator for LlmJudgePort that automatically emits structured scores to Langfuse."""

    def __init__(
        self,
        inner_judge: LlmJudgePort,
        langfuse_client: Any | None = None,
    ) -> None:
        """Initialize Langfuse judge telemetry decorator.

        Args:
            inner_judge: The wrapped LlmJudgePort adapter.
            langfuse_client: Optional Langfuse client instance for telemetry emission.
        """
        self._inner_judge = inner_judge
        self._langfuse_client = langfuse_client

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate using inner judge and emit individual criterion scores to Langfuse."""
        evaluation = self._inner_judge.evaluate(context)

        effective_trace_id = evaluation.trace_id or context.trace_id
        if self._langfuse_client is not None and effective_trace_id:
            score_fn = getattr(self._langfuse_client, "create_score", None) or getattr(
                self._langfuse_client, "score", None
            )
            for score in evaluation.criteria_scores:
                try:
                    if score_fn is not None:
                        # Clean Telemetry (ADR-036): Stage-namespaced metric + observation_id binding
                        score_name = (
                            f"{context.stage_name}.{score.criterion.value}"
                            if context.stage_name
                            else score.criterion.value
                        )
                        score_kwargs: dict[str, Any] = {
                            "trace_id": effective_trace_id,
                            "name": score_name,
                            "value": float(score.score),
                            "comment": score.reasoning,
                        }
                        if context.observation_id:
                            score_kwargs["observation_id"] = context.observation_id

                        score_fn(**score_kwargs)
                except Exception as exc:  # noqa: BLE001 - Observability and telemetry errors must never crash pipeline execution
                    logger.warning(
                        "Failed to emit Langfuse score for criterion '%s': %s",
                        score.criterion.value,
                        exc,
                    )

            try:
                if hasattr(self._langfuse_client, "flush"):
                    self._langfuse_client.flush()
            except Exception as exc:  # noqa: BLE001
                logger.debug("Failed to flush Langfuse telemetry: %s", exc)

        return evaluation
