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
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Final

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.ports import (
    MetricName,
    MetricsPort,
    TelemetryAttributeValue,
    TelemetryPort,
    TelemetrySpan,
    format_stage_span_name,
)
from cresmo.domain.value_objects import (
    Channel,
    JudgeEvaluation,
)

FALLBACK_TRACE_ID_PREFIX: Final[str] = "cresmo_"
JUDGE_VERDICT_PASS: Final[str] = "PASS"
JUDGE_VERDICT_NEEDS_REWRITE: Final[str] = "NEEDS_REWRITE"
SPAN_ATTR_JUDGE_VERDICT: Final[str] = "judge.verdict"
SPAN_ATTR_JUDGE_OVERALL_SCORE: Final[str] = "judge.overall_score"
SPAN_ATTR_STAGE_CHANNEL_ID: Final[str] = "cresmo.stage.channel.id"
SPAN_ATTR_STAGE_CONTENT_ID: Final[str] = "cresmo.stage.content.id"
SPAN_ATTR_STAGE_CHANNEL_NAME: Final[str] = "cresmo.stage.channel.name"
SPAN_ATTR_STAGE_CONTENT_TITLE: Final[str] = "cresmo.stage.content.title"

_EVAL_OUT_KEY_VERDICT: Final[str] = "verdict"
_EVAL_OUT_KEY_OVERALL_SCORE: Final[str] = "overall_score"
_EVAL_OUT_KEY_SCORES: Final[str] = "scores"
_EVAL_OUT_KEY_REASONS: Final[str] = "reasons"
_EVAL_OUT_KEY_SUGGESTIONS: Final[str] = "suggestions"

METRIC_INCREMENT_ONE: Final[float] = 1.0
METRIC_LABEL_ERROR_TYPE: Final[str] = "error_type"
METRIC_LABEL_CHANNEL_ID: Final[str] = "channel_id"
METRIC_LABEL_STAGE: Final[str] = "stage"
METRIC_LABEL_STATUS: Final[str] = "status"
METRIC_LABEL_PASSED: Final[str] = "passed"
METRIC_LABEL_ATTEMPT: Final[str] = "attempt"
STAGE_METRIC_STATUS_SUCCESS: Final[str] = "success"
STAGE_METRIC_STATUS_FAILURE: Final[str] = "failure"


def resolve_active_trace_id(
    context: PipelineExecutionContext,
    *,
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

    ch_token = context.channel.id.value if context.channel.id else context.channel.name
    return f"{FALLBACK_TRACE_ID_PREFIX}{ch_token}_{context.content.id.value}"


def attach_evaluation_span_attributes(
    span: TelemetrySpan | None,
    evaluation: JudgeEvaluation | None,
) -> None:
    """Attach structured LLM judge verdict, scores, reasons, and suggestions to TelemetrySpan."""
    if span is None or evaluation is None:
        return

    verdict_val = JUDGE_VERDICT_PASS if evaluation.passed else JUDGE_VERDICT_NEEDS_REWRITE
    score_val = float(evaluation.overall_score)
    span.set_attributes(
        {
            SPAN_ATTR_JUDGE_VERDICT: verdict_val,
            SPAN_ATTR_JUDGE_OVERALL_SCORE: score_val,
        }
    )

    scores_dict: dict[str, float] = {}
    reasons_dict: dict[str, str] = {}
    suggestions_dict: dict[str, str] = {}
    for criterion_entry in evaluation.criteria_scores:
        crit_key = criterion_entry.criterion.value
        scores_dict[crit_key] = float(criterion_entry.score)
        if criterion_entry.reasoning:
            reasons_dict[crit_key] = criterion_entry.reasoning
        if criterion_entry.improvement_suggestion:
            suggestions_dict[crit_key] = criterion_entry.improvement_suggestion

    eval_output: dict[str, Any] = {
        _EVAL_OUT_KEY_VERDICT: verdict_val,
        _EVAL_OUT_KEY_OVERALL_SCORE: score_val,
        _EVAL_OUT_KEY_SCORES: scores_dict,
    }
    if reasons_dict:
        eval_output[_EVAL_OUT_KEY_REASONS] = reasons_dict
    if suggestions_dict:
        eval_output[_EVAL_OUT_KEY_SUGGESTIONS] = suggestions_dict

    span.set_output(eval_output)


def record_error_metric(
    metrics_port: MetricsPort,
    *,
    exc: Exception,
    stage_name: str,
    channel: Channel,
) -> None:
    """Increment stage error counter with low-cardinality dimensional labels."""
    metrics_port.increment_counter(
        MetricName.PIPELINE_ERRORS,
        METRIC_INCREMENT_ONE,
        labels={
            METRIC_LABEL_ERROR_TYPE: exc.__class__.__name__,
            METRIC_LABEL_CHANNEL_ID: channel.id.value if channel.id else "",
            METRIC_LABEL_STAGE: stage_name,
        },
    )


def record_duration_metric(
    metrics_port: MetricsPort,
    *,
    elapsed: float,
    stage_name: str,
    channel: Channel,
    status: str,
) -> None:
    """Observe stage execution duration histogram in seconds."""
    metrics_port.observe_histogram(
        MetricName.PIPELINE_STAGE_DURATION,
        elapsed,
        labels={
            METRIC_LABEL_STAGE: stage_name,
            METRIC_LABEL_CHANNEL_ID: channel.id.value if channel.id else "",
            METRIC_LABEL_STATUS: status,
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
        MetricName.JUDGE_EVALUATIONS,
        METRIC_INCREMENT_ONE,
        labels={
            METRIC_LABEL_STAGE: stage_name,
            METRIC_LABEL_PASSED: str(passed).lower(),
            METRIC_LABEL_ATTEMPT: str(attempt),
        },
    )


@contextmanager
def measure_stage_execution(
    telemetry_port: TelemetryPort,
    metrics_port: MetricsPort,
    *,
    stage_name: str,
    context: PipelineExecutionContext,
) -> Generator[TelemetrySpan]:
    """Wrap stage execution in a TelemetryPort stage span and record SRE golden signals."""
    start_time = time.perf_counter()
    status = STAGE_METRIC_STATUS_SUCCESS
    effective_channel = context.channel
    effective_content = context.content

    stage_attributes: dict[str, TelemetryAttributeValue] = {
        SPAN_ATTR_STAGE_CHANNEL_ID: effective_channel.id.value if effective_channel.id else "",
        SPAN_ATTR_STAGE_CONTENT_ID: effective_content.id.value,
        SPAN_ATTR_STAGE_CHANNEL_NAME: effective_channel.name,
        SPAN_ATTR_STAGE_CONTENT_TITLE: effective_content.title,
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
            status = STAGE_METRIC_STATUS_FAILURE
            record_error_metric(
                metrics_port,
                exc=exc,
                stage_name=stage_name,
                channel=effective_channel,
            )
            raise
        finally:
            record_duration_metric(
                metrics_port,
                elapsed=time.perf_counter() - start_time,
                stage_name=stage_name,
                channel=effective_channel,
                status=status,
            )
