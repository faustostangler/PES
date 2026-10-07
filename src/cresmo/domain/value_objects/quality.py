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

    ORALITY_REMOVAL = "orality_removal"
    SEMANTIC_FAITHFULNESS = "semantic_faithfulness"
    NER_PRESERVATION = "ner_preservation"
    STRUCTURAL_COMPLIANCE = "structural_compliance"
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
    """

    target_stage: str
    passed: bool
    overall_score: float
    criteria_scores: tuple[CriterionScore, ...]
    provider: str
    latency_ms: float = 0.0
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate aggregate invariants."""
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError(
                f"Overall score must be between 0.0 and 1.0, got: {self.overall_score}"
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
        if hasattr(source, "body"):
            return str(source.body)
        return str(source)
