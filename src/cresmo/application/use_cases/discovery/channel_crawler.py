"""Concurrent channel feed crawler and resolver service.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta

from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discovery.manifests import (
    matches_category_target,
    matches_channel_target,
    matches_video_target,
)
from cresmo.application.use_cases.discovery.models import (
    _BatchSourceAccumulator,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    SourceModality,
    SyncFilterCriteria,
)

logger = logging.getLogger(__name__)


class ChannelFeedCrawlerService:
    """Encapsulates concurrent channel resolution and feed probing logic."""

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        notify_fn: Callable[[str], None] | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self._notify = notify_fn or (lambda msg: None)

    def resolve_remote_channels(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
        filter_criteria: SyncFilterCriteria | None = None,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        criteria = filter_criteria or SyncFilterCriteria()
        if not videos:
            return

        max_workers = max(1, min(workers, len(videos)))
        self._notify(
            f"[crawler] Resolving parent channels for {len(videos)} seed videos with {max_workers} workers\n"
        )
        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="CresmoChannelResolver",
        ) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                if stop_event is not None and stop_event.is_set():
                    break
                try:
                    resolved_chan = fut.result()
                    if (
                        isinstance(resolved_chan, str)
                        and resolved_chan.strip()
                        and resolved_chan not in probed_channels
                    ):
                        chan_clean = resolved_chan.strip()
                        if criteria.is_empty() or (
                            matches_channel_target(criteria, chan_clean)
                            and matches_category_target(criteria, chan_clean)
                        ):
                            probed_channels.add(chan_clean)
                            channels_to_probe.append(chan_clean)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def probe_channel_feeds(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
        filter_criteria: SyncFilterCriteria | None = None,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently (Stage B).

        ADR-012: Channels are pre-sorted alphabetically by caller. Applies video ID filter
        when filter_criteria specifies video_ids.
        """
        criteria = filter_criteria or SyncFilterCriteria()
        if not channels:
            return

        self._notify(
            f"[crawler] Stage B: Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))
        discovered_count = 0

        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="CresmoFeedProber",
        ) as executor:
            future_to_url = {
                executor.submit(
                    self.probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                if stop_event is not None and stop_event.is_set():
                    break
                try:
                    discovered_urls = future.result()
                except Exception as exc:  # noqa: BLE001
                    u = future_to_url[future]
                    self._notify(f"[crawler] Warning: Failed to probe feed for {u}: {exc}\n")
                    continue

                for d_url in discovered_urls:
                    if stop_event is not None and stop_event.is_set():
                        break
                    cid = ContentId.extract_from_text(d_url)
                    vid_token = cid or d_url
                    # Stage B: Skip if already in raw lake or already queued
                    if not acc.has_seen(vid_token):
                        # ADR-012: apply video ID filter before scheduling ingestion
                        if not matches_video_target(criteria, cid or d_url, d_url):
                            continue
                        added = acc.add_source(
                            kind=SourceModality.URL, target=d_url, content_id=cid
                        )
                        if added is not None:
                            discovered_count += 1

        self._notify(
            f"[crawler] Stage B complete: Discovered {discovered_count} new video(s) for ingestion "
            f"(excluding items already existing in local raw lake)\n"
        )

    def probe_single_channel_feed(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []
