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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁSyncChannelUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁSyncChannelUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class SyncChannelUseCase:
    """Application orchestrator coordinating feed polling, idempotency, and synthesis."""

    @_mutmut_mutated(mutants_xǁSyncChannelUseCaseǁ__init____mutmut)
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

    def xǁSyncChannelUseCaseǁ__init____mutmut_orig(
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

    def xǁSyncChannelUseCaseǁ__init____mutmut_1(
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
        self.media_ingestion_port = None
        self.ledger_port = ledger_port
        self.pipeline = pipeline
        self.preflight_checker = preflight_checker

    def xǁSyncChannelUseCaseǁ__init____mutmut_2(
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
        self.ledger_port = None
        self.pipeline = pipeline
        self.preflight_checker = preflight_checker

    def xǁSyncChannelUseCaseǁ__init____mutmut_3(
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
        self.pipeline = None
        self.preflight_checker = preflight_checker

    def xǁSyncChannelUseCaseǁ__init____mutmut_4(
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
        self.preflight_checker = None

    @_mutmut_mutated(mutants_xǁSyncChannelUseCaseǁexecute__mutmut)
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_orig(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_1(
        self,
        query: ChannelFeedQuery,
        dry_run: bool = True,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_2(
        self,
        query: ChannelFeedQuery,
        dry_run: bool = False,
        force_refresh: bool = True,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_3(
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
        if self.preflight_checker is None:
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_4(
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

        start_time = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_5(
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
        raw_items = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_6(
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
        raw_items = self.media_ingestion_port.discover_channel_feed(None)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_7(
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
        now = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_8(
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
        now = datetime.now(None)
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_9(
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
        cutoff = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_10(
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
        cutoff = now + timedelta(days=query.lookback_days)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_11(
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
        cutoff = now - timedelta(days=None)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_12(
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

        in_window_items: list[DiscoveredMediaItem] = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_13(
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
            pub_date = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_14(
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
            if pub_date.tzinfo is not None:
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_15(
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
                pub_date = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_16(
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
                pub_date = pub_date.replace(tzinfo=None)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_17(
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

            if pub_date > cutoff:
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_18(
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
                in_window_items.append(None)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_19(
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

            if len(in_window_items) > query.max_videos:
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_20(
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
                return

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_21(
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

        processed_count = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_22(
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

        processed_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_23(
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
        skipped_count = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_24(
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
        skipped_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_25(
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
        failed_count = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_26(
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
        failed_count = 1

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_27(
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
            if not force_refresh or self.ledger_port.is_processed(item.content_id):
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_28(
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
            if force_refresh and self.ledger_port.is_processed(item.content_id):
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_29(
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
            if not force_refresh and self.ledger_port.is_processed(None):
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_30(
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
                skipped_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_31(
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
                skipped_count -= 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_32(
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
                skipped_count += 2
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_33(
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
                break

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_34(
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
                processed_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_35(
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
                processed_count -= 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_36(
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
                processed_count += 2
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_37(
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
                break

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_38(
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

            item_start = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_39(
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

            item_start = datetime.now(None)
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_40(
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
                None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_41(
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
                    content_id=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_42(
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
                    media_url=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_43(
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
                    title=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_44(
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
                    channel_name=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_45(
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
                    status=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_46(
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
                    started_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_47(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_48(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_49(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_50(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_51(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_52(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_53(
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
                result = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_54(
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
                result = self.pipeline.run_for_video(video_url=None)
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_55(
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
                completed_at = None

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_56(
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
                completed_at = datetime.now(None)

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

    def xǁSyncChannelUseCaseǁexecute__mutmut_57(
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
                    processed_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_58(
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
                    processed_count -= 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_59(
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
                    processed_count += 2
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_60(
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
                        None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_61(
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
                            content_id=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_62(
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
                            media_url=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_63(
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
                            title=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_64(
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
                            channel_name=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_65(
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
                            status=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_66(
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
                            notes_count=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_67(
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
                            started_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_68(
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
                            completed_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_69(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_70(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_71(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_72(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_73(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_74(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_75(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_76(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_77(
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
                    failed_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_78(
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
                    failed_count -= 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_79(
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
                    failed_count += 2
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_80(
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
                        None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_81(
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
                            content_id=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_82(
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
                            media_url=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_83(
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
                            title=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_84(
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
                            channel_name=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_85(
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
                            status=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_86(
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
                            error_message=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_87(
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
                            started_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_88(
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
                            completed_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_89(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_90(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_91(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_92(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_93(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_94(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_95(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_96(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_97(
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
                failed_count = 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_98(
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
                failed_count -= 1
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_99(
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
                failed_count += 2
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_100(
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
                    None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_101(
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
                        content_id=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_102(
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
                        media_url=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_103(
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
                        title=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_104(
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
                        channel_name=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_105(
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
                        status=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_106(
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
                        error_message=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_107(
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
                        started_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_108(
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
                        completed_at=None,
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_109(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_110(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_111(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_112(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_113(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_114(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_115(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_116(
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_117(
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
                        error_message=str(None),
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_118(
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
                        completed_at=datetime.now(None),
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_119(
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

        duration = None
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_120(
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

        duration = time.perf_counter() + start_time
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_121(
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
        final_status = None

        return SyncSummary(
            channel_url=query.channel_url,
            total_discovered=len(in_window_items),
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_122(
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
            PipelineStatus.COMPLETED if failed_count != 0 else PipelineStatus.FAILED_TRANSFORMATION
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_123(
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
            PipelineStatus.COMPLETED if failed_count == 1 else PipelineStatus.FAILED_TRANSFORMATION
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

    def xǁSyncChannelUseCaseǁexecute__mutmut_124(
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
            channel_url=None,
            total_discovered=len(in_window_items),
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_125(
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
            total_discovered=None,
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_126(
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
            processed_count=None,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_127(
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
            skipped_count=None,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_128(
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
            failed_count=None,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_129(
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
            duration_seconds=None,
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_130(
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
            status=None,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_131(
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
            total_discovered=len(in_window_items),
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_132(
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
            processed_count=processed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_133(
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
            skipped_count=skipped_count,
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_134(
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
            failed_count=failed_count,
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_135(
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
            duration_seconds=round(duration, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_136(
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
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_137(
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
            )

    def xǁSyncChannelUseCaseǁexecute__mutmut_138(
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
            duration_seconds=round(None, 3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_139(
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
            duration_seconds=round(duration, None),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_140(
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
            duration_seconds=round(3),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_141(
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
            duration_seconds=round(duration, ),
            status=final_status,
        )

    def xǁSyncChannelUseCaseǁexecute__mutmut_142(
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
            duration_seconds=round(duration, 4),
            status=final_status,
        )

mutants_xǁSyncChannelUseCaseǁ__init____mutmut['_mutmut_orig'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁ__init____mutmut['xǁSyncChannelUseCaseǁ__init____mutmut_1'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁ__init____mutmut['xǁSyncChannelUseCaseǁ__init____mutmut_2'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁ__init____mutmut['xǁSyncChannelUseCaseǁ__init____mutmut_3'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁ__init____mutmut['xǁSyncChannelUseCaseǁ__init____mutmut_4'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated

mutants_xǁSyncChannelUseCaseǁexecute__mutmut['_mutmut_orig'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_1'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_2'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_3'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_4'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_5'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_6'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_7'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_8'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_9'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_10'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_11'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_12'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_13'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_14'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_15'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_16'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_17'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_18'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_19'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_20'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_21'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_22'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_23'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_24'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_25'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_26'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_27'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_28'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_29'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_30'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_31'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_32'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_33'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_34'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_35'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_36'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_37'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_38'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_39'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_40'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_41'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_42'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_43'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_44'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_45'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_46'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_47'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_48'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_49'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_50'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_51'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_52'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_53'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_54'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_55'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_56'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_57'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_58'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_59'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_60'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_61'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_62'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_63'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_64'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_65'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_66'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_67'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_68'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_69'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_69 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_70'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_70 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_71'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_71 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_72'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_72 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_73'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_73 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_74'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_74 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_75'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_75 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_76'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_76 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_77'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_77 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_78'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_78 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_79'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_79 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_80'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_80 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_81'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_81 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_82'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_82 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_83'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_83 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_84'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_84 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_85'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_85 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_86'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_86 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_87'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_87 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_88'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_88 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_89'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_89 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_90'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_90 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_91'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_91 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_92'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_92 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_93'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_93 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_94'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_94 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_95'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_95 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_96'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_96 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_97'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_97 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_98'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_98 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_99'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_99 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_100'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_100 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_101'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_101 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_102'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_102 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_103'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_103 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_104'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_104 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_105'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_105 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_106'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_106 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_107'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_107 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_108'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_108 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_109'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_109 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_110'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_110 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_111'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_111 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_112'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_112 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_113'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_113 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_114'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_114 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_115'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_115 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_116'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_116 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_117'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_117 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_118'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_118 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_119'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_119 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_120'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_120 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_121'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_121 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_122'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_122 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_123'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_123 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_124'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_124 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_125'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_125 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_126'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_126 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_127'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_127 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_128'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_128 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_129'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_129 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_130'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_130 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_131'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_131 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_132'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_132 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_133'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_133 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_134'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_134 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_135'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_135 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_136'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_136 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_137'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_137 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_138'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_138 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_139'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_139 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_140'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_140 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_141'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_141 # type: ignore # mutmut generated
mutants_xǁSyncChannelUseCaseǁexecute__mutmut['xǁSyncChannelUseCaseǁexecute__mutmut_142'] = SyncChannelUseCase.xǁSyncChannelUseCaseǁexecute__mutmut_142 # type: ignore # mutmut generated
