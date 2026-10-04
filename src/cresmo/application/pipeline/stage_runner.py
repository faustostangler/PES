"""Telemetry-instrumented stage execution runner and session metrics recorder.

Conforms to:
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC), Rule 7 (Parameter Objects)
- ADR-030: Stage Quality Gate & Evaluator Closed-Loop Retry Fabric
- ADR-031: CandidateText and Stage Descriptor Abstractions, Reflection, and Quarantine
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeVar

from opentelemetry import trace

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.quarantine import record_stage_quarantine
from cresmo.application.pipeline.stage_descriptor import StageConfig
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
    UserIdentity,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CandidateText,
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    JudgeEvaluation,
    StageEvaluationSpec,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline.stage_factory import StageFactory

logger = logging.getLogger(__name__)

_StageRet = TypeVar("_StageRet")
_TSource = TypeVar("_TSource")
_TOutput = TypeVar("_TOutput")


def _as_str(
    val: ChannelName | ContentId | ChannelId | PipelineSessionId | UserIdentity | str | None,
) -> str:
    """Extract canonical string value from Value Objects or return primitive string safely."""
    if val is None:
        return ""
    if isinstance(val, (ChannelName, ContentId, ChannelId, PipelineSessionId, UserIdentity)):
        return val.value
    return val


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
        judge_max_attempts: int = 1,
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
    ) -> _TOutput:
        """Execute a standardized pipeline stage with closed-loop reflection, critique, and telemetry (ADR-031)."""
        stage_config = self._resolve_stage_config(stage)
        prompt_provider = self._resolve_prompt_provider(prompt_provider)
        llm_port = self._resolve_llm_transformation_port(llm_transformation_port)
        stage_name = stage_config.stage_name

        effective_max_attempts = max(
            stage_config.max_attempts,
            stage_config.eval_spec.max_attempts if stage_config.eval_spec else 1,
            self.judge_max_attempts,
        )

        critique: str | None = None
        candidate: CandidateText | None = None
        evaluation: JudgeEvaluation | None = None

        channel_id_val = context.channel.id.value if context.channel.id else ""
        content_id_val = context.content.id.value
        channel_name_val = context.channel.name
        content_title_val = context.content.title

        with self._measure_stage(
            stage_name=stage_name,
            channel_id=channel_id_val,
            content_id=content_id_val,
            channel_name=channel_name_val,
            content_title=content_title_val,
        ):
            for attempt in range(1, effective_max_attempts + 1):
                system_instruction, user_prompt = stage_config.build_transform_prompt(
                    prompt_provider,
                    source,
                    channel_name=channel_name_val,
                    channel_id=channel_id_val,
                    content_id=content_id_val,
                    content_title=content_title_val,
                    critique=critique,
                )
                active_trace_id = self._get_active_trace_id(
                    channel=context.channel.id or channel_name_val,
                    content_id=context.content.id,
                    channel_id=context.channel.id,
                    channel_name=channel_name_val,
                )

                candidate = CandidateText(
                    text=llm_port.transform(
                        prompt=user_prompt,
                        system_instruction=system_instruction,
                        temperature=stage_config.temperature,
                        trace_id=active_trace_id,
                        session_id=context.session_id.value,
                        user_id=context.user_identity.value,
                    ),
                    stage_name=stage_name,
                    metadata={
                        "channel_id": channel_id_val,
                        "content_id": content_id_val,
                        "channel_name": channel_name_val,
                        "content_title": content_title_val,
                        "attempt": attempt,
                    },
                )

                if self.llm_judge is None or stage_config.eval_spec is None:
                    break

                eval_context = EvaluationContext(
                    stage_name=stage_name,
                    raw_text=stage_config.eval_spec.extract_source_text(source),
                    candidate_text=(
                        stage_config.eval_spec.candidate_extractor(candidate)
                        if stage_config.eval_spec.candidate_extractor
                        else candidate.text
                    ),
                    metadata={
                        "channel_id": channel_id_val,
                        "content_id": content_id_val,
                        "channel_name": channel_name_val,
                        "content_title": content_title_val,
                        "attempt": attempt,
                        **stage_config.eval_spec.metadata,
                    },
                    trace_id=active_trace_id,
                    required_criteria=stage_config.eval_spec.required_criteria,
                )

                evaluation = self.llm_judge.evaluate(eval_context)
                self._record_evaluation_metrics(stage_name, evaluation.passed, attempt)

                if evaluation.passed:
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
                        "cresmo_judge_retries_total", 1.0, labels={"stage": stage_name}
                    )

            if (
                evaluation is not None
                and not evaluation.passed
                and (stage_config.blocking or self.judge_blocking)
            ):
                record_stage_quarantine(
                    stage_name=stage_name,
                    content_id=context.content.id,
                    channel_name=channel_name_val,
                    channel_id=context.channel.id,
                    content_title=content_title_val,
                    evaluation=evaluation,
                    critique=critique or self._synthesize_critique(evaluation, stage_name),
                    effective_max_attempts=effective_max_attempts,
                    ledger_port=self.ledger_port,
                    metrics_port=self.metrics_port,
                )

            if candidate is None:
                raise DomainValidationError(f"Stage '{stage_name}' produced no candidate text.")

            return stage_config.post_process(candidate, source)

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
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage within a closed-loop quality evaluation gate with retries (Legacy ADR-030)."""
        if self.llm_judge is None or eval_spec is None:
            return self.run_stage(
                stage_name,
                fn,
                channel_name=channel_name,
                content_id=content_id,
                channel_id=channel_id,
                content_title=content_title,
                fatal=fatal,
                fallback=fallback,
            )

        effective_max_attempts = max(eval_spec.max_attempts, self.judge_max_attempts)
        candidate: _StageRet | None = None
        evaluation: JudgeEvaluation | None = None

        for attempt in range(1, effective_max_attempts + 1):
            candidate = self.run_stage(
                stage_name,
                fn,
                channel_name=channel_name,
                content_id=content_id,
                channel_id=channel_id,
                content_title=content_title,
                fatal=fatal,
                fallback=fallback,
            )
            if candidate is None:
                return fallback

            active_trace_id = self._get_active_trace_id(
                channel=channel_id or channel_name,
                content_id=content_id,
                channel_id=channel_id,
                channel_name=channel_name,
            )
            eval_context = EvaluationContext(
                stage_name=stage_name,
                raw_text=eval_spec.raw_text,
                candidate_text=eval_spec.candidate_extractor(candidate),
                metadata={
                    "channel_id": _as_str(channel_id),
                    "content_id": _as_str(content_id),
                    "channel_name": _as_str(channel_name),
                    "content_title": content_title or str(getattr(candidate, "title", "")),
                    "attempt": attempt,
                    **eval_spec.metadata,
                },
                trace_id=active_trace_id,
                required_criteria=eval_spec.required_criteria,
            )
            evaluation = self.llm_judge.evaluate(eval_context)
            self._record_evaluation_metrics(stage_name, evaluation.passed, attempt)

            if evaluation.passed:
                return candidate

            logger.warning(
                "LLM judge reported low score for '%s' on attempt %d/%d (overall=%.2f, passed=%s).",
                stage_name,
                attempt,
                effective_max_attempts,
                evaluation.overall_score,
                evaluation.passed,
            )
            if attempt < effective_max_attempts:
                self.metrics_port.increment_counter(
                    "cresmo_judge_retries_total", 1.0, labels={"stage": stage_name}
                )

        if self.judge_blocking:
            raise DomainValidationError(
                f"{stage_name} quality evaluation failed threshold after {effective_max_attempts} attempts: "
                f"{(evaluation.overall_score if evaluation else 0.0):.2f}"
            )

        logger.warning(
            "Quality evaluation for '%s' exhausted all %d attempts without passing. Returning candidate as judge_blocking is False.",
            stage_name,
            effective_max_attempts,
        )
        return candidate

    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName | str,
        content_id: ContentId | str,
        channel_id: ChannelId | str | None = None,
        content_title: str = "",
        fatal: bool = True,
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage wrapped with telemetry spans, metrics, and error handling."""
        channel_name_str = _as_str(channel_name)
        content_id_str = _as_str(content_id)
        channel_id_str = _as_str(channel_id)
        try:
            with self._measure_stage(
                stage_name=stage_name,
                channel_id=channel_id_str,
                content_id=content_id_str,
                channel_name=channel_name_str,
                content_title=content_title,
            ):
                return fn()
        except Exception as exc:
            if fatal:
                raise
            logger.warning("[Pipeline] %s skipped for %s: %s", stage_name, content_id_str, exc)
            return fallback

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
        lbls = {
            "channel_id": _as_str(channel_id),
            "channel_name": _as_str(channel_name),
            "content_id": _as_str(content_id),
        }
        self.metrics_port.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={**lbls, "status": "completed", "modality": "transcript"},
        )
        self.metrics_port.increment_counter(
            "cresmo_atomic_notes_synthesized_total",
            float(len(synthesized_notes)),
            labels={**lbls, "note_type": "all"},
        )

        item_count = len(inventory.items) if hasattr(inventory, "items") else 1
        sess_vo = (
            session_id
            if isinstance(session_id, PipelineSessionId)
            else PipelineSessionId(session_id)
        )
        cnt_vo = (
            content_id if isinstance(content_id, ContentId) else ContentId.from_string(content_id)
        )
        self.telemetry_port.record_session_coherence(
            session_id=sess_vo,
            content_id=cnt_vo,
            score=(min(1.0, len(synthesized_notes) / max(1, item_count)) if item_count else 1.0),
            details={
                "synthesized_notes_count": len(synthesized_notes),
                "inventory_count": item_count,
                "mocs_count": len(mocs),
                "duplicates_unified": dedup_report.duplicates_unified_count,
            },
        )

    # --------------------------------------------------------------------------
    # Private Helper Decomposition
    # --------------------------------------------------------------------------

    @contextmanager
    def _measure_stage(
        self,
        stage_name: str,
        channel_id: str,
        content_id: str,
        channel_name: str = "",
        content_title: str = "",
    ) -> Generator[None]:
        start_time = time.perf_counter()
        status = "success"
        stage_attributes = {
            "channel.id": channel_id,
            "content.id": content_id,
            "channel.name": channel_name,
            "content.title": content_title,
        }
        with self.telemetry_port.start_stage_span(stage_name, attributes=stage_attributes):
            try:
                yield
            except Exception as exc:
                status = "failure"
                self._record_error_metric(
                    exc=exc,
                    stage_name=stage_name,
                    channel_id=channel_id,
                    content_id=content_id,
                    channel_name=channel_name,
                )
                raise
            finally:
                self._record_duration_metric(
                    elapsed=time.perf_counter() - start_time,
                    stage_name=stage_name,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    status=status,
                )

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
    ) -> StageConfig[_TSource, _TOutput]:
        if isinstance(stage, str):
            if self.stage_factory is None:
                raise ValueError(
                    f"Cannot resolve stage '{stage}' from string without an injected StageFactory."
                )
            return self.stage_factory.build_stage(stage)
        return stage

    # Backward compatibility alias
    _resolve_stage_descriptor = _resolve_stage_config

    @staticmethod
    def _get_active_trace_id(
        channel: ChannelId | ChannelName | str | None = None,
        content_id: ContentId | str = "",
        *,
        channel_id: ChannelId | str | None = None,
        channel_name: ChannelName | str | None = None,
    ) -> str:
        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        if ctx and ctx.trace_id:
            return format(ctx.trace_id, "032x")
        effective_ch_id = channel_id or (channel if isinstance(channel, ChannelId) else None)
        effective_ch_name = channel_name or (
            channel if not isinstance(channel, ChannelId) else None
        )
        ch_token = (
            _as_str(effective_ch_id)
            if effective_ch_id
            else (_as_str(effective_ch_name) if effective_ch_name else "cresmo")
        )
        return f"cresmo_{ch_token}_{_as_str(content_id)}"

    def _synthesize_critique(self, evaluation: JudgeEvaluation, stage_name: str) -> str:
        if self.critique_synthesizer is not None:
            return self.critique_synthesizer.synthesize(evaluation, stage_name)
        return evaluation.extract_critique()

    def _record_error_metric(
        self,
        exc: Exception,
        stage_name: str,
        channel_id: str,
        content_id: str,
        channel_name: str = "",
    ) -> None:
        self.metrics_port.increment_counter(
            "cresmo_pipeline_errors_total",
            1.0,
            labels={
                "error_type": exc.__class__.__name__,
                "channel_id": channel_id,
                "content_id": content_id,
                "channel_name": channel_name,
                "stage": stage_name,
            },
        )

    def _record_duration_metric(
        self,
        elapsed: float,
        stage_name: str,
        channel_id: str,
        channel_name: str,
        status: str,
    ) -> None:
        self.metrics_port.observe_histogram(
            "cresmo_pipeline_stage_duration_seconds",
            elapsed,
            labels={
                "stage": stage_name,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "status": status,
            },
        )

    def _record_evaluation_metrics(self, stage_name: str, passed: bool, attempt: int) -> None:
        self.metrics_port.increment_counter(
            "cresmo_judge_evaluations_total",
            1.0,
            labels={"stage": stage_name, "passed": str(passed).lower(), "attempt": str(attempt)},
        )
