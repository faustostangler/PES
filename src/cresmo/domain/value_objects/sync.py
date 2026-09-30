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
    c_url = (channel_url or "").strip().lower()
    if isinstance(channel_name, ChannelName):
        return channel_name.value.strip().lower(), c_url
    if isinstance(channel_name, str):
        c_name = channel_name.strip().lower()
        if not c_url and ("http" in c_name or "/" in c_name or "@" in c_name):
            return c_name, c_name
        return c_name, c_url
    return "", c_url


def _target_matches_channel(target: str, c_name: str, c_url: str) -> bool:
    """Check if single target filter token matches normalized name or url."""
    if c_name and (target in c_name or c_name in target):
        return True
    if c_url and target in c_url:
        return True
    if c_name and target.startswith("@") and target[1:] in c_name:
        return True
    if c_url and f"@{target}" in c_url:
        return True
    return bool(c_name and f"@{target}" in c_name)


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
        norm_channels: list[str] = []
        for ch in self.channels:
            cleaned = ch.strip().lower()
            if not cleaned:
                raise DomainValidationError("Channel filter token cannot be empty.")
            norm_channels.append(cleaned)

        norm_categories: list[str] = []
        for cat in self.categories:
            cleaned = cat.strip().lower()
            if not cleaned:
                raise DomainValidationError("Category filter token cannot be empty.")
            norm_categories.append(cleaned)

        norm_vids: list[str] = []
        for vid in self.video_ids:
            cleaned = vid.strip()
            if not cleaned:
                raise DomainValidationError("Video filter token cannot be empty.")
            norm_vids.append(cleaned)

        object.__setattr__(self, "channels", tuple(norm_channels))
        object.__setattr__(self, "categories", tuple(norm_categories))
        object.__setattr__(self, "video_ids", tuple(norm_vids))

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
                    p = part.strip()
                    if p:
                        tokens.append(p)
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

        c_name, c_url = _resolve_channel_name_and_url(channel_name, channel_url)
        return any(_target_matches_channel(target, c_name, c_url) for target in self.channels)

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
        domain, cat_type = classify_channel(target)
        domain_lower = domain.lower()
        cat_lower = cat_type.lower()

        return domain_lower in self.categories or cat_lower in self.categories

    def matches_video(
        self,
        video_id: ContentId | None = None,
        video_url: str | None = None,
    ) -> bool:
        """Evaluate whether a video matches the configured video ID/URL criteria."""
        if not self.video_ids:
            return True

        vurl_clean = (video_url or "").strip()
        if isinstance(video_id, ContentId):
            vid_clean = video_id.value.strip()
        elif isinstance(video_id, str):
            vid_clean = video_id.strip()
            if not vurl_clean and ("http" in vid_clean or "/" in vid_clean):
                vurl_clean = vid_clean
        else:
            vid_clean = ""

        for target in self.video_ids:
            target_str = target.strip()
            if vid_clean and (target_str == vid_clean or vid_clean in target_str):
                return True
            if vurl_clean and (target_str in vurl_clean or vurl_clean in target_str):
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
