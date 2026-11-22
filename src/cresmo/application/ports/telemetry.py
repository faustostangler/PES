"""Hexagonal Telemetry Port and Null-Object implementation.

Conforms to:
- ADR-016: Distributed Tracing & Langfuse Convention
- ADR-027: Unified Telemetry Vocabulary & Langfuse Conventions
- ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar
from typing import Any, Final

from cresmo.domain.entities import (
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.value_objects import ContentId

PIPELINE_TRACE_NAME: Final[str] = "cresmo.pipeline"
PIPELINE_ROOT_SPAN_NAME: Final[str] = "cresmo.coordinator"
LLM_GENERATION_SPAN_NAME: Final[str] = "cresmo.llm.generate"
LLM_GENERATION_FALLBACK_SPAN_NAME: Final[str] = "cresmo.llm.generate_fallback"

_ACTIVE_TELEMETRY_STAGE: ContextVar[str | None] = ContextVar(
    "cresmo_active_telemetry_stage",
    default=None,
)
_ACTIVE_TELEMETRY_PASS: ContextVar[int | None] = ContextVar(
    "cresmo_active_telemetry_pass",
    default=None,
)


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


def format_stage_generation_span_name(
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
    base = LLM_GENERATION_FALLBACK_SPAN_NAME if fallback else LLM_GENERATION_SPAN_NAME
    return f"{base}{pass_suffix}"


def format_stage_judge_span_name(stage_name: str) -> str:
    """Return canonical Tier 3B judge evaluation span name (``cresmo.{stage_name}.judge``)."""
    return f"cresmo.{_normalize_stage_name(stage_name)}.judge"


def get_active_telemetry_stage() -> str | None:
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
    effective_stage = stage_name if stage_name is not None else get_active_telemetry_stage()
    effective_pass = pass_num if pass_num is not None else get_active_telemetry_pass()
    return format_stage_generation_span_name(
        effective_stage,
        fallback=fallback,
        pass_num=effective_pass,
    )


class TelemetryPort(ABC):
    """Hexagonal Port for OpenTelemetry distributed tracing, session replays, and FinOps metrics.

    Conforms to ADR-016. Decouples application use cases from concrete telemetry backends
    (OpenTelemetry SDK, Langfuse API, Prometheus).
    """

    @abstractmethod
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | str,
        channel_tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        trace_name: str | None = None,
    ) -> AbstractContextManager[Any]:
        """Initiate root OpenTelemetry span binding session_id and user_id attributes.

        Args:
            session_id: Canonical multi-stage content session identifier.
            user_id: UserIdentity (anonymous or identified OAuth user), or string.
            channel_tenant_id: Optional Channel tenant identifier for cost and volume aggregation.
            metadata: Additional contextual metadata (e.g. source, pipeline version).
            trace_name: Optional canonical root operation name (defaults to PIPELINE_TRACE_NAME).

        Returns:
            ContextManager managing the root span lifecycle.
        """
        raise NotImplementedError

    @abstractmethod
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        """Create child OpenTelemetry span demarcating a discrete pipeline stage.

        Args:
            stage_name: Identifier for the active pipeline stage.
            attributes: Optional key-value attributes to attach to the stage span.

        Returns:
            ContextManager managing the child stage span.
        """
        raise NotImplementedError

    @abstractmethod
    def start_stage_evaluation_span(
        self,
        stage_name: str,
        attempt: int = 1,
        attributes: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        """Create child OpenTelemetry span demarcating candidate evaluation by LLM judge (ADR-037).

        Chronologically positioned AFTER candidate generation to reflect true causal evaluation order.

        Args:
            stage_name: Identifier for the active pipeline stage.
            attempt: 1-based candidate generation attempt.
            attributes: Optional evaluation diagnostic attributes.

        Returns:
            ContextManager managing the child evaluation span.
        """
        raise NotImplementedError

    @abstractmethod
    def record_judge_evaluation(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        iteration: int,
        max_iterations: int,
        verdict: str,
    ) -> None:
        """Record an LLM-as-a-judge evaluation iteration and its friction ratio.

        Args:
            session_id: Content session identifier.
            content_id: Media content identifier.
            iteration: 1-based attempt index.
            max_iterations: Configured retry ceiling.
            verdict: PASS or NEEDS_REWRITE verdict.
        """
        raise NotImplementedError

    @abstractmethod
    def record_session_coherence(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        score: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record an end-to-end session coherence evaluation score.

        Args:
            session_id: Content session identifier.
            content_id: Media content identifier.
            score: Coherence score in [0.0, 1.0].
            details: Supporting diagnostic attributes (e.g. wikilink counts).
        """
        raise NotImplementedError

    @abstractmethod
    def record_score(
        self,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
        observation_id: str | None = None,
    ) -> None:
        """Record an arbitrary evaluation or clinical score to telemetry backend.

        Args:
            name: Identifier for the score (e.g. 'style_compliance', 'faithfulness').
            value: Score metric value.
            comment: Optional explanatory context or rubric details.
            trace_id: Optional trace ID to associate score with directly.
            observation_id: Optional observation / span ID to bind score in-context.
        """
        raise NotImplementedError

    @abstractmethod
    def record_session_output(self, output: dict[str, Any]) -> None:
        """Record structured business outcome payload on the active root session span.

        Adheres to CNCF OpenTelemetry and Langfuse semantic conventions.

        Args:
            output: Structured dictionary representing high-signal execution results.
        """
        raise NotImplementedError

    @abstractmethod
    def record_stage_io(
        self,
        input_payload: dict[str, Any] | str | None = None,
        output_payload: dict[str, Any] | str | None = None,
    ) -> None:
        """Record domain input and output summaries on the active stage span (ADR-037).

        Populates Langfuse stage inspection panels (Input/Output tabs).

        Args:
            input_payload: Structured dict or text received by stage.
            output_payload: Structured dict or text produced by stage.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Flush pending spans, metrics, and buffer queues to backend telemetry collectors.

        Default no-op implementation allowing concrete adapters to gracefully drain
        in-memory buffers without raising NotImplementedError.
        """


class NoOpTelemetryPort(TelemetryPort):
    """Hermetic Null-Object implementation of TelemetryPort for offline/test environments."""

    @contextmanager
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | str,
        channel_tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        trace_name: str | None = None,
    ) -> Generator[Any]:
        """No-op session context manager."""
        _ = (session_id, user_id, channel_tenant_id, metadata, trace_name)
        yield None

    @contextmanager
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op stage span context manager."""
        _ = attributes
        with active_telemetry_stage(stage_name):
            yield None

    @contextmanager
    def start_stage_evaluation_span(
        self,
        stage_name: str,
        attempt: int = 1,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op stage evaluation span context manager."""
        _ = (stage_name, attempt, attributes)
        yield None

    def record_judge_evaluation(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        iteration: int,
        max_iterations: int,
        verdict: str,
    ) -> None:
        """No-op judge evaluation recorder."""

    def record_session_coherence(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        score: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """No-op session coherence recorder."""

    def record_score(
        self,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
        observation_id: str | None = None,
    ) -> None:
        """No-op score recorder."""

    def record_session_output(self, output: dict[str, Any]) -> None:
        """No-op session output recorder."""

    def record_stage_io(
        self,
        input_payload: dict[str, Any] | str | None = None,
        output_payload: dict[str, Any] | str | None = None,
    ) -> None:
        """No-op stage I/O recorder."""

    def flush(self) -> None:
        """No-op flush."""
