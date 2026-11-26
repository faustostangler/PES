"""Telemetry-instrumented stage execution runner and session metrics recorder.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC), Rule 7 (Parameter Objects)
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions, Reflection, and Quarantine
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
- ADR-077: Strict Runner Contracts & PEP 695 Generics
"""

from __future__ import annotations

from typing import Final

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_execution import (
    evaluate_stage_candidate,
    generate_stage_candidate,
)
from cresmo.application.pipeline.stage_telemetry import (
    measure_stage_execution,
    resolve_active_trace_id,
)
from cresmo.application.ports import MetricName
from cresmo.domain.entities import StageTranscript
from cresmo.domain.entities.transcripts import extract_source_text
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import CandidateText, JudgeEvaluation

logger = structlog.get_logger(__name__)

STAGE_STATUS_APPROVED: Final[str] = "APPROVED"
STAGE_STATUS_COMPLETED_UNBLOCKING: Final[str] = "COMPLETED_UNBLOCKING"
METRIC_INCREMENT_ONE: Final[float] = 1.0
METRIC_LABEL_STAGE: Final[str] = "stage"
RATIO_ROUND_DECIMAL_PLACES: Final[int] = 3

_PAYLOAD_KEY_STAGE_NAME: Final[str] = "stage_name"
_PAYLOAD_KEY_SOURCE_TYPE: Final[str] = "source_type"
_PAYLOAD_KEY_SOURCE_CHARACTERS: Final[str] = "source_characters"
_PAYLOAD_KEY_SOURCE_WORDS: Final[str] = "source_words"
_PAYLOAD_KEY_STATUS: Final[str] = "status"
_PAYLOAD_KEY_OUTPUT_CHARACTERS: Final[str] = "output_characters"
_PAYLOAD_KEY_OUTPUT_WORDS: Final[str] = "output_words"
_PAYLOAD_KEY_ATTEMPTS: Final[str] = "attempts"
_PAYLOAD_KEY_RETRIES: Final[str] = "retries"
_PAYLOAD_KEY_EXPANSION_RATIO: Final[str] = "expansion_ratio"
_PAYLOAD_KEY_JUDGE_PASSED: Final[str] = "judge_passed"
_PAYLOAD_KEY_JUDGE_OVERALL_SCORE: Final[str] = "judge_overall_score"

__all__ = ["PipelineStageRunner"]


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(self, dependencies: PipelineDependencies) -> None:
        """Initialize PipelineStageRunner via PipelineDependencies DTO."""
        if dependencies.telemetry_port is None or dependencies.metrics_port is None:
            raise ValueError("Both telemetry_port and metrics_port must be provided.")
        if dependencies.prompt_provider is None:
            raise ValueError("prompt_provider must be provided.")
        if dependencies.llm_transformation_port is None:
            raise ValueError("llm_transformation_port must be provided.")
        self.telemetry_port = dependencies.telemetry_port
        self.metrics_port = dependencies.metrics_port
        self.llm_judge = dependencies.llm_judge
        self.judge_blocking = dependencies.judge_blocking
        self.judge_max_attempts = dependencies.judge_max_attempts
        self.prompt_provider = dependencies.prompt_provider
        self.llm_transformation_port = dependencies.llm_transformation_port
        self.stage_factory = dependencies.stage_factory
        self.critique_synthesizer = dependencies.critique_synthesizer
        self.ledger_port = dependencies.ledger_port

    def warmup(self) -> None:
        """Asynchronously trigger warmup for transformation and critique LLM ports."""
        self.llm_transformation_port.warmup()
        if self.critique_synthesizer is not None:
            self.critique_synthesizer.warmup()

    def execute_stage[TSource, TOutput](
        self,
        stage: str | StageConfig[TSource, TOutput],
        source: TSource,
        *,
        context: PipelineExecutionContext,
        max_passes: int | None = None,
    ) -> TOutput:
        """Execute a standardized pipeline stage with closed-loop reflection, critique, and telemetry."""
        stage_config = self._resolve_stage_config(stage, max_passes=max_passes)
        stage_name = stage_config.stage_name

        eval_spec_attempts = (
            stage_config.eval_spec.max_attempts
            if stage_config.eval_spec is not None
            else stage_config.max_attempts
        )
        effective_max_attempts = max(
            stage_config.max_attempts,
            eval_spec_attempts,
            self.judge_max_attempts,
        )

        critique: str | None = None
        candidate: CandidateText | None = None
        evaluation: JudgeEvaluation | None = None

        with measure_stage_execution(
            self.telemetry_port,
            self.metrics_port,
            stage_name=stage_name,
            context=context,
        ) as stage_span:
            source_text = (
                extract_source_text(source)
                if isinstance(source, (StageTranscript, CandidateText, str))
                else str(source)
            )
            source_words = len(source_text.split())
            stage_span.set_input(
                {
                    _PAYLOAD_KEY_STAGE_NAME: stage_name,
                    _PAYLOAD_KEY_SOURCE_TYPE: type(source).__name__,
                    _PAYLOAD_KEY_SOURCE_CHARACTERS: len(source_text),
                    _PAYLOAD_KEY_SOURCE_WORDS: source_words,
                }
            )

            attempts_run = 0
            for attempt in range(1, effective_max_attempts + 1):
                attempts_run = attempt
                active_trace_id = resolve_active_trace_id(
                    context,
                    telemetry_port=self.telemetry_port,
                )
                candidate = generate_stage_candidate(
                    stage_config,
                    source,
                    context=context,
                    prompt_provider=self.prompt_provider,
                    llm_port=self.llm_transformation_port,
                    attempt=attempt,
                    active_trace_id=active_trace_id,
                    critique=critique,
                    telemetry_port=self.telemetry_port,
                )

                evaluation = evaluate_stage_candidate(
                    stage_config,
                    source,
                    candidate,
                    context=context,
                    attempt=attempt,
                    llm_judge=self.llm_judge,
                    telemetry_port=self.telemetry_port,
                    metrics_port=self.metrics_port,
                )

                if evaluation is None or evaluation.passed:
                    break

                logger.warning(
                    "Quality evaluation for '%s' reported low score on attempt %d/%d (overall=%.2f, passed=%s).",
                    stage_name,
                    attempt,
                    effective_max_attempts,
                    evaluation.overall_score,
                    evaluation.passed,
                )

                critique = self._synthesize_critique(evaluation, stage_name)
                if attempt < effective_max_attempts:
                    self.metrics_port.increment_counter(
                        MetricName.JUDGE_RETRY_COUNT,
                        METRIC_INCREMENT_ONE,
                        labels={METRIC_LABEL_STAGE: stage_name},
                    )

            if (
                evaluation is not None
                and not evaluation.passed
                and (stage_config.blocking or self.judge_blocking)
            ):
                record_stage_quarantine(
                    stage_name=stage_name,
                    context=context,
                    provenance=source.provenance if isinstance(source, StageTranscript) else None,
                    evaluation=evaluation,
                    critique=critique or evaluation.extract_critique(),
                    effective_max_attempts=effective_max_attempts,
                    ledger_port=self.ledger_port,
                    metrics_port=self.metrics_port,
                    telemetry_port=self.telemetry_port,
                )

            if candidate is None:
                raise DomainValidationError(f"Stage '{stage_name}' produced no candidate text.")

            output_object: TOutput = stage_config.post_process(candidate, source)
            output_text = (
                extract_source_text(output_object)
                if isinstance(output_object, (StageTranscript, CandidateText, str))
                else candidate.text
            ) or candidate.text
            output_words = len(output_text.split())
            stage_span.set_output(
                {
                    _PAYLOAD_KEY_STATUS: (
                        STAGE_STATUS_APPROVED
                        if (evaluation is None or evaluation.passed)
                        else STAGE_STATUS_COMPLETED_UNBLOCKING
                    ),
                    _PAYLOAD_KEY_OUTPUT_CHARACTERS: len(output_text),
                    _PAYLOAD_KEY_OUTPUT_WORDS: output_words,
                    _PAYLOAD_KEY_ATTEMPTS: attempts_run,
                    _PAYLOAD_KEY_RETRIES: max(0, attempts_run - 1),
                    _PAYLOAD_KEY_EXPANSION_RATIO: round(
                        output_words / max(source_words, 1), RATIO_ROUND_DECIMAL_PLACES
                    ),
                    _PAYLOAD_KEY_JUDGE_PASSED: (
                        evaluation.passed if evaluation is not None else None
                    ),
                    _PAYLOAD_KEY_JUDGE_OVERALL_SCORE: (
                        evaluation.overall_score if evaluation is not None else None
                    ),
                }
            )
            return output_object

    def _resolve_stage_config[TSource, TOutput](
        self,
        stage: str | StageConfig[TSource, TOutput],
        *,
        max_passes: int | None = None,
    ) -> StageConfig[TSource, TOutput]:
        if isinstance(stage, str):
            if self.stage_factory is None:
                raise ValueError(
                    f"Cannot resolve stage '{stage}' from string without an injected StageFactory."
                )
            built_stage: StageConfig[TSource, TOutput] = self.stage_factory.build_stage(
                stage,
                max_passes=max_passes,
            )
            return built_stage
        return stage

    def _synthesize_critique(self, evaluation: JudgeEvaluation, stage_name: str) -> str:
        if self.critique_synthesizer is not None:
            return self.critique_synthesizer.synthesize(evaluation, stage_name)
        return evaluation.extract_critique()
