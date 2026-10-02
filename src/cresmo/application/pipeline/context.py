"""Pipeline execution context value object encapsulating session, user, channel, and content provenance."""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import Channel, ChannelId, ChannelName, Content, ContentId


@dataclass(frozen=True, slots=True)
class PipelineExecutionContext:
    """Execution context binding session, user identity, channel, and content provenance.

    Encapsulates the four foundational pillars of pipeline execution:
    1. session_id: unique run session identifier
    2. user_identity: authenticated or anonymous operator
    3. channel: composite creator and channel identity
    4. content: composite media item, video, and transcript identity

    Conforms to ADR-031 and ADR-032.
    """

    session_id: PipelineSessionId
    user_identity: UserIdentity
    channel: Channel
    content: Content

    def __init__(
        self,
        session_id: PipelineSessionId,
        user_identity: UserIdentity,
        channel: Channel | None = None,
        content: Content | None = None,
        *,
        # Backward-compatible keyword arguments
        channel_name: ChannelName | str | None = None,
        content_id: ContentId | str | None = None,
        channel_id: ChannelId | str | None = None,
    ) -> None:
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "user_identity", user_identity)

        if channel is not None:
            resolved_channel = channel
        elif channel_name is not None:
            resolved_channel = Channel.from_name(name=channel_name, id=channel_id)
        else:
            raise ValueError("Either 'channel' or 'channel_name' must be provided.")
        object.__setattr__(self, "channel", resolved_channel)

        if content is not None:
            resolved_content = content
        elif content_id is not None:
            resolved_content = Content.create(id=content_id)
        else:
            raise ValueError("Either 'content' or 'content_id' must be provided.")
        object.__setattr__(self, "content", resolved_content)

    @property
    def channel_name(self) -> ChannelName:
        """Backward-compatible convenience property for human-readable channel name."""
        return self.channel.name

    @property
    def channel_id(self) -> ChannelId | None:
        """Backward-compatible convenience property for channel platform identifier."""
        return self.channel.id

    @property
    def content_id(self) -> ContentId:
        """Backward-compatible convenience property for canonical content identifier."""
        return self.content.id

    @property
    def video(self) -> Content:
        """Alias for content providing natural media terminology."""
        return self.content
