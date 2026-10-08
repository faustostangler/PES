"""Resilient Composite Judge Adapter Implementing Automatic Fallback.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeEvaluation

logger = logging.getLogger(__name__)


class ResilientCompositeJudgeAdapter(LlmJudgePort):
    """Resilient composite adapter that fails over to a secondary judge when primary fails."""

    def __init__(
        self,
        primary: LlmJudgePort,
        fallback: LlmJudgePort,
    ) -> None:
        """Initialize composite adapter with primary and fallback providers.

        Args:
            primary: Primary LlmJudgePort adapter (e.g. GeminiJudgeAdapter).
            fallback: Fallback LlmJudgePort adapter (e.g. OllamaJudgeAdapter).
        """
        self._primary = primary
        self._fallback = fallback

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate with primary adapter, falling back to secondary upon failure."""
        try:
            return self._primary.evaluate(context)
        except Exception as exc:  # noqa: BLE001 - Resilience circuit failover must intercept any provider anomaly
            logger.warning(
                "Primary quality judge failed (%s: %s). Activating fallback judge for stage '%s'.",
                type(exc).__name__,
                exc,
                context.stage_name,
            )
            return self._fallback.evaluate(context)
