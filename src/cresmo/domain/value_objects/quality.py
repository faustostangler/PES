"""Domain Value Objects for Quality Evaluation and Decision-Model Evaluators.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Final

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.prompt import PromptKey

SCORE_MIN_BOUND: Final[float] = 0.0
SCORE_MAX_BOUND: Final[float] = 1.0
DEFAULT_CRITERION_WEIGHT: Final[float] = 1.0
DEFAULT_PASS_THRESHOLD: Final[float] = 0.80
DEFAULT_VETO_THRESHOLD: Final[float] = 0.80
OVERALL_SCORE_DECIMAL_PLACES: Final[int] = 4
MECHANICAL_VETO_CRITIQUE_PREFIX: Final[str] = "[CRITICAL MECHANICAL VETO]: "
CRITIQUE_REASON_SEPARATOR: Final[str] = "; "
DEFAULT_QUALITY_FAILURE_CRITIQUE: Final[str] = "Quality threshold not met."
MIN_EVALUATION_ATTEMPTS: Final[int] = 1


class JudgeCriterion(StrEnum):
    """Canonical semantic criteria for stage quality evaluation."""

    # Stage 1: Fluid Prose Criteria
    ORALITY_REMOVAL = "orality_removal"
    SEMANTIC_FAITHFULNESS = "semantic_faithfulness"
    NER_PRESERVATION = "ner_preservation"
    STRUCTURAL_COMPLIANCE = "structural_compliance"
    EPISTEMIC_CRITIQUE = "epistemic_critique"
    AUTHORIAL_VOICE = "authorial_voice"

    # Stage 2: Specialized Gap Filler Criteria (ADR-060)
    EPISTEMIC_GROUNDING_SEGREGATION = "epistemic_grounding_segregation"
    CONCEPTUAL_MECHANICAL_DECOMPOSITION = "conceptual_mechanical_decomposition"
    BRAUDELIAN_STRATIFICATION = "braudelian_stratification"
    GENEALOGY_HIDDEN_AGENCY = "genealogy_hidden_agency"
    COMPETING_HYPOTHESES = "competing_hypotheses"
    EXTRA_INFO_GRANULARITY = "extra_info_granularity"
    LINEAR_STYLE_NATURALISM = "linear_style_naturalism"

    # Stage 3: Long & Wide Expander Criteria (ADR-073)
    LONGUE_DUREE_STRATIFICATION = "longue_duree_stratification"
    HISTORICAL_PALIMPSEST = "historical_palimpsest"
    EMPIRICAL_HISTORICAL_GROUNDING = "empirical_historical_grounding"
    IMPLICIT_FRAMING_STYLE = "implicit_framing_style"
    SYNCHRONIC_CONNECTIVITY = "synchronic_connectivity"
    COMPARATIVE_PARALLELISM = "comparative_parallelism"

    # Downstream Stages
    INVENTORY_COHERENCE = "inventory_coherence"
    INDEX_SYNTHESIS_QUALITY = "index_synthesis_quality"


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
class CriterionScore:
    """Immutable evaluation score and verdict for an individual criterion.

    Attributes:
        criterion: The specific quality criterion being scored.
        score: Normalized quality score bounded in [0.0, 1.0].
        passed: Boolean verdict indicating compliance with stage threshold.
        reasoning: Succinct explanation of the score or failure rationale.
        improvement_suggestion: Optional actionable correction suggestion for closed-loop retries.
    """

    criterion: JudgeCriterion
    score: float
    passed: bool
    reasoning: str = ""
    improvement_suggestion: str = ""

    def __post_init__(self) -> None:
        """Validate value object invariants."""
        if not (SCORE_MIN_BOUND <= self.score <= SCORE_MAX_BOUND):
            raise ValueError(
                f"Score must be between {SCORE_MIN_BOUND} and {SCORE_MAX_BOUND}, got: {self.score}"
            )


DEFAULT_FLUID_PROSE_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.SEMANTIC_FAITHFULNESS: 0.25,
    JudgeCriterion.NER_PRESERVATION: 0.25,
    JudgeCriterion.ORALITY_REMOVAL: 0.20,
    JudgeCriterion.EPISTEMIC_CRITIQUE: 0.10,
    JudgeCriterion.STRUCTURAL_COMPLIANCE: 0.10,
    JudgeCriterion.AUTHORIAL_VOICE: 0.10,
}

DEFAULT_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset(
    {
        JudgeCriterion.SEMANTIC_FAITHFULNESS,
        JudgeCriterion.NER_PRESERVATION,
    }
)

GAP_FILLER_CANONICAL_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION: 0.20,
    JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION: 0.15,
    JudgeCriterion.BRAUDELIAN_STRATIFICATION: 0.15,
    JudgeCriterion.GENEALOGY_HIDDEN_AGENCY: 0.15,
    JudgeCriterion.COMPETING_HYPOTHESES: 0.15,
    JudgeCriterion.EXTRA_INFO_GRANULARITY: 0.10,
    JudgeCriterion.LINEAR_STYLE_NATURALISM: 0.10,
}

GAP_FILLER_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset(
    {
        JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
        JudgeCriterion.EXTRA_INFO_GRANULARITY,
    }
)

LONG_EXPANDER_CANONICAL_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.LONGUE_DUREE_STRATIFICATION: 0.35,
    JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING: 0.25,
    JudgeCriterion.HISTORICAL_PALIMPSEST: 0.20,
    JudgeCriterion.EXTRA_INFO_GRANULARITY: 0.10,
    JudgeCriterion.IMPLICIT_FRAMING_STYLE: 0.10,
}

LONG_EXPANDER_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset(
    {
        JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING,
        JudgeCriterion.EXTRA_INFO_GRANULARITY,
    }
)

WIDE_EXPANDER_CANONICAL_WEIGHTS: dict[JudgeCriterion, float] = {
    JudgeCriterion.SYNCHRONIC_CONNECTIVITY: 0.30,
    JudgeCriterion.COMPARATIVE_PARALLELISM: 0.30,
    JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING: 0.20,
    JudgeCriterion.EXTRA_INFO_GRANULARITY: 0.10,
    JudgeCriterion.IMPLICIT_FRAMING_STYLE: 0.10,
}

WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA: frozenset[JudgeCriterion] = frozenset(
    {
        JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING,
        JudgeCriterion.EXTRA_INFO_GRANULARITY,
    }
)

_STAGE_SCORING_POLICIES: dict[
    str, tuple[dict[JudgeCriterion, float], frozenset[JudgeCriterion]]
] = {
    "gap_filler": (GAP_FILLER_CANONICAL_WEIGHTS, GAP_FILLER_MECHANICAL_VETO_CRITERIA),
    "long_expander": (LONG_EXPANDER_CANONICAL_WEIGHTS, LONG_EXPANDER_MECHANICAL_VETO_CRITERIA),
    "wide_expander": (WIDE_EXPANDER_CANONICAL_WEIGHTS, WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA),
}


def resolve_stage_scoring_policy(
    stage_name: str,
) -> tuple[dict[JudgeCriterion, float], frozenset[JudgeCriterion]]:
    """Resolve canonical criterion weights and mechanical veto criteria for a pipeline stage."""
    return _STAGE_SCORING_POLICIES.get(
        stage_name,
        (DEFAULT_FLUID_PROSE_WEIGHTS, DEFAULT_MECHANICAL_VETO_CRITERIA),
    )


def compute_composite_verdict(
    criteria_scores: tuple[CriterionScore, ...] | list[CriterionScore],
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    veto_threshold: float = DEFAULT_VETO_THRESHOLD,
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
        return SCORE_MIN_BOUND, False, False, ()

    active_weights = weights or DEFAULT_FLUID_PROSE_WEIGHTS
    active_veto = veto_criteria if veto_criteria is not None else DEFAULT_MECHANICAL_VETO_CRITERIA

    weighted_sum = SCORE_MIN_BOUND
    total_weight = SCORE_MIN_BOUND
    veto_reasons: list[str] = []

    for criterion_score in scores:
        weight = active_weights.get(criterion_score.criterion, DEFAULT_CRITERION_WEIGHT)
        weighted_sum += criterion_score.score * weight
        total_weight += weight

        if criterion_score.criterion in active_veto and (
            criterion_score.score < veto_threshold or not criterion_score.passed
        ):
            veto_reasons.append(
                f"Mechanical Veto on critical criterion '{criterion_score.criterion.value}': "
                f"score {criterion_score.score:.2f} < threshold {veto_threshold:.2f}"
            )

    overall_score = (
        round(weighted_sum / total_weight, OVERALL_SCORE_DECIMAL_PLACES)
        if total_weight > SCORE_MIN_BOUND
        else SCORE_MIN_BOUND
    )
    overall_score = max(SCORE_MIN_BOUND, min(SCORE_MAX_BOUND, overall_score))

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
        if not (SCORE_MIN_BOUND <= self.overall_score <= SCORE_MAX_BOUND):
            raise ValueError(
                f"Overall score must be between {SCORE_MIN_BOUND} and {SCORE_MAX_BOUND}, got: {self.overall_score}"
            )

    @classmethod
    def create_with_composite_verdict(
        cls,
        target_stage: str,
        criteria_scores: tuple[CriterionScore, ...] | list[CriterionScore],
        provider: str,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
        veto_threshold: float = DEFAULT_VETO_THRESHOLD,
        latency_ms: float = 0.0,
        trace_id: str | None = None,
        weights: dict[JudgeCriterion, float] | None = None,
        veto_criteria: frozenset[JudgeCriterion] | None = None,
    ) -> JudgeEvaluation:
        """Construct JudgeEvaluation with weighted average and mechanical veto resolution."""
        if weights is None or veto_criteria is None:
            resolved_weights, resolved_vetoes = resolve_stage_scoring_policy(target_stage)
            effective_weights = weights if weights is not None else resolved_weights
            effective_vetoes = veto_criteria if veto_criteria is not None else resolved_vetoes
        else:
            effective_weights = weights
            effective_vetoes = veto_criteria
        scores_tuple = tuple(criteria_scores)
        overall_score, passed, is_vetoed, veto_reasons = compute_composite_verdict(
            criteria_scores=scores_tuple,
            pass_threshold=pass_threshold,
            veto_threshold=veto_threshold,
            weights=effective_weights,
            veto_criteria=effective_vetoes,
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
            failures.append(
                MECHANICAL_VETO_CRITIQUE_PREFIX + CRITIQUE_REASON_SEPARATOR.join(self.veto_reasons)
            )
        for score in self.criteria_scores:
            if not score.passed:
                part = f"- {score.criterion.value}: {score.reasoning}"
                if score.improvement_suggestion:
                    part += f" (Suggestion: {score.improvement_suggestion})"
                failures.append(part)
        return "\n".join(failures) if failures else DEFAULT_QUALITY_FAILURE_CRITIQUE


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
        observation_id: Optional parent OpenTelemetry / Langfuse observation ID.
        judge_prompt_key: Canonical PromptKey selecting the judge prompt template.
    """

    stage_name: str
    raw_text: str
    candidate_text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    required_criteria: tuple[JudgeCriterion, ...] = ()
    observation_id: str | None = None
    judge_prompt_key: PromptKey | None = None


@dataclass(frozen=True, slots=True)
class StageEvaluationSpec:
    """Specification of quality evaluation criteria and candidate extractor for a pipeline stage.

    Attributes:
        candidate_extractor: Callable extracting candidate text from stage result.
        required_criteria: Tuple of JudgeCriterion required for this stage.
        metadata: Optional stage metadata for evaluation tracking.
        max_attempts: Maximum generation attempts if evaluation fails (must be >= 1).
    """

    candidate_extractor: Callable[[Any], str] = field(
        default_factory=lambda: lambda result: str(result)
    )
    required_criteria: tuple[JudgeCriterion, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    max_attempts: int = MIN_EVALUATION_ATTEMPTS

    def __post_init__(self) -> None:
        if self.max_attempts < MIN_EVALUATION_ATTEMPTS:
            raise ValueError(
                f"max_attempts must be >= {MIN_EVALUATION_ATTEMPTS}, got {self.max_attempts}"
            )
