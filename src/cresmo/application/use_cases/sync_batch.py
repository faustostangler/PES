"""Application Use Case orchestrating filtered multi-channel synchronization.

Conforms to:
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final

from cresmo.application.ports import ChannelTaxonomyPort
from cresmo.application.use_cases.discovery.manifests import read_manifest_lines
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    SyncFilterCriteria,
    normalize_to_uploads_playlist_url,
)
from cresmo.domain.value_objects.media import ALLOWED_URL_SCHEMES

if TYPE_CHECKING:
    from cresmo.application.use_cases.sync_channel import SyncChannelUseCase

DEFAULT_SYNC_LOOKBACK_DAYS: Final[int] = 7 * 52 * 2
DEFAULT_SYNC_MAX_VIDEOS: Final[int] = 250
DEFAULT_SYNC_MODE_DESCRIPTION: Final[str] = "full manifest"
MODE_TOKEN_DELIMITER: Final[str] = ","
MODE_PARTS_SEPARATOR: Final[str] = ", "
YOUTUBE_WATCH_URL_PREFIX: Final[str] = "https://www.youtube.com/watch?v="
DIRECT_VIDEO_MAX_COUNT: Final[int] = 1


class SyncTargetEventKind(StrEnum):
    """Discriminator for per-target synchronization progress events."""

    VIDEO = "video"
    CHANNEL = "channel"


@dataclass(frozen=True, slots=True)
class SyncTargetEvent:
    """Immutable telemetry event emitted after syncing a video or channel feed."""

    kind: SyncTargetEventKind
    target: str
    total_discovered: int
    processed: int
    skipped: int
    failed: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class SyncBatchRequest:
    """Immutable request DTO for multi-target feed synchronization."""

    channels: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    video_ids: tuple[str, ...] = ()
    manifest: Path | None = None
    lookback: int = DEFAULT_SYNC_LOOKBACK_DAYS
    max_videos: int = DEFAULT_SYNC_MAX_VIDEOS
    dry_run: bool = False
    force_refresh: bool = False


@dataclass(frozen=True, slots=True)
class SyncBatchOutcome:
    """Immutable summary outcome returned by SyncBatchUseCase."""

    channels_synced: int = 0
    total_discovered: int = 0
    total_processed: int = 0
    total_skipped: int = 0
    total_failed: int = 0
    no_matching_channels: bool = False
    mode_description: str = DEFAULT_SYNC_MODE_DESCRIPTION
    manifest_path: Path | None = None
    direct_video_mode: bool = False

    @property
    def success(self) -> bool:
        """Return True iff zero sync targets failed."""
        return self.total_failed == 0


def _describe_mode(criteria: SyncFilterCriteria) -> str:
    parts: list[str] = []
    if criteria.channels:
        parts.append(f"channels={MODE_TOKEN_DELIMITER.join(criteria.channels)}")
    if criteria.categories:
        parts.append(f"categories={MODE_TOKEN_DELIMITER.join(criteria.categories)}")
    return MODE_PARTS_SEPARATOR.join(parts) if parts else DEFAULT_SYNC_MODE_DESCRIPTION


def _emit(
    on_event: Callable[[SyncTargetEvent], None] | None,
    event: SyncTargetEvent,
) -> None:
    if on_event is not None:
        on_event(event)


class SyncBatchUseCase:
    """Application orchestrator for filtered channel and direct-video sync batches."""

    def __init__(
        self,
        sync_channel_use_case: SyncChannelUseCase,
        default_manifest_path: Path | None = None,
        taxonomy_port: ChannelTaxonomyPort | None = None,
    ) -> None:
        self._sync_channel_use_case = sync_channel_use_case
        self._default_manifest_path = default_manifest_path
        self._taxonomy_port = taxonomy_port

    def execute(
        self,
        request: SyncBatchRequest,
        on_event: Callable[[SyncTargetEvent], None] | None = None,
    ) -> SyncBatchOutcome:
        """Resolve sync targets, enforce ADR-012 ordering, and execute syncs.

        Args:
            request: Immutable sync batch filter and window parameters.
            on_event: Optional per-target progress observer callback.

        Returns:
            SyncBatchOutcome aggregating discovered, processed, skipped, and failed counts.
        """
        filter_criteria = SyncFilterCriteria.from_strings(
            channels=list(request.channels),
            categories=list(request.categories),
            video_ids=list(request.video_ids),
        )

        if filter_criteria.video_ids:
            return self._sync_targets(
                targets=sorted(filter_criteria.video_ids),
                kind=SyncTargetEventKind.VIDEO,
                request=request,
                on_event=on_event,
                manifest_path=None,
            )

        manifest_path = request.manifest or self._default_manifest_path
        channels_to_sync = self._resolve_channels(manifest_path, filter_criteria)
        if not channels_to_sync:
            return SyncBatchOutcome(
                no_matching_channels=True,
                mode_description=_describe_mode(filter_criteria),
                manifest_path=manifest_path,
            )

        # ADR-012: enforce case-insensitive ascending alphabetical processing order
        sorted_channels = sorted(channels_to_sync, key=str.lower)
        return self._sync_targets(
            targets=sorted_channels,
            kind=SyncTargetEventKind.CHANNEL,
            request=request,
            on_event=on_event,
            manifest_path=manifest_path,
        )

    def _sync_targets(
        self,
        *,
        targets: Sequence[str],
        kind: SyncTargetEventKind,
        request: SyncBatchRequest,
        on_event: Callable[[SyncTargetEvent], None] | None,
        manifest_path: Path | None,
    ) -> SyncBatchOutcome:
        total_discovered = 0
        total_processed = 0
        total_skipped = 0
        total_failed = 0
        is_direct_video = kind is SyncTargetEventKind.VIDEO

        for target in targets:
            channel_url = (
                target
                if not is_direct_video or target.startswith(ALLOWED_URL_SCHEMES)
                else f"{YOUTUBE_WATCH_URL_PREFIX}{target}"
            )
            query = ChannelFeedQuery(
                channel_url=channel_url,
                lookback_days=request.lookback,
                max_videos=DIRECT_VIDEO_MAX_COUNT if is_direct_video else request.max_videos,
            )
            summary = self._sync_channel_use_case.execute(
                query=query,
                dry_run=request.dry_run,
                force_refresh=request.force_refresh,
            )
            total_discovered += summary.total_discovered
            total_processed += summary.processed_count
            total_skipped += summary.skipped_count
            total_failed += summary.failed_count
            _emit(
                on_event,
                SyncTargetEvent(
                    kind=kind,
                    target=target,
                    total_discovered=summary.total_discovered,
                    processed=summary.processed_count,
                    skipped=summary.skipped_count,
                    failed=summary.failed_count,
                    duration_seconds=summary.duration_seconds,
                ),
            )

        return SyncBatchOutcome(
            channels_synced=0 if is_direct_video else len(targets),
            total_discovered=total_discovered,
            total_processed=total_processed,
            total_skipped=total_skipped,
            total_failed=total_failed,
            manifest_path=manifest_path,
            direct_video_mode=is_direct_video,
        )

    def _resolve_channels(
        self,
        manifest_path: Path | None,
        filter_criteria: SyncFilterCriteria,
    ) -> list[str]:
        if filter_criteria.channels:
            return [
                ch
                if ch.startswith(ALLOWED_URL_SCHEMES)
                else normalize_to_uploads_playlist_url(ch)
                for ch in filter_criteria.channels
            ]

        classifier = self._taxonomy_port.classify if self._taxonomy_port is not None else None
        lines = read_manifest_lines(manifest_path)
        resolved: list[str] = []
        for channel_url in lines:
            normalized = normalize_to_uploads_playlist_url(channel_url)
            if filter_criteria.is_empty() or filter_criteria.matches_category(
                channel_url=channel_url,
                classifier=classifier,
            ):
                resolved.append(normalized)
        return resolved
