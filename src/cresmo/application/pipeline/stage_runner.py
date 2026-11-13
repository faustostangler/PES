"""Telemetry-instrumented stage execution runner and session metrics recorder.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC), Rule 7 (Parameter Objects)
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions, Reflection, and Quarantine
"""

from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, TypeVar, cast

import structlog
from opentelemetry import trace

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_execution import (
    evaluate_stage_candidate,
    execute_evaluated_stage_loop,
    generate_stage_candidate,
)
from cresmo.application.pipeline.stage_telemetry import (
    as_str,
    measure_stage_execution,
    record_duration_metric,
    record_error_metric,
    record_evaluation_metric,
    record_session_completion_telemetry,
    resolve_active_trace_id,
)
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MetricsPort,
    PromptProviderPort,
    TelemetryPort,
)
from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    MapOfContent,
    PipelineSessionId,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CandidateText,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    JudgeEvaluation,
    StageEvaluationSpec,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline.stage_factory import StageFactory

logger = structlog.get_logger(__name__)

__all__ = ["PipelineStageRunner", "_as_str", "trace"]
_as_str = as_str
_StageRet = TypeVar("_StageRet")
_TSource = TypeVar("_TSource")
_TOutput = TypeVar("_TOutput")


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(
        self,
        dependencies: PipelineDependencies | None = None,
        *,
        telemetry_port: TelemetryPort | None = None,
        metrics_port: MetricsPort | None = None,
        llm_judge: LlmJudgePort | None = None,
        judge_blocking: bool = False,
        judge_max_attempts: int = 2,
        prompt_provider: PromptProviderPort | None = None,
        llm_transformation_port: LLMTransformationPort | None = None,
        stage_factory: StageFactory | None = None,
        critique_synthesizer: CritiqueSynthesizerPort | None = None,
        ledger_port: LedgerRepositoryPort | None = None,
    ) -> None:
        """Initialize PipelineStageRunner via PipelineDependencies DTO or keyword arguments."""
        deps = dependencies or PipelineDependencies(
            telemetry_port=telemetry_port,  # type: ignore[arg-type]
            metrics_port=metrics_port,  # type: ignore[arg-type]
            llm_judge=llm_judge,
            judge_blocking=judge_blocking,
            judge_max_attempts=judge_max_attempts,
            prompt_provider=prompt_provider,
            llm_transformation_port=llm_transformation_port,
            stage_factory=stage_factory,
            critique_synthesizer=critique_synthesizer,
            ledger_port=ledger_port,
        )
        if deps.telemetry_port is None or deps.metrics_port is None:
            raise ValueError("Both telemetry_port and metrics_port must be provided.")
        self.telemetry_port = deps.telemetry_port
        self.metrics_port = deps.metrics_port
        self.llm_judge = deps.llm_judge
        self.judge_blocking = deps.judge_blocking
        self.judge_max_attempts = deps.judge_max_attempts
        self.prompt_provider = deps.prompt_provider
        self.llm_transformation_port = deps.llm_transformation_port
        self.stage_factory = deps.stage_factory
        self.critique_synthesizer = deps.critique_synthesizer
        self.ledger_port = deps.ledger_port

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
        """Execute a standardized pipeline stage with closed-loop reflection, critique, and telemetry (ADR-031)."""
        stage_config = self._resolve_stage_config(stage, max_passes=max_passes)
        prompt_provider = self._resolve_prompt_provider(prompt_provider)
        llm_port = self._resolve_llm_transformation_port(llm_transformation_port)
        stage = stage_config.stage_name

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

        with self._measure_stage(stage_name=stage, context=context):
            source_content = getattr(source, "content", None)
            source_text = (
                stage_config.eval_spec.extract_source_text(source)
                if stage_config.eval_spec
                else (
                    source_content.text
                    if isinstance(source_content, Content)
                    else (getattr(source, "text", None) or str(source))
                )
            )
            self.telemetry_port.record_stage_io(
                input_payload={
                    "stage_name": stage,
                    "source_type": type(source).__name__,
                    "source_characters": len(source_text) if isinstance(source_text, str) else 0,
                    "source_words": len(source_text.split()) if isinstance(source_text, str) else 0,
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
                self.telemetry_port.flush()

                evaluation = self._evaluate_candidate(
                    stage_config,
                    source,
                    candidate,
                    context=context,
                    attempt=attempt,
                )
                self.telemetry_port.flush()

                if evaluation is None or evaluation.passed:
                    break

                logger.warning(
                    "Quality evaluation for '%s' reported low score on attempt %d/%d (overall=%.2f, passed=%s).",
                    stage,
                    attempt,
                    effective_max_attempts,
                    evaluation.overall_score,
                    evaluation.passed,
                )

                critique = self._synthesize_critique(evaluation, stage)
                if attempt < effective_max_attempts:
                    self.metrics_port.increment_counter(
                        "cresmo_judge_retries_total", 1.0, labels={"stage": stage}
                    )

            if (
                evaluation is not None
                and not evaluation.passed
                and (stage_config.blocking or self.judge_blocking)
            ):
                record_stage_quarantine(
                    stage_name=stage,
                    context=context,
                    provenance=getattr(source, "provenance", None),
                    evaluation=evaluation,
                    critique=critique or self._synthesize_critique(evaluation, stage),
                    effective_max_attempts=effective_max_attempts,
                    ledger_port=self.ledger_port,
                    metrics_port=self.metrics_port,
                )

            if candidate is None:
                raise DomainValidationError(f"Stage '{stage}' produced no candidate text.")

            output_object: _TOutput = stage_config.post_process(candidate, source)
            output_content = getattr(output_object, "content", None)
            if isinstance(output_content, Content):
                output_text = output_content.text
            elif hasattr(output_object, "text"):
                output_text = output_object.text
            else:
                output_text = candidate.text
            self.telemetry_port.record_stage_io(
                output_payload={
                    "status": (
                        "APPROVED"
                        if (evaluation is None or evaluation.passed)
                        else "COMPLETED_UNBLOCKING"
                    ),
                    "output_characters": len(output_text) if isinstance(output_text, str) else 0,
                    "output_words": len(output_text.split()) if isinstance(output_text, str) else 0,
                    "attempts": attempt,
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

    def run_evaluated_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName | str,
        content_id: ContentId | str,
        eval_spec: StageEvaluationSpec | None = None,
        channel_id: ChannelId | str | None = None,
        content_title: str = "",
        fatal: bool = True,
        fallback: _StageRet | Callable[[], _StageRet] | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage within a closed-loop quality evaluation gate with retries (Legacy ADR-030)."""
        return execute_evaluated_stage_loop(
            self,
            stage_name,
            fn,
            channel_name=channel_name,
            content_id=content_id,
            eval_spec=eval_spec,
            channel_id=channel_id,
            content_title=content_title,
            fatal=fatal,
            fallback=fallback,
        )

    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel: Channel | None = None,
        content: Content | None = None,
        channel_name: ChannelName | str | None = None,
        content_id: ContentId | str | None = None,
        channel_id: ChannelId | str | None = None,
        content_title: str = "",
        fatal: bool = True,
        fallback: _StageRet | Callable[[], _StageRet] | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage wrapped with telemetry spans, metrics, and error handling."""
        resolved_channel = channel or Channel(name=as_str(channel_name) or "unknown", id=channel_id)
        resolved_content_id = (
            content.id
            if content is not None
            else (ContentId.from_string(content_id) if content_id else ContentId("unknown"))
        )
        resolved_content = content or Content(id=resolved_content_id, title=content_title)
        try:
            with self._measure_stage(
                stage_name=stage_name,
                channel=resolved_channel,
                content=resolved_content,
            ):
                return fn()
        except Exception as exc:
            if fatal:
                raise
            logger.warning(
                "[Pipeline] %s skipped for %s: %s", stage_name, resolved_content.id.value, exc
            )
            return fallback() if callable(fallback) else fallback

    def record_session_completion(
        self,
        session_id: PipelineSessionId | str,
        content_id: ContentId | str,
        channel_name: ChannelName | str,
        synthesized_notes: Sequence[AtomicNote],
        inventory: AtomicEntityInventory,
        mocs: Sequence[MapOfContent],
        dedup_report: DeduplicationReport,
        channel_id: ChannelId | str | None = None,
    ) -> None:
        """Record completed process metrics and session coherence evaluation score."""
        record_session_completion_telemetry(
            self.metrics_port,
            self.telemetry_port,
            session_id=session_id,
            content_id=content_id,
            channel_name=channel_name,
            synthesized_notes=synthesized_notes,
            inventory=inventory,
            mocs=mocs,
            dedup_report=dedup_report,
            channel_id=channel_id,
        )

    @contextmanager
    def _measure_stage(
        self,
        *,
        stage_name: str,
        context: PipelineExecutionContext | None = None,
        channel: Channel | None = None,
        content: Content | None = None,
    ) -> Generator[None]:
        with measure_stage_execution(
            self.telemetry_port,
            self.metrics_port,
            stage_name=stage_name,
            context=context,
            channel=channel,
            content=content,
        ):
            yield

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

    _resolve_stage_descriptor = _resolve_stage_config
    _get_active_trace_id = staticmethod(resolve_active_trace_id)

    def _synthesize_critique(self, evaluation: JudgeEvaluation, stage_name: str) -> str:
        if self.critique_synthesizer is not None:
            return self.critique_synthesizer.synthesize(evaluation, stage_name)
        return evaluation.extract_critique()

    def _record_error_metric(
        self,
        exc: Exception,
        stage_name: str,
        channel: Channel,
        content: Content,
    ) -> None:
        record_error_metric(
            self.metrics_port,
            exc=exc,
            stage_name=stage_name,
            channel=channel,
            content=content,
        )

    def _record_duration_metric(
        self,
        elapsed: float,
        stage_name: str,
        channel: Channel,
        content: Content,
        status: str,
    ) -> None:
        record_duration_metric(
            self.metrics_port,
            elapsed=elapsed,
            stage_name=stage_name,
            channel=channel,
            content=content,
            status=status,
        )

    def _record_evaluation_metrics(self, stage_name: str, passed: bool, attempt: int) -> None:
        record_evaluation_metric(
            self.metrics_port,
            stage_name=stage_name,
            passed=passed,
            attempt=attempt,
        )
