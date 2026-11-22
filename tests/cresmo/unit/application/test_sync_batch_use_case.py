"""Hermetic unit tests for SyncBatchUseCase (TDD Red -> Green -> Mutmut 0).

Conforms to:
    - ADR-012: Multi-Criteria Sync Filtering & Alphabetical Feed Ordering
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.ports import ChannelTaxonomyPort
from cresmo.application.use_cases.sync_batch import (
    SyncBatchRequest,
    SyncBatchUseCase,
    SyncTargetEvent,
    SyncTargetEventKind,
    _describe_mode,
)
from cresmo.domain.value_objects import PipelineStatus, SyncFilterCriteria, SyncSummary


def _summary(
    *,
    channel_url: str = "https://youtube.com",
    discovered: int = 3,
    processed: int = 2,
    skipped: int = 1,
    failed: int = 0,
    duration: float = 0.5,
) -> SyncSummary:
    return SyncSummary(
        channel_url=channel_url,
        total_discovered=discovered,
        processed_count=processed,
        skipped_count=skipped,
        failed_count=failed,
        duration_seconds=duration,
        status=PipelineStatus.COMPLETED if failed == 0 else PipelineStatus.FAILED_TRANSFORMATION,
    )


class TestSyncBatchUseCase:
    """Hermetic unit tests for multi-mode channel and direct-video sync batches."""

    def test_direct_video_ids_mode_supports_bare_ids_and_urls(self) -> None:
        mock_sync_channel = MagicMock()
        mock_sync_channel.execute.side_effect = [
            _summary(discovered=3, processed=1, skipped=2, failed=1, duration=0.25),
            _summary(discovered=4, processed=2, skipped=1, failed=2, duration=0.75),
            _summary(discovered=2, processed=0, skipped=3, failed=0, duration=1.5),
        ]
        events: list[SyncTargetEvent] = []
        use_case = SyncBatchUseCase(sync_channel_use_case=mock_sync_channel)

        outcome = use_case.execute(
            SyncBatchRequest(
                video_ids=(
                    "https://www.youtube.com/watch?v=fullurl0001",
                    "http://youtube.com/watch?v=httpurl0003",
                    "bareid00002",
                ),
                lookback=14,
                dry_run=True,
                force_refresh=True,
            ),
            on_event=events.append,
        )

        assert outcome.direct_video_mode is True
        assert outcome.channels_synced == 0
        assert outcome.total_discovered == 9
        assert outcome.total_processed == 3
        assert outcome.total_skipped == 6
        assert outcome.total_failed == 3
        assert outcome.success is False
        assert len(events) == 3
        assert events == [
            SyncTargetEvent(
                kind=SyncTargetEventKind.VIDEO,
                target="bareid00002",
                total_discovered=3,
                processed=1,
                skipped=2,
                failed=1,
                duration_seconds=0.25,
            ),
            SyncTargetEvent(
                kind=SyncTargetEventKind.VIDEO,
                target="http://youtube.com/watch?v=httpurl0003",
                total_discovered=4,
                processed=2,
                skipped=1,
                failed=2,
                duration_seconds=0.75,
            ),
            SyncTargetEvent(
                kind=SyncTargetEventKind.VIDEO,
                target="https://www.youtube.com/watch?v=fullurl0001",
                total_discovered=2,
                processed=0,
                skipped=3,
                failed=0,
                duration_seconds=1.5,
            ),
        ]
        called_urls = [
            c.kwargs["query"].channel_url for c in mock_sync_channel.execute.call_args_list
        ]
        assert called_urls == [
            "https://www.youtube.com/watch?v=bareid00002",
            "http://youtube.com/watch?v=httpurl0003",
            "https://www.youtube.com/watch?v=fullurl0001",
        ]
        for c in mock_sync_channel.execute.call_args_list:
            assert c.kwargs["query"].max_videos == 1
            assert c.kwargs["query"].lookback_days == 14
            assert c.kwargs["dry_run"] is True
            assert c.kwargs["force_refresh"] is True

    def test_explicit_channels_sorted_alphabetically_and_normalized(self) -> None:
        mock_sync_channel = MagicMock()
        mock_sync_channel.execute.side_effect = lambda query, **_: _summary(
            channel_url=query.channel_url,
            discovered=2,
            processed=1,
            skipped=1,
            failed=0,
            duration=0.4,
        )
        events: list[SyncTargetEvent] = []
        use_case = SyncBatchUseCase(sync_channel_use_case=mock_sync_channel)

        outcome = use_case.execute(
            SyncBatchRequest(
                channels=(
                    "ZuluChannel",
                    "http://youtube.com/@gamma",
                    "https://youtube.com/@beta",
                    "alpha",
                ),
                lookback=30,
                max_videos=25,
                dry_run=True,
                force_refresh=True,
            ),
            on_event=events.append,
        )

        expected_targets = [
            "http://youtube.com/@gamma",
            "https://alpha",
            "https://youtube.com/@beta",
            "https://zuluchannel",
        ]
        assert outcome.direct_video_mode is False
        assert outcome.channels_synced == 4
        assert outcome.total_discovered == 8
        assert outcome.total_processed == 4
        assert outcome.total_skipped == 4
        assert outcome.total_failed == 0
        assert outcome.success is True
        assert len(events) == 4
        assert events == [
            SyncTargetEvent(
                kind=SyncTargetEventKind.CHANNEL,
                target=target,
                total_discovered=2,
                processed=1,
                skipped=1,
                failed=0,
                duration_seconds=0.4,
            )
            for target in expected_targets
        ]
        called_urls = [
            c.kwargs["query"].channel_url for c in mock_sync_channel.execute.call_args_list
        ]
        assert called_urls == expected_targets
        for c in mock_sync_channel.execute.call_args_list:
            assert c.kwargs["query"].lookback_days == 30
            assert c.kwargs["query"].max_videos == 25
            assert c.kwargs["dry_run"] is True
            assert c.kwargs["force_refresh"] is True

    def test_manifest_case_insensitive_sorting_and_failure_accumulation(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "mixed_case.txt"
        manifest.write_text(
            "https://youtube.com/@Zulu\nhttps://youtube.com/@alpha\n",
            encoding="utf-8",
        )
        mock_sync_channel = MagicMock()
        mock_sync_channel.execute.side_effect = [
            _summary(discovered=5, processed=3, skipped=0, failed=2, duration=1.1),
            _summary(discovered=2, processed=1, skipped=0, failed=1, duration=0.9),
        ]
        events: list[SyncTargetEvent] = []
        use_case = SyncBatchUseCase(
            sync_channel_use_case=mock_sync_channel,
            default_manifest_path=manifest,
        )

        outcome = use_case.execute(
            SyncBatchRequest(lookback=7, max_videos=10, dry_run=False, force_refresh=False),
            on_event=events.append,
        )

        expected_targets = [
            "https://youtube.com/@alpha/videos",
            "https://youtube.com/@Zulu/videos",
        ]
        assert [
            c.kwargs["query"].channel_url for c in mock_sync_channel.execute.call_args_list
        ] == (expected_targets)
        assert outcome.channels_synced == 2
        assert outcome.total_discovered == 7
        assert outcome.total_processed == 4
        assert outcome.total_skipped == 0
        assert outcome.total_failed == 3
        assert outcome.success is False
        assert outcome.manifest_path == manifest
        assert len(events) == 2
        for c in mock_sync_channel.execute.call_args_list:
            assert c.kwargs["query"].lookback_days == 7
            assert c.kwargs["query"].max_videos == 10
            assert c.kwargs["dry_run"] is False
            assert c.kwargs["force_refresh"] is False

    def test_manifest_category_filtering_reads_manifest_and_uses_taxonomy_port(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text(
            "# comment line\n\nhttps://youtube.com/@Mises\nhttps://youtube.com/@AlphaNews\n",
            encoding="utf-8",
        )
        taxonomy = MagicMock(spec=ChannelTaxonomyPort)
        taxonomy.classify.side_effect = lambda url: (
            ("Economics", "perennial") if "Mises" in url else ("News", "volatile")
        )
        mock_sync_channel = MagicMock()
        mock_sync_channel.execute.return_value = _summary(discovered=1, processed=1, skipped=0)

        use_case = SyncBatchUseCase(
            sync_channel_use_case=mock_sync_channel,
            default_manifest_path=manifest,
            taxonomy_port=taxonomy,
        )
        outcome = use_case.execute(SyncBatchRequest(categories=("economics",)))

        assert outcome.channels_synced == 1
        assert outcome.manifest_path == manifest
        called_query = mock_sync_channel.execute.call_args.kwargs["query"]
        assert "Mises" in called_query.channel_url

    def test_no_matching_channels_reports_mode_and_empty_outcome(self, tmp_path: Path) -> None:
        manifest = tmp_path / "empty.txt"
        manifest.write_text("# only comments\n", encoding="utf-8")
        mock_sync_channel = MagicMock()
        use_case = SyncBatchUseCase(
            sync_channel_use_case=mock_sync_channel,
            default_manifest_path=manifest,
        )

        outcome = use_case.execute(SyncBatchRequest(categories=("Philosophy", "History")))
        assert outcome.no_matching_channels is True
        assert outcome.channels_synced == 0
        assert outcome.mode_description == "categories=philosophy,history"
        assert outcome.manifest_path == manifest
        mock_sync_channel.execute.assert_not_called()

        full_outcome = use_case.execute(SyncBatchRequest())
        assert full_outcome.no_matching_channels is True
        assert full_outcome.mode_description == "full manifest"

    def test_describe_mode_formats_all_criteria_combinations(self) -> None:
        assert _describe_mode(SyncFilterCriteria()) == "full manifest"
        assert _describe_mode(SyncFilterCriteria(channels=("c1", "c2"))) == "channels=c1,c2"
        assert _describe_mode(SyncFilterCriteria(video_ids=("v1", "v2"))) == "videos=v1,v2"
        assert (
            _describe_mode(
                SyncFilterCriteria(
                    channels=("c1", "c2"),
                    categories=("cat1", "cat2"),
                    video_ids=("v1", "v2"),
                )
            )
            == "channels=c1,c2, categories=cat1,cat2, videos=v1,v2"
        )
