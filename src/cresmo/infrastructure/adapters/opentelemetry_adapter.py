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
from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from typing import Any, Final

from opentelemetry import trace
from opentelemetry.trace import Tracer

from cresmo.application.ports import TelemetryPort
from cresmo.domain.entities import (
    ContentId,
    JudgeFrictionMetric,
    PipelineSessionId,
    UserIdentity,
)

try:
    from langfuse import propagate_attributes
except ImportError:  # pragma: no cover
    propagate_attributes = None

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE_VERSION: str = "cresmo:v2"
OTEL_FLUSH_TIMEOUT_MS: int = 2000
_MIN_STRUCTURED_USER_PARTS: Final[int] = 3


_LANGFUSE_INPUT_KEYS: frozenset[str] = frozenset(
    {
        "title",
        "content_title",
        "channel",
        "channel_name",
        "channel_id",
        "content_id",
        "video_url",
    }
)

_CANONICAL_ROOT_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "title",
        "content_title",
        "channel",
        "channel_name",
        "channel_id",
        "content_id",
    }
)


from cresmo.infrastructure.adapters.telemetry import (
    NoOpTelemetryAdapter,
    name_telemetry_threads,
)


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


def _resolve_identity_from_string(user_id: str) -> tuple[UserIdentity, str | None]:
    """Parse string representation of user identity and optional channel tenant."""
    if user_id.startswith("system:"):
        worker_name = user_id.split(":", 1)[1]
        return UserIdentity.worker(worker_name), None
    if user_id.startswith("channel:"):
        channel_name = user_id.split(":", 1)[1]
        return UserIdentity.from_channel(channel_name), f"channel:{channel_name}"
    if user_id == "anonymous":
        return UserIdentity.anonymous(), None
    if user_id.startswith("user:"):
        identity_segments = user_id.split(":")
        if len(identity_segments) >= _MIN_STRUCTURED_USER_PARTS:
            return UserIdentity.identified(
                subject=":".join(identity_segments[2:]),
                provider=identity_segments[1],
            ), None
        return UserIdentity.identified(subject=identity_segments[1], provider="oauth"), None
    return UserIdentity.identified(subject=user_id, provider="oauth"), None


def _resolve_user_identity_and_tenant(
    user_id: UserIdentity | str,
    channel_tenant_id: str | None,
    session_id: PipelineSessionId,
) -> tuple[UserIdentity, str]:
    """Normalize polymorphic user identification and resolve channel tenant."""
    normalized_user: UserIdentity
    resolved_tenant = channel_tenant_id

    if isinstance(user_id, UserIdentity):
        normalized_user = user_id
    elif isinstance(user_id, str):
        normalized_user, parsed_tenant = _resolve_identity_from_string(user_id)
        if resolved_tenant is None:
            resolved_tenant = parsed_tenant
    else:
        normalized_user = UserIdentity.anonymous()

    if resolved_tenant is None:
        resolved_tenant = f"channel:{session_id.channel_id}"

    return normalized_user, resolved_tenant


def _build_langfuse_input_payload(
    metadata: dict[str, Any],
    channel_name: str,
    channel_id: str,
    content_id: str,
    content_title: str,
    attributes: dict[str, Any],
) -> None:
    """Populate OpenTelemetry and Langfuse metadata attributes and JSON input payload."""
    input_payload: dict[str, Any] = {}
    for key, value in metadata.items():
        formatted_value = str(value)
        if key not in _CANONICAL_ROOT_METADATA_KEYS:
            attributes[f"cresmo.metadata.{key}"] = formatted_value
        if key in _LANGFUSE_INPUT_KEYS:
            attributes[f"langfuse.input.{key}"] = formatted_value
            input_payload[key] = formatted_value

    # ID-ID Parity: Symmetrically guarantee channel_id and content_id in langfuse.input
    if channel_id:
        attributes["langfuse.input.channel_id"] = channel_id
        input_payload["channel_id"] = channel_id
    if content_id:
        attributes["langfuse.input.content_id"] = content_id
        input_payload["content_id"] = content_id

    # TXT-TXT Parity: Symmetrically guarantee channel and channel_name aliases
    resolved_channel = metadata.get("channel") or metadata.get("channel_name") or channel_name
    if resolved_channel:
        formatted_channel = str(resolved_channel)
        attributes["langfuse.input.channel"] = formatted_channel
        attributes["langfuse.input.channel_name"] = formatted_channel
        input_payload["channel"] = formatted_channel
        input_payload["channel_name"] = formatted_channel

    # TXT-TXT Parity: Symmetrically guarantee title and content_title aliases in langfuse.input
    resolved_title = metadata.get("title") or metadata.get("content_title") or content_title
    if resolved_title:
        formatted_title = str(resolved_title)
        attributes["langfuse.input.title"] = formatted_title
        attributes["langfuse.input.content_title"] = formatted_title
        input_payload["title"] = formatted_title
        input_payload["content_title"] = formatted_title

    if input_payload:
        attributes["langfuse.input"] = json.dumps(input_payload)


def _build_session_span_attributes(
    session_id: PipelineSessionId,
    user: UserIdentity,
    tenant: str,
    pipeline_version: str,
    metadata: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Assemble atomic OpenTelemetry and Langfuse session span attributes and tags."""
    # 1. Resolve Algorithmic Pair (ID - ID Parity: Machines & Indexes)
    content_id = session_id.content_id
    channel_id = str(metadata.get("channel_id") or session_id.channel_id or "").strip()

    # 2. Resolve Cognitive Pair (TXT - TXT Parity: Humans & Observability)
    resolved_channel_name = str(
        metadata.get("channel_name") or metadata.get("channel") or session_id.channel_id
    ).strip()
    content_title = str(
        metadata.get("title") or metadata.get("content_title") or content_id
    ).strip()

    tags = [resolved_channel_name, pipeline_version, f"auth:{user.provider}"]

    attributes: dict[str, Any] = {
        "langfuse.observation.type": "span",
        "langfuse.session.id": session_id.value,
        "langfuse.user.id": user.value,
        "langfuse.trace.tags": tags,
        # Algorithmic Pair (ID - ID Parity)
        "cresmo.channel.id": channel_id,
        "cresmo.content.id": content_id,
        # Cognitive Pair (TXT - TXT Parity)
        "cresmo.channel.name": resolved_channel_name,
        "cresmo.content.title": content_title,
        # Tenant & Auth Identity
        "cresmo.tenant_id": tenant,
        "cresmo.user.is_anonymous": user.is_anonymous,
        "cresmo.user.provider": user.provider,
    }

    if user.subject:
        attributes["cresmo.user.subject"] = user.subject

    _build_langfuse_input_payload(
        metadata=metadata,
        channel_name=resolved_channel_name,
        channel_id=channel_id,
        content_id=content_id,
        content_title=content_title,
        attributes=attributes,
    )
    return attributes, tags


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
        user_id: UserIdentity | str,
        channel_tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        trace_name: str | None = None,
    ) -> Generator[Any]:
        """Initiate root OpenTelemetry span binding session_id and user_id attributes.

        Args:
            session_id: Canonical multi-stage content session identifier ({channel_id}:{content_id}).
            user_id: UserIdentity (anonymous, identified IAM, or system:worker) or string.
            channel_tenant_id: Optional Channel tenant identifier for cost and volume aggregation.
            metadata: Additional contextual metadata.
            trace_name: Optional canonical root operation name (defaults to cresmo.pipeline.execution).

        Yields:
            The active root OpenTelemetry span.
        """
        normalized_user, tenant = _resolve_user_identity_and_tenant(
            user_id=user_id,
            channel_tenant_id=channel_tenant_id,
            session_id=session_id,
        )
        effective_metadata = metadata or {}
        pipeline_version = str(
            effective_metadata.get("pipeline_version")
            or effective_metadata.get("version")
            or self._pipeline_version
        )

        session_attributes, tags = _build_session_span_attributes(
            session_id=session_id,
            user=normalized_user,
            tenant=tenant,
            pipeline_version=pipeline_version,
            metadata=effective_metadata,
        )

        root_operation = trace_name or "cresmo.pipeline.execution"
        with self._tracer.start_as_current_span(
            root_operation, attributes=session_attributes
        ) as span:
            propagation_context: Any = nullcontext()
            if self._langfuse is not None and propagate_attributes is not None:
                try:
                    propagation_context = propagate_attributes(
                        session_id=session_id.value,
                        user_id=normalized_user.value,
                        tags=tags,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Failed to initialize Langfuse propagate_attributes: %s", exc)

            with propagation_context:
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
                for attribute_key, attribute_value in attributes.items():
                    span.set_attribute(f"cresmo.stage.{attribute_key}", str(attribute_value))
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
                    "judge.channel_id": session_id.channel_id,
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
            event_attributes: dict[str, Any] = {
                "eval.session_id": session_id.value,
                "eval.content_id": content_id.value,
                "eval.channel_id": session_id.channel_id,
                "eval.coherence_score": score,
            }
            output_payload: dict[str, Any] = {"coherence_score": score}
            if details:
                for detail_key, detail_value in details.items():
                    event_attributes[f"eval.details.{detail_key}"] = detail_value
                    # Explicit root output summary according to Langfuse best practices
                    current_span.set_attribute(f"langfuse.output.{detail_key}", str(detail_value))
                    output_payload[detail_key] = detail_value
            current_span.set_attribute("langfuse.output.coherence_score", str(score))
            current_span.set_attribute("langfuse.output", json.dumps(output_payload))
            current_span.add_event("session_coherence", attributes=event_attributes)

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
            score_attributes: dict[str, Any] = {
                "score.name": name,
                "score.value": value,
            }
            if comment:
                score_attributes["score.comment"] = comment
            if trace_id:
                score_attributes["score.trace_id"] = trace_id
            current_span.add_event("telemetry_score", attributes=score_attributes)

        if self._langfuse is not None:
            try:
                score_arguments: dict[str, Any] = {
                    "name": name,
                    "value": value,
                }
                if comment is not None:
                    score_arguments["comment"] = comment
                if trace_id is not None:
                    score_arguments["trace_id"] = trace_id
                self._langfuse.score(**score_arguments)
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
            force_flush_method = getattr(tracer_provider, "force_flush", None)
            if callable(force_flush_method):
                force_flush_method(timeout_millis=OTEL_FLUSH_TIMEOUT_MS)
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "[OpenTelemetryAdapter] OpenTelemetry tracer provider flush skipped: %s", exc
            )


__all__ = [
    "DEFAULT_PIPELINE_VERSION",
    "NoOpTelemetryAdapter",
    "OpenTelemetryAdapter",
    "annotate_llm_span",
    "name_telemetry_threads",
]
