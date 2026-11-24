"""Pure mapping helpers translating SessionTelemetrySpec into OTel/Langfuse attributes.

Conforms to:
- ADR-016: OpenTelemetry Semantic Conventions & Session Replays
- ADR-034: Algorithmic ID-ID & Cognitive TXT-TXT Parity
- ADR-035: SOTA-KISS Batch Correlation
- ADR-063: Zero Attribute Duplication & Dynamic Versioning
- ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from cresmo.application.ports.telemetry import (
    PIPELINE_ROOT_SPAN_NAME,
    PIPELINE_TRACE_NAME,
    SessionTelemetrySpec,
)
from cresmo.domain.entities import PipelineSessionId

_GIT_SHA_SHORT_LENGTH: Final[int] = 8
# Infra limit: Langfuse drops propagated attribute values longer than 200 characters.
_LANGFUSE_PROPAGATED_VALUE_MAX_CHARS: Final[int] = 200

_CANONICAL_ROOT_METADATA_KEYS: Final[frozenset[str]] = frozenset(
    {
        "batch_id",
        "title",
        "content_title",
        "channel",
        "channel_name",
        "channel_id",
        "content_id",
        "source",
        "raw_words",
        "raw_characters",
        "expansion_max_passes",
        "force_reprocess",
        "publication_date",
        "pipeline_version",
        "version",
        "git_sha",
    }
)


def short_git_sha(git_sha: str | None) -> str | None:
    """Normalize and truncate git commit SHA to short length."""
    if git_sha and git_sha.strip():
        return git_sha.strip()[:_GIT_SHA_SHORT_LENGTH]
    return None


def parse_session_parts(session_id: PipelineSessionId) -> tuple[str, str]:
    """Extract (channel_token, content_token) from PipelineSessionId value."""
    parts = session_id.value.split(":")
    return parts[0], parts[1]


def resolve_root_operation_name(trace_name: str | None) -> tuple[str, str]:
    """Resolve canonical (trace_name, root_span_name) separation per ADR-037 & ADR-065."""
    resolved_trace_name = trace_name or PIPELINE_TRACE_NAME
    if trace_name is None or trace_name == PIPELINE_TRACE_NAME:
        return resolved_trace_name, PIPELINE_ROOT_SPAN_NAME
    return resolved_trace_name, trace_name


def build_session_span_attributes(
    spec: SessionTelemetrySpec,
    *,
    pipeline_version: str,
    git_sha: str | None = None,
    resolved_trace_name: str | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    """Build atomic OTel/Langfuse session span attributes, trace tags, and root input payload."""
    channel_token, content_token = parse_session_parts(spec.session_id)
    user = spec.user_id

    # Algorithmic Pair (ID-ID Parity: Machines & Indexes)
    content_id = spec.content_id.strip() or content_token
    channel_id = spec.channel_id.strip() or channel_token

    # Cognitive Pair (TXT-TXT Parity: Humans & Observability)
    resolved_channel_name = spec.channel_name.strip() or channel_token
    content_title = spec.content_title.strip() or content_id
    tenant = spec.channel_tenant_id or f"channel:{channel_token}"

    effective_trace_name = (
        resolved_trace_name
        if resolved_trace_name is not None
        else resolve_root_operation_name(spec.trace_name)[0]
    )
    tags = [resolved_channel_name, pipeline_version, f"auth:{user.provider}"]

    attributes: dict[str, Any] = {
        "langfuse.observation.type": "span",
        "langfuse.session.id": spec.session_id.value,
        "langfuse.user.id": user.value,
        "langfuse.trace.name": effective_trace_name,
        "langfuse.trace.tags": tags,
        "cresmo.pipeline.version": pipeline_version,
        "cresmo.channel.id": channel_id,
        "cresmo.content.id": content_id,
        "cresmo.channel.name": resolved_channel_name,
        "cresmo.content.title": content_title,
        "cresmo.tenant_id": tenant,
        "cresmo.user.is_anonymous": user.is_anonymous,
        "cresmo.user.provider": user.provider,
        "cresmo.content.word_count": spec.raw_words,
        "cresmo.content.char_count": spec.raw_characters,
        "cresmo.pipeline.force_reprocess": spec.force_reprocess,
    }

    if spec.expansion_max_passes is not None:
        attributes["cresmo.pipeline.expansion_max_passes"] = spec.expansion_max_passes

    if spec.source.strip():
        attributes["cresmo.content.source"] = spec.source.strip()

    if spec.publication_date and spec.publication_date.strip():
        attributes["cresmo.content.publication_date"] = spec.publication_date.strip()

    if clean_sha := short_git_sha(git_sha):
        attributes["cresmo.pipeline.git_sha"] = clean_sha
        tags.append(f"git:{clean_sha}")

    if user.subject:
        attributes["cresmo.user.subject"] = user.subject

    clean_batch_id = spec.batch_id.strip() if spec.batch_id else ""
    if clean_batch_id:
        attributes["cresmo.batch_id"] = clean_batch_id
        tags.append(f"batch:{clean_batch_id}")

    for key, value in spec.extra_metadata.items():
        if key not in _CANONICAL_ROOT_METADATA_KEYS:
            attributes[f"cresmo.metadata.{key}"] = str(value)

    input_payload: dict[str, Any] = {
        "channel_id": channel_id,
        "content_id": content_id,
        "channel_name": resolved_channel_name,
        "content_title": content_title,
        "raw_characters": str(spec.raw_characters),
        "raw_words": str(spec.raw_words),
    }
    if clean_batch_id:
        input_payload["batch_id"] = clean_batch_id
    if spec.video_url and spec.video_url.strip():
        input_payload["video_url"] = spec.video_url.strip()

    return attributes, tags, input_payload


def build_propagated_trace_metadata(attributes: Mapping[str, Any]) -> dict[str, str]:
    """Derive short identity metadata (<= 200 chars) propagated to every child observation."""
    candidates = {
        "channel_id": attributes.get("cresmo.channel.id"),
        "channel_name": attributes.get("cresmo.channel.name"),
        "content_id": attributes.get("cresmo.content.id"),
        "content_title": attributes.get("cresmo.content.title"),
        "batch_id": attributes.get("cresmo.batch_id"),
    }
    return {
        key: str(value)[:_LANGFUSE_PROPAGATED_VALUE_MAX_CHARS]
        for key, value in candidates.items()
        if value
    }
