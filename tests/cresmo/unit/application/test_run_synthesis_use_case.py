"""Hermetic unit tests for RunSynthesisUseCase (TDD Red -> Green -> Mutmut 0).

Conforms to:
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call

import pytest

from cresmo.application.ports import NoOpProcessRuntimePort
from cresmo.application.services.preflight import PreflightResult
from cresmo.application.use_cases.discovery.models import BatchDiscoveryQuery, BatchSource
from cresmo.application.use_cases.run_synthesis import (
    BatchItemEvent,
    BatchItemEventKind,
    RunExitStatus,
    RunSynthesisRequest,
    RunSynthesisUseCase,
)
from cresmo.domain.exceptions import (
    CresmoDomainError,
    IngestionNetworkError,
    PreflightError,
    QuotaPoolExhaustedError,
    RateLimitExceededError,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    BatchId,
    ChannelName,
    ContentId,
    DiscoveryPolicy,
    MasterDocumentResult,
    SourceModality,
)


def _make_use_case(
    *,
    discovery_policy: DiscoveryPolicy | None = None,
    preflight_result: PreflightResult | None = None,
    preflight_exc: BaseException | None = None,
    pipeline: Any = None,
    sources: Iterable[BatchSource] = (),
    concat_master: Any = None,
    runtime_port: Any = None,
    default_manifest_path: Path | None = Path("data/playlist.txt"),
    capture_discovery_args: list[tuple[BatchDiscoveryQuery, Any]] | None = None,
    capture_media_ports: list[Any] | None = None,
    progress_messages: list[str] | None = None,
) -> tuple[RunSynthesisUseCase, MagicMock, MagicMock, MagicMock]:
    cfg = discovery_policy or DiscoveryPolicy()
    preflight_checker = MagicMock()
    if preflight_exc is not None:
        preflight_checker.check_all.return_value = MagicMock(
            assert_healthy=MagicMock(side_effect=preflight_exc),
        )
    else:
        res = preflight_result or PreflightResult(is_healthy=True, errors=())
        preflight_checker.check_all.return_value = res

    mock_pipeline = pipeline or MagicMock()
    pipeline_factory = MagicMock(return_value=mock_pipeline)

    def _discover_factory(
        media_ingestion_port: Any,
        progress_callback: Any = None,
    ) -> Any:
        if capture_media_ports is not None:
            capture_media_ports.append(media_ingestion_port)
        discoverer = MagicMock()

        def _execute(query: BatchDiscoveryQuery) -> Any:
            if capture_discovery_args is not None:
                capture_discovery_args.append((query, progress_callback))
            if progress_callback is not None and progress_messages:
                for msg in progress_messages:
                    progress_callback(msg)
            return sources if isinstance(sources, Iterator) else list(sources)

        discoverer.execute.side_effect = _execute
        return discoverer

    mock_concat = concat_master or MagicMock()
    concat_factory = MagicMock(return_value=mock_concat)

    use_case = RunSynthesisUseCase(
        discovery_policy=cfg,
        preflight_checker=preflight_checker,
        pipeline_factory=pipeline_factory,
        discover_sources_factory=_discover_factory,
        concat_master_factory=concat_factory,
        runtime_port=runtime_port,
        default_manifest_path=default_manifest_path,
    )
    return use_case, preflight_checker, pipeline_factory, concat_factory


class TestRunSynthesisUseCase:
    """Hermetic unit tests covering single-video, batch, dry-run, quota, and cleanup paths."""

    def test_preflight_failure_aborts_before_pipeline_construction(self) -> None:
        use_case, preflight_checker, pipeline_factory, _ = _make_use_case(
            preflight_exc=PreflightError("Missing ffmpeg"),
        )

        with pytest.raises(PreflightError, match="Missing ffmpeg"):
            use_case.execute(RunSynthesisRequest())

        preflight_checker.check_all.assert_called_once_with()
        pipeline_factory.assert_not_called()

    def test_warmup_called_regardless_of_web_index_and_skipped_for_dry_run(self) -> None:
        pipeline = MagicMock()
        pipeline.run_for_video.return_value = MagicMock(
            already_processed=True,
            content_id=ContentId("dQw4w9WgXcQ"),
        )
        use_case, _, _, _ = _make_use_case(pipeline=pipeline)

        outcome = use_case.execute(
            RunSynthesisRequest(url="https://youtube.com/watch?v=dQw4w9WgXcQ", web_index=False),
        )

        assert outcome.status is RunExitStatus.SUCCESS
        pipeline.warmup.assert_called_once_with()

        pipeline.reset_mock()
        pipeline.ingest_raw_transcript.execute.return_value = MagicMock(
            content=MagicMock(id=ContentId("dQw4w9WgXcQ"), text="raw")
        )
        use_case.execute(
            RunSynthesisRequest(
                url="https://youtube.com/watch?v=dQw4w9WgXcQ", dry_run=True, web_index=True
            ),
        )
        pipeline.warmup.assert_not_called()

    def test_single_video_dry_run_success_and_missing_transcript(self) -> None:
        pipeline = MagicMock()
        transcript = MagicMock()
        transcript.content.id.value = "dQw4w9WgXcQ"
        transcript.content.text = "Hello world transcript"
        pipeline.ingest_raw_transcript.execute.return_value = transcript

        events: list[BatchItemEvent] = []
        use_case, _, _, _ = _make_use_case(pipeline=pipeline)
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        req = RunSynthesisRequest(url=url, dry_run=True)
        outcome = use_case.execute(req, on_event=events.append)

        pipeline.ingest_raw_transcript.execute.assert_called_once_with(video_url=url)
        assert outcome.status is RunExitStatus.SUCCESS
        assert outcome.dry_run is True
        assert outcome.dry_run_validated == 1
        assert outcome.dry_run_total == 1
        assert events == [
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_URL,
                message=f"[1/1] Dry-run ingested: [dQw4w9WgXcQ] ({len('Hello world transcript')} chars)",
            )
        ]
        pipeline.run_for_video.assert_not_called()

        events.clear()
        pipeline.ingest_raw_transcript.execute.return_value = None
        missing_outcome = use_case.execute(req, on_event=events.append)
        assert missing_outcome.status is RunExitStatus.SUCCESS
        assert missing_outcome.dry_run is True
        assert missing_outcome.dry_run_validated == 0
        assert missing_outcome.dry_run_total == 1
        assert events == [
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_FAILED,
                message=f"[1/1] Ingestion failed for: {url}",
            )
        ]

    def test_single_video_success_consolidates_master_and_handles_warning(self) -> None:
        events: list[BatchItemEvent] = []
        pipeline = MagicMock()
        cid = ContentId("dQw4w9WgXcQ")
        final_transcript = MagicMock()
        final_transcript.content.text = "Expanded synthesis text."
        pipeline.run_for_video.return_value = MagicMock(
            already_processed=False,
            content_id=cid,
            stage_artifacts={
                StageName.FLUID_PROSE: MagicMock(),
                StageName.WIDE_EXPANDER: final_transcript,
            },
            final_transcript=final_transcript,
        )
        concat_master = MagicMock()

        use_case, _, _, concat_factory = _make_use_case(
            pipeline=pipeline,
            concat_master=concat_master,
        )
        outcome = use_case.execute(
            RunSynthesisRequest(
                url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                passes=4,
                force_reprocess=True,
            ),
            on_event=events.append,
        )

        assert outcome.status is RunExitStatus.SUCCESS
        assert outcome.batch_id is not None
        assert outcome.manifest_display == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert outcome.completed == 1
        assert outcome.total_items == 1
        pipeline.run_for_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            expansion_max_passes=4,
            force_reprocess=True,
            batch_id=outcome.batch_id,
        )
        concat_factory.assert_called_with(pipeline.vault_port)
        concat_master.execute_all.assert_called_once_with()

        concat_master.execute_all.side_effect = RuntimeError("Disk full")
        events.clear()
        warn_outcome = use_case.execute(
            RunSynthesisRequest(url="https://youtube.com/watch?v=dQw4w9WgXcQ"),
            on_event=events.append,
        )
        assert warn_outcome.status is RunExitStatus.SUCCESS
        assert warn_outcome.batch_id is not None
        assert warn_outcome.total_items == 1
        assert events[-1] == BatchItemEvent(
            kind=BatchItemEventKind.MASTER_WARNING,
            message="Warning: Master consolidation failed: Disk full",
        )

    def test_single_video_skipped_and_failed_exception_channel(self) -> None:
        pipeline = MagicMock()
        cid = ContentId("abc123def45")
        pipeline.run_for_video.return_value = MagicMock(
            already_processed=True,
            content_id=cid,
        )
        use_case, _, _, _ = _make_use_case(pipeline=pipeline)

        skipped = use_case.execute(
            RunSynthesisRequest(url="https://youtube.com/watch?v=abc123def45")
        )
        assert skipped.status is RunExitStatus.SUCCESS
        assert skipped.batch_id is not None
        assert skipped.skipped == 1
        assert skipped.total_items == 1

        pipeline.run_for_video.side_effect = CresmoDomainError("Stage aborted")
        failed = use_case.execute(
            RunSynthesisRequest(url="https://youtube.com/watch?v=abc123def45")
        )
        assert failed.status is RunExitStatus.INTERNAL_ERROR
        assert failed.failed == 1
        assert failed.total_items == 1

    def test_batch_dry_run_empty_and_mixed_artifacts_and_urls(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "manifest.txt"
        use_case_empty, _, _, _ = _make_use_case(sources=[])
        empty_outcome = use_case_empty.execute(
            RunSynthesisRequest(manifest=manifest_file, scan_raw=True, dry_run=True),
        )
        assert empty_outcome.status is RunExitStatus.SUCCESS
        assert empty_outcome.dry_run is True
        assert empty_outcome.empty_sources is True
        assert empty_outcome.manifest_display == str(manifest_file)
        assert empty_outcome.scan_raw is True

        artifact_file = tmp_path / "_canal.md"
        valid_file_1 = tmp_path / "lecture_01.md"
        valid_file_2 = tmp_path / "lecture_02.md"
        ok_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        missing_url = "https://youtube.com/watch?v=missing00001"
        sources = [
            BatchSource(kind=SourceModality.FILE, target=str(artifact_file)),
            BatchSource(kind=SourceModality.FILE, target=str(valid_file_1)),
            BatchSource(kind=SourceModality.FILE, target=str(valid_file_2)),
            BatchSource(kind=SourceModality.URL, target=ok_url),
            BatchSource(kind=SourceModality.URL, target=missing_url),
        ]
        pipeline = MagicMock()
        ingested = MagicMock()
        ingested.content.id.value = "dQw4w9WgXcQ"
        ingested.content.text = "transcript body"
        pipeline.ingest_raw_transcript.execute.side_effect = [ingested, None]
        runtime = MagicMock(spec=NoOpProcessRuntimePort)
        runtime.get_file_size_bytes.side_effect = [2048, 4096]

        events: list[BatchItemEvent] = []
        use_case, _, _, _ = _make_use_case(
            pipeline=pipeline,
            sources=sources,
            runtime_port=runtime,
        )
        outcome = use_case.execute(
            RunSynthesisRequest(manifest=manifest_file, dry_run=True, scan_raw=True),
            on_event=events.append,
        )

        assert outcome.status is RunExitStatus.SUCCESS
        assert outcome.dry_run is True
        assert outcome.dry_run_validated == 3
        assert outcome.dry_run_total == 5
        assert outcome.manifest_display == str(manifest_file)
        assert outcome.scan_raw is True
        assert runtime.get_file_size_bytes.call_args_list == [
            call(valid_file_1),
            call(valid_file_2),
        ]
        assert pipeline.ingest_raw_transcript.execute.call_args_list == [
            call(video_url=ok_url),
            call(video_url=missing_url),
        ]
        assert events == [
            BatchItemEvent(
                kind=BatchItemEventKind.SKIPPED_ARTIFACT,
                message="[1/5] Dry-run skipped artifact: [_canal.md]",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_TEXT,
                message="[2/5] Dry-run text: [lecture_01] (2048 bytes)",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_TEXT,
                message="[3/5] Dry-run text: [lecture_02] (4096 bytes)",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_URL,
                message=f"[4/5] Dry-run ingested: [dQw4w9WgXcQ] ({len('transcript body')} chars)",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.DRY_RUN_FAILED,
                message=f"[5/5] Ingestion failed for: {missing_url}",
            ),
        ]

    def test_batch_run_unsized_generator_mixed_outcomes_single_batch_id_and_cleanup(
        self, tmp_path: Path
    ) -> None:
        artifact = BatchSource(kind=SourceModality.FILE, target=str(tmp_path / "_index.md"))
        text_ok_1 = BatchSource(kind=SourceModality.FILE, target=str(tmp_path / "talk_01.txt"))
        text_ok_2 = BatchSource(kind=SourceModality.FILE, target=str(tmp_path / "talk_02.txt"))
        vid_skip = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid11111111"
        )
        vid_rate = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid22222222"
        )
        vid_net = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid33333333"
        )
        vid_err = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid44444444"
        )
        vid_fail_res = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid55555555"
        )

        def _gen() -> Iterator[BatchSource]:
            yield from (
                artifact,
                text_ok_1,
                text_ok_2,
                vid_skip,
                vid_rate,
                vid_net,
                vid_err,
                vid_fail_res,
            )

        pipeline = MagicMock()
        pipeline.run_for_text_file.side_effect = [
            MagicMock(
                already_processed=False,
                content_id=ContentId("talk_01"),
                stage_artifacts={StageName.FLUID_PROSE: MagicMock()},
            ),
            MagicMock(
                already_processed=False,
                content_id=ContentId("talk_02"),
                stage_artifacts={
                    StageName.FLUID_PROSE: MagicMock(),
                    StageName.GAP_FILLER: MagicMock(),
                    StageName.LONG_EXPANDER: MagicMock(),
                    StageName.WIDE_EXPANDER: MagicMock(),
                },
            ),
        ]
        pipeline.run_for_video.side_effect = [
            MagicMock(already_processed=True, content_id=ContentId("vid11111111")),
            RateLimitExceededError("HTTP 429 transient"),
            IngestionNetworkError("Socket reset"),
            RuntimeError("Boom"),
            CresmoDomainError("Eval gate failed"),
        ]
        runtime = MagicMock(spec=NoOpProcessRuntimePort)
        runtime.get_process_rss_bytes.return_value = 64_000_000.0
        concat_master = MagicMock()
        concat_master.execute_all.return_value = {
            "Mises": [
                MasterDocumentResult(
                    channel_name=ChannelName("Mises"),
                    channel_category="Mises",
                    output_path=tmp_path / "Mises_MASTER_001.md",
                    part_number=1,
                    word_count=100,
                    document_count=1,
                )
            ]
        }

        events: list[BatchItemEvent] = []
        captured_ports: list[Any] = []
        use_case, _, _, concat_factory = _make_use_case(
            pipeline=pipeline,
            sources=_gen(),
            concat_master=concat_master,
            runtime_port=runtime,
            capture_media_ports=captured_ports,
            progress_messages=["Discovered 8 sources\n"],
        )
        outcome = use_case.execute(
            RunSynthesisRequest(passes=5, force_reprocess=True, scan_raw=False),
            on_event=events.append,
        )

        assert captured_ports == [pipeline.media_ingestion_port]
        concat_factory.assert_called_once_with(pipeline.vault_port)
        assert outcome.status is RunExitStatus.INTERNAL_ERROR
        assert outcome.completed == 2
        assert outcome.skipped == 2
        assert outcome.failed == 4
        assert outcome.total_items == 8
        assert outcome.manifest_display == "data/playlist.txt"
        assert outcome.scan_raw is False
        assert outcome.batch_id is not None

        assert pipeline.run_for_text_file.call_args_list == [
            call(
                file_path=tmp_path / "talk_01.txt",
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
            call(
                file_path=tmp_path / "talk_02.txt",
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
        ]
        assert pipeline.run_for_video.call_args_list == [
            call(
                video_url=vid_skip.target,
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
            call(
                video_url=vid_rate.target,
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
            call(
                video_url=vid_net.target,
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
            call(
                video_url=vid_err.target,
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
            call(
                video_url=vid_fail_res.target,
                expansion_max_passes=5,
                force_reprocess=True,
                batch_id=outcome.batch_id,
            ),
        ]

        assert events == [
            BatchItemEvent(
                kind=BatchItemEventKind.DISCOVERY_PROGRESS,
                message="Discovered 8 sources\n",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.SKIPPED_ARTIFACT,
                message="[1] [SKIPPED] [_index.md] Ignored internal Cresmo artifact or system index.",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.COMPLETED,
                message="[2] [DONE] [talk_01]: 1 stages completed (fluid_prose).",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.COMPLETED,
                message="[3] [DONE] [talk_02]: 4 stages completed (wide_expander).",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.SKIPPED_IDEMPOTENT,
                message="[4] [SKIPPED] [vid11111111] Already processed in ledger.",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.ITEM_RATE_LIMITED,
                message=f"[5] [RATE LIMIT] {vid_rate.target}: HTTP 429 transient",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.ITEM_NETWORK_ERROR,
                message=f"[6] [NETWORK ERROR] {vid_net.target}: Socket reset",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.ITEM_FAILED,
                message=f"[7] [FAILED] {vid_err.target}: Boom",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.ITEM_FAILED,
                message=f"[8] [FAILED] {vid_fail_res.target}: Eval gate failed",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.MASTER_CONSOLIDATED,
                message="Master consolidation complete: 1 master document(s) generated across 1 channel(s).",
            ),
        ]

        # Per-item cleanup invoked for every processed source
        assert runtime.collect_garbage.call_count == 8
        assert pipeline.telemetry_port.flush.call_count == 8
        pipeline.metrics_port.set_gauge.assert_called_with(
            "cresmo_process_resident_memory_bytes",
            64_000_000.0,
            labels={"role": "cli"},
        )
        pipeline.metrics_port.increment_counter.assert_called_with(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )

    def test_batch_run_quota_pool_exhausted_aborts_immediately(self) -> None:
        sources = [
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=vid11111111"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=vid22222222"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=vid33333333"),
        ]
        pipeline = MagicMock()
        pipeline.run_for_video.side_effect = [
            RuntimeError("Prior failure"),
            QuotaPoolExhaustedError("All keys cooling down", retry_after_seconds=30.0),
        ]
        pipeline.telemetry_port.flush.side_effect = RuntimeError("Telemetry offline")
        concat_master = MagicMock()

        events: list[BatchItemEvent] = []
        use_case, _, _, _ = _make_use_case(
            pipeline=pipeline,
            sources=sources,
            concat_master=concat_master,
            runtime_port=None,
        )
        outcome = use_case.execute(RunSynthesisRequest(), on_event=events.append)

        assert outcome.status is RunExitStatus.RATE_LIMITED
        assert outcome.failed == 2
        assert outcome.total_items == 2
        assert outcome.manifest_display == "data/playlist.txt"
        assert pipeline.run_for_video.call_count == 2
        concat_master.execute_all.assert_not_called()
        assert events[-1] == BatchItemEvent(
            kind=BatchItemEventKind.QUOTA_ABORT,
            message=(
                "[2/3] [COOLDOWN ABORT] https://youtube.com/watch?v=vid22222222: "
                "All keys cooling down\n"
                "Halting batch processing immediately (fail-fast cooldown)."
            ),
        )

    def test_batch_run_empty_and_master_consolidation_failure(self, tmp_path: Path) -> None:
        empty_manifest = tmp_path / "empty_manifest.txt"
        use_case_empty, _, _, concat_empty = _make_use_case(sources=[])
        empty_outcome = use_case_empty.execute(
            RunSynthesisRequest(manifest=empty_manifest, scan_raw=True)
        )
        assert empty_outcome.status is RunExitStatus.SUCCESS
        assert empty_outcome.batch_id is not None
        assert empty_outcome.empty_sources is True
        assert empty_outcome.total_items == 0
        assert empty_outcome.manifest_display == str(empty_manifest)
        assert empty_outcome.scan_raw is True
        concat_empty.return_value.execute_all.assert_not_called()

        pipeline = MagicMock()
        pipeline.run_for_video.return_value = MagicMock(
            already_processed=False,
            content_id=ContentId("vid11111111"),
            stage_artifacts={},
        )
        concat_master = MagicMock()
        concat_master.execute_all.side_effect = RuntimeError("Concat failure")
        events: list[BatchItemEvent] = []
        batch_manifest = tmp_path / "batch_manifest.txt"
        use_case, _, _, _ = _make_use_case(
            pipeline=pipeline,
            sources=[
                BatchSource(
                    kind=SourceModality.URL, target="https://youtube.com/watch?v=vid11111111"
                )
            ],
            concat_master=concat_master,
        )
        outcome = use_case.execute(
            RunSynthesisRequest(manifest=batch_manifest, scan_raw=True),
            on_event=events.append,
        )
        assert outcome.status is RunExitStatus.SUCCESS
        assert outcome.scan_raw is True
        assert outcome.manifest_display == str(batch_manifest)
        assert events == [
            BatchItemEvent(
                kind=BatchItemEventKind.COMPLETED,
                message="[1/1] [DONE] [vid11111111]: 0 stages completed (none).",
            ),
            BatchItemEvent(
                kind=BatchItemEventKind.MASTER_WARNING,
                message="Warning: Master consolidation failed: Concat failure",
            ),
        ]

    def test_discovery_query_respects_crawler_and_filter_flags(self, tmp_path: Path) -> None:
        policy = DiscoveryPolicy()
        captured: list[tuple[BatchDiscoveryQuery, Any]] = []
        use_case, _, _, _ = _make_use_case(
            discovery_policy=policy,
            sources=[],
            capture_discovery_args=captured,
        )
        manifest = tmp_path / "custom.txt"
        use_case.execute(
            RunSynthesisRequest(
                manifest=manifest,
                scan_raw=True,
                crawl=True,
                channel_max_videos=12,
                channels=("Mises",),
                categories=("Economics",),
                video_ids=("dQw4w9WgXcQ",),
            )
        )

        assert len(captured) == 1
        query, _ = captured[0]
        assert query.explicit_manifest == manifest
        assert query.scan_raw is True
        assert query.enable_channel_crawler is True
        assert query.channel_max_videos == 12
        assert query.lookback_days == policy.lookback_days
        assert query.discovery_workers == policy.discovery_workers
        assert query.queue_maxsize == policy.queue_maxsize
        assert "mises" in query.filter_criteria.channels
        assert "economics" in query.filter_criteria.categories
        assert "dQw4w9WgXcQ" in query.filter_criteria.video_ids

        # crawl=False defaults to policy.enable_channel_crawler (False)
        captured.clear()
        use_case.execute(RunSynthesisRequest(scan_raw=False, crawl=False))
        assert captured[0][0].scan_raw is False
        assert captured[0][0].enable_channel_crawler is False

        # crawl=False inherits enable_channel_crawler from DiscoveryPolicy
        captured_true: list[tuple[BatchDiscoveryQuery, Any]] = []
        use_case_true, _, _, _ = _make_use_case(
            discovery_policy=DiscoveryPolicy(enable_channel_crawler=True),
            sources=[],
            capture_discovery_args=captured_true,
        )
        use_case_true.execute(RunSynthesisRequest(scan_raw=False, crawl=False))
        assert captured_true[0][0].enable_channel_crawler is True

        captured_false: list[tuple[BatchDiscoveryQuery, Any]] = []
        use_case_false, _, _, _ = _make_use_case(
            discovery_policy=DiscoveryPolicy(enable_channel_crawler=False),
            sources=[],
            capture_discovery_args=captured_false,
        )
        use_case_false.execute(RunSynthesisRequest(scan_raw=False, crawl=False))
        assert captured_false[0][0].enable_channel_crawler is False

    def test_private_helper_contracts_for_defensive_fallbacks(self) -> None:
        pipeline = MagicMock()
        use_case, _, _, _ = _make_use_case(pipeline=pipeline)

        batch_id = BatchId.generate()
        source = BatchSource(
            kind=SourceModality.URL, target="https://youtube.com/watch?v=vid11111111"
        )
        req = RunSynthesisRequest()

        for exc in (
            RateLimitExceededError("429"),
            IngestionNetworkError("reset"),
            CresmoDomainError("domain err"),
            RuntimeError("boom"),
        ):
            pipeline.run_for_video.side_effect = exc
            assert (
                use_case._process_batch_item(
                    pipeline=pipeline,
                    source=source,
                    request=req,
                    item_prefix="[1/1]",
                    batch_id=batch_id,
                    on_event=None,
                )
                == "failed"
            )

    def test_single_video_none_final_transcript_and_drain_debug_logging(self) -> None:
        import structlog.testing

        pipeline = MagicMock()
        pipeline.run_for_video.return_value = MagicMock(
            already_processed=False,
            content_id=ContentId("vid11111111"),
            source_transcript=None,
            stage_artifacts={},
            final_transcript=None,
        )
        pipeline.vault_port.get_stage_transcript.return_value = None
        pipeline.telemetry_port.flush.side_effect = RuntimeError("tele boom")
        pipeline.metrics_port.flush.side_effect = RuntimeError("metrics boom")

        use_case, _, _, _ = _make_use_case(pipeline=pipeline)
        outcome = use_case.execute(RunSynthesisRequest(url="https://youtube.com/watch?v=vid11111111"))
        assert outcome.status is RunExitStatus.SUCCESS
        assert outcome.completed == 1
        assert outcome.batch_id is not None

        with structlog.testing.capture_logs() as cap_logs:
            use_case._drain_telemetry_and_memory(pipeline)
        assert len(cap_logs) == 2
        assert cap_logs[0]["event"] == "Telemetry flush failed during batch drain: %s"
        assert cap_logs[0]["log_level"] == "debug"
        assert str(cap_logs[0]["positional_args"][0]) == "tele boom"
        assert cap_logs[1]["event"] == "Metrics/GC drain failed during batch drain: %s"
        assert cap_logs[1]["log_level"] == "debug"
        assert str(cap_logs[1]["positional_args"][0]) == "metrics boom"
