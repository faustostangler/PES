"""OpenTelemetry infrastructure adapter for Cresmo Knowledge Synthesis Modular Monolith.

Conforms to ADR-016:
    - Full OpenTelemetry Semantic Conventions for pipeline orchestration and LLM generations.
    - Sets Langfuse-compatible root span attributes: langfuse.session.id, langfuse.user.id.
    - Demarcates discrete stage child spans maintaining trace context hierarchy.
    - Emits clinical metrics: LLM-as-a-judge friction ratios and session coherence scores.
    - Provides NoOpTelemetryAdapter for graceful degradation during offline or test runs.
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from typing import Any, Final

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

try:
    from langfuse import propagate_attributes
except ImportError:  # pragma: no cover
    propagate_attributes = None

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE_VERSION: str = "cresmo:v2"
OTEL_FLUSH_TIMEOUT_MS: int = 2000
_MIN_STRUCTURED_USER_PARTS: Final[int] = 3


_LANGFUSE_INPUT_KEYS: frozenset[str] = frozenset(
    {"title", "channel", "channel_name", "channel_id", "content_id", "video_url"}
)

_CANONICAL_ROOT_METADATA_KEYS: frozenset[str] = frozenset(
    {"title", "channel", "channel_name", "channel_id", "content_id"}
)


def name_telemetry_threads(langfuse_client: Any | None = None) -> None:
    """Assign canonical SOTA-KISS thread names to background telemetry workers.

    Prevents anonymous threads ('Thread-1', 'Thread-2', etc.) in Linux thread dumps
    and APMs per ADR-020 Pillar 5 (Thread Hierarchy & APM Visibility).
    """
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


def annotate_llm_span(
    *,
    system: str,
    model: str,
    prompt_tokens: int,
    candidate_tokens: int,
    session_id: str | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
    temperature: float | None = None,
) -> None:
    """Annotate the current OpenTelemetry span with GenAI Semantic Conventions.

    Centralises the span-decoration pattern shared by every LLM adapter
    (Ollama, Gemini, …) to honour DRY and ensure all adapters emit
    identical attribute keys.

    Why a module-level function instead of a base class method: the adapters
    are already bound to concrete external SDKs and should not inherit shared
    state — a pure function is the lightest ACL boundary here.

    Args:
        system: GenAI system identifier (e.g. 'google', 'ollama').
        model: Model tag used for the request (e.g. 'qwen2.5:7b').
        prompt_tokens: Number of input/prompt tokens consumed.
        candidate_tokens: Number of output/completion tokens generated.
        session_id: Optional Cresmo pipeline session identifier.
        user_id: Optional operator or channel identifier.
        trace_id: Optional domain trace identifier (e.g. ContentId).
        temperature: Optional sampling temperature override for diagnostics.
    """
    current_span = trace.get_current_span()
    if not (current_span and current_span.is_recording()):
        return

    current_span.set_attribute("gen_ai.system", system)
    current_span.set_attribute("gen_ai.request.model", model)
    current_span.set_attribute("gen_ai.usage.input_tokens", prompt_tokens)
    current_span.set_attribute("gen_ai.usage.output_tokens", candidate_tokens)
    current_span.set_attribute("langfuse.observation.type", "generation")
    if session_id:
        current_span.set_attribute("langfuse.session.id", session_id)
    if user_id:
        current_span.set_attribute("langfuse.user.id", user_id)
    if trace_id:
        current_span.set_attribute("cresmo.trace_id", trace_id)
    if temperature is not None:
        current_span.set_attribute("cresmo.temperature", temperature)


def _resolve_user_identity_and_tenant(
    user_id: UserIdentity | ChannelTenantId | str,
    channel_tenant_id: ChannelTenantId | None,
    session_id: PipelineSessionId,
) -> tuple[UserIdentity, ChannelTenantId]:
    """Normalize polymorphic user identification and resolve channel tenant."""
    norm_user: UserIdentity
    resolved_tenant = channel_tenant_id

    if isinstance(user_id, UserIdentity):
        norm_user = user_id
    elif isinstance(user_id, ChannelTenantId):
        norm_user = UserIdentity.from_channel(user_id.channel_token)
        if resolved_tenant is None:
            resolved_tenant = user_id
    elif isinstance(user_id, str):
        if user_id.startswith("channel:"):
            c_name = user_id.split(":", 1)[1]
            norm_user = UserIdentity.from_channel(c_name)
            if resolved_tenant is None:
                resolved_tenant = ChannelTenantId.create(ChannelName(c_name))
        elif user_id == "anonymous":
            norm_user = UserIdentity.anonymous()
        elif user_id.startswith("user:"):
            parts = user_id.split(":")
            if len(parts) >= _MIN_STRUCTURED_USER_PARTS:
                norm_user = UserIdentity.identified(subject=":".join(parts[2:]), provider=parts[1])
            else:
                norm_user = UserIdentity.identified(subject=parts[1], provider="oauth")
        else:
            norm_user = UserIdentity.identified(subject=user_id, provider="oauth")
    else:
        norm_user = UserIdentity.anonymous()

    if resolved_tenant is None:
        resolved_tenant = ChannelTenantId.create(ChannelName(session_id.channel_token))

    return norm_user, resolved_tenant


def _build_session_span_attributes(
    session_id: PipelineSessionId,
    user: UserIdentity,
    tenant: ChannelTenantId,
    tags: list[str],
    chan_name: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Assemble atomic OpenTelemetry and Langfuse session span attributes."""
    meta = metadata or {}
    attrs: dict[str, Any] = {
        "langfuse.observation.type": "span",
        "langfuse.session.id": session_id.value,
        "langfuse.user.id": user.value,
        "langfuse.trace.tags": tags,
        "cresmo.content.id": session_id.content_id,
        "cresmo.channel.name": chan_name,
        "cresmo.tenant_id": tenant.value,
        "cresmo.user.is_anonymous": user.is_anonymous,
        "cresmo.user.provider": user.provider,
    }
    if "title" in meta:
        attrs["cresmo.content.title"] = str(meta["title"])
    if "channel_id" in meta:
        attrs["cresmo.channel.id"] = str(meta["channel_id"])
    if user.subject:
        attrs["cresmo.user.subject"] = user.subject

    input_payload: dict[str, Any] = {}
    for key, val in meta.items():
        str_val = str(val)
        if key not in _CANONICAL_ROOT_METADATA_KEYS:
            attrs[f"cresmo.metadata.{key}"] = str_val
        if key in _LANGFUSE_INPUT_KEYS:
            attrs[f"langfuse.input.{key}"] = str_val
            input_payload[key] = str_val

    # Ensure channel and channel_name aliases are present symmetrically in langfuse.input
    if "channel" in meta and "channel_name" not in input_payload:
        attrs["langfuse.input.channel_name"] = str(meta["channel"])
        input_payload["channel_name"] = str(meta["channel"])
    elif "channel_name" in meta and "channel" not in input_payload:
        attrs["langfuse.input.channel"] = str(meta["channel_name"])
        input_payload["channel"] = str(meta["channel_name"])
    elif "channel" not in input_payload and chan_name:
        attrs["langfuse.input.channel"] = chan_name
        attrs["langfuse.input.channel_name"] = chan_name
        input_payload["channel"] = chan_name
        input_payload["channel_name"] = chan_name

    if input_payload:
        attrs["langfuse.input"] = json.dumps(input_payload)

    return attrs


class OpenTelemetryAdapter(TelemetryPort):
    """Production Telemetry adapter integrating CNCF OpenTelemetry and Langfuse.

    Implements TelemetryPort to provide distributed tracing across the
    Cresmo synthesis pipeline, binding content sessions, user identities, and channel
    tenants into first-class telemetry entities.
    """

    def __init__(
        self,
        tracer: Tracer | None = None,
        langfuse_client: Any | None = None,
        pipeline_version: str | None = None,
    ) -> None:
        """Initialize OpenTelemetryAdapter with tracer, optional Langfuse client and pipeline version.

        Args:
            tracer: Configured OpenTelemetry Tracer instance.
            langfuse_client: Optional Langfuse client for session/trace scoring.
            pipeline_version: Operational pipeline version tag (defaults to DEFAULT_PIPELINE_VERSION).
        """
        self._tracer = tracer or trace.get_tracer("cresmo.pipeline")
        self._langfuse = langfuse_client
        self._pipeline_version = pipeline_version or DEFAULT_PIPELINE_VERSION
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
        norm_user, tenant = _resolve_user_identity_and_tenant(
            user_id=user_id,
            channel_tenant_id=channel_tenant_id,
            session_id=session_id,
        )
        meta = metadata or {}
        chan_name = str(meta["channel"]) if "channel" in meta else tenant.channel_token
        pipeline_version = str(
            meta.get("pipeline_version") or meta.get("version") or self._pipeline_version
        )
        tags = [chan_name, pipeline_version, f"auth:{norm_user.provider}"]

        attrs = _build_session_span_attributes(
            session_id=session_id,
            user=norm_user,
            tenant=tenant,
            tags=tags,
            chan_name=chan_name,
            metadata=metadata,
        )

        with self._tracer.start_as_current_span("synthesize_content", attributes=attrs) as span:
            cm: Any = nullcontext()
            if self._langfuse is not None and propagate_attributes is not None:
                try:
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
            output_payload: dict[str, Any] = {"coherence_score": score}
            if details:
                for k, v in details.items():
                    attrs[f"eval.details.{k}"] = v
                    # Explicit root output summary according to Langfuse best practices
                    current_span.set_attribute(f"langfuse.output.{k}", str(v))
                    output_payload[k] = v
            current_span.set_attribute("langfuse.output.coherence_score", str(score))
            current_span.set_attribute("langfuse.output", json.dumps(output_payload))
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
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            attrs: dict[str, Any] = {
                "score.name": name,
                "score.value": value,
            }
            if comment:
                attrs["score.comment"] = comment
            if trace_id:
                attrs["score.trace_id"] = trace_id
            current_span.add_event("telemetry_score", attributes=attrs)

        if self._langfuse is not None:
            try:
                kwargs: dict[str, Any] = {
                    "name": name,
                    "value": value,
                }
                if comment is not None:
                    kwargs["comment"] = comment
                if trace_id is not None:
                    kwargs["trace_id"] = trace_id
                self._langfuse.score(**kwargs)
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
            flush_fn = getattr(tracer_provider, "force_flush", None)
            if callable(flush_fn):
                flush_fn(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)
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
