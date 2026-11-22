"""Telemetry and Prometheus metrics helpers for PipelineStageRunner.

Conforms to:
- ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
- ADR-026: Rule 5 (Bounded Modularity < 500 LOC)
- ADR-035: Atomic Work-Item Traces & SOTA-KISS Batch Correlation
- ADR-036: Clean Telemetry Namespacing & Observation Binding
- ADR-037: Lean Telemetry Topography and Chronological Evaluation
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle (Zero OTel SDK in Application)
"""

from __future__ import annotations

import time
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import Any

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.ports import (
    MetricsPort,
    TelemetryAttributeValue,
    TelemetryPort,
    TelemetrySpan,
    format_stage_span_name,
)
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
    telemetry_port: TelemetryPort | None = None,
    span: TelemetrySpan | None = None,
) -> str:
    """Resolve active trace ID from TelemetrySpan/TelemetryPort or build deterministic fallback."""
    active_span = (
        span
        if span is not None
        else (telemetry_port.current_span() if telemetry_port is not None else None)
    )
    if active_span is not None and isinstance(active_span.trace_id, str) and active_span.trace_id:
        return active_span.trace_id

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
        effective_ch_name = channel_name or channel
        ch_token = (
            as_str(effective_ch_id)
            if effective_ch_id
            else (as_str(effective_ch_name) if effective_ch_name else "cresmo")
        )
    return f"cresmo_{ch_token}_{resolved_cid}"


def attach_evaluation_span_attributes(
    span: TelemetrySpan | None,
    evaluation: JudgeEvaluation | None,
) -> None:
    """Attach structured LLM judge verdict, scores, reasons, and suggestions to TelemetrySpan."""
    if span is None or evaluation is None:
        return

    verdict_val = "PASS" if evaluation.passed else "NEEDS_REWRITE"
    span_attrs: dict[str, TelemetryAttributeValue] = {"judge.verdict": verdict_val}
    score_val: float | str = (
        float(evaluation.overall_score)
        if isinstance(evaluation.overall_score, (int, float))
        else str(evaluation.overall_score)
    )
    if isinstance(score_val, float):
        span_attrs["judge.overall_score"] = score_val
    span.set_attributes(span_attrs)

    scores_dict: dict[str, float | str] = {}
    reasons_dict: dict[str, str] = {}
    suggestions_dict: dict[str, str] = {}
    for criterion_entry in getattr(evaluation, "criteria_scores", ()):
        crit_key = str(getattr(criterion_entry.criterion, "value", criterion_entry.criterion))
        crit_score: float | str = (
            float(criterion_entry.score)
            if isinstance(criterion_entry.score, (int, float))
            else str(criterion_entry.score)
        )
        scores_dict[crit_key] = crit_score
        if hasattr(criterion_entry, "reasoning") and criterion_entry.reasoning:
            reasons_dict[crit_key] = str(criterion_entry.reasoning)
        if (
            hasattr(criterion_entry, "improvement_suggestion")
            and criterion_entry.improvement_suggestion
        ):
            suggestions_dict[crit_key] = str(criterion_entry.improvement_suggestion)

    eval_output: dict[str, Any] = {
        "verdict": verdict_val,
        "overall_score": score_val,
        "scores": scores_dict,
    }
    if reasons_dict:
        eval_output["reasons"] = reasons_dict
    if suggestions_dict:
        eval_output["suggestions"] = suggestions_dict

    span.set_output(eval_output)


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
    """Record completed atomic_notes metrics and session coherence evaluation telemetry."""
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
    coherence_score = (
        min(1.0, len(synthesized_notes) / max(1, item_count)) if item_count else 1.0
    )
    details = {
        "synthesized_notes_count": len(synthesized_notes),
        "inventory_count": item_count,
        "mocs_count": len(mocs),
        "duplicates_unified": dedup_report.duplicates_unified_count,
    }
    sess_vo = (
        session_id if isinstance(session_id, PipelineSessionId) else PipelineSessionId(session_id)
    )
    cnt_vo = ContentId.from_string(content_id)

    session_parts = sess_vo.value.split(":")
    channel_token = (
        session_parts[1]
        if session_parts[0] == "content" and len(session_parts) == 3
        else session_parts[0]
    )

    active_span = telemetry_port.current_span()
    active_span.set_output({"coherence_score": coherence_score, **details})
    active_span.add_event(
        "session_coherence",
        attributes={
            "eval.session_id": sess_vo.value,
            "eval.content_id": cnt_vo.value,
            "eval.channel_id": channel_token,
            "eval.coherence_score": coherence_score,
            "eval.details.synthesized_notes_count": details["synthesized_notes_count"],
            "eval.details.inventory_count": details["inventory_count"],
            "eval.details.mocs_count": details["mocs_count"],
            "eval.details.duplicates_unified": details["duplicates_unified"],
        },
    )
    telemetry_port.record_score(
        name="session_coherence",
        value=coherence_score,
        comment=f"Coherence for {cnt_vo.value}",
        trace_id=active_span.trace_id,
        observation_id=active_span.span_id,
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
) -> Generator[TelemetrySpan]:
    """Wrap stage execution in a TelemetryPort stage span and record SRE golden signals."""
    start_time = time.perf_counter()
    status = "success"
    effective_channel = context.channel if context is not None else channel
    effective_content = context.content if context is not None else content
    if effective_channel is None or effective_content is None:
        raise ValueError("_measure_stage requires context or (channel and content)")

    stage_attributes: dict[str, TelemetryAttributeValue] = {
        "cresmo.stage.channel.id": effective_channel.id.value if effective_channel.id else "",
        "cresmo.stage.content.id": effective_content.id.value,
        "cresmo.stage.channel.name": effective_channel.name,
        "cresmo.stage.content.title": effective_content.title,
    }

    with telemetry_port.start_span(
        format_stage_span_name(stage_name),
        attributes=stage_attributes,
        stage_name=stage_name,
        record_exceptions=True,
        flush_on_exit=True,
    ) as stage_span:
        try:
            yield stage_span
        except Exception as exc:
            status = "failure"
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
