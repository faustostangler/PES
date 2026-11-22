"""Hexagonal Telemetry Emission Decorator for LLM Judge Evaluations.

Conforms to:
- ADR-029: Unified LlmJudgePort and Resilient Multi-Provider Adapters
- ADR-036: Clean Telemetry Namespacing & Observation Binding
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

import structlog

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.application.ports.telemetry import NoOpTelemetryPort, TelemetryPort
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeEvaluation

logger = structlog.get_logger(__name__)


class TelemetryJudgeDecorator(LlmJudgePort):
    """Decorator for LlmJudgePort emitting structured criterion scores through TelemetryPort."""

    def __init__(
        self,
        inner_judge: LlmJudgePort,
        telemetry_port: TelemetryPort | None = None,
    ) -> None:
        """Initialize judge telemetry decorator with injected TelemetryPort."""
        self._inner_judge = inner_judge
        self._telemetry: TelemetryPort = telemetry_port or NoOpTelemetryPort()

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate via inner judge and emit stage-namespaced scores through TelemetryPort."""
        evaluation = self._inner_judge.evaluate(context)
        effective_trace_id = evaluation.trace_id or context.trace_id
        if not effective_trace_id:
            return evaluation

        for score in evaluation.criteria_scores:
            score_name = (
                f"{context.stage_name}.{score.criterion.value}"
                if context.stage_name
                else score.criterion.value
            )
            try:
                self._telemetry.record_score(
                    name=score_name,
                    value=float(score.score),
                    comment=score.reasoning,
                    trace_id=effective_trace_id,
                    observation_id=context.observation_id,
                )
            except Exception as exc:  # noqa: BLE001 - Observability errors must never crash pipeline
                logger.warning(
                    "Failed to emit telemetry score for criterion '%s': %s",
                    score.criterion.value,
                    exc,
                )

        return evaluation
