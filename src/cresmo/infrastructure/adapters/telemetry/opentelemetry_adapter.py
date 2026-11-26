"""OpenTelemetry infrastructure adapter for Cresmo Knowledge Synthesis Modular Monolith.

Conforms to:
- ADR-016: OpenTelemetry Semantic Conventions & Session Replays
- ADR-037: Lean Telemetry Topography
- ADR-063: Zero Attribute Duplication & Dynamic Versioning
- ADR-065: Hierarchical Stage-Scoped Nomenclature & Deterministic Post-Span Flush
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from collections.abc import Generator, Mapping
from contextlib import contextmanager, nullcontext
from typing import Any, Final

import structlog
from opentelemetry import trace
from opentelemetry.trace import Tracer

from cresmo.application.ports.telemetry import (
    SessionTelemetrySpec,
    SpanKind,
    TelemetryAttributeValue,
    TelemetryPort,
    TelemetrySpan,
    active_telemetry_stage,
)
from cresmo.infrastructure.adapters.telemetry.otel_span import (
    OTelTelemetrySpan,
    is_valid_otel_value,
    wrap_current_otel_span,
)
from cresmo.infrastructure.adapters.telemetry.session_mapper import (
    build_propagated_trace_metadata,
    build_session_span_attributes,
    resolve_root_operation_name,
    short_git_sha,
)
from cresmo.infrastructure.adapters.telemetry.thread_naming import name_telemetry_threads
from cresmo.infrastructure.config import resolve_default_pipeline_version

logger = structlog.get_logger(__name__)

DEFAULT_PIPELINE_VERSION: Final[str] = resolve_default_pipeline_version()
OTEL_FLUSH_TIMEOUT_MS: Final[int] = 2000
_TRACER_NAME: Final[str] = "cresmo.pipeline"
_ATTR_OBSERVATION_TYPE: Final[str] = "langfuse.observation.type"
_ATTR_SCORE_NAME: Final[str] = "score.name"
_ATTR_SCORE_VALUE: Final[str] = "score.value"
_ATTR_SCORE_COMMENT: Final[str] = "score.comment"
_ATTR_SCORE_TRACE_ID: Final[str] = "score.trace_id"
_ATTR_SCORE_OBSERVATION_ID: Final[str] = "score.observation_id"
_EVENT_TELEMETRY_SCORE: Final[str] = "telemetry_score"
_KEY_NAME: Final[str] = "name"
_KEY_VALUE: Final[str] = "value"
_KEY_COMMENT: Final[str] = "comment"
_KEY_TRACE_ID: Final[str] = "trace_id"
_KEY_OBSERVATION_ID: Final[str] = "observation_id"


# Defer langfuse import to runtime per ADR-026/ADR-053/ADR-055
def propagate_attributes(**kwargs: Any) -> Any:
    """Propagate trace attributes lazily through Langfuse context (ADR-055)."""
    from langfuse import propagate_attributes as _real_propagate

    return _real_propagate(**kwargs)


class OpenTelemetryAdapter(TelemetryPort):
    """Production TelemetryPort integrating CNCF OpenTelemetry and Langfuse."""

    def __init__(
        self,
        tracer: Tracer | None = None,
        langfuse_client: Any | None = None,
        pipeline_version: str | None = None,
        git_sha: str | None = None,
    ) -> None:
        self._tracer = tracer or trace.get_tracer(_TRACER_NAME)
        self._langfuse = langfuse_client
        self._pipeline_version = pipeline_version or DEFAULT_PIPELINE_VERSION
        self._git_sha: str | None = short_git_sha(git_sha)
        name_telemetry_threads(langfuse_client)

    @contextmanager
    def start_session(
        self,
        spec: SessionTelemetrySpec,
    ) -> Generator[TelemetrySpan]:
        """Initiate root OpenTelemetry span, bind Langfuse propagation, and flush after exit."""
        resolved_trace_name, root_operation = resolve_root_operation_name(spec.trace_name)
        session_attributes, tags, input_payload = build_session_span_attributes(
            spec,
            pipeline_version=self._pipeline_version,
            git_sha=self._git_sha,
            resolved_trace_name=resolved_trace_name,
        )

        # Outer finally drains buffers AFTER the root span closes (ADR-065).
        try:
            with self._tracer.start_as_current_span(
                root_operation,
                attributes=session_attributes,
                record_exception=False,
                set_status_on_exception=False,
            ) as otel_span:
                wrapped = OTelTelemetrySpan(otel_span, is_root=True)
                wrapped.set_input(input_payload)

                propagation_context: Any = nullcontext()
                if self._langfuse is not None:
                    try:
                        propagation_context = propagate_attributes(
                            session_id=spec.session_id.value,
                            user_id=spec.user_id.value,
                            tags=tags,
                            trace_name=resolved_trace_name,
                            metadata=build_propagated_trace_metadata(session_attributes),
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("Failed to initialize Langfuse propagate_attributes: %s", exc)

                with propagation_context:
                    try:
                        yield wrapped
                    except Exception as exc:
                        wrapped.record_error(exc)
                        raise
        finally:
            self.flush()

    @contextmanager
    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.SPAN,
        attributes: Mapping[str, TelemetryAttributeValue] | None = None,
        stage_name: str | None = None,
        record_exceptions: bool = True,
        flush_on_exit: bool = False,
    ) -> Generator[TelemetrySpan]:
        """Create child OTel span with creation-time observation kind and optional stage scope."""
        init_attributes: dict[str, Any] = {_ATTR_OBSERVATION_TYPE: kind.value}
        if attributes:
            for key, value in attributes.items():
                if is_valid_otel_value(value):
                    init_attributes[key] = value

        stage_ctx = active_telemetry_stage(stage_name) if stage_name is not None else nullcontext()
        try:
            with (
                stage_ctx,
                self._tracer.start_as_current_span(
                    name,
                    attributes=init_attributes,
                    record_exception=False,
                    set_status_on_exception=False,
                ) as otel_span,
            ):
                wrapped = OTelTelemetrySpan(otel_span, is_root=False)
                try:
                    yield wrapped
                except Exception as exc:
                    if record_exceptions:
                        wrapped.record_error(exc)
                    raise
        finally:
            if flush_on_exit:
                self.flush()

    def current_span(self) -> TelemetrySpan:
        """Return TelemetrySpan handle wrapping the active recording OTel span."""
        return wrap_current_otel_span()

    def record_score(
        self,
        *,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
        observation_id: str | None = None,
    ) -> None:
        """Emit an evaluation or clinical score to active span event and Langfuse backend."""
        active_span = wrap_current_otel_span()
        resolved_observation_id = (
            observation_id if observation_id is not None else active_span.span_id
        )

        event_attributes: dict[str, TelemetryAttributeValue] = {
            _ATTR_SCORE_NAME: name,
            _ATTR_SCORE_VALUE: value,
        }
        if comment:
            event_attributes[_ATTR_SCORE_COMMENT] = comment
        if trace_id:
            event_attributes[_ATTR_SCORE_TRACE_ID] = trace_id
        if resolved_observation_id:
            event_attributes[_ATTR_SCORE_OBSERVATION_ID] = resolved_observation_id
        if isinstance(active_span, OTelTelemetrySpan):
            active_span.add_event(_EVENT_TELEMETRY_SCORE, attributes=event_attributes)

        if self._langfuse is not None:
            score_fn = getattr(self._langfuse, "create_score", None)
            if callable(score_fn):
                try:
                    score_arguments: dict[str, Any] = {_KEY_NAME: name, _KEY_VALUE: value}
                    if comment is not None:
                        score_arguments[_KEY_COMMENT] = comment
                    if trace_id is not None:
                        score_arguments[_KEY_TRACE_ID] = trace_id
                    if resolved_observation_id is not None:
                        score_arguments[_KEY_OBSERVATION_ID] = resolved_observation_id
                    score_fn(**score_arguments)
                except Exception as exc:  # noqa: BLE001
                    logger.debug("[OpenTelemetryAdapter] Langfuse score emission skipped: %s", exc)

    def flush(self) -> None:
        """Flush Langfuse client queues and OpenTelemetry TracerProvider buffers."""
        if self._langfuse is not None:
            try:
                self._langfuse.flush()
            except Exception as exc:  # noqa: BLE001
                logger.debug("[OpenTelemetryAdapter] Langfuse client flush skipped: %s", exc)
        try:
            tracer_provider = trace.get_tracer_provider()
            force_flush_method = getattr(tracer_provider, "force_flush", None)
            if callable(force_flush_method):
                force_flush_method(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "[OpenTelemetryAdapter] OpenTelemetry tracer provider flush skipped: %s",
                exc,
            )


__all__ = [
    "DEFAULT_PIPELINE_VERSION",
    "OTEL_FLUSH_TIMEOUT_MS",
    "OpenTelemetryAdapter",
    "name_telemetry_threads",
    "propagate_attributes",
]
