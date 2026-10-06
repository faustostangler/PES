"""Hexagonal Telemetry Port and Null-Object implementation.

Conforms to:
- ADR-016: Distributed Tracing & Langfuse Convention
- ADR-027: Unified Telemetry Vocabulary & Langfuse Conventions
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from cresmo.domain.entities import (
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.value_objects import ContentId


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
            trace_name: Optional canonical root operation name (defaults to cresmo.pipeline.execution).

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
    ) -> None:
        """Record an arbitrary evaluation or clinical score to telemetry backend.

        Args:
            name: Identifier for the score (e.g. 'style_compliance', 'faithfulness').
            value: Score metric value.
            comment: Optional explanatory context or rubric details.
            trace_id: Optional trace ID to associate score with directly.
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
        _ = (stage_name, attributes)
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
    ) -> None:
        """No-op score recorder."""

    def record_session_output(self, output: dict[str, Any]) -> None:
        """No-op session output recorder."""

    def flush(self) -> None:
        """No-op flush."""
