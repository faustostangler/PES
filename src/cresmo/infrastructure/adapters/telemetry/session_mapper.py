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
_SESSION_ID_SEPARATOR: Final[str] = ":"
_TENANT_CHANNEL_PREFIX: Final[str] = "channel:"
_TAG_AUTH_PREFIX: Final[str] = "auth:"
_TAG_GIT_PREFIX: Final[str] = "git:"
_TAG_BATCH_PREFIX: Final[str] = "batch:"
_OBS_TYPE_SPAN: Final[str] = "span"
_ATTR_OBS_TYPE: Final[str] = "langfuse.observation.type"
_ATTR_SESSION_ID: Final[str] = "langfuse.session.id"
_ATTR_USER_ID: Final[str] = "langfuse.user.id"
_ATTR_TRACE_NAME: Final[str] = "langfuse.trace.name"
_ATTR_TRACE_TAGS: Final[str] = "langfuse.trace.tags"
_ATTR_PIPELINE_VERSION: Final[str] = "cresmo.pipeline.version"
_ATTR_CHANNEL_ID: Final[str] = "cresmo.channel.id"
_ATTR_CONTENT_ID: Final[str] = "cresmo.content.id"
_ATTR_CHANNEL_NAME: Final[str] = "cresmo.channel.name"
_ATTR_CONTENT_TITLE: Final[str] = "cresmo.content.title"
_ATTR_TENANT_ID: Final[str] = "cresmo.tenant_id"
_ATTR_USER_IS_ANON: Final[str] = "cresmo.user.is_anonymous"
_ATTR_USER_PROVIDER: Final[str] = "cresmo.user.provider"
_ATTR_WORD_COUNT: Final[str] = "cresmo.content.word_count"
_ATTR_CHAR_COUNT: Final[str] = "cresmo.content.char_count"
_ATTR_FORCE_REPROCESS: Final[str] = "cresmo.pipeline.force_reprocess"
_ATTR_EXPANSION_MAX_PASSES: Final[str] = "cresmo.pipeline.expansion_max_passes"
_ATTR_CONTENT_SOURCE: Final[str] = "cresmo.content.source"
_ATTR_PUBLICATION_DATE: Final[str] = "cresmo.content.publication_date"
_ATTR_GIT_SHA: Final[str] = "cresmo.pipeline.git_sha"
_ATTR_USER_SUBJECT: Final[str] = "cresmo.user.subject"
_ATTR_BATCH_ID: Final[str] = "cresmo.batch_id"
_KEY_CHANNEL_ID: Final[str] = "channel_id"
_KEY_CONTENT_ID: Final[str] = "content_id"
_KEY_CHANNEL_NAME: Final[str] = "channel_name"
_KEY_CONTENT_TITLE: Final[str] = "content_title"
_KEY_RAW_CHARACTERS: Final[str] = "raw_characters"
_KEY_RAW_WORDS: Final[str] = "raw_words"
_KEY_BATCH_ID: Final[str] = "batch_id"
_KEY_VIDEO_URL: Final[str] = "video_url"


def short_git_sha(git_sha: str | None) -> str | None:
    """Normalize and truncate git commit SHA to short length."""
    if git_sha and git_sha.strip():
        return git_sha.strip()[:_GIT_SHA_SHORT_LENGTH]
    return None


def parse_session_parts(session_id: PipelineSessionId) -> tuple[str, str]:
    """Extract (channel_token, content_token) from PipelineSessionId value."""
    parts = session_id.value.split(_SESSION_ID_SEPARATOR)
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
    tenant = spec.channel_tenant_id or f"{_TENANT_CHANNEL_PREFIX}{channel_token}"

    effective_trace_name = (
        resolved_trace_name
        if resolved_trace_name is not None
        else resolve_root_operation_name(spec.trace_name)[0]
    )
    tags = [resolved_channel_name, pipeline_version, f"{_TAG_AUTH_PREFIX}{user.provider}"]

    attributes: dict[str, Any] = {
        _ATTR_OBS_TYPE: _OBS_TYPE_SPAN,
        _ATTR_SESSION_ID: spec.session_id.value,
        _ATTR_USER_ID: user.value,
        _ATTR_TRACE_NAME: effective_trace_name,
        _ATTR_TRACE_TAGS: tags,
        _ATTR_PIPELINE_VERSION: pipeline_version,
        _ATTR_CHANNEL_ID: channel_id,
        _ATTR_CONTENT_ID: content_id,
        _ATTR_CHANNEL_NAME: resolved_channel_name,
        _ATTR_CONTENT_TITLE: content_title,
        _ATTR_TENANT_ID: tenant,
        _ATTR_USER_IS_ANON: user.is_anonymous,
        _ATTR_USER_PROVIDER: user.provider,
        _ATTR_WORD_COUNT: spec.raw_words,
        _ATTR_CHAR_COUNT: spec.raw_characters,
        _ATTR_FORCE_REPROCESS: spec.force_reprocess,
    }

    if spec.expansion_max_passes is not None:
        attributes[_ATTR_EXPANSION_MAX_PASSES] = spec.expansion_max_passes

    if spec.source.strip():
        attributes[_ATTR_CONTENT_SOURCE] = spec.source.strip()

    if spec.publication_date and spec.publication_date.strip():
        attributes[_ATTR_PUBLICATION_DATE] = spec.publication_date.strip()

    if clean_sha := short_git_sha(git_sha):
        attributes[_ATTR_GIT_SHA] = clean_sha
        tags.append(f"{_TAG_GIT_PREFIX}{clean_sha}")

    if user.subject:
        attributes[_ATTR_USER_SUBJECT] = user.subject

    clean_batch_id = spec.batch_id.strip() if spec.batch_id else ""
    if clean_batch_id:
        attributes[_ATTR_BATCH_ID] = clean_batch_id
        tags.append(f"{_TAG_BATCH_PREFIX}{clean_batch_id}")

    input_payload: dict[str, Any] = {
        _KEY_CHANNEL_ID: channel_id,
        _KEY_CONTENT_ID: content_id,
        _KEY_CHANNEL_NAME: resolved_channel_name,
        _KEY_CONTENT_TITLE: content_title,
        _KEY_RAW_CHARACTERS: str(spec.raw_characters),
        _KEY_RAW_WORDS: str(spec.raw_words),
    }
    if clean_batch_id:
        input_payload[_KEY_BATCH_ID] = clean_batch_id
    if spec.video_url and spec.video_url.strip():
        input_payload[_KEY_VIDEO_URL] = spec.video_url.strip()

    return attributes, tags, input_payload


def build_propagated_trace_metadata(attributes: Mapping[str, Any]) -> dict[str, str]:
    """Derive short identity metadata (<= 200 chars) propagated to every child observation."""
    candidates = {
        _KEY_CHANNEL_ID: attributes.get(_ATTR_CHANNEL_ID),
        _KEY_CHANNEL_NAME: attributes.get(_ATTR_CHANNEL_NAME),
        _KEY_CONTENT_ID: attributes.get(_ATTR_CONTENT_ID),
        _KEY_CONTENT_TITLE: attributes.get(_ATTR_CONTENT_TITLE),
        _KEY_BATCH_ID: attributes.get(_ATTR_BATCH_ID),
    }
    return {
        key: str(value)[:_LANGFUSE_PROPAGATED_VALUE_MAX_CHARS]
        for key, value in candidates.items()
        if value
    }
