"""OpenTelemetry infrastructure adapter for Cresmo Knowledge Synthesis Modular Monolith.

Conforms to ADR-016:
    - Full OpenTelemetry Semantic Conventions for pipeline orchestration and LLM generations.
    - Sets Langfuse-compatible root span attributes: langfuse.session.id, langfuse.user.id.
    - Demarcates discrete stage child spans maintaining trace context hierarchy.
    - Emits clinical metrics: LLM-as-a-judge friction ratios and session coherence scores.
    - Provides NoOpTelemetryAdapter for graceful degradation during offline or test runs.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Tracer

from cresmo.application.ports import TelemetryPort
from cresmo.domain.entities import (
    ChannelTenantId,
    ContentId,
    JudgeFrictionMetric,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.value_objects import ChannelName

logger = logging.getLogger(__name__)


def name_telemetry_threads(langfuse_client: Any | None = None) -> None:
    """Assign canonical SOTA-KISS thread names to background telemetry workers.

    Prevents anonymous threads ('Thread-1', 'Thread-2', etc.) in Linux thread dumps
    and APMs per ADR-020 Pillar 5 (Thread Hierarchy & APM Visibility).
    """
    import threading

    if langfuse_client is not None:
        try:
            resources = getattr(langfuse_client, "_resources", None)
            if resources:
                for idx, consumer in enumerate(getattr(resources, "_media_upload_consumers", [])):
                    consumer.name = f"LangfuseMediaUploadConsumer-{idx}"
                for idx, consumer in enumerate(getattr(resources, "_ingestion_consumers", [])):
                    consumer.name = f"LangfuseScoreIngestionConsumer-{idx}"
                pc = getattr(resources, "prompt_cache", None)
                if pc:
                    ptm = getattr(pc, "_task_manager", None)
                    if ptm:
                        for idx, consumer in enumerate(getattr(ptm, "_consumers", [])):
                            consumer.name = f"LangfusePromptCacheConsumer-{idx}"
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to assign canonical names to Langfuse threads: %s", exc)

    try:
        for t in threading.enumerate():
            if t.name == "OtelBatchSpanRecordProcessor":
                t.name = "CresmoOtelBatchSpanProcessor"
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to assign canonical name to OpenTelemetry thread: %s", exc)


class OpenTelemetryAdapter(TelemetryPort):
    """Production Telemetry adapter integrating CNCF OpenTelemetry and Langfuse.

    Implements TelemetryPort to provide distributed tracing across the 6-stage
    Cresmo synthesis pipeline, binding content sessions, user identities, and channel
    tenants into first-class telemetry entities.
    """

    def __init__(
        self,
        tracer: Tracer | None = None,
        langfuse_client: Any | None = None,
    ) -> None:
        """Initialize OpenTelemetryAdapter with tracer and optional Langfuse client.

        Args:
            tracer: Configured OpenTelemetry Tracer instance.
            langfuse_client: Optional Langfuse client for session/trace scoring.
        """
        self._tracer = tracer or trace.get_tracer("cresmo.pipeline")
        self._langfuse = langfuse_client
        name_telemetry_threads(langfuse_client)

    @contextmanager
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | ChannelTenantId,
        channel_tenant_id: ChannelTenantId | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """Initiate root OpenTelemetry span binding session_id and user_id attributes.

        Args:
            session_id: Canonical multi-stage content session identifier.
            user_id: UserIdentity (anonymous or identified OAuth), ChannelTenantId, or string.
            channel_tenant_id: Optional Channel tenant identifier for cost and volume aggregation.
            metadata: Additional contextual metadata.

        Yields:
            The active root OpenTelemetry span.
        """
        # Normalize UserIdentity
        if isinstance(user_id, UserIdentity):
            norm_user = user_id
        elif isinstance(user_id, ChannelTenantId):
            norm_user = UserIdentity.from_channel(user_id.channel_name)
            if channel_tenant_id is None:
                channel_tenant_id = user_id
        elif isinstance(user_id, str):
            if user_id.startswith("channel:"):
                c_name = user_id.split(":", 1)[1]
                norm_user = UserIdentity.from_channel(c_name)
                if channel_tenant_id is None:
                    channel_tenant_id = ChannelTenantId.create(ChannelName(c_name))
            elif user_id == "anonymous":
                norm_user = UserIdentity.anonymous()
            elif user_id.startswith("user:"):
                parts = user_id.split(":")
                if len(parts) >= 3:
                    norm_user = UserIdentity.identified(
                        subject=":".join(parts[2:]), provider=parts[1]
                    )
                else:
                    norm_user = UserIdentity.identified(subject=parts[1], provider="oauth")
            else:
                norm_user = UserIdentity.identified(subject=user_id, provider="oauth")
        else:
            norm_user = UserIdentity.anonymous()

        # Resolve ChannelTenantId
        tenant = channel_tenant_id or ChannelTenantId.create(ChannelName(session_id.channel_name))

        with self._tracer.start_as_current_span("cresmo.pipeline.execution") as span:
            span.set_attribute("langfuse.observation.type", "span")
            span.set_attribute("langfuse.session.id", session_id.value)
            span.set_attribute("langfuse.user.id", norm_user.value)
            span.set_attribute("cresmo.content_id", session_id.content_id)
            span.set_attribute("cresmo.channel", tenant.channel_name)
            span.set_attribute("cresmo.tenant_id", tenant.value)
            span.set_attribute("cresmo.user.is_anonymous", norm_user.is_anonymous)
            span.set_attribute("cresmo.user.provider", norm_user.provider)
            if norm_user.subject:
                span.set_attribute("cresmo.user.subject", norm_user.subject)

            tags = [tenant.channel_name, "cresmo:v2", f"auth:{norm_user.provider}"]
            span.set_attribute("langfuse.trace.tags", tags)

            if metadata:
                for key, val in metadata.items():
                    span.set_attribute(f"cresmo.metadata.{key}", str(val))
                    if key in ("title", "channel", "video_url", "content_id"):
                        span.set_attribute(f"langfuse.input.{key}", str(val))

            cm: Any = nullcontext()
            if self._langfuse is not None:
                try:
                    from langfuse import propagate_attributes

                    cm = propagate_attributes(
                        session_id=session_id.value,
                        user_id=norm_user.value,
                        tags=tags,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Failed to initialize Langfuse propagate_attributes: %s", exc)

            with cm:
                yield span

    @contextmanager
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """Create child OpenTelemetry span demarcating a discrete pipeline stage.

        Args:
            stage_name: Identifier for the active pipeline stage.
            attributes: Optional stage diagnostic attributes.

        Yields:
            The active child stage span.
        """
        span_name = f"cresmo.stage.{stage_name}"
        with self._tracer.start_as_current_span(span_name) as span:
            span.set_attribute("langfuse.observation.type", "span")
            if attributes:
                for key, val in attributes.items():
                    span.set_attribute(f"cresmo.stage.{key}", str(val))
            yield span

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
        metric = JudgeFrictionMetric(
            iterations=iteration,
            max_iterations=max_iterations,
            verdict=verdict,
        )

        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.add_event(
                "judge_evaluation",
                attributes={
                    "judge.session_id": session_id.value,
                    "judge.content_id": content_id.value,
                    "judge.iteration": iteration,
                    "judge.max_iterations": max_iterations,
                    "judge.verdict": verdict,
                    "judge.friction_ratio": metric.friction_ratio,
                },
            )

        if self._langfuse is not None:
            try:
                self._langfuse.score(
                    name="judge_friction",
                    value=metric.friction_ratio,
                    comment=f"Iteration {iteration}/{max_iterations} - {verdict}",
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("[OpenTelemetryAdapter] Langfuse score emission skipped: %s", exc)

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
            details: Supporting diagnostic attributes.
        """
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            attrs: dict[str, Any] = {
                "eval.session_id": session_id.value,
                "eval.content_id": content_id.value,
                "eval.coherence_score": score,
            }
            if details:
                for k, v in details.items():
                    attrs[f"eval.details.{k}"] = v
            current_span.add_event("session_coherence", attributes=attrs)

        if self._langfuse is not None:
            try:
                self._langfuse.score(
                    name="session_coherence",
                    value=score,
                    comment=f"Coherence for {content_id.value}",
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("[OpenTelemetryAdapter] Langfuse score emission skipped: %s", exc)

    def flush(self) -> None:
        """Flush in-memory OpenTelemetry spans and Langfuse client buffer queues."""
        if self._langfuse is not None:
            try:
                self._langfuse.flush()
            except Exception as exc:  # noqa: BLE001
                logger.debug("[OpenTelemetryAdapter] Langfuse client flush skipped: %s", exc)
        try:
            tracer_provider = trace.get_tracer_provider()
            if hasattr(tracer_provider, "force_flush"):
                tracer_provider.force_flush(timeout_millis=2000)
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "[OpenTelemetryAdapter] OpenTelemetry tracer provider flush skipped: %s", exc
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
        yield None

    @contextmanager
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op stage span context manager."""
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

    def flush(self) -> None:
        """No-op flush for offline/test runs."""
