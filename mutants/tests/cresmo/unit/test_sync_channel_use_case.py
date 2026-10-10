"""Unit tests for SyncChannelUseCase.

Verifies feed discovery, lookback window filtering, ACID ledger idempotency checks,
dry-run execution, failure trapping, and preflight health check integration per SPEC-003.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import ANY, MagicMock

import pytest

from cresmo.application.pipeline import CresmoPipeline, PipelineResult
from cresmo.application.ports import LedgerRepositoryPort, MediaIngestionPort
from cresmo.application.services.preflight import PreflightHealthChecker, PreflightResult
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.domain.entities import AtomicNote, UserIdentity
from cresmo.domain.exceptions import PreflightError
from cresmo.domain.value_objects import (
    BatchId,
    CausalMatrix,
    ChannelFeedQuery,
    ChannelName,
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
            channel_name=ChannelName("TestChannel"),
        )
        old_item = DiscoveredMediaItem(
            content_id=ContentId("oldVideo0001"),
            title="Old Video",
            published_at=now - timedelta(days=20),
            media_url="https://youtube.com/watch?v=oldVideo0001",
            channel_name=ChannelName("TestChannel"),
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
        mock_pipeline.run_for_video.assert_called_once_with(
            video_url=recent_item.media_url,
            user=UserIdentity.worker(),
            batch_id=ANY,
        )
        assert isinstance(mock_pipeline.run_for_video.call_args.kwargs["batch_id"], BatchId)

        calls = mock_ledger_port.save_entry.call_args_list
        assert len(calls) == 2
        running_entry = calls[0][0][0]
        assert running_entry.content_id == recent_item.content_id
        assert running_entry.media_url == recent_item.media_url
        assert running_entry.title == recent_item.title
        assert running_entry.channel_name == recent_item.channel_name
        assert running_entry.status == PipelineStatus.RUNNING
        assert running_entry.started_at is not None
        assert running_entry.started_at.tzinfo == UTC

        completed_entry = calls[1][0][0]
        assert completed_entry.content_id == recent_item.content_id
        assert completed_entry.media_url == recent_item.media_url
        assert completed_entry.title == recent_item.title
        assert completed_entry.channel_name == recent_item.channel_name
        assert completed_entry.status == PipelineStatus.COMPLETED
        assert completed_entry.notes_count == 1
        assert completed_entry.started_at == running_entry.started_at
        assert completed_entry.completed_at is not None
        assert completed_entry.completed_at.tzinfo == UTC

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
            channel_name=ChannelName("TestChannel"),
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
            channel_name=ChannelName("TestChannel"),
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
        mock_pipeline.run_for_video.assert_called_once_with(
            video_url=item.media_url,
            user=UserIdentity.worker(),
            batch_id=ANY,
        )
        assert isinstance(mock_pipeline.run_for_video.call_args.kwargs["batch_id"], BatchId)

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
            channel_name=ChannelName("TestChannel"),
        )
        succeeding_item = DiscoveredMediaItem(
            content_id=ContentId("successVideo"),
            title="Success Video",
            published_at=now - timedelta(days=2),
            media_url="https://youtube.com/watch?v=successVideo",
            channel_name=ChannelName("TestChannel"),
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
            channel_name=ChannelName("TestChannel"),
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

    def test_sync_channel_default_force_refresh_is_false(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("alreadyDoneDef"),
            title="Already Processed Default",
            published_at=now - timedelta(days=1),
            media_url="https://youtube.com/watch?v=alreadyDoneDef",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item]
        mock_ledger_port.is_processed.return_value = True

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        # Call execute WITHOUT specifying force_refresh (tests default force_refresh=False)
        summary = use_case.execute(query)

        assert summary.processed_count == 0
        assert summary.skipped_count == 1
        assert summary.failed_count == 0
        mock_pipeline.run_for_video.assert_not_called()

    def test_sync_channel_naive_datetime_and_exact_cutoff_boundary(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        from unittest.mock import patch

        frozen_now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        # Naive datetime safely within lookback (3 days ago with 5 days lookback)
        recent_naive = (frozen_now - timedelta(days=3)).replace(tzinfo=None)
        old_naive = (frozen_now - timedelta(days=7)).replace(tzinfo=None)
        # Exact cutoff boundary item (must be included with >=, excluded with >)
        exact_cutoff = frozen_now - timedelta(days=5)

        item_recent = DiscoveredMediaItem(
            content_id=ContentId("recentNaiveVid"),
            title="Recent Naive Video",
            published_at=recent_naive,
            media_url="https://youtube.com/watch?v=recentNaiveVid",
            channel_name=ChannelName("TestChannel"),
        )
        item_boundary = DiscoveredMediaItem(
            content_id=ContentId("exactCutoffVid"),
            title="Exact Cutoff Video",
            published_at=exact_cutoff,
            media_url="https://youtube.com/watch?v=exactCutoffVid",
            channel_name=ChannelName("TestChannel"),
        )
        item_old = DiscoveredMediaItem(
            content_id=ContentId("tooOldVideo001"),
            title="Too Old Video",
            published_at=old_naive,
            media_url="https://youtube.com/watch?v=tooOldVideo001",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item_recent, item_boundary, item_old]

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@TestChannel",
            lookback_days=5,
        )
        with patch("cresmo.application.use_cases.sync_channel.datetime") as mock_dt:
            mock_dt.now.return_value = frozen_now
            summary = use_case.execute(query)

        # Both recent and exact cutoff boundary items are discovered (2 total)
        assert summary.total_discovered == 2
        assert summary.processed_count == 2

    def test_sync_channel_max_videos_limit_enforcement(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        items = [
            DiscoveredMediaItem(
                content_id=ContentId(f"vid_item_{i:04d}"),
                title=f"Video {i}",
                published_at=now - timedelta(hours=i),
                media_url=f"https://youtube.com/watch?v=vid_item_{i:04d}",
                channel_name=ChannelName("TestChannel"),
            )
            for i in range(5)
        ]
        mock_ingestion_port.discover_channel_feed.return_value = items

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@TestChannel",
            lookback_days=10,
            max_videos=2,
        )
        summary = use_case.execute(query)

        assert summary.total_discovered == 2
        assert summary.processed_count == 2
        assert mock_pipeline.run_for_video.call_count == 2

    def test_sync_channel_ledger_entry_lifecycle_and_exception_handling(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("crashItem1"),
            title="Crash Video",
            published_at=now - timedelta(hours=1),
            media_url="https://youtube.com/watch?v=crashItem1",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item]
        mock_pipeline.run_for_video.side_effect = RuntimeError("Fatal pipeline failure")

        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
        )

        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query)

        assert summary.failed_count == 1
        assert summary.status == PipelineStatus.FAILED_TRANSFORMATION
        assert summary.channel_url == "https://youtube.com/@TestChannel"
        assert summary.duration_seconds >= 0.0

        # Verify saved ledger entry has error message
        calls = mock_ledger_port.save_entry.call_args_list
        assert len(calls) == 2
        # First call is RUNNING
        assert calls[0][0][0].status == PipelineStatus.RUNNING
        assert calls[0][0][0].content_id.value == "crashItem1"
        # Second call is FAILED_TRANSFORMATION with error_message
        assert calls[1][0][0].status == PipelineStatus.FAILED_TRANSFORMATION
        assert "Fatal pipeline failure" in calls[1][0][0].error_message

    def test_init_attributes(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        checker = MagicMock(spec=PreflightHealthChecker)
        use_case = SyncChannelUseCase(
            media_ingestion_port=mock_ingestion_port,
            ledger_port=mock_ledger_port,
            pipeline=mock_pipeline,
            preflight_checker=checker,
        )
        assert use_case.media_ingestion_port is mock_ingestion_port
        assert use_case.ledger_port is mock_ledger_port
        assert use_case.pipeline is mock_pipeline
        assert use_case.preflight_checker is checker

    def test_sync_channel_duration_and_discovery_query(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        from unittest.mock import patch

        with patch("time.perf_counter") as mock_perf:
            mock_perf.side_effect = [100.0, 101.123456]
            mock_ingestion_port.discover_channel_feed.return_value = []
            use_case = SyncChannelUseCase(mock_ingestion_port, mock_ledger_port, mock_pipeline)
            query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
            summary = use_case.execute(query)

            mock_ingestion_port.discover_channel_feed.assert_called_once_with(query)
            assert summary.duration_seconds == 1.123

    def test_sync_channel_multiple_skips_and_is_processed_argument(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item1 = DiscoveredMediaItem(
            content_id=ContentId("done1"),
            title="V1",
            published_at=now - timedelta(hours=1),
            media_url="https://youtube.com/watch?v=done1",
            channel_name=ChannelName("TestChannel"),
        )
        item2 = DiscoveredMediaItem(
            content_id=ContentId("done2"),
            title="V2",
            published_at=now - timedelta(hours=2),
            media_url="https://youtube.com/watch?v=done2",
            channel_name=ChannelName("TestChannel"),
        )
        item3 = DiscoveredMediaItem(
            content_id=ContentId("new1"),
            title="V3",
            published_at=now - timedelta(hours=3),
            media_url="https://youtube.com/watch?v=new1",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item1, item2, item3]
        mock_ledger_port.is_processed.side_effect = lambda cid: cid.value in ("done1", "done2")

        use_case = SyncChannelUseCase(mock_ingestion_port, mock_ledger_port, mock_pipeline)
        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query)

        assert summary.skipped_count == 2
        assert summary.processed_count == 1
        assert mock_ledger_port.is_processed.call_args_list[0][0][0] == ContentId("done1")
        assert mock_ledger_port.is_processed.call_args_list[1][0][0] == ContentId("done2")
        assert mock_ledger_port.is_processed.call_args_list[2][0][0] == ContentId("new1")

    def test_dry_run_multiple_items_and_continue(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item1 = DiscoveredMediaItem(
            content_id=ContentId("dry1"),
            title="D1",
            published_at=now - timedelta(hours=1),
            media_url="https://youtube.com/watch?v=dry1",
            channel_name=ChannelName("TestChannel"),
        )
        item2 = DiscoveredMediaItem(
            content_id=ContentId("dry2"),
            title="D2",
            published_at=now - timedelta(hours=2),
            media_url="https://youtube.com/watch?v=dry2",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item1, item2]

        use_case = SyncChannelUseCase(mock_ingestion_port, mock_ledger_port, mock_pipeline)
        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query, dry_run=True)

        assert summary.processed_count == 2

    def test_sync_channel_multiple_pipeline_failures_and_ledger_validation(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item1 = DiscoveredMediaItem(
            content_id=ContentId("fail1"),
            title="F1",
            published_at=now - timedelta(hours=1),
            media_url="https://youtube.com/watch?v=fail1",
            channel_name=ChannelName("TestChannel"),
        )
        item2 = DiscoveredMediaItem(
            content_id=ContentId("fail2"),
            title="F2",
            published_at=now - timedelta(hours=2),
            media_url="https://youtube.com/watch?v=fail2",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item1, item2]
        mock_pipeline.run_for_video.side_effect = [
            PipelineResult(content_id=ContentId("fail1"), success=False, error_message="Err1"),
            PipelineResult(content_id=ContentId("fail2"), success=False, error_message="Err2"),
        ]

        use_case = SyncChannelUseCase(mock_ingestion_port, mock_ledger_port, mock_pipeline)
        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query)

        assert summary.failed_count == 2
        assert summary.status == PipelineStatus.FAILED_TRANSFORMATION

        calls = mock_ledger_port.save_entry.call_args_list
        assert len(calls) == 4  # 2 running + 2 failed

        fail1 = calls[1][0][0]
        assert fail1.content_id == ContentId("fail1")
        assert fail1.media_url == "https://youtube.com/watch?v=fail1"
        assert fail1.title == "F1"
        assert fail1.channel_name == ChannelName("TestChannel")
        assert fail1.status == PipelineStatus.FAILED_TRANSFORMATION
        assert fail1.error_message == "Err1"
        assert fail1.started_at is not None
        assert fail1.completed_at is not None

        fail2 = calls[3][0][0]
        assert fail2.content_id == ContentId("fail2")
        assert fail2.error_message == "Err2"

    def test_sync_channel_multiple_exceptions_and_ledger_validation(
        self,
        mock_ingestion_port: MagicMock,
        mock_ledger_port: MagicMock,
        mock_pipeline: MagicMock,
    ) -> None:
        now = datetime.now(UTC)
        item1 = DiscoveredMediaItem(
            content_id=ContentId("exc1"),
            title="E1",
            published_at=now - timedelta(hours=1),
            media_url="https://youtube.com/watch?v=exc1",
            channel_name=ChannelName("TestChannel"),
        )
        item2 = DiscoveredMediaItem(
            content_id=ContentId("exc2"),
            title="E2",
            published_at=now - timedelta(hours=2),
            media_url="https://youtube.com/watch?v=exc2",
            channel_name=ChannelName("TestChannel"),
        )
        mock_ingestion_port.discover_channel_feed.return_value = [item1, item2]
        mock_pipeline.run_for_video.side_effect = [
            RuntimeError("Crash 1"),
            ValueError("Crash 2"),
        ]

        use_case = SyncChannelUseCase(mock_ingestion_port, mock_ledger_port, mock_pipeline)
        query = ChannelFeedQuery(channel_url="https://youtube.com/@TestChannel")
        summary = use_case.execute(query)

        assert summary.failed_count == 2
        assert summary.status == PipelineStatus.FAILED_TRANSFORMATION

        calls = mock_ledger_port.save_entry.call_args_list
        assert len(calls) == 4

        exc_entry1 = calls[1][0][0]
        assert exc_entry1.content_id == ContentId("exc1")
        assert exc_entry1.media_url == "https://youtube.com/watch?v=exc1"
        assert exc_entry1.title == "E1"
        assert exc_entry1.channel_name == ChannelName("TestChannel")
        assert exc_entry1.status == PipelineStatus.FAILED_TRANSFORMATION
        assert exc_entry1.error_message == "Crash 1"
        assert exc_entry1.started_at is not None
        assert exc_entry1.started_at.tzinfo == UTC
        assert exc_entry1.completed_at is not None
        assert exc_entry1.completed_at.tzinfo == UTC

        exc_entry2 = calls[3][0][0]
        assert exc_entry2.content_id == ContentId("exc2")
        assert exc_entry2.error_message == "Crash 2"
