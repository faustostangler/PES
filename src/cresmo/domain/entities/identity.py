"""Identity, Session, Tenant, and Telemetry Value Objects and Entities.

Conforms to:
- ADR-016: Cost-Center Observability and Channel Multi-Tenancy
- ADR-027: User & Worker Unified Identity Modalities
- ADR-013: LLM Judge Friction Metrics
"""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
)

CANONICAL_SESSION_ID_PARTS: int = 2
LEGACY_SESSION_ID_PARTS: int = 3
PIPELINE_SESSION_ID_PART_COUNT: int = LEGACY_SESSION_ID_PARTS


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
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    @classmethod
    def create(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @property
    def channel_id(self) -> str:
        """Algorithmic channel identifier token stored in the session key (ID or name)."""
        parts = self.value.split(":")
        return (
            parts[1]
            if parts[0] == "content" and len(parts) == LEGACY_SESSION_ID_PARTS
            else parts[0]
        )

    @property
    def content_id(self) -> str:
        """Content identifier stored in the session key."""
        parts = self.value.split(":")
        return (
            parts[2]
            if parts[0] == "content" and len(parts) == LEGACY_SESSION_ID_PARTS
            else parts[1]
        )


@dataclass(frozen=True)
class UserIdentity:
    """Value Object representing the user/operator executing the synthesis pipeline.

    Supports forward-compatible identity modalities per ADR-027:
    - Anonymous (unauthenticated, guest, CLI): 'anonymous'
    - Identified (authenticated via IAM / OAuth): 'user:iam:alice' or 'user:oauth:subject'
    - Scheduled workers (daemons, batch sync): 'system:worker'
    - Channel fallback (legacy background worker pipelines): 'channel:...'
    """

    value: str
    is_anonymous: bool = True
    provider: str = "anonymous"
    subject: str = ""

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    @classmethod
    def anonymous(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def identified(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

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

    @classmethod
    def from_channel(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )


@dataclass(frozen=True)
class JudgeFrictionMetric:
    """Value Object calculating LLM-as-a-judge retry friction per ADR-013 & ADR-016.

    Friction ratio = (iterations - 1) / (max_iterations - 1).
    0.0 = perfect first pass; 1.0 = all retries exhausted.
    """

    iterations: int
    max_iterations: int
    verdict: str

    def __post_init__(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    @property
    def friction_ratio(self) -> float:
        if self.iterations <= 1 or self.max_iterations <= 1:
            return 0.0
        return min(1.0, (self.iterations - 1) / (self.max_iterations - 1))
