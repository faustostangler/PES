"""Channel Synchronization Use Case for Cresmo Knowledge Engine.

Coordinates feed polling, lookback window filtering, ACID ledger idempotency checks,
and bounded pipeline execution for channels and playlists per ADR-003 and SPEC-003.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final

from cresmo.application.ports import LedgerRepositoryPort, MediaIngestionPort
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.domain.entities import UserIdentity
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    BatchId,
    ChannelFeedQuery,
    DiscoveredMediaItem,
    PipelineStatus,
    SyncSummary,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline.coordinator import CresmoPipeline

DURATION_ROUND_DECIMAL_PLACES: Final[int] = 3


class SyncChannelUseCase:
    """Application orchestrator coordinating feed polling, idempotency, and synthesis."""

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        ledger_port: LedgerRepositoryPort,
        pipeline: CresmoPipeline,
        preflight_checker: PreflightHealthChecker | None = None,
    ) -> None:
        """Initialize channel sync orchestrator with injected dependencies.

        Args:
            media_ingestion_port: Port for discovering channel/playlist feeds.
            ledger_port: Persistence port for querying and updating idempotency state.
            pipeline: Core synthesis pipeline orchestrator.
            preflight_checker: Optional diagnostic checker enforcing environment invariants.
        """
        self.media_ingestion_port = media_ingestion_port
        self.ledger_port = ledger_port
        self.pipeline = pipeline
        self.preflight_checker = preflight_checker

    def execute(
        self,
        query: ChannelFeedQuery,
        dry_run: bool = False,
        force_refresh: bool = False,
    ) -> SyncSummary:
        """Execute channel synchronization workflow.

        Args:
            query: Encapsulated query constraints (channel URL, lookback days, max videos).
            dry_run: If True, discovers and filters items without invoking synthesis.
            force_refresh: If True, re-processes items even if marked completed in ledger.

        Returns:
            SyncSummary detailing discovery count, processed count, skips, and status.
        """
        # Step 1: Execute preflight sanity check fail-fast
        if self.preflight_checker is not None:
            self.preflight_checker.check_all().assert_healthy()

        start_time = time.perf_counter()

        # Step 2: Query feed via MediaIngestionPort
        raw_items = self.media_ingestion_port.discover_channel_feed(query)

        # Step 3: Filter by lookback window
        now = datetime.now(UTC)
        cutoff = now - timedelta(days=query.lookback_days)

        in_window_items: list[DiscoveredMediaItem] = []
        for item in raw_items:
            pub_date = item.published_at
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=UTC)

            if pub_date >= cutoff:
                in_window_items.append(item)

            if len(in_window_items) >= query.max_videos:
                break

        processed_count = 0
        skipped_count = 0
        failed_count = 0
        batch_id = BatchId.generate()

        if not dry_run and in_window_items:
            self.pipeline.warmup()

        # Step 4: Process items with idempotency skip check
        for item in in_window_items:
            # Idempotency check against ledger avoids downloading already processed media
            if not force_refresh and self.ledger_port.is_processed(item.content_id):
                skipped_count += 1
                continue

            if dry_run:
                processed_count += 1
                continue

            try:
                result = self.pipeline.run_for_video(
                    video_url=item.media_url,
                    user=UserIdentity.worker(),
                    batch_id=batch_id,
                    force_reprocess=force_refresh,
                )
                if result.already_processed:
                    skipped_count += 1
                else:
                    processed_count += 1
            except StageQuarantinedError:
                failed_count += 1
            except Exception:  # noqa: BLE001 - Failure isolation across items
                failed_count += 1

        duration = time.perf_counter() - start_time
        final_status = (
            PipelineStatus.COMPLETED if failed_count == 0 else PipelineStatus.FAILED_TRANSFORMATION
        )

        return SyncSummary(
            channel_url=query.channel_url,
            total_discovered=len(in_window_items),
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, DURATION_ROUND_DECIMAL_PLACES),
            status=final_status,
        )
