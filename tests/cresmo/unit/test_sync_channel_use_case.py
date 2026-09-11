"""Unit tests for SyncChannelUseCase.

Verifies feed discovery, lookback window filtering, ACID ledger idempotency checks,
dry-run execution, failure trapping, and preflight health check integration per SPEC-003.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from cresmo.application.pipeline import CresmoPipeline, PipelineResult
from cresmo.application.ports import LedgerRepositoryPort, MediaIngestionPort
from cresmo.application.services.preflight import PreflightHealthChecker, PreflightResult
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.domain.entities import AtomicNote
from cresmo.domain.exceptions import PreflightError
from cresmo.domain.value_objects import (
    CausalMatrix,
    ChannelFeedQuery,
    ContentId,
    CrossContextRelations,
    DiscoveredMediaItem,
    NoteTitle,
    NoteType,
    PipelineStatus,
)


@pytest.fixture
def mock_ingestion_port() -> MagicMock:
    return MagicMock(spec=MediaIngestionPort)


@pytest.fixture
def mock_ledger_port() -> MagicMock:
    port = MagicMock(spec=LedgerRepositoryPort)
    port.is_processed.return_value = False
    return port


@pytest.fixture
def mock_pipeline() -> MagicMock:
    pipeline = MagicMock(spec=CresmoPipeline)
    note = AtomicNote(
        title=NoteTitle("Quantum Mechanics"),
        note_type=NoteType.CONCEPT,
        definition="Fundamental physics framework with comprehensive contextual analysis.",
        direct_relations=(NoteTitle("Wave Function"),),
        causal_matrix=CausalMatrix(cause="Subatomic observation", effect="Wave packet collapse"),
        cross_context=CrossContextRelations(),
    )
    pipeline.run_for_video.return_value = PipelineResult(
        content_id=ContentId("dQw4w9WgXcQ"),
        success=True,
        synthesized_notes=(note,),
        reconciled_mocs=(),
    )
    return pipeline


class TestSyncChannelUseCase:
    """Test suite for SyncChannelUseCase orchestrator."""

    def test_sync_channel_filters_out_of_window_items(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        recent_item = DiscoveredMediaItem(
            content_id=ContentId("recentVideo1"),
            title="Recent Video",
            published_at=now - timedelta(days=2),
            media_url="https://youtube.com/watch?v=recentVideo1",
            channel_name="TestChannel",
        )
        old_item = DiscoveredMediaItem(
            content_id=ContentId("oldVideo0001"),
            title="Old Video",
            published_at=now - timedelta(days=20),
            media_url="https://youtube.com/watch?v=oldVideo0001",
            channel_name="TestChannel",
        )
        mock_ingestion_port.discover_channel_feed.return_value = [recent_item, old_item]

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@TestChannel",
            lookback_days=7,
        )
        summary = use_case.execute(query)

        assert summary.total_discovered == 1
        assert summary.processed_count == 1
        assert summary.skipped_count == 0
        assert summary.failed_count == 0
        assert summary.status == PipelineStatus.COMPLETED
        mock_pipeline.run_for_video.assert_called_once_with(video_url=recent_item.media_url)

    def test_sync_channel_skips_already_processed_items(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("alreadyDone1"),
            title="Already Processed Video",
            published_at=now - timedelta(days=1),
            media_url="https://youtube.com/watch?v=alreadyDone1",
            channel_name="TestChannel",
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item]
        mock_ledger_port.is_processed.return_value = True

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query, force_refresh=False)

        assert summary.total_discovered == 1
        assert summary.processed_count == 0
        assert summary.skipped_count == 1
        assert summary.failed_count == 0
        mock_pipeline.run_for_video.assert_not_called()

    def test_sync_channel_force_refresh_bypasses_idempotency_skip(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("alreadyDone1"),
            title="Already Processed Video",
            published_at=now - timedelta(days=1),
            media_url="https://youtube.com/watch?v=alreadyDone1",
            channel_name="TestChannel",
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item]
        mock_ledger_port.is_processed.return_value = True

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query, force_refresh=True)

        assert summary.processed_count == 1
        assert summary.skipped_count == 0
        mock_pipeline.run_for_video.assert_called_once_with(video_url=item.media_url)

    def test_sync_channel_handles_individual_item_failure_gracefully(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        failing_item = DiscoveredMediaItem(
            content_id=ContentId("failingVideo"),
            title="Failing Video",
            published_at=now - timedelta(days=1),
            media_url="https://youtube.com/watch?v=failingVideo",
            channel_name="TestChannel",
        )
        succeeding_item = DiscoveredMediaItem(
            content_id=ContentId("successVideo"),
            title="Success Video",
            published_at=now - timedelta(days=2),
            media_url="https://youtube.com/watch?v=successVideo",
            channel_name="TestChannel",
        )
        mock_ingestion_port.discover_channel_feed.return_value = [failing_item, succeeding_item]

        mock_pipeline.run_for_video.side_effect = [
            PipelineResult(
                content_id=ContentId("failingVideo"),
                success=False,
                synthesized_notes=(),
                reconciled_mocs=(),
                error_message="LLM Rate limit reached",
            ),
            PipelineResult(
                content_id=ContentId("successVideo"),
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
            ),
        ]

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query)

        assert summary.total_discovered == 2
        assert summary.processed_count == 1
        assert summary.failed_count == 1
        assert summary.status == PipelineStatus.FAILED_TRANSFORMATION

    def test_dry_run_does_not_execute_pipeline_or_write_ledger(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("dryRunVideo1"),
            title="Dry Run Video",
            published_at=now - timedelta(days=1),
            media_url="https://youtube.com/watch?v=dryRunVideo1",
            channel_name="TestChannel",
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item]

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query, dry_run=True)

        assert summary.processed_count == 1
        assert summary.skipped_count == 0
        mock_pipeline.run_for_video.assert_not_called()
        mock_ledger_port.save_entry.assert_not_called()

    def test_preflight_check_failure_aborts_synchronization(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        mock_preflight = MagicMock(spec=PreflightHealthChecker)
        mock_preflight.check_all.return_value = PreflightResult(
            is_healthy=False,
            errors=("Missing GEMINI_API_KEY",),
        )

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
            preflight_checker=mock_preflight,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        with pytest.raises(PreflightError, match="Missing GEMINI_API_KEY"):
            use_case.execute(query)

        mock_ingestion_port.discover_channel_feed.assert_not_called()
