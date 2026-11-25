"""Identity, Session, Tenant, and Telemetry Value Objects and Entities.

Conforms to:
- ADR-016: Cost-Center Observability and Channel Multi-Tenancy
- ADR-027: User & Worker Unified Identity Modalities
- ADR-013: LLM Judge Friction Metrics
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
)

_CANONICAL_SESSION_ID_PARTS: Final[int] = 2


@dataclass(frozen=True)
class PipelineSessionId:
    """Value Object representing the holistic multi-stage content lifecycle session.

    Conforms to ADR-016, ADR-027, and ADR-033.
    Ensures end-to-end Session Replay in Langfuse for exactly one content item.
    Canonical format: {channel_id}:{content_id}
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) != _CANONICAL_SESSION_ID_PARTS or not parts[0].strip() or not parts[1].strip():
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    @classmethod
    def create(
        cls,
        channel: Channel | ChannelName,
        content_id: Content | ContentId,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO or human-readable ChannelName.
            content_id: Composite Content VO or ContentId.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = channel_id.value if channel_id else channel.value

        content_identifier = (
            content_id.id.value if isinstance(content_id, Content) else content_id.value
        )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @property
    def channel_id(self) -> str:
        """Extract the channel identifier from the session id."""
        return self.value.split(":")[0]

    @property
    def content_id(self) -> str:
        """Extract the content identifier from the session id."""
        return self.value.split(":")[1]


@dataclass(frozen=True)
class UserIdentity:
    """Value Object representing the user/operator executing the synthesis pipeline.

    Supports identity modalities per ADR-027 and ADR-077:
    - Anonymous (unauthenticated, guest, CLI): 'anonymous'
    - Scheduled workers (daemons, batch sync): 'system:worker'
    """

    value: str
    is_anonymous: bool = True
    provider: str = "anonymous"
    subject: str = ""

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    @classmethod
    def anonymous(cls) -> UserIdentity:
        """Create an anonymous user identity."""
        return cls(value="anonymous")

    @classmethod
    def worker(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )
