"""Telemetry-instrumented stage execution runner and session metrics recorder."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal, TypeVar, overload

from opentelemetry import trace

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.stage_descriptor import StageDescriptor
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
from cresmo.domain.exceptions import DomainValidationError, StageQuarantinedError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CandidateText,
    ChannelId,
    ChannelName,
    ContentId,
    EvaluationContext,
    LedgerEntry,
    PipelineStatus,
    StageEvaluationSpec,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline.stage_factory import StageFactory

logger = logging.getLogger(__name__)

_StageRet = TypeVar("_StageRet")
_TSource = TypeVar("_TSource")
_TOutput = TypeVar("_TOutput")


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(
        self,
        telemetry_port: TelemetryPort,
        metrics_port: MetricsPort,
        llm_judge: LlmJudgePort | None = None,
        judge_blocking: bool = False,
        judge_max_attempts: int = 1,
        prompt_provider: PromptProviderPort | None = None,
        llm_transformation_port: LLMTransformationPort | None = None,
        stage_factory: StageFactory | None = None,
        critique_synthesizer: CritiqueSynthesizerPort | None = None,
        ledger_port: LedgerRepositoryPort | None = None,
    ) -> None:
        self.telemetry_port = telemetry_port
        self.metrics_port = metrics_port
        self.llm_judge = llm_judge
        self.judge_blocking = judge_blocking
        self.judge_max_attempts = judge_max_attempts
        self.prompt_provider = prompt_provider
        self.llm_transformation_port = llm_transformation_port
        self.stage_factory = stage_factory
        self.critique_synthesizer = critique_synthesizer
        self.ledger_port = ledger_port

    def execute_stage(
        self,
        stage: str | StageDescriptor[_TSource, _TOutput] | None = None,
        source: _TSource | None = None,
        *,
        descriptor: StageDescriptor[_TSource, _TOutput] | None = None,
        context: PipelineExecutionContext | None = None,
        channel_name: ChannelName | None = None,
        content_id: ContentId | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        prompt_provider: PromptProviderPort | None = None,
        llm_transformation_port: LLMTransformationPort | None = None,
        channel_id: ChannelId | None = None,
    ) -> _TOutput:
        """Execute a standardized pipeline stage with closed-loop reflection, critique, and telemetry.

        Conforms to ADR-031:
        1. Resolves stage descriptor dynamically via string identifier from StageFactory or direct StageDescriptor.
        2. Resolves provenance either via PipelineExecutionContext or individual arguments.
        3. Resolves prompts via prompt_provider (injecting directed critique on retry attempts).
        4. Executes LLM transformation to produce CandidateText.
        5. If judge and eval_spec are configured, validates CandidateText.
        6. If validation fails and attempts remain, synthesizes directed critique via Ollama and retries.
        7. If attempts are exhausted and blocking is True, initiates Fail-Fast with Quarantine:
           - Records quarantine status in SQLite Ledger.
           - Sets quarantine span attributes in OpenTelemetry/Langfuse.
           - Increments Prometheus counter 'cresmo_stage_quarantines_total'.
           - Raises StageQuarantinedError.
        8. Runs optional post_processor and returns output domain aggregate.
        """
        if source is None:
            raise ValueError("source must be provided to execute_stage")

        target_descriptor: StageDescriptor[_TSource, _TOutput]
        if stage is not None:
            if isinstance(stage, str):
                if self.stage_factory is None:
                    raise ValueError(
                        f"Cannot resolve stage '{stage}' from string without an injected StageFactory."
                    )
                target_descriptor = self.stage_factory.build_stage(stage)
            else:
                target_descriptor = stage
        elif descriptor is not None:
            target_descriptor = descriptor
        else:
            raise ValueError("Must provide either 'stage' or 'descriptor' to execute_stage.")

        if context is not None:
            c_name = context.channel_name
            c_id = context.content_id
            s_id = context.session_id.value
            u_id = context.user_identity.value
            ch_id = context.channel_id
        else:
            if channel_name is None or content_id is None or session_id is None or user_id is None:
                raise ValueError(
                    "Must provide either 'context' or all provenance keyword arguments"
                )
            c_name = channel_name
            c_id = content_id
            s_id = session_id
            u_id = user_id
            ch_id = channel_id

        p_provider = prompt_provider or self.prompt_provider
        if p_provider is None:
            raise ValueError(
                "PromptProviderPort must be provided via constructor or execute_stage argument"
            )

        llm_port = llm_transformation_port or self.llm_transformation_port
        if llm_port is None:
            raise ValueError(
                "LLMTransformationPort must be provided via constructor or execute_stage argument"
            )

        start_time = time.perf_counter()
        status = "success"
        ch_id_str = ch_id.value if ch_id else ""
        stage_name = target_descriptor.stage_name

        effective_max_attempts = max(
            target_descriptor.max_attempts,
            target_descriptor.eval_spec.max_attempts if target_descriptor.eval_spec else 1,
            self.judge_max_attempts,
        )

        critique: str | None = None
        candidate: CandidateText | None = None
        evaluation = None

        with self.telemetry_port.start_stage_span(stage_name):
            try:
                for attempt in range(1, effective_max_attempts + 1):
                    # 1. Build prompt (clean on attempt 1, injected directed critique on attempt > 1)
                    system_instruction, user_prompt = target_descriptor.build_transform_prompt(
                        p_provider,
                        source,
                        channel_name=c_name.value,
                        content_id=c_id.value,
                        critique=critique,
                    )

                    # 2. Invoke LLM transformation to generate CandidateText
                    span = trace.get_current_span()
                    ctx = span.get_span_context() if span else None
                    active_trace_id = (
                        format(ctx.trace_id, "032x")
                        if ctx and ctx.trace_id
                        else f"cresmo_{c_name.value}_{c_id.value}"
                    )

                    raw_output = llm_port.transform(
                        prompt=user_prompt,
                        system_instruction=system_instruction,
                        temperature=target_descriptor.temperature,
                        trace_id=active_trace_id,
                        session_id=s_id,
                        user_id=u_id,
                    )

                    candidate = CandidateText(
                        text=raw_output,
                        stage_name=stage_name,
                        metadata={
                            "content_id": c_id.value,
                            "channel_name": c_name.value,
                            "attempt": attempt,
                        },
                    )

                    # 3. Judge evaluation quality gate
                    if self.llm_judge is None or target_descriptor.eval_spec is None:
                        break

                    candidate_eval_text = (
                        target_descriptor.eval_spec.candidate_extractor(candidate)
                        if target_descriptor.eval_spec.candidate_extractor
                        else candidate.text
                    )

                    eval_metadata = {
                        "content_id": c_id.value,
                        "channel_name": c_name.value,
                        "attempt": attempt,
                        **target_descriptor.eval_spec.metadata,
                    }

                    raw_text_target = (
                        target_descriptor.eval_spec.extract_source_text(source)
                        if target_descriptor.eval_spec
                        else getattr(source, "body", str(source))
                    )

                    eval_context = EvaluationContext(
                        stage_name=stage_name,
                        raw_text=raw_text_target,
                        candidate_text=candidate_eval_text,
                        metadata=eval_metadata,
                        trace_id=active_trace_id,
                        required_criteria=target_descriptor.eval_spec.required_criteria,
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
                        break

                    logger.warning(
                        "Quality evaluation for '%s' reported low score on attempt %d/%d (overall=%.2f, passed=%s).",
                        stage_name,
                        attempt,
                        effective_max_attempts,
                        evaluation.overall_score,
                        evaluation.passed,
                    )

                    # Synthesize directed critique via Ollama or fallback to judge critique
                    if self.critique_synthesizer is not None:
                        critique = self.critique_synthesizer.synthesize(evaluation, stage_name)
                    else:
                        critique = evaluation.extract_critique()

                    if attempt < effective_max_attempts:
                        self.metrics_port.increment_counter(
                            "cresmo_judge_retries_total",
                            1.0,
                            labels={"stage": stage_name},
                        )

                # Check if evaluation passed or fail-fast with quarantine is triggered
                if (
                    evaluation is not None
                    and not evaluation.passed
                    and (target_descriptor.blocking or self.judge_blocking)
                ):
                    # Fail-Fast with Quarantine (ADR-031)
                    if critique is None:
                        if self.critique_synthesizer is not None:
                            critique = self.critique_synthesizer.synthesize(evaluation, stage_name)
                        else:
                            critique = evaluation.extract_critique()

                    # 1. SQLite Ledger Audit Record
                    if self.ledger_port is not None:
                        try:
                            existing = self.ledger_port.get_entry(c_id)
                            media_url = (
                                existing.media_url
                                if existing
                                else f"https://cresmo.internal/content/{c_id.value}"
                            )
                            title = (
                                existing.title if existing else f"Quarantined Content {c_id.value}"
                            )
                            started_at = existing.started_at if existing else None
                            entry = LedgerEntry(
                                content_id=c_id,
                                media_url=media_url,
                                title=title,
                                channel_name=c_name,
                                status=PipelineStatus.QUARANTINED,
                                error_message=f"Stage '{stage_name}' quarantined: {critique}",
                                started_at=started_at,
                                completed_at=datetime.now(UTC),
                            )
                            self.ledger_port.save_entry(entry)
                        except Exception as ledger_err:  # noqa: BLE001 - Resilient audit persistence
                            logger.error(
                                "Failed to record quarantine entry in ledger for %s: %s",
                                c_id.value,
                                ledger_err,
                            )

                    # 2. Tag Span in OpenTelemetry / Langfuse
                    span = trace.get_current_span()
                    if span:
                        span.set_attribute("quarantined", True)
                        span.set_attribute("quarantine.stage", stage_name)
                        span.set_attribute("quarantine.critique", critique or "")
                        span.set_attribute("quarantine.attempts", effective_max_attempts)
                        span.set_attribute("quarantine.overall_score", evaluation.overall_score)

                    # 3. Increment Prometheus Metric
                    self.metrics_port.increment_counter(
                        "cresmo_stage_quarantines_total",
                        1.0,
                        labels={"stage": stage_name, "channel_name": c_name.value},
                    )

                    # 4. Raise StageQuarantinedError
                    raise StageQuarantinedError(
                        stage_name=stage_name,
                        content_id=c_id.value,
                        attempts=effective_max_attempts,
                        critique=critique or "",
                        overall_score=evaluation.overall_score,
                    )

                if candidate is None:
                    raise DomainValidationError(f"Stage '{stage_name}' produced no candidate text.")

                # 4. Optional Post-Processing
                if target_descriptor.post_processor is not None:
                    return target_descriptor.post_processor(candidate, source)

                return candidate  # type: ignore[return-value]

            except Exception as exc:
                status = "failure"
                self.metrics_port.increment_counter(
                    "cresmo_pipeline_errors_total",
                    1.0,
                    labels={
                        "error_type": exc.__class__.__name__,
                        "channel_id": ch_id_str,
                        "channel_name": c_name.value,
                        "content_id": c_id.value,
                        "stage": stage_name,
                    },
                )
                raise
            finally:
                elapsed = time.perf_counter() - start_time
                self.metrics_port.observe_histogram(
                    "cresmo_pipeline_stage_duration_seconds",
                    elapsed,
                    labels={
                        "stage": stage_name,
                        "channel_id": ch_id_str,
                        "channel_name": c_name.value,
                        "status": status,
                    },
                )

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
