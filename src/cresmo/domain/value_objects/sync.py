"""Channel Synchronization and Filtering Value Objects.

Conforms to:
- ADR-012: Channel Synchronization and Selective Batch Discovery
- SPEC-003: §2 (Channel Sync Models & Normalization Rules)
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects.identity import ChannelName, ContentId
from cresmo.domain.value_objects.media import PipelineStatus


def _resolve_channel_name_and_url(
    channel_name: ChannelName | str | None,
    channel_url: str | None,
) -> tuple[str, str]:
    """Extract normalized lowercase (channel_name, channel_url) pair."""
    resolved_url = (channel_url or "").strip().lower()
    if isinstance(channel_name, ChannelName):
        return channel_name.value.strip().lower(), resolved_url
    if isinstance(channel_name, str):
        resolved_name = channel_name.strip().lower()
        if not resolved_url and ("http" in resolved_name or "/" in resolved_name or "@" in resolved_name):
            return resolved_name, resolved_name
        return resolved_name, resolved_url
    return "", resolved_url


def _target_matches_channel(target: str, channel_name: str, channel_url: str) -> bool:
    """Check if single target filter token matches normalized name or url."""
    if channel_name and (target in channel_name or channel_name in target):
        return True
    if channel_url and target in channel_url:
        return True
    if channel_name and target.startswith("@") and target[1:] in channel_name:
        return True
    if channel_url and f"@{target}" in channel_url:
        return True
    return bool(channel_name and f"@{target}" in channel_name)


@dataclass(frozen=True)
class SyncFilterCriteria:
    """Immutable multi-criteria filter for channel synchronization and batch discovery.

    Conforms to ADR-012.

    Attributes:
        channels: Tuple of target channel names, handles, or URLs (normalized lowercase).
        categories: Tuple of target domain categories or volatility types (normalized lowercase).
        video_ids: Tuple of target video IDs or URLs.
    """

    channels: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    video_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized_channels: list[str] = []
        for channel_token in self.channels:
            cleaned = channel_token.strip().lower()
            if not cleaned:
                raise DomainValidationError("Channel filter token cannot be empty.")
            normalized_channels.append(cleaned)

        normalized_categories: list[str] = []
        for category_token in self.categories:
            cleaned = category_token.strip().lower()
            if not cleaned:
                raise DomainValidationError("Category filter token cannot be empty.")
            normalized_categories.append(cleaned)

        normalized_video_ids: list[str] = []
        for video_token in self.video_ids:
            cleaned = video_token.strip()
            if not cleaned:
                raise DomainValidationError("Video filter token cannot be empty.")
            normalized_video_ids.append(cleaned)

        object.__setattr__(self, "channels", tuple(normalized_channels))
        object.__setattr__(self, "categories", tuple(normalized_categories))
        object.__setattr__(self, "video_ids", tuple(normalized_video_ids))

    @classmethod
    def from_strings(
        cls,
        channels: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        video_ids: Iterable[str] | None = None,
    ) -> SyncFilterCriteria:
        """Parse multi-value strings (including comma-separated lists) into a SyncFilterCriteria."""

        def _parse_tokens(items: Iterable[str] | None) -> tuple[str, ...]:
            if not items:
                return ()
            tokens: list[str] = []
            for item in items:
                if not item:
                    continue
                for part in item.split(","):
                    token = part.strip()
                    if token:
                        tokens.append(token)
            return tuple(tokens)

        return cls(
            channels=_parse_tokens(channels),
            categories=_parse_tokens(categories),
            video_ids=_parse_tokens(video_ids),
        )

    def is_empty(self) -> bool:
        """Return True if no filter criteria are specified (full pipeline flow)."""
        return not self.channels and not self.categories and not self.video_ids

    def matches_channel(
        self,
        channel_name: ChannelName | None = None,
        channel_url: str | None = None,
    ) -> bool:
        """Evaluate whether a channel matches the configured channel criteria."""
        if not self.channels:
            return True

        resolved_name, resolved_url = _resolve_channel_name_and_url(channel_name, channel_url)
        return any(
            _target_matches_channel(target, resolved_name, resolved_url)
            for target in self.channels
        )

    def matches_category(
        self,
        channel_name: ChannelName | None = None,
        channel_url: str | None = None,
    ) -> bool:
        """Evaluate whether a channel matches the configured category criteria.

        Per ADR-012, checks both domain name (e.g. 'politics_br') and volatility type
        (e.g. 'volatile' or 'perennial') returned by classify_channel.
        """
        if not self.categories:
            return True

        target: ChannelName | str = (
            channel_name if channel_name is not None else (channel_url or "")
        )
        domain, volatility_category = classify_channel(target)
        domain_lower = domain.lower()
        volatility_lower = volatility_category.lower()

        return domain_lower in self.categories or volatility_lower in self.categories

    def matches_video(
        self,
        video_id: ContentId | None = None,
        video_url: str | None = None,
    ) -> bool:
        """Evaluate whether a video matches the configured video ID/URL criteria."""
        if not self.video_ids:
            return True

        cleaned_video_url = (video_url or "").strip()
        if isinstance(video_id, ContentId):
            cleaned_video_id = video_id.value.strip()
        elif isinstance(video_id, str):
            cleaned_video_id = video_id.strip()
            if not cleaned_video_url and ("http" in cleaned_video_id or "/" in cleaned_video_id):
                cleaned_video_url = cleaned_video_id
        else:
            cleaned_video_id = ""

        for target in self.video_ids:
            target_str = target.strip()
            if cleaned_video_id and (target_str == cleaned_video_id or cleaned_video_id in target_str):
                return True
            if cleaned_video_url and (target_str in cleaned_video_url or cleaned_video_url in target_str):
                return True

        return False


@dataclass(frozen=True)
class SyncSummary:
    """Immutable batch execution report aggregating outcomes for a channel sync run.

    Attributes:
        channel_url: Canonical target channel URL.
        total_discovered: Total count of items retrieved from channel crawler.
        processed_count: Count of items successfully processed and persisted.
        skipped_count: Count of items bypassed due to idempotency ledger matches.
        failed_count: Count of items that failed ingestion or synthesis.
        duration_seconds: Wall-clock duration of the sync run.
        status: Overall pipeline execution termination status.
    """

    channel_url: str
    total_discovered: int
    processed_count: int
    skipped_count: int
    failed_count: int
    duration_seconds: float
    status: PipelineStatus
