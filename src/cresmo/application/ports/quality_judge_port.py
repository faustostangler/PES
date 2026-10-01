"""Application Port for Quality Evaluation and Decision-Model Evaluators.

Conforms to:
    - ADR-029: Unified QualityJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: Quality Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from cresmo.domain.value_objects.quality import EvaluationContext, JudgeEvaluation


class QualityJudgePort(ABC):
    """Hexagonal Application Port for semantic quality evaluation and LLM-as-a-Judge."""

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against ground-truth context across required criteria.

        Args:
            context: Immutable evaluation context with candidate and reference text.

        Returns:
            JudgeEvaluation: Immutable evaluation verdict containing scores and pass status.
        """
