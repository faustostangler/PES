"""Pipeline execution context value object encapsulating session, user, channel, and content provenance."""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import Channel, Content


@dataclass(frozen=True, slots=True)
class PipelineExecutionContext:
    """Execution context binding session, user identity, channel, and content provenance.

    Encapsulates the four foundational pillars of pipeline execution:
    1. session_id: unique run session identifier
    2. user_identity: authenticated or anonymous operator
    3. channel: composite creator and channel identity (Channel VO)
    4. content: composite media item, video, and transcript identity (Content VO)

    Conforms to ADR-031, ADR-032, and ADR-033 (zero backward-compatibility shims).
    """

    session_id: PipelineSessionId
    user_identity: UserIdentity
    channel: Channel
    content: Content

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, PipelineSessionId):
            raise TypeError(f"session_id must be PipelineSessionId, got {type(self.session_id)}")
        if not isinstance(self.user_identity, UserIdentity):
            raise TypeError(f"user_identity must be UserIdentity, got {type(self.user_identity)}")
        if not isinstance(self.channel, Channel):
            raise TypeError(f"channel must be Channel, got {type(self.channel)}")
        if not isinstance(self.content, Content):
            raise TypeError(f"content must be Content, got {type(self.content)}")
