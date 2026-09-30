"""No-op Telemetry adapter for offline, disconnected, or test executions.

Conforms to:
- ADR-014: Fail-Fast Preflight Probing & Telemetry Circuit Breaking
- ADR-016: CNCF OpenTelemetry & Langfuse Semantic Conventions
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from cresmo.application.ports import TelemetryPort
from cresmo.domain.entities import (
    ChannelTenantId,
    ContentId,
    PipelineSessionId,
    UserIdentity,
)


class NoOpTelemetryAdapter(TelemetryPort):
    """Graceful degradation adapter deployed when observability services are offline.

    Conforms to ADR-014 fail-fast preflight rules, guaranteeing zero background
    thread overhead or network retry storms when Langfuse is offline.
    """

    @contextmanager
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | ChannelTenantId,
        channel_tenant_id: ChannelTenantId | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op session context manager."""
        _ = (session_id, user_id, channel_tenant_id, metadata)
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
        """No-op score recorder for offline/test runs."""

    def flush(self) -> None:
        """No-op flush for offline/test runs."""
