"""Hexagonal Telemetry Port, typed span handle, and canonical Null-Object implementation.

Conforms to:
- ADR-016: Distributed Tracing & Langfuse Convention
- ADR-027: Unified Telemetry Vocabulary & Langfuse Conventions
- ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping, Sequence
from contextlib import AbstractContextManager, contextmanager, nullcontext
from contextvars import ContextVar
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol

from cresmo.domain.entities import (
    PipelineSessionId,
    UserIdentity,
)

PIPELINE_TRACE_NAME: Final[str] = "cresmo.pipeline"
PIPELINE_ROOT_SPAN_NAME: Final[str] = "cresmo.coordinator"
_LLM_GENERATION_SPAN_NAME: Final[str] = "cresmo.llm.generate"
_LLM_GENERATION_FALLBACK_SPAN_NAME: Final[str] = "cresmo.llm.generate_fallback"

type TelemetryAttributeValue = str | int | float | bool | tuple[str, ...]
type TelemetryPayload = Mapping[str, object] | Sequence[object] | str

_ACTIVE_TELEMETRY_STAGE: ContextVar[str | None] = ContextVar(
    "cresmo_active_telemetry_stage",
    default=None,
)
_ACTIVE_TELEMETRY_PASS: ContextVar[int | None] = ContextVar(
    "cresmo_active_telemetry_pass",
    default=None,
)


class SpanKind(StrEnum):
    """Canonical observation kinds mapped by concrete telemetry adapters."""

    SPAN = "span"
    GENERATION = "generation"


@dataclass(frozen=True, slots=True)
class SessionTelemetrySpec:
    """Immutable Value Object encapsulating root pipeline session telemetry metadata."""

    session_id: PipelineSessionId
    user_id: UserIdentity
    channel_tenant_id: str | None = None
    trace_name: str | None = None
    channel_id: str = ""
    channel_name: str = ""
    content_id: str = ""
    content_title: str = ""
    source: str = "transcript"
    raw_characters: int = 0
    raw_words: int = 0
    expansion_max_passes: int | None = None
    force_reprocess: bool = False
    batch_id: str | None = None
    video_url: str | None = None
    publication_date: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.raw_characters, bool) or self.raw_characters < 0:
            raise ValueError("raw_characters must be >= 0")
        if isinstance(self.raw_words, bool) or self.raw_words < 0:
            raise ValueError("raw_words must be >= 0")
        if self.expansion_max_passes is not None and (
            isinstance(self.expansion_max_passes, bool) or self.expansion_max_passes < 1
        ):
            raise ValueError("expansion_max_passes must be >= 1 when provided")


class TelemetrySpan(Protocol):
    """Framework-agnostic handle to an active telemetry observation span."""

    @property
    def trace_id(self) -> str | None:
        """Return 32-character hex trace identifier when active, else None."""
        ...

    @property
    def span_id(self) -> str | None:
        """Return 16-character hex span/observation identifier when active, else None."""
        ...

    def set_attributes(self, attributes: Mapping[str, TelemetryAttributeValue]) -> None:
        """Attach typed diagnostic attributes to the active span."""
        ...

    def set_input(self, payload: TelemetryPayload) -> None:
        """Record structured or textual input payload on the active span."""
        ...

    def set_output(self, payload: TelemetryPayload) -> None:
        """Record structured or textual output payload on the active span."""
        ...


class NoOpTelemetrySpan:
    """Hermetic Null-Object TelemetrySpan performing zero side effects."""

    @property
    def trace_id(self) -> str | None:
        """Always returns None when telemetry tracing is inactive."""
        return None

    @property
    def span_id(self) -> str | None:
        """Always returns None when telemetry tracing is inactive."""
        return None

    def set_attributes(self, attributes: Mapping[str, TelemetryAttributeValue]) -> None:
        """No-op attribute attachment."""
        _ = attributes

    def set_input(self, payload: TelemetryPayload) -> None:
        """No-op input payload attachment."""
        _ = payload

    def set_output(self, payload: TelemetryPayload) -> None:
        """No-op output payload attachment."""
        _ = payload


NOOP_TELEMETRY_SPAN: Final[NoOpTelemetrySpan] = NoOpTelemetrySpan()


def _normalize_stage_name(stage_name: str) -> str:
    """Validate and trim a telemetry stage identifier."""
    normalized = stage_name.strip()
    if not normalized:
        raise ValueError("stage_name must be a non-empty string")
    return normalized


def _validate_pass_num(pass_num: int) -> int:
    """Validate that a sequential pass index is a positive integer."""
    if isinstance(pass_num, bool) or pass_num < 1:
        raise ValueError("pass_num must be a positive integer")
    return pass_num


def format_stage_span_name(stage_name: str) -> str:
    """Return canonical Tier 2 stage span name (``cresmo.{stage_name}``)."""
    return f"cresmo.{_normalize_stage_name(stage_name)}"


def _format_stage_generation_span_name(
    stage_name: str | None,
    *,
    fallback: bool = False,
    pass_num: int | None = None,
) -> str:
    """Return canonical Tier 3A LLM generation observation name, scoped to stage and pass."""
    pass_suffix = f".pass_{_validate_pass_num(pass_num)}" if pass_num is not None else ""
    if stage_name is not None:
        normalized = stage_name.strip()
        if normalized:
            suffix = "generate_fallback" if fallback else "generate"
            return f"cresmo.{normalized}.{suffix}{pass_suffix}"
    base = _LLM_GENERATION_FALLBACK_SPAN_NAME if fallback else _LLM_GENERATION_SPAN_NAME
    return f"{base}{pass_suffix}"


def format_stage_judge_span_name(stage_name: str) -> str:
    """Return canonical Tier 3B judge evaluation span name (``cresmo.{stage_name}.judge``)."""
    return f"cresmo.{_normalize_stage_name(stage_name)}.judge"


def format_stage_saturation_span_name(
    stage_name: str,
    pass_num: int | None = None,
) -> str:
    """Return canonical Tier 3C saturation evaluation span name, optionally pass-scoped."""
    base = f"cresmo.{_normalize_stage_name(stage_name)}.saturation"
    if pass_num is not None:
        return f"{base}.pass_{_validate_pass_num(pass_num)}"
    return base


def _get_active_telemetry_stage() -> str | None:
    """Return the active pipeline stage identifier from the current execution context, if any."""
    return _ACTIVE_TELEMETRY_STAGE.get()


def get_active_telemetry_pass() -> int | None:
    """Return the active sequential pass index from the current execution context, if any."""
    return _ACTIVE_TELEMETRY_PASS.get()


@contextmanager
def active_telemetry_stage(stage_name: str) -> Generator[None]:
    """Bind the active pipeline stage identifier and isolate nested pass state."""
    normalized = _normalize_stage_name(stage_name)
    stage_token = _ACTIVE_TELEMETRY_STAGE.set(normalized)
    pass_token = _ACTIVE_TELEMETRY_PASS.set(None)
    try:
        yield
    finally:
        _ACTIVE_TELEMETRY_PASS.reset(pass_token)
        _ACTIVE_TELEMETRY_STAGE.reset(stage_token)


@contextmanager
def active_telemetry_pass(pass_num: int) -> Generator[None]:
    """Bind the active sequential pass index to contextvars for multi-pass LLM observations."""
    validated = _validate_pass_num(pass_num)
    token = _ACTIVE_TELEMETRY_PASS.set(validated)
    try:
        yield
    finally:
        _ACTIVE_TELEMETRY_PASS.reset(token)


def resolve_llm_generation_span_name(
    stage_name: str | None = None,
    *,
    fallback: bool = False,
    pass_num: int | None = None,
) -> str:
    """Resolve Tier 3A LLM generation observation name from explicit or active stage and pass."""
    effective_stage = stage_name if stage_name is not None else _get_active_telemetry_stage()
    effective_pass = pass_num if pass_num is not None else get_active_telemetry_pass()
    return _format_stage_generation_span_name(
        effective_stage,
        fallback=fallback,
        pass_num=effective_pass,
    )


class TelemetryPort(ABC):
    """Hexagonal Port for distributed tracing, LLM generations, and clinical scores.

    Conforms to ADR-016 and ADR-070. Decouples application use cases and adapters from
    concrete OpenTelemetry and Langfuse SDKs through a minimal 5-method contract.
    """

    @abstractmethod
    def start_session(
        self,
        spec: SessionTelemetrySpec,
    ) -> AbstractContextManager[TelemetrySpan]:
        """Initiate root telemetry session span, propagate identity metadata, and flush on exit.

        Args:
            spec: Immutable SessionTelemetrySpec containing session identity, content metrics,
                conveyor options, and lineage metadata.

        Returns:
            Context manager yielding a TelemetrySpan handle bound to the root pipeline span.
        """
        raise NotImplementedError

    @abstractmethod
    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.SPAN,
        attributes: Mapping[str, TelemetryAttributeValue] | None = None,
        stage_name: str | None = None,
        record_exceptions: bool = True,
        flush_on_exit: bool = False,
    ) -> AbstractContextManager[TelemetrySpan]:
        """Create a child observation span (stage, judge, saturation, generation, or custom op).

        Args:
            name: Canonical dot-delimited observation name (e.g. ``cresmo.fluid_prose``).
            kind: Observation kind classifying standard spans vs LLM generations.
            attributes: Optional typed initial attributes attached on span creation.
            stage_name: Optional pipeline stage name bound to contextvars for nested generation naming.
            record_exceptions: When True, marks span ERROR and records uncaught exceptions.
            flush_on_exit: When True, invokes flush() deterministically after span completion.

        Returns:
            Context manager yielding a TelemetrySpan handle bound to the newly opened child span.
        """
        raise NotImplementedError

    @abstractmethod
    def current_span(self) -> TelemetrySpan:
        """Return handle to the active span, or NOOP_TELEMETRY_SPAN outside an active span.

        Returns:
            Active TelemetrySpan handle or NOOP_TELEMETRY_SPAN when no recording span is active.
        """
        raise NotImplementedError

    @abstractmethod
    def record_score(
        self,
        *,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
        observation_id: str | None = None,
    ) -> None:
        """Record an evaluation or clinical score bound to trace/observation context.

        Args:
            name: Score metric identifier (e.g. ``session_coherence`` or criterion name).
            value: Numeric score value.
            comment: Optional human-readable diagnostic or judge reasoning text.
            trace_id: Optional 32-char hex trace identifier; falls back to active span context.
            observation_id: Optional 16-char hex observation identifier; falls back to active span.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Flush buffered spans and scores to backend telemetry collectors.

        Adapters should perform bounded, fail-silent flushes and never raise telemetry transport
        exceptions into application control flow.
        """
        return None


class NoOpTelemetryPort(TelemetryPort):
    """Canonical Null-Object TelemetryPort for offline, preflight-bypassed, and test runs."""

    @contextmanager
    def start_session(
        self,
        spec: SessionTelemetrySpec,
    ) -> Generator[TelemetrySpan]:
        """No-op root session context manager yielding NOOP_TELEMETRY_SPAN."""
        _ = spec
        yield NOOP_TELEMETRY_SPAN

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
        """No-op child span context manager preserving active_telemetry_stage scope."""
        _ = (name, kind, attributes, record_exceptions, flush_on_exit)
        stage_ctx = active_telemetry_stage(stage_name) if stage_name is not None else nullcontext()
        with stage_ctx:
            yield NOOP_TELEMETRY_SPAN

    def current_span(self) -> TelemetrySpan:
        """Return singleton NOOP_TELEMETRY_SPAN."""
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
        """No-op score recorder."""
        _ = (name, value, comment, trace_id, observation_id)

    def flush(self) -> None:
        """No-op flush."""
