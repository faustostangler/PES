"""Domain Value Objects for Quality Evaluation and Decision-Model Evaluators.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cresmo.domain.exceptions import DomainValidationError


class JudgeCriterion(str, Enum):
    """Canonical semantic criteria for stage quality evaluation."""

    # Stage 1: Fluid Prose Criteria
    ORALITY_REMOVAL = "orality_removal"
    SEMANTIC_FAITHFULNESS = "semantic_faithfulness"
    NER_PRESERVATION = "ner_preservation"
    STRUCTURAL_COMPLIANCE = "structural_compliance"
    EPISTEMIC_CRITIQUE = "epistemic_critique"
    AUTHORIAL_VOICE = "authorial_voice"

    # Stage 2: Specialized Gap Filler Criteria
    FACTUAL_GROUNDING = "factual_grounding"
    SOCRATIC_EPISTEMIC_DEPTH = "socratic_epistemic_depth"
    CAUSAL_STRATIFICATION_AGENCY = "causal_stratification_agency"
    COMPLEMENTARY_SUBSTANCE = "complementary_substance"
    AUTHORIAL_NATURALISM = "authorial_naturalism"
    EPISTEMIC_SATURATION = "epistemic_saturation"

    # Downstream Stages
    INVENTORY_COHERENCE = "inventory_coherence"
    INDEX_SYNTHESIS_QUALITY = "index_synthesis_quality"


class VerdictType(str, Enum):
    """Canonical evaluation return types conforming to decision-model primitives (ADR-031)."""

    NOUL = "noul"  # Boolean / Binary assertion (TypeSafe System One / Jev primitive)
    CHOICE = "choice"  # Categorical selection among defined options
    SCORE = "score"  # Scaled numeric rating bounded in [0.0, 1.0]


@dataclass(frozen=True, slots=True)
class CandidateText:
    """Strongly-typed Value Object encapsulating raw intermediate LLM transformation outputs.

    Attributes:
        text: Intermediate generated response text.
        stage_name: Associated pipeline stage identifier.
        metadata: Stage execution provenance and generative parameters.
    """

    text: str
    stage_name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate CandidateText construction invariants."""
        if not self.text.strip():
            raise DomainValidationError(
                f"CandidateText for '{self.stage_name}' cannot be empty or whitespace."
            )
        if not self.stage_name.strip():
            raise DomainValidationError("CandidateText stage_name cannot be empty or whitespace.")


@dataclass(frozen=True, slots=True)
class TypedVerdict:
    """Strongly-typed criterion evaluation verdict with confidence and actionable critique."""

    criterion: JudgeCriterion
    verdict_type: VerdictType
    passed: bool
    score: float
    choice_value: str | None = None
    confidence: float | None = None
    reasoning: str = ""
    improvement_suggestion: str = ""

    def __post_init__(self) -> None:
        """Validate typed verdict invariants."""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got: {self.score}")
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0 if provided, got: {self.confidence}"
            )


@dataclass(frozen=True, slots=True)
class CriterionScore:
    """Immutable evaluation score and verdict for an individual criterion.

    Attributes:
        criterion: The specific quality criterion being scored.
        score: Normalized quality score bounded in [0.0, 1.0].
        passed: Boolean verdict indicating compliance with stage threshold.
        confidence: Optional calibrated probability confidence in [0.0, 1.0].
        reasoning: Succinct explanation of the score or failure rationale.
        verdict_type: Evaluation primitive type (defaults to SCORE).
        improvement_suggestion: Optional actionable correction suggestion for closed-loop retries.
    """

    criterion: JudgeCriterion
    score: float
    passed: bool
    confidence: float | None = None
    reasoning: str = ""
    verdict_type: VerdictType = VerdictType.SCORE
    improvement_suggestion: str = ""

    def __post_init__(self) -> None:
        """Validate value object invariants."""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got: {self.score}")
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0 if provided, got: {self.confidence}"
            )


DEFAULT_FLUID_PROSE_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.SEMANTIC_FAITHFULNESS: 0.25,
    JudgeCriterion.NER_PRESERVATION: 0.25,
    JudgeCriterion.ORALITY_REMOVAL: 0.20,
    JudgeCriterion.EPISTEMIC_CRITIQUE: 0.10,
    JudgeCriterion.STRUCTURAL_COMPLIANCE: 0.10,
    JudgeCriterion.AUTHORIAL_VOICE: 0.10,
}

DEFAULT_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset({
    JudgeCriterion.SEMANTIC_FAITHFULNESS,
    JudgeCriterion.NER_PRESERVATION,
})

GAP_FILLER_CANONICAL_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.FACTUAL_GROUNDING: 0.25,
    JudgeCriterion.SOCRATIC_EPISTEMIC_DEPTH: 0.25,
    JudgeCriterion.CAUSAL_STRATIFICATION_AGENCY: 0.20,
    JudgeCriterion.COMPLEMENTARY_SUBSTANCE: 0.15,
    JudgeCriterion.AUTHORIAL_NATURALISM: 0.15,
}

GAP_FILLER_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset({
    JudgeCriterion.FACTUAL_GROUNDING,
    JudgeCriterion.COMPLEMENTARY_SUBSTANCE,
})


def compute_composite_verdict(
    criteria_scores: tuple[CriterionScore, ...] | list[CriterionScore],
    pass_threshold: float = 0.80,
    veto_threshold: float = 0.80,
    weights: dict[JudgeCriterion, float] | None = None,
    veto_criteria: frozenset[JudgeCriterion] | None = None,
) -> tuple[float, bool, bool, tuple[str, ...]]:
    """Compute weighted composite score and apply two-layered mechanical veto.

    Conforms to:
        - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates

    Layer 1 (Mechanical Veto):
        Non-negotiable veto floor on critical epistemic criteria (Semantic Faithfulness,
        NER Preservation). If any veto criterion scores below veto_threshold or fails,
        the entire evaluation is rejected unconditionally.

    Layer 2 (Weighted Aggregation):
        Evaluates overall weighted mean against pass_threshold.

    Returns:
        tuple[float, bool, bool, tuple[str, ...]]:
            (overall_score, passed, is_vetoed, veto_reasons)
    """
    scores = tuple(criteria_scores)
    if not scores:
        return 0.0, False, False, ()

    active_weights = weights or DEFAULT_FLUID_PROSE_WEIGHTS
    active_veto = (
        veto_criteria if veto_criteria is not None else DEFAULT_MECHANICAL_VETO_CRITERIA
    )

    weighted_sum = 0.0
    total_weight = 0.0
    veto_reasons: list[str] = []

    for cs in scores:
        w = active_weights.get(cs.criterion, 1.0)
        weighted_sum += cs.score * w
        total_weight += w

        if cs.criterion in active_veto and (cs.score < veto_threshold or not cs.passed):
            veto_reasons.append(
                f"Mechanical Veto on critical criterion '{cs.criterion.value}': "
                f"score {cs.score:.2f} < threshold {veto_threshold:.2f}"
            )

    overall_score = round(weighted_sum / total_weight, 4) if total_weight > 0.0 else 0.0
    overall_score = max(0.0, min(1.0, overall_score))

    is_vetoed = len(veto_reasons) > 0
    passed = (not is_vetoed) and (overall_score >= pass_threshold)

    return overall_score, passed, is_vetoed, tuple(veto_reasons)


@dataclass(frozen=True, slots=True)
class JudgeEvaluation:
    """Immutable aggregate result of a stage quality evaluation.

    Attributes:
        target_stage: Canonical stage identifier (e.g. 'fluid_prose', 'raw_indexing').
        passed: Aggregate pass/fail verdict across required criteria.
        overall_score: Composite score normalized in [0.0, 1.0].
        criteria_scores: Immutable collection of individual criterion evaluations.
        provider: Provider identifier that generated this evaluation (e.g. 'gemini', 'ollama', 'typesafe').
        latency_ms: Roundtrip inference and evaluation latency in milliseconds.
        trace_id: OpenTelemetry / Langfuse trace correlation identifier.
        is_vetoed: Boolean indicating whether mechanical veto was triggered.
        veto_reasons: Immutable collection of specific mechanical veto causes.
    """

    target_stage: str
    passed: bool
    overall_score: float
    criteria_scores: tuple[CriterionScore, ...]
    provider: str
    latency_ms: float = 0.0
    trace_id: str | None = None
    is_vetoed: bool = False
    veto_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate aggregate invariants."""
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError(
                f"Overall score must be between 0.0 and 1.0, got: {self.overall_score}"
            )

    @classmethod
    def create_with_composite_verdict(
        cls,
        target_stage: str,
        criteria_scores: tuple[CriterionScore, ...] | list[CriterionScore],
        provider: str,
        pass_threshold: float = 0.80,
        veto_threshold: float = 0.80,
        latency_ms: float = 0.0,
        trace_id: str | None = None,
        weights: dict[JudgeCriterion, float] | None = None,
        veto_criteria: frozenset[JudgeCriterion] | None = None,
    ) -> JudgeEvaluation:
        """Construct JudgeEvaluation with weighted average and mechanical veto resolution."""
        scores_tuple = tuple(criteria_scores)
        overall_score, passed, is_vetoed, veto_reasons = compute_composite_verdict(
            criteria_scores=scores_tuple,
            pass_threshold=pass_threshold,
            veto_threshold=veto_threshold,
            weights=weights,
            veto_criteria=veto_criteria,
        )
        return cls(
            target_stage=target_stage,
            passed=passed,
            overall_score=overall_score,
            criteria_scores=scores_tuple,
            provider=provider,
            latency_ms=latency_ms,
            trace_id=trace_id,
            is_vetoed=is_vetoed,
            veto_reasons=veto_reasons,
        )

    def get_score(self, criterion: JudgeCriterion) -> CriterionScore | None:
        """Query score for a specific criterion, or None if not evaluated."""
        for criterion_score in self.criteria_scores:
            if criterion_score.criterion == criterion:
                return criterion_score
        return None

    def extract_critique(self) -> str:
        """Extract formatted critique and improvement suggestions from failed criteria.

        Returns a structured string designed to be injected into subsequent LLM retry prompts
        for closed-loop self-healing reflection.
        """
        failures: list[str] = []
        if self.is_vetoed and self.veto_reasons:
            failures.append("[CRITICAL MECHANICAL VETO]: " + "; ".join(self.veto_reasons))
        for score in self.criteria_scores:
            if not score.passed:
                part = f"- {score.criterion.value}: {score.reasoning}"
                if score.improvement_suggestion:
                    part += f" (Suggestion: {score.improvement_suggestion})"
                failures.append(part)
        return "\n".join(failures) if failures else "Quality threshold not met."


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    """Immutable input context provided to LlmJudgePort for assessment.

    Attributes:
        stage_name: Name of pipeline stage being assessed (e.g. 'fluid_prose').
        raw_text: Source reference or ground-truth context.
        candidate_text: Output candidate text produced by the transformation.
        metadata: Domain and pipeline provenance metadata.
        trace_id: OpenTelemetry / Langfuse active trace ID.
        required_criteria: Criteria tuple that must be evaluated for this stage.
    """

    stage_name: str
    raw_text: str
    candidate_text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    required_criteria: tuple[JudgeCriterion, ...] = ()
    observation_id: str | None = None


@dataclass(frozen=True, slots=True)
class StageEvaluationSpec:
    """Specification of quality evaluation criteria and extractors for a pipeline stage.

    Attributes:
        candidate_extractor: Callable extracting candidate text from stage result.
        required_criteria: Tuple of JudgeCriterion required for this stage.
        raw_text: Optional explicit source reference text. If empty, extracted via source_extractor.
        metadata: Optional stage metadata for evaluation tracking.
        max_attempts: Maximum generation attempts if evaluation fails (must be >= 1).
        source_extractor: Optional callable extracting source reference text from stage input.
    """

    candidate_extractor: Callable[[Any], str] = field(
        default_factory=lambda: lambda result: str(result)
    )
    required_criteria: tuple[JudgeCriterion, ...] = ()
    raw_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 1
    source_extractor: Callable[[Any], str] | None = None

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")

    def extract_source_text(self, source: Any) -> str:
        """Extract source reference text from stage input or return explicit raw_text."""
        if self.raw_text:
            return self.raw_text
        if self.source_extractor:
            return self.source_extractor(source)
        if hasattr(source, "content") and hasattr(source.content, "body"):
            return str(source.content.body)
        if hasattr(source, "body"):
            return str(source.body)
        return str(source)
