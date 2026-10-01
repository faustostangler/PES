"""Langfuse Telemetry Emission Decorator for Quality Judge Evaluations.

Conforms to:
    - ADR-029: Unified QualityJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: Quality Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging
from typing import Any

from cresmo.application.ports.quality_judge_port import QualityJudgePort
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeEvaluation

logger = logging.getLogger(__name__)


class LangfuseJudgeDecorator(QualityJudgePort):
    """Decorator for QualityJudgePort that automatically emits structured scores to Langfuse."""

    def __init__(
        self,
        inner_judge: QualityJudgePort,
        langfuse_client: Any | None = None,
    ) -> None:
        """Initialize Langfuse judge telemetry decorator.

        Args:
            inner_judge: The wrapped QualityJudgePort adapter.
            langfuse_client: Optional Langfuse client instance for telemetry emission.
        """
        self._inner_judge = inner_judge
        self._langfuse_client = langfuse_client

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate using inner judge and emit individual criterion scores to Langfuse."""
        evaluation = self._inner_judge.evaluate(context)

        effective_trace_id = evaluation.trace_id or context.trace_id
        if self._langfuse_client is not None and effective_trace_id:
            for score in evaluation.criteria_scores:
                try:
                    self._langfuse_client.score(
                        trace_id=effective_trace_id,
                        name=score.criterion.value,
                        value=float(score.score),
                        comment=score.reasoning,
                    )
                except Exception as exc:  # noqa: BLE001 - Observability and telemetry errors must never crash pipeline execution
                    logger.warning(
                        "Failed to emit Langfuse score for criterion '%s': %s",
                        score.criterion.value,
                        exc,
                    )

        return evaluation
