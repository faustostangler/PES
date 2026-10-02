"""Telemetry-instrumented stage execution runner and session metrics recorder."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence
from typing import Literal, TypeVar, overload

from opentelemetry import trace

from cresmo.application.ports import (
    LlmJudgePort,
    MetricsPort,
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
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    StageEvaluationSpec,
)

logger = logging.getLogger(__name__)

_StageRet = TypeVar("_StageRet")


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(
        self,
        telemetry_port: TelemetryPort,
        metrics_port: MetricsPort,
        llm_judge: LlmJudgePort | None = None,
        judge_blocking: bool = False,
        judge_max_attempts: int = 1,
    ) -> None:
        self.telemetry_port = telemetry_port
        self.metrics_port = metrics_port
        self.llm_judge = llm_judge
        self.judge_blocking = judge_blocking
        self.judge_max_attempts = judge_max_attempts

    @overload
    def run_evaluated_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        eval_spec: StageEvaluationSpec | None = ...,
        channel_id: ChannelId | None = ...,
        fatal: Literal[True] = ...,
        fallback: _StageRet | None = ...,
    ) -> _StageRet: ...

    @overload
    def run_evaluated_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        eval_spec: StageEvaluationSpec | None = ...,
        channel_id: ChannelId | None = ...,
        fatal: Literal[False],
        fallback: _StageRet | None = ...,
    ) -> _StageRet | None: ...

    def run_evaluated_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        eval_spec: StageEvaluationSpec | None = None,
        channel_id: ChannelId | None = None,
        fatal: bool = True,
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage within a closed-loop quality evaluation gate with retries.

        If eval_spec or llm_judge is None, delegates directly to run_stage without evaluation.
        Otherwise, repeatedly executes fn() up to max_attempts until the judge evaluation passes.
        If all attempts fail and judge_blocking is True, raises DomainValidationError.
        If judge_blocking is False, logs a warning and returns candidate result.
        """
        if self.llm_judge is None or eval_spec is None:
            return self.run_stage(
                stage_name,
                fn,
                channel_name=channel_name,
                content_id=content_id,
                channel_id=channel_id,
                fatal=fatal,
                fallback=fallback,
            )

        effective_max_attempts = max(eval_spec.max_attempts, self.judge_max_attempts)
        candidate: _StageRet | None = None
        evaluation = None

        for attempt in range(1, effective_max_attempts + 1):
            candidate = self.run_stage(
                stage_name,
                fn,
                channel_name=channel_name,
                content_id=content_id,
                channel_id=channel_id,
                fatal=fatal,
                fallback=fallback,
            )

            if candidate is None:
                return fallback

            candidate_text = eval_spec.candidate_extractor(candidate)

            span = trace.get_current_span()
            ctx = span.get_span_context() if span else None
            active_trace_id = (
                format(ctx.trace_id, "032x")
                if ctx and ctx.trace_id
                else f"cresmo_{channel_name.value}_{content_id.value}"
            )

            eval_metadata = {
                "content_id": content_id.value,
                "channel_name": channel_name.value,
                "attempt": attempt,
                **eval_spec.metadata,
            }

            eval_context = EvaluationContext(
                stage_name=stage_name,
                raw_text=eval_spec.raw_text,
                candidate_text=candidate_text,
                metadata=eval_metadata,
                trace_id=active_trace_id,
                required_criteria=eval_spec.required_criteria,
            )

            evaluation = self.llm_judge.evaluate(eval_context)

            self.metrics_port.increment_counter(
                "cresmo_judge_evaluations_total",
                1.0,
                labels={
                    "stage": stage_name,
                    "passed": str(evaluation.passed).lower(),
                    "attempt": str(attempt),
                },
            )

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
                    "cresmo_judge_retries_total",
                    1.0,
                    labels={"stage": stage_name},
                )

        if self.judge_blocking:
            score_str = f"{evaluation.overall_score:.2f}" if evaluation else "0.00"
            raise DomainValidationError(
                f"{stage_name} quality evaluation failed threshold after {effective_max_attempts} attempts: {score_str}"
            )

        logger.warning(
            "Quality evaluation for '%s' exhausted all %d attempts without passing. Returning candidate as judge_blocking is False.",
            stage_name,
            effective_max_attempts,
        )
        return candidate

    @overload
    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = ...,
        fatal: Literal[True] = ...,
        fallback: _StageRet | None = ...,
    ) -> _StageRet: ...

    @overload
    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = ...,
        fatal: Literal[False],
        fallback: _StageRet | None = ...,
    ) -> _StageRet | None: ...

    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = None,
        fatal: bool = True,
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage wrapped with telemetry spans, metrics, and error handling.

        Args:
            stage_name: Identifier for the stage (e.g. 'fluid_prose', 'atomic_batch').
            fn: Callable executing the use case logic.
            channel_name: Target channel name for metric labeling (cognitive).
            content_id: Target content identifier for audit logging and metrics (algorithmic).
            channel_id: Optional platform channel ID (algorithmic).
            fatal: If True, re-raises any caught exception. If False, logs warning and returns fallback.
            fallback: Value returned when non-fatal execution encounters an exception.

        Returns:
            Result of fn() or fallback if non-fatal exception caught.
        """
        start_time = time.perf_counter()
        status = "success"
        ch_id_str = channel_id.value if channel_id else ""

        with self.telemetry_port.start_stage_span(stage_name):
            try:
                return fn()
            except Exception as exc:
                status = "failure"
                self.metrics_port.increment_counter(
                    "cresmo_pipeline_errors_total",
                    1.0,
                    labels={
                        "error_type": exc.__class__.__name__,
                        "channel_id": ch_id_str,
                        "channel_name": channel_name.value,
                        "content_id": content_id.value,
                        "stage": stage_name,
                    },
                )
                if fatal:
                    raise
                logger.warning(
                    "[Pipeline] %s skipped for %s: %s",
                    stage_name,
                    content_id.value,
                    exc,
                )
                return fallback
            finally:
                elapsed = time.perf_counter() - start_time
                self.metrics_port.observe_histogram(
                    "cresmo_pipeline_stage_duration_seconds",
                    elapsed,
                    labels={
                        "stage": stage_name,
                        "channel_id": ch_id_str,
                        "channel_name": channel_name.value,
                        "status": status,
                    },
                )

    def record_session_completion(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        channel_name: ChannelName,
        synthesized_notes: Sequence[AtomicNote],
        inventory: AtomicEntityInventory,
        mocs: Sequence[MapOfContent],
        dedup_report: DeduplicationReport,
        channel_id: ChannelId | None = None,
    ) -> None:
        """Record completed process metrics and session coherence evaluation score."""
        ch_id_str = channel_id.value if channel_id else ""
        self.metrics_port.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": ch_id_str,
                "channel_name": channel_name.value,
                "content_id": content_id.value,
                "status": "completed",
                "modality": "transcript",
            },
        )
        self.metrics_port.increment_counter(
            "cresmo_atomic_notes_synthesized_total",
            float(len(synthesized_notes)),
            labels={
                "channel_id": ch_id_str,
                "channel_name": channel_name.value,
                "content_id": content_id.value,
                "note_type": "all",
            },
        )

        item_count = len(inventory.items) if hasattr(inventory, "items") else 1
        coherence_score = (
            min(1.0, len(synthesized_notes) / max(1, item_count)) if item_count else 1.0
        )
        self.telemetry_port.record_session_coherence(
            session_id=session_id,
            content_id=content_id,
            score=coherence_score,
            details={
                "synthesized_notes_count": len(synthesized_notes),
                "inventory_count": item_count,
                "mocs_count": len(mocs),
                "duplicates_unified": dedup_report.duplicates_unified_count,
            },
        )
