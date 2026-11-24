"""Telemetry-instrumented stage execution runner and session metrics recorder.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC), Rule 7 (Parameter Objects)
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions, Reflection, and Quarantine
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, TypeVar, cast

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_descriptor import StageConfig, extract_stage_source_text
from cresmo.application.pipeline.stage_execution import (
    evaluate_stage_candidate,
    generate_stage_candidate,
)
from cresmo.application.pipeline.stage_telemetry import (
    measure_stage_execution,
    resolve_active_trace_id,
)
from cresmo.application.ports import (
    LLMTransformationPort,
    MetricName,
    PromptProviderPort,
    TelemetrySpan,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    CandidateText,
    JudgeEvaluation,
)

logger = structlog.get_logger(__name__)

__all__ = ["PipelineStageRunner"]
_TSource = TypeVar("_TSource")
_TOutput = TypeVar("_TOutput")


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(self, dependencies: PipelineDependencies) -> None:
        """Initialize PipelineStageRunner via PipelineDependencies DTO."""
        if dependencies.telemetry_port is None or dependencies.metrics_port is None:
            raise ValueError("Both telemetry_port and metrics_port must be provided.")
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

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously trigger warmup for the stage runner LLM transformation port."""
        if self.llm_transformation_port is not None:
            self.llm_transformation_port.warmup(timeout_seconds=timeout_seconds)

    def execute_stage(
        self,
        stage: str | StageConfig[_TSource, _TOutput],
        source: _TSource,
        *,
        context: PipelineExecutionContext,
        prompt_provider: PromptProviderPort | None = None,
        llm_transformation_port: LLMTransformationPort | None = None,
        max_passes: int | None = None,
    ) -> _TOutput:
        """Execute a standardized pipeline stage with closed-loop reflection, critique, and telemetry."""
        stage_config = self._resolve_stage_config(stage, max_passes=max_passes)
        prompt_provider = self._resolve_prompt_provider(prompt_provider)
        llm_port = self._resolve_llm_transformation_port(llm_transformation_port)
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

        with self._measure_stage(stage_name=stage_name, context=context) as stage_span:
            source_text = (
                stage_config.eval_spec.extract_source_text(source)
                if stage_config.eval_spec
                else extract_stage_source_text(source)
            )
            source_words = len(source_text.split()) if isinstance(source_text, str) else 0
            stage_span.set_input(
                {
                    "stage_name": stage_name,
                    "source_type": type(source).__name__,
                    "source_characters": len(source_text) if isinstance(source_text, str) else 0,
                    "source_words": source_words,
                }
            )

            for attempt in range(1, effective_max_attempts + 1):
                candidate = self._generate_candidate(
                    stage_config,
                    source,
                    context=context,
                    prompt_provider=prompt_provider,
                    llm_port=llm_port,
                    attempt=attempt,
                    critique=critique,
                )

                evaluation = self._evaluate_candidate(
                    stage_config,
                    source,
                    candidate,
                    context=context,
                    attempt=attempt,
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
                    provenance=getattr(source, "provenance", None),
                    evaluation=evaluation,
                    critique=critique or self._synthesize_critique(evaluation, stage_name),
                    effective_max_attempts=effective_max_attempts,
                    ledger_port=self.ledger_port,
                    metrics_port=self.metrics_port,
                    telemetry_port=self.telemetry_port,
                )

            if candidate is None:
                raise DomainValidationError(f"Stage '{stage_name}' produced no candidate text.")

            output_object: _TOutput = stage_config.post_process(candidate, source)
            output_text = extract_stage_source_text(output_object) or candidate.text
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
                    "attempts": attempt,
                    "retries": attempt - 1,
                    "expansion_ratio": round(output_words / max(source_words, 1), 3),
                    "judge_passed": evaluation.passed if evaluation is not None else None,
                    "judge_overall_score": (
                        evaluation.overall_score if evaluation is not None else None
                    ),
                }
            )
            return output_object

    def _generate_candidate(
        self,
        stage_config: StageConfig[_TSource, _TOutput],
        source: _TSource,
        *,
        context: PipelineExecutionContext,
        prompt_provider: PromptProviderPort,
        llm_port: LLMTransformationPort,
        attempt: int,
        critique: str | None = None,
    ) -> CandidateText:
        """Build prompt and invoke LLM transformation port to generate CandidateText."""
        return generate_stage_candidate(
            stage_config,
            source,
            context=context,
            prompt_provider=prompt_provider,
            llm_port=llm_port,
            attempt=attempt,
            active_trace_id=self._get_active_trace_id(context=context),
            critique=critique,
            telemetry_port=self.telemetry_port,
        )

    def _evaluate_candidate(
        self,
        stage_config: StageConfig[_TSource, _TOutput],
        source: _TSource,
        candidate: CandidateText,
        *,
        context: PipelineExecutionContext,
        attempt: int,
    ) -> JudgeEvaluation | None:
        """Evaluate candidate text against stage quality criteria if judge and eval_spec are configured."""
        return evaluate_stage_candidate(
            self,
            stage_config,
            source,
            candidate,
            context=context,
            attempt=attempt,
        )

    @contextmanager
    def _measure_stage(
        self,
        *,
        stage_name: str,
        context: PipelineExecutionContext,
    ) -> Generator[TelemetrySpan]:
        with measure_stage_execution(
            self.telemetry_port,
            self.metrics_port,
            stage_name=stage_name,
            context=context,
        ) as stage_span:
            yield stage_span

    def _resolve_prompt_provider(
        self, prompt_provider: PromptProviderPort | None
    ) -> PromptProviderPort:
        resolved = prompt_provider or self.prompt_provider
        if resolved is None:
            raise ValueError(
                "PromptProviderPort must be provided via constructor or execute_stage argument"
            )
        return resolved

    def _resolve_llm_transformation_port(
        self, llm_transformation_port: LLMTransformationPort | None
    ) -> LLMTransformationPort:
        resolved = llm_transformation_port or self.llm_transformation_port
        if resolved is None:
            raise ValueError(
                "LLMTransformationPort must be provided via constructor or execute_stage argument"
            )
        return resolved

    def _resolve_stage_config(
        self,
        stage: str | StageConfig[_TSource, _TOutput],
        *,
        max_passes: int | None = None,
    ) -> StageConfig[_TSource, _TOutput]:
        if isinstance(stage, str):
            if self.stage_factory is None:
                raise ValueError(
                    f"Cannot resolve stage '{stage}' from string without an injected StageFactory."
                )
            kwargs: dict[str, Any] = {}
            if max_passes is not None:
                kwargs["max_passes"] = max_passes
            built_stage = self.stage_factory.build_stage(stage, **kwargs)
            return cast(StageConfig[_TSource, _TOutput], built_stage)
        return stage

    def _get_active_trace_id(
        self,
        *,
        context: PipelineExecutionContext,
        span: TelemetrySpan | None = None,
    ) -> str:
        """Resolve active trace ID from TelemetryPort or build deterministic fallback."""
        return resolve_active_trace_id(
            context,
            telemetry_port=self.telemetry_port,
            span=span,
        )

    def _synthesize_critique(self, evaluation: JudgeEvaluation, stage_name: str) -> str:
        if self.critique_synthesizer is not None:
            return self.critique_synthesizer.synthesize(evaluation, stage_name)
        return evaluation.extract_critique()
