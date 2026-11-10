"""Telemetry and Prometheus metrics helpers for PipelineStageRunner.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC)
- ADR-035: Atomic Work-Item Traces & SOTA-KISS Batch Correlation
- ADR-036: Clean Telemetry Namespacing & Observation Binding
- ADR-037: Lean Telemetry Topography and Chronological Evaluation
"""

from __future__ import annotations

import json
import time
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import Any

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.ports import MetricsPort, TelemetryPort
from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    MapOfContent,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    JudgeEvaluation,
)


def as_str(
    val: ChannelName | ContentId | ChannelId | PipelineSessionId | UserIdentity | str | None,
) -> str:
    """Extract canonical string value from Value Objects or return primitive string safely."""
    if val is None:
        return ""
    if isinstance(val, (ChannelName, ContentId, ChannelId, PipelineSessionId, UserIdentity)):
        return val.value
    return val


def resolve_active_trace_id(
    channel: Channel | ChannelId | ChannelName | str | None = None,
    content: Content | ContentId | str | None = None,
    *,
    context: PipelineExecutionContext | None = None,
    channel_id: ChannelId | str | None = None,
    channel_name: ChannelName | str | None = None,
    content_id: ContentId | str | None = None,
    current_span_getter: Any = None,
) -> str:
    """Resolve active OpenTelemetry 32-hex trace ID or construct deterministic fallback ID."""
    if current_span_getter is None:
        from cresmo.application.pipeline import stage_runner as _sr

        current_span_getter = _sr.trace.get_current_span
    span = current_span_getter()
    ctx = span.get_span_context() if span else None
    if ctx and ctx.trace_id:
        return format(ctx.trace_id, "032x")
    if context is not None:
        channel = context.channel
        content = context.content
    resolved_cid = (
        content.id.value
        if isinstance(content, Content)
        else (as_str(content_id) if content_id else as_str(content))
    )
    if isinstance(channel, Channel):
        ch_token = channel.id.value if channel.id else channel.name
    else:
        effective_ch_id = channel_id or (channel if isinstance(channel, ChannelId) else None)
        effective_ch_name = channel_name or (
            channel if not isinstance(channel, ChannelId) else None
        )
        ch_token = (
            as_str(effective_ch_id)
            if effective_ch_id
            else (as_str(effective_ch_name) if effective_ch_name else "cresmo")
        )
    return f"cresmo_{ch_token}_{resolved_cid}"


def attach_evaluation_span_attributes(
    current_span: Any,
    evaluation: JudgeEvaluation | None,
) -> None:
    """Attach structured LLM judge verdict, scores, reasons, and suggestions to active OTel span."""
    if not (current_span and current_span.is_recording() and evaluation is not None):
        return

    passed_val = evaluation.passed
    verdict_val = "PASS" if passed_val else "NEEDS_REWRITE"
    current_span.set_attribute("judge.verdict", verdict_val)
    score_val = (
        float(evaluation.overall_score)
        if isinstance(evaluation.overall_score, (int, float))
        else str(evaluation.overall_score)
    )
    if isinstance(score_val, float):
        current_span.set_attribute("judge.overall_score", score_val)

    scores_dict: dict[str, float | str] = {}
    reasons_dict: dict[str, str] = {}
    suggestions_dict: dict[str, str] = {}
    for c in getattr(evaluation, "criteria_scores", ()):
        crit_key = str(getattr(c.criterion, "value", c.criterion))
        crit_score = float(c.score) if isinstance(c.score, (int, float)) else str(c.score)
        scores_dict[crit_key] = crit_score
        if hasattr(c, "reasoning") and c.reasoning:
            reasons_dict[crit_key] = str(c.reasoning)
        if hasattr(c, "improvement_suggestion") and c.improvement_suggestion:
            suggestions_dict[crit_key] = str(c.improvement_suggestion)

    eval_output: dict[str, Any] = {
        "verdict": verdict_val,
        "overall_score": score_val,
        "scores": scores_dict,
    }
    if reasons_dict:
        eval_output["reasons"] = reasons_dict
    if suggestions_dict:
        eval_output["suggestions"] = suggestions_dict

    serialized_eval_out = json.dumps(eval_output)
    current_span.set_attribute("output.value", serialized_eval_out)
    current_span.set_attribute("langfuse.observation.output", serialized_eval_out)


def record_error_metric(
    metrics_port: MetricsPort,
    *,
    exc: Exception,
    stage_name: str,
    channel: Channel,
    content: Content,
) -> None:
    """Increment stage error counter with algorithmic and cognitive parity labels."""
    metrics_port.increment_counter(
        "cresmo_pipeline_errors_total",
        1.0,
        labels={
            "error_type": exc.__class__.__name__,
            "channel_id": channel.id.value if channel.id else "",
            "content_id": content.id.value,
            "channel_name": channel.name,
            "stage": stage_name,
        },
    )


def record_duration_metric(
    metrics_port: MetricsPort,
    *,
    elapsed: float,
    stage_name: str,
    channel: Channel,
    content: Content,
    status: str,
) -> None:
    """Observe stage execution duration histogram in seconds."""
    metrics_port.observe_histogram(
        "cresmo_pipeline_stage_duration_seconds",
        elapsed,
        labels={
            "stage": stage_name,
            "channel_id": channel.id.value if channel.id else "",
            "channel_name": channel.name,
            "status": status,
        },
    )


def record_evaluation_metric(
    metrics_port: MetricsPort,
    *,
    stage_name: str,
    passed: bool,
    attempt: int,
) -> None:
    """Increment judge evaluation counter."""
    metrics_port.increment_counter(
        "cresmo_judge_evaluations_total",
        1.0,
        labels={"stage": stage_name, "passed": str(passed).lower(), "attempt": str(attempt)},
    )


def record_session_completion_telemetry(
    metrics_port: MetricsPort,
    telemetry_port: TelemetryPort,
    *,
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
        "channel_id": as_str(channel_id),
        "channel_name": as_str(channel_name),
        "content_id": as_str(content_id),
    }
    metrics_port.increment_counter(
        "cresmo_transcripts_processed_total",
        1.0,
        labels={**lbls, "status": "completed", "modality": "transcript"},
    )
    metrics_port.increment_counter(
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
    telemetry_port.record_session_coherence(
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


@contextmanager
def measure_stage_execution(
    telemetry_port: TelemetryPort,
    metrics_port: MetricsPort,
    *,
    stage_name: str,
    context: PipelineExecutionContext | None = None,
    channel: Channel | None = None,
    content: Content | None = None,
) -> Generator[None]:
    """Context manager wrapping stage execution in an OTel stage span and recording golden signals."""
    start_time = time.perf_counter()
    status = "success"
    effective_channel = context.channel if context is not None else channel
    effective_content = context.content if context is not None else content
    if effective_channel is None or effective_content is None:
        raise ValueError("_measure_stage requires context or (channel and content)")
    stage_attributes = {
        "channel.id": effective_channel.id.value if effective_channel.id else "",
        "content.id": effective_content.id.value,
        "channel.name": effective_channel.name,
        "content.title": effective_content.title,
    }
    with telemetry_port.start_stage_span(stage_name, attributes=stage_attributes):
        try:
            yield
        except Exception as exc:
            status = "failure"
            from cresmo.application.pipeline import stage_runner as _sr

            current_span = _sr.trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.record_exception(exc)
                current_span.set_status(_sr.trace.StatusCode.ERROR, str(exc))
                current_span.set_attribute("langfuse.observation.level", "ERROR")
            record_error_metric(
                metrics_port,
                exc=exc,
                stage_name=stage_name,
                channel=effective_channel,
                content=effective_content,
            )
            raise
        finally:
            record_duration_metric(
                metrics_port,
                elapsed=time.perf_counter() - start_time,
                stage_name=stage_name,
                channel=effective_channel,
                content=effective_content,
                status=status,
            )
