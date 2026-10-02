"""Pipeline execution context value object encapsulating session and identity provenance."""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import ChannelId, ChannelName, ContentId


@dataclass(frozen=True, slots=True)
class PipelineExecutionContext:
    """Execution context binding session, identity, channel, and content provenance.

    Passed across pipeline stages to eliminate repetitive parameter clumps (ADR-031).

    Attributes:
        session_id: Unique pipeline run session identifier.
        user_identity: Authenticated or anonymous execution principal.
        channel_name: Human-readable creator channel name.
        content_id: Target canonical content/media identifier.
        channel_id: Optional platform channel identifier.
    """

    session_id: PipelineSessionId
    user_identity: UserIdentity
    channel_name: ChannelName
    content_id: ContentId
    channel_id: ChannelId | None = None
