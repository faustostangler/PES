"""Channel Synchronization Use Case for Cresmo Knowledge Engine.

Coordinates feed polling, lookback window filtering, ACID ledger idempotency checks,
and bounded pipeline execution for channels and playlists per ADR-003 and SPEC-003.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from cresmo.application.ports import LedgerRepositoryPort, MediaIngestionPort
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    DiscoveredMediaItem,
    LedgerEntry,
    PipelineStatus,
    SyncSummary,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline import CresmoPipeline


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

        # Step 4: Process items with idempotency skip check
        for item in in_window_items:
            # Idempotency check against ledger
            if not force_refresh and self.ledger_port.is_processed(item.content_id):
                skipped_count += 1
                continue

            if dry_run:
                processed_count += 1
                continue

            item_start = datetime.now(UTC)
            self.ledger_port.save_entry(
                LedgerEntry(
                    content_id=item.content_id,
                    media_url=item.media_url,
                    title=item.title,
                    channel_name=item.channel_name,
                    status=PipelineStatus.RUNNING,
                    started_at=item_start,
                )
            )

            try:
                result = self.pipeline.run_for_video(video_url=item.media_url)
                completed_at = datetime.now(UTC)

                if result.success:
                    processed_count += 1
                    self.ledger_port.save_entry(
                        LedgerEntry(
                            content_id=item.content_id,
                            media_url=item.media_url,
                            title=item.title,
                            channel_name=item.channel_name,
                            status=PipelineStatus.COMPLETED,
                            notes_count=len(result.synthesized_notes),
                            started_at=item_start,
                            completed_at=completed_at,
                        )
                    )
                else:
                    failed_count += 1
                    self.ledger_port.save_entry(
                        LedgerEntry(
                            content_id=item.content_id,
                            media_url=item.media_url,
                            title=item.title,
                            channel_name=item.channel_name,
                            status=PipelineStatus.FAILED_TRANSFORMATION,
                            error_message=result.error_message,
                            started_at=item_start,
                            completed_at=completed_at,
                        )
                    )
            except Exception as exc:  # noqa: BLE001 - Failure isolation across items
                failed_count += 1
                self.ledger_port.save_entry(
                    LedgerEntry(
                        content_id=item.content_id,
                        media_url=item.media_url,
                        title=item.title,
                        channel_name=item.channel_name,
                        status=PipelineStatus.FAILED_TRANSFORMATION,
                        error_message=str(exc),
                        started_at=item_start,
                        completed_at=datetime.now(UTC),
                    )
                )

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
            duration_seconds=round(duration, 3),
            status=final_status,
        )
