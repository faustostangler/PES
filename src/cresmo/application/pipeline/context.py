"""Pipeline execution context value object encapsulating user, channel, and content provenance."""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.entities import UserIdentity
from cresmo.domain.value_objects import Channel, Content


@dataclass(frozen=True, slots=True)
class PipelineExecutionContext:
    """Execution context binding user identity, channel, and content provenance.

    Encapsulates the three foundational pillars of pipeline execution:
    1. user_identity: authenticated or anonymous operator
    2. channel: composite creator and channel identity (Channel VO)
    3. content: composite media item, video, transcript, and session identity (Content VO)

    Conforms to ADR-031, ADR-032, and ADR-033 (zero backward-compatibility shims).
    """

    user_identity: UserIdentity
    channel: Channel
    content: Content

    def __post_init__(self) -> None:
        if not isinstance(self.user_identity, UserIdentity):
            raise TypeError(f"user_identity must be UserIdentity, got {type(self.user_identity)}")
        if not isinstance(self.channel, Channel):
            raise TypeError(f"channel must be Channel, got {type(self.channel)}")
        if not isinstance(self.content, Content):
            raise TypeError(f"content must be Content, got {type(self.content)}")
        if not self.content.session_id:
            ch_token = self.channel.id.value if self.channel.id else self.channel.name
            object.__setattr__(
                self,
                "content",
                Content(
                    id=self.content.id,
                    title=self.content.title,
                    text=self.content.text,
                    session_id=f"{ch_token}:{self.content.id.value}",
                ),
            )
