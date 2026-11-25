"""Telemetry-instrumented stage execution runner and session metrics recorder.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC), Rule 7 (Parameter Objects)
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions, Reflection, and Quarantine
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
- ADR-077: Strict Runner Contracts & PEP 695 Generics
"""

from __future__ import annotations

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
                    "stage_name": stage_name,
                    "source_type": type(source).__name__,
                    "source_characters": len(source_text),
                    "source_words": source_words,
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
                        MetricName.JUDGE_RETRY_COUNT, 1.0, labels={"stage": stage_name}
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
                    "status": (
                        "APPROVED"
                        if (evaluation is None or evaluation.passed)
                        else "COMPLETED_UNBLOCKING"
                    ),
                    "output_characters": len(output_text),
                    "output_words": output_words,
                    "attempts": attempts_run,
                    "retries": max(0, attempts_run - 1),
                    "expansion_ratio": round(output_words / max(source_words, 1), 3),
                    "judge_passed": evaluation.passed if evaluation is not None else None,
                    "judge_overall_score": (
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
