"""Hermetic in-memory TelemetryPort test double for unit and integration suites.

Records full span trees, attributes, inputs, outputs, events, exceptions, scores,
and flush ordering without depending on OpenTelemetry or Langfuse SDKs.

Conforms to ADR-070 and SPEC-070.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field

from cresmo.application.ports.telemetry import (
    NOOP_TELEMETRY_SPAN,
    SessionTelemetrySpec,
    SpanKind,
    TelemetryAttributeValue,
    TelemetryPayload,
    TelemetryPort,
    TelemetrySpan,
    active_telemetry_stage,
)


@dataclass
class RecordedScore:
    """Captured evaluation or clinical score emitted to InMemoryTelemetryPort."""

    name: str
    value: float
    comment: str | None = None
    trace_id: str | None = None
    observation_id: str | None = None


@dataclass
class RecordedSpan:
    """In-memory TelemetrySpan implementation capturing all telemetry mutations."""

    name: str
    kind: SpanKind
    trace_id_value: str
    span_id_value: str
    parent_span_id: str | None = None
    is_root: bool = False
    session_spec: SessionTelemetrySpec | None = None
    attributes: dict[str, TelemetryAttributeValue] = field(default_factory=dict)
    inputs: list[TelemetryPayload] = field(default_factory=list)
    outputs: list[TelemetryPayload] = field(default_factory=list)
    events: list[tuple[str, dict[str, TelemetryAttributeValue]]] = field(default_factory=list)
    errors: list[BaseException] = field(default_factory=list)
    closed: bool = False

    @property
    def trace_id(self) -> str | None:
        return self.trace_id_value

    @property
    def span_id(self) -> str | None:
        return self.span_id_value

    def set_attributes(self, attributes: Mapping[str, TelemetryAttributeValue]) -> None:
        self.attributes.update(attributes)

    def set_input(self, payload: TelemetryPayload) -> None:
        self.inputs.append(payload)

    def set_output(self, payload: TelemetryPayload) -> None:
        self.outputs.append(payload)

    def add_event(
        self,
        name: str,
        attributes: Mapping[str, TelemetryAttributeValue] | None = None,
    ) -> None:
        self.events.append((name, dict(attributes) if attributes else {}))

    def record_error(self, exc: BaseException) -> None:
        self.errors.append(exc)


class InMemoryTelemetryPort(TelemetryPort):
    """Pure Python TelemetryPort fake recording spans, scores, and lifecycle events."""

    def __init__(self, *, trace_id: str = "a" * 32) -> None:
        self._trace_id = trace_id
        self._next_id = 1
        self._stack: list[RecordedSpan] = []
        self.spans: list[RecordedSpan] = []
        self.scores: list[RecordedScore] = []
        self.flush_count: int = 0
        self.lifecycle_events: list[str] = []

    def _allocate_span_id(self) -> str:
        sid = f"{self._next_id:016x}"
        self._next_id += 1
        return sid

    @contextmanager
    def start_session(
        self,
        spec: SessionTelemetrySpec,
    ) -> Generator[TelemetrySpan]:
        span = RecordedSpan(
            name=spec.trace_name or "cresmo.coordinator",
            kind=SpanKind.SPAN,
            trace_id_value=self._trace_id,
            span_id_value=self._allocate_span_id(),
            parent_span_id=self._stack[-1].span_id if self._stack else None,
            is_root=True,
            session_spec=spec,
        )
        self.spans.append(span)
        self._stack.append(span)
        self.lifecycle_events.append(f"session_enter:{span.name}")
        try:
            try:
                yield span
            except Exception as exc:
                span.record_error(exc)
                raise
            finally:
                span.closed = True
                self._stack.pop()
                self.lifecycle_events.append(f"session_exit:{span.name}")
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
        span = RecordedSpan(
            name=name,
            kind=kind,
            trace_id_value=self._trace_id,
            span_id_value=self._allocate_span_id(),
            parent_span_id=self._stack[-1].span_id if self._stack else None,
            attributes=dict(attributes) if attributes else {},
        )
        self.spans.append(span)
        stage_ctx = active_telemetry_stage(stage_name) if stage_name is not None else nullcontext()
        try:
            with stage_ctx:
                self._stack.append(span)
                self.lifecycle_events.append(f"span_enter:{name}")
                try:
                    yield span
                except Exception as exc:
                    if record_exceptions:
                        span.record_error(exc)
                    raise
                finally:
                    span.closed = True
                    self._stack.pop()
                    self.lifecycle_events.append(f"span_exit:{name}")
        finally:
            if flush_on_exit:
                self.flush()

    def current_span(self) -> TelemetrySpan:
        if self._stack:
            return self._stack[-1]
        return NOOP_TELEMETRY_SPAN

    def record_score(
        self,
        *,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
        observation_id: str | None = None,
    ) -> None:
        resolved_obs = observation_id
        if resolved_obs is None and self._stack:
            resolved_obs = self._stack[-1].span_id
        self.scores.append(
            RecordedScore(
                name=name,
                value=value,
                comment=comment,
                trace_id=trace_id,
                observation_id=resolved_obs,
            )
        )

    def flush(self) -> None:
        self.flush_count += 1
        self.lifecycle_events.append("flush")
