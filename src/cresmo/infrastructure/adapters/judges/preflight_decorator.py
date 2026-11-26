"""Deterministic Mechanical Preflight Decorator for LLM Judges.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import structlog

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.services.prose_syntax_guard import (
    validate_expanded_prose_syntax,
    validate_fluid_prose_syntax,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)

logger = structlog.get_logger(__name__)

_PREFLIGHT_VIOLATION_SEPARATOR: Final[str] = "; "
_PREFLIGHT_FAILURE_SCORE: Final[float] = 0.0
_PREFLIGHT_PROVIDER_NAME: Final[str] = "mechanical_preflight"
_PREFLIGHT_NOMINAL_LATENCY_MS: Final[float] = 0.1

_STAGE_PREFLIGHT_VALIDATORS: Final[dict[str, tuple[Callable[[str], list[str]], JudgeCriterion]]] = {
    StageName.FLUID_PROSE: (validate_fluid_prose_syntax, JudgeCriterion.STRUCTURAL_COMPLIANCE),
    StageName.GAP_FILLER: (validate_expanded_prose_syntax, JudgeCriterion.EXTRA_INFO_GRANULARITY),
    StageName.LONG_EXPANDER: (
        validate_expanded_prose_syntax,
        JudgeCriterion.EXTRA_INFO_GRANULARITY,
    ),
    StageName.WIDE_EXPANDER: (
        validate_expanded_prose_syntax,
        JudgeCriterion.EXTRA_INFO_GRANULARITY,
    ),
}


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
        stage_rule = _STAGE_PREFLIGHT_VALIDATORS.get(context.stage_name)
        if stage_rule is not None:
            validator_fn, criterion = stage_rule
            violations = validator_fn(context.candidate_text)
            if violations:
                violations_msg = _PREFLIGHT_VIOLATION_SEPARATOR.join(violations)
                logger.info(
                    "[MechanicalPreflight] Candidate failed syntactic invariants for %s: %s",
                    context.stage_name,
                    violations_msg,
                )
                criterion_score = CriterionScore(
                    criterion=criterion,
                    score=_PREFLIGHT_FAILURE_SCORE,
                    passed=False,
                    reasoning=f"Mechanical invariants failed: {violations_msg}",
                    improvement_suggestion=f"Fix syntax errors: {violations_msg}",
                )
                return JudgeEvaluation(
                    target_stage=context.stage_name,
                    passed=False,
                    overall_score=_PREFLIGHT_FAILURE_SCORE,
                    criteria_scores=(criterion_score,),
                    provider=_PREFLIGHT_PROVIDER_NAME,
                    latency_ms=_PREFLIGHT_NOMINAL_LATENCY_MS,
                    trace_id=context.trace_id,
                )

        # Layer 2: Delegate to underlying LLM judge
        return self._inner_judge.evaluate(context)
