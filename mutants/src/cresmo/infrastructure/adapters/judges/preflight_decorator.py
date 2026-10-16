"""Deterministic Mechanical Preflight Decorator for LLM Judges.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

import logging

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.services.mechanical_validator import (
    validate_fluid_prose_mechanical_invariants,
)
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    VerdictType,
)

logger = logging.getLogger(__name__)


class MechanicalPreflightJudgeDecorator(LlmJudgePort):
    """Decorator executing deterministic syntactic validation before delegating to LLM judges."""

    def __init__(self, inner_judge: LlmJudgePort) -> None:
        """Initialize decorator.

        Args:
            inner_judge: Wrapped LlmJudgePort instance.
        """
        self._inner_judge = inner_judge

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Short-circuit evaluation if deterministic mechanical invariants fail."""
        # Layer 1: Check mechanical syntax for fluid_prose stage
        if context.stage_name == "fluid_prose":
            violations = validate_fluid_prose_mechanical_invariants(context.candidate_text)
            if violations:
                violations_msg = "; ".join(violations)
                logger.info(
                    "[MechanicalPreflight] Candidate failed syntactic invariants: %s",
                    violations_msg,
                )
                criterion_score = CriterionScore(
                    criterion=JudgeCriterion.STRUCTURAL_COMPLIANCE,
                    score=0.0,
                    passed=False,
                    reasoning=f"Mechanical invariants failed: {violations_msg}",
                    verdict_type=VerdictType.NOUL,
                    improvement_suggestion=f"Fix syntax errors: {violations_msg}",
                )
                return JudgeEvaluation(
                    target_stage=context.stage_name,
                    passed=False,
                    overall_score=0.0,
                    criteria_scores=(criterion_score,),
                    provider="mechanical_preflight",
                    latency_ms=0.1,
                    trace_id=context.trace_id,
                )

        # Layer 2: Delegate to underlying LLM judge
        return self._inner_judge.evaluate(context)
