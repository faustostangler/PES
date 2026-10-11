"""Unit tests for 'cresmo run' presentation command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-007: Pipeline Template Method DRY
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - ADR-020: Observability Telemetry & Golden Signals
    - SPEC-001: Core Knowledge Synthesis Specifications
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline import PipelineResult
from cresmo.application.use_cases.discover_batch_sources import BatchDiscoveryQuery, BatchSource
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    SourceModality,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.commands.run import (
    _build_batch_discovery_query,
    _consolidate_master_if_needed,
    _drain_telemetry_and_memory,
    execute_batch_dry_run,
    execute_batch_run,
    execute_single_video_run,
    handle_run,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class TestRunCommand:
    """Test suite for cresmo run presentation logic and helpers."""

    def test_drain_telemetry_and_memory(self) -> None:
        """Verify telemetry flush and golden signal metrics are emitted during drain."""
        mock_pipeline = MagicMock()
        with (
            patch("cresmo.presentation.commands.run.get_process_rss_bytes", return_value=104857600),
            patch("gc.collect") as mock_gc,
        ):
            _drain_telemetry_and_memory(mock_pipeline)
            mock_pipeline.telemetry_port.flush.assert_called_once()
            mock_gc.assert_called_once()
            mock_pipeline.metrics_port.set_gauge.assert_called_once_with(
                "cresmo_process_resident_memory_bytes",
                104857600,
                labels={"role": "worker"},
            )
            mock_pipeline.metrics_port.increment_counter.assert_called_once_with(
                "cresmo_gc_collections_total",
                1.0,
                labels={"generation": "all"},
            )

    def test_drain_telemetry_and_memory_exception_resilience(self) -> None:
        """Verify drain swallows exceptions during flush and metrics emission."""
        mock_pipeline = MagicMock()
        mock_pipeline.telemetry_port.flush.side_effect = RuntimeError("Telemetry offline")
        mock_pipeline.metrics_port.set_gauge.side_effect = RuntimeError("Metrics offline")

        # Must not raise
        _drain_telemetry_and_memory(mock_pipeline)

    def test_execute_single_video_run_dry_run(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify single video --dry-run prints transcript length on success and handles None."""
        mock_pipeline = MagicMock()
        args = argparse.Namespace(url="https://youtube.com/watch?v=dry1", dry_run=True)

        # 1. Success
        mock_raw = MagicMock()
        mock_raw.content.id.value = "dry1"
        mock_raw.content.body = "A" * 150
        mock_pipeline.ingest_raw_transcript.execute.return_value = mock_raw

        assert execute_single_video_run(mock_pipeline, args) == EXIT_SUCCESS
        mock_pipeline.ingest_raw_transcript.execute.assert_called_once_with(video_url="https://youtube.com/watch?v=dry1")
        captured = capsys.readouterr()
        assert "Dry run successful for [dry1]: Transcript length: 150 characters.\n" in captured.out

        # 2. Ingestion returned None
        mock_pipeline.ingest_raw_transcript.execute.return_value = None
        assert execute_single_video_run(mock_pipeline, args) == EXIT_INGESTION_ERROR
        captured = capsys.readouterr()
        assert "Dry-run ingestion returned no transcript for https://youtube.com/watch?v=dry1\n" in captured.err

    def test_execute_single_video_run_already_processed_in_ledger(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify skipped message when video is marked already processed."""
        mock_pipeline = MagicMock()
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=skip1",
            dry_run=False,
            passes=3,
            force_reprocess=False,
        )

        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("skip1"),
            success=True,
            already_processed=True,
        )

        assert execute_single_video_run(mock_pipeline, args) == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert (
            "[SKIPPED] Content [skip1] was already marked as COMPLETED in the ledger. "
            "Use --force-reprocess to bypass.\n"
        ) in captured.out

    def test_execute_single_video_run_success_and_master_consolidation(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify synthesis completion message and channel master consolidation trigger."""
        mock_pipeline = MagicMock()
        mock_pipeline.settings = CresmoSettings()
        mock_raw = MagicMock()
        mock_raw.channel.name = "Fabio Akita"
        mock_pipeline.vault_port.get_raw_transcript.return_value = mock_raw

        args = argparse.Namespace(
            url="https://youtube.com/watch?v=success1",
            dry_run=False,
            passes=2,
            force_reprocess=True,
        )

        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("success1"),
            success=True,
            synthesized_notes=(MagicMock(), MagicMock()),
            reconciled_mocs=(MagicMock(),),
            duplicates_unified=1,
        )

        with patch("cresmo.presentation.commands.run.build_concat_master_use_case") as mock_build_concat:
            mock_concat_uc = MagicMock()
            mock_build_concat.return_value = mock_concat_uc

            assert execute_single_video_run(mock_pipeline, args) == EXIT_SUCCESS
            mock_pipeline.vault_port.get_raw_transcript.assert_called_once_with(ContentId("success1"))
            mock_build_concat.assert_called_once_with(
                settings=mock_pipeline.settings,
                vault_port=mock_pipeline.vault_port,
            )
            mock_concat_uc.execute.assert_called_once_with(ChannelName("Fabio Akita"))

            captured = capsys.readouterr()
            assert (
                "Synthesis completed successfully for [success1]: "
                "2 atomic notes synthesized, 1 MOCs reconciled, 1 duplicate clusters unified.\n"
            ) in captured.out

    def test_execute_single_video_run_master_consolidation_exception(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify master consolidation warning when vault lookup or consolidation raises."""
        mock_pipeline = MagicMock()
        mock_pipeline.settings = CresmoSettings()
        mock_pipeline.vault_port.get_raw_transcript.side_effect = RuntimeError("Vault locked")

        args = argparse.Namespace(
            url="https://youtube.com/watch?v=warn1",
            dry_run=False,
            passes=1,
            force_reprocess=False,
        )

        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("warn1"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        assert execute_single_video_run(mock_pipeline, args) == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "Warning: Master consolidation failed: Vault locked\n" in captured.err

    def test_execute_single_video_run_failure(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify pipeline failure returns EXIT_INTERNAL_ERROR with error message."""
        mock_pipeline = MagicMock()
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=fail1",
            dry_run=False,
            passes=3,
            force_reprocess=False,
        )

        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("fail1"),
            success=False,
            error_message="Ollama out of memory",
        )

        assert execute_single_video_run(mock_pipeline, args) == EXIT_INTERNAL_ERROR
        captured = capsys.readouterr()
        assert "Pipeline error: Ollama out of memory\n" in captured.err

    def test_execute_batch_run_empty_sources(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify batch run with 0 sources logs informative notice and returns EXIT_SUCCESS."""
        mock_pipeline = MagicMock()
        args = argparse.Namespace(manifest=None, no_scan_raw=False)

        assert execute_batch_run(mock_pipeline, [], args) == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert (
            "No sources found to process (manifest: data/playlist.txt, raw lake scan: True).\n"
            in captured.out
        )

    def test_execute_batch_run_mixed_outcomes_and_summary(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        """Verify batch run loops through items, tallies completed/skipped/failed, and reports summary."""
        mock_pipeline = MagicMock()
        mock_pipeline.settings = CresmoSettings()

        valid_file = tmp_path / "valid.md"
        valid_file.write_text("Valid transcript content", encoding="utf-8")

        sources = [
            BatchSource(kind=SourceModality.FILE, target=str(valid_file)),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=skipVid"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=failVid"),
        ]

        args = argparse.Namespace(
            manifest=None,
            no_scan_raw=False,
            passes=3,
            force_reprocess=False,
        )

        # 1: FILE succeeds
        mock_pipeline.run_for_text_file.return_value = PipelineResult(
            content_id=ContentId("valid"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )
        # 2: URL skipped
        # 3: URL fails
        mock_pipeline.run_for_video.side_effect = [
            PipelineResult(content_id=ContentId("skipVid"), success=True, already_processed=True),
            PipelineResult(content_id=ContentId("failVid"), success=False, error_message="Network glitch"),
        ]

        with (
            patch("cresmo.presentation.commands.run._drain_telemetry_and_memory"),
            patch("cresmo.presentation.commands.run.build_concat_master_use_case") as mock_build_concat,
        ):
            mock_concat = MagicMock()
            mock_concat.execute_all.return_value = {"tech": [MagicMock()]}
            mock_build_concat.return_value = mock_concat

            code = execute_batch_run(mock_pipeline, sources, args)
            assert code == EXIT_INTERNAL_ERROR  # failed > 0

            captured = capsys.readouterr()
            assert "Batch Synthesis Summary" in captured.out
            assert "- Total Items: 3\n" in captured.out
            assert "- Completed: 1\n" in captured.out
            assert "- Skipped (Idempotent): 1\n" in captured.out
            assert "- Failed: 1\n" in captured.out
            assert "Consolidating master compendiums for RAG...\n" in captured.out
            assert "Master consolidation complete: 1 master document(s) generated across 1 channel(s).\n" in captured.out

    def test_execute_batch_dry_run_artifacts_and_urls(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        """Verify execute_batch_dry_run validates files and queries media ingestion without generative models."""
        mock_pipeline = MagicMock()

        # Valid text file
        doc_file = tmp_path / "valid_lecture.md"
        doc_file.write_text("Hello lecture text", encoding="utf-8")

        # System artifact (should be skipped)
        index_file = tmp_path / "_index.md"
        index_file.write_text("system index", encoding="utf-8")

        sources = [
            BatchSource(kind=SourceModality.FILE, target=str(doc_file)),
            BatchSource(kind=SourceModality.FILE, target=str(index_file)),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dryVid"),
            BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dryFail"),
        ]

        mock_raw = MagicMock()
        mock_raw.content.id.value = "dryVid"
        mock_raw.content.body = "A" * 200
        mock_pipeline.ingest_raw_transcript.execute.side_effect = [mock_raw, None]

        code = execute_batch_dry_run(mock_pipeline, sources)
        assert code == EXIT_SUCCESS

        captured = capsys.readouterr()
        assert "[1/4] Dry-run text: [valid_lecture] (18 bytes)\n" in captured.out
        assert "[2/4] Dry-run skipped artifact: [_index.md]\n" in captured.out
        assert "[3/4] Dry-run ingested: [dryVid] (200 chars)\n" in captured.out
        assert "[4/4] Ingestion failed for: https://youtube.com/watch?v=dryFail\n" in captured.err
        assert "Dry-run completed: 2/4 items validated.\n" in captured.out

    def test_build_batch_discovery_query(self) -> None:
        """Verify _build_batch_discovery_query accurately propagates CLI overrides and settings defaults."""
        settings = CresmoSettings(days_lookback=45, channel_discovery_workers=8, discovery_queue_maxsize=200)
        args = argparse.Namespace(
            manifest=Path("custom_playlist.txt"),
            no_scan_raw=True,
            channel_max_videos=15,
            no_crawl=True,
            channels=["Channel1"],
            categories=["tech_ai"],
            video_ids=["vidA"],
        )

        query = _build_batch_discovery_query(args, settings)
        assert isinstance(query, BatchDiscoveryQuery)
        assert query.explicit_manifest == Path("custom_playlist.txt")
        assert query.scan_raw is False
        assert query.lookback_days == 45
        assert query.channel_max_videos == 15
        assert query.discovery_workers == 8
        assert query.enable_channel_crawler is False
        assert query.queue_maxsize == 200
        assert query.filter_criteria.channels == ("channel1",)
        assert query.filter_criteria.categories == ("tech_ai",)
        assert query.filter_criteria.video_ids == ("vidA",)

    def test_handle_run_preflight_and_exceptions(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify handle_run preflight warnings and exception taxonomy mapping."""
        args = argparse.Namespace(
            lookback=60,
            batch_size=None,
            web_index=False,
            url=None,
            dry_run=False,
            no_scan_raw=False,
            manifest=None,
            channel_max_videos=50,
        )

        mock_preflight = MagicMock()
        mock_preflight_res = MagicMock(spec=["warnings", "assert_healthy"])
        mock_preflight_res.warnings = ["GPU driver outdated", "Disk low"]
        mock_preflight_res.assert_healthy.return_value = None
        mock_preflight.check_all.return_value = mock_preflight_res

        with (
            patch("cresmo.presentation.commands.run.build_preflight_checker", return_value=mock_preflight),
            patch("cresmo.presentation.commands.run.build_pipeline") as mock_build_pipeline,
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[]),
        ):
            code = handle_run(args)
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "[preflight warning] GPU driver outdated\n" in captured.err
            assert "[preflight warning] Disk low\n" in captured.err

        # Test exception mapping
        exceptions = [
            (RateLimitExceededError("Quota"), EXIT_RATE_LIMIT_EXCEEDED, "Rate limit exceeded:"),
            (IngestionNetworkError("Socket timeout"), EXIT_INGESTION_ERROR, "Ingestion network error:"),
            (PreflightError("FFmpeg missing"), EXIT_CONFIG_OR_USAGE_ERROR, "Preflight error:"),
            (DomainValidationError("Invalid"), EXIT_DOMAIN_VALIDATION_ERROR, "Domain validation error:"),
            (RuntimeError("Crash"), EXIT_INTERNAL_ERROR, "Unexpected internal error:"),
        ]

        for exc, expected_code, expected_msg in exceptions:
            with patch("cresmo.presentation.commands.run.build_preflight_checker", side_effect=exc):
                assert handle_run(args) == expected_code
                captured = capsys.readouterr()
                assert expected_msg in captured.err

    def test_process_single_batch_item_outcomes(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        """Verify _process_single_batch_item for all modalities, statuses, and exceptions."""
        from cresmo.presentation.commands.run import _process_single_batch_item

        mock_pipeline = MagicMock()
        args = argparse.Namespace(passes=3, force_reprocess=False)
        batch_id = MagicMock()

        # 1. Unprocessable file
        unproc = tmp_path / "_index.md"
        unproc.write_text("cresmo-gap-filler", encoding="utf-8")
        src_unproc = BatchSource(kind=SourceModality.FILE, target=str(unproc))
        assert _process_single_batch_item(mock_pipeline, src_unproc, args, "[1/1]", batch_id) == "skipped"
        captured = capsys.readouterr()
        assert "[1/1] [SKIPPED] [_index.md] Ignored internal Cresmo artifact or system index.\n" in captured.out

        # 2. Processable file already processed
        valid_file = tmp_path / "lecture.md"
        valid_file.write_text("Hello lecture", encoding="utf-8")
        src_file = BatchSource(kind=SourceModality.FILE, target=str(valid_file))
        mock_pipeline.run_for_text_file.return_value = PipelineResult(
            content_id=ContentId("f1"),
            success=True,
            already_processed=True,
        )
        assert _process_single_batch_item(mock_pipeline, src_file, args, "[1/2]", batch_id) == "skipped"
        mock_pipeline.run_for_text_file.assert_called_once_with(
            file_path=valid_file,
            gap_filler_passes=3,
            force_reprocess=False,
            batch_id=batch_id,
        )
        captured = capsys.readouterr()
        assert "[1/2] [SKIPPED] [f1] Already processed in ledger.\n" in captured.out

        # 3. Processable file success
        mock_pipeline.reset_mock()
        mock_pipeline.run_for_text_file.return_value = PipelineResult(
            content_id=ContentId("f2"),
            success=True,
            synthesized_notes=(MagicMock(), MagicMock()),
            reconciled_mocs=(MagicMock(),),
            duplicates_unified=2,
        )
        assert _process_single_batch_item(mock_pipeline, src_file, args, "[2/2]", batch_id) == "completed"
        captured = capsys.readouterr()
        assert "[2/2] [DONE] [f2]: 2 atomic notes synthesized, 1 MOCs reconciled, 2 duplicate clusters unified.\n" in captured.out

        # 4. URL item failure
        src_url = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=fail")
        mock_pipeline.run_for_video.return_value = PipelineResult(
            content_id=ContentId("fail"),
            success=False,
            error_message="Synthesis failure",
        )
        assert _process_single_batch_item(mock_pipeline, src_url, args, "[3/3]", batch_id) == "failed"
        mock_pipeline.run_for_video.assert_called_once_with(
            video_url="https://youtube.com/watch?v=fail",
            gap_filler_passes=3,
            force_reprocess=False,
            batch_id=batch_id,
        )
        captured = capsys.readouterr()
        assert "[3/3] [ERROR] https://youtube.com/watch?v=fail: Synthesis failure\n" in captured.err

        # 5. Rate limit error
        mock_pipeline.run_for_video.side_effect = RateLimitExceededError("Rate limited")
        assert _process_single_batch_item(mock_pipeline, src_url, args, "[4/4]", batch_id) == "failed"
        captured = capsys.readouterr()
        assert "[4/4] [RATE LIMIT] https://youtube.com/watch?v=fail: Rate limited\n" in captured.err

        # 6. Ingestion network error
        mock_pipeline.run_for_video.side_effect = IngestionNetworkError("Network down")
        assert _process_single_batch_item(mock_pipeline, src_url, args, "[5/5]", batch_id) == "failed"
        captured = capsys.readouterr()
        assert "[5/5] [NETWORK ERROR] https://youtube.com/watch?v=fail: Network down\n" in captured.err

        # 7. Generic exception
        mock_pipeline.run_for_video.side_effect = RuntimeError("Fatal fault")
        assert _process_single_batch_item(mock_pipeline, src_url, args, "[6/6]", batch_id) == "failed"
        captured = capsys.readouterr()
        assert "[6/6] [FAILED] https://youtube.com/watch?v=fail: Fatal fault\n" in captured.err

    def test_execute_run_pipeline_warmup_and_dispatch(self) -> None:
        """Verify warmup is skipped when web_index is active, called when inactive, and routes correctly."""
        from cresmo.presentation.commands.run import _execute_run_pipeline

        mock_pipeline = MagicMock()
        settings = CresmoSettings()

        # 1. web_index=True -> warmup not called
        args_web = argparse.Namespace(web_index=True, url="https://youtube.com/watch?v=vid1")
        with patch("cresmo.presentation.commands.run.execute_single_video_run", return_value=EXIT_SUCCESS) as mock_single:
            assert _execute_run_pipeline(args_web, settings, mock_pipeline) == EXIT_SUCCESS
            mock_pipeline.warmup.assert_not_called()
            mock_single.assert_called_once_with(mock_pipeline, args_web)

        # 2. web_index=False -> warmup called
        mock_pipeline.reset_mock()
        args_local = argparse.Namespace(web_index=False, url="https://youtube.com/watch?v=vid2")
        with patch("cresmo.presentation.commands.run.execute_single_video_run", return_value=EXIT_SUCCESS) as mock_single:
            assert _execute_run_pipeline(args_local, settings, mock_pipeline) == EXIT_SUCCESS
            mock_pipeline.warmup.assert_called_once()
            mock_single.assert_called_once_with(mock_pipeline, args_local)

    def test_load_batch_sources_and_progress_callback(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify load_batch_sources configures use case and wires progress_callback to stdout."""
        from cresmo.presentation.commands.run import load_batch_sources

        mock_uc = MagicMock()
        mock_uc.execute.return_value = iter([])
        settings = CresmoSettings()
        query = MagicMock()

        with patch("cresmo.presentation.commands.run.build_discover_batch_sources_use_case", return_value=mock_uc) as mock_build_uc:
            sources = list(load_batch_sources(query=query, settings=settings))
            assert sources == []
            mock_build_uc.assert_called_once()
            callback = mock_build_uc.call_args.kwargs["progress_callback"]
            callback("Crawling channel feed...\n")
            captured = capsys.readouterr()
            assert captured.out == "Crawling channel feed...\n"

    def test_consolidate_master_if_needed_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify _consolidate_master_if_needed writes warning on failure and skips when completed <= 0."""
        from cresmo.presentation.commands.run import _consolidate_master_if_needed

        mock_pipeline = MagicMock()

        # completed <= 0 -> no-op
        _consolidate_master_if_needed(mock_pipeline, completed=0)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        # completed > 0 with failure
        with patch("cresmo.presentation.commands.run.build_concat_master_use_case", side_effect=RuntimeError("Disk full")):
            _consolidate_master_if_needed(mock_pipeline, completed=1)
            captured = capsys.readouterr()
            assert "Warning: Master consolidation failed: Disk full\n" in captured.err

    def test_consolidate_master_if_needed_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify _consolidate_master_if_needed when completed > 0 formats summary table accurately."""
        from cresmo.presentation.commands.run import _consolidate_master_if_needed

        mock_pipeline = MagicMock()
        mock_pipeline.settings = CresmoSettings()
        mock_concat = MagicMock()
        mock_concat.execute_all.return_value = {
            "tech": [MagicMock(), MagicMock()],
            "philosophy": [MagicMock()],
        }

        with patch("cresmo.presentation.commands.run.build_concat_master_use_case", return_value=mock_concat) as mock_build_concat:
            _consolidate_master_if_needed(mock_pipeline, completed=2)
            mock_build_concat.assert_called_once_with(
                settings=mock_pipeline.settings,
                vault_port=mock_pipeline.vault_port,
            )
            captured = capsys.readouterr()
            expected = (
                "\nConsolidating master compendiums for RAG...\n"
                "Master consolidation complete: 3 master document(s) generated across 2 channel(s).\n"
            )
            assert captured.out == expected

    def test_handle_run_with_custom_flags(self) -> None:
        """Verify handle_run passes custom lookback, batch_size, and web_index to pipeline builder."""
        args = argparse.Namespace(
            lookback=90,
            batch_size=8,
            web_index=True,
            url=None,
            dry_run=False,
            no_scan_raw=False,
            manifest=None,
            channel_max_videos=50,
        )

        mock_preflight = MagicMock()
        mock_preflight_res = MagicMock(spec=["warnings", "assert_healthy"])
        mock_preflight_res.warnings = []
        mock_preflight_res.assert_healthy.return_value = None
        mock_preflight.check_all.return_value = mock_preflight_res

        with (
            patch("cresmo.presentation.commands.run.build_preflight_checker", return_value=mock_preflight) as mock_build_preflight,
            patch("cresmo.presentation.commands.run.build_pipeline") as mock_build_pipeline,
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[]),
        ):
            code = handle_run(args)
            assert code == EXIT_SUCCESS
            mock_build_preflight.assert_called_once()
            assert mock_build_preflight.call_args.kwargs["check_ffmpeg"] is True
            mock_build_pipeline.assert_called_once()
            call_kwargs = mock_build_pipeline.call_args.kwargs
            assert call_kwargs["settings"].days_lookback == 90
            assert call_kwargs["batch_size_override"] == 8
            assert call_kwargs["web_index"] is True

    def test_execute_batch_run_unsized_generator_sources(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        """Verify execute_batch_run formats item prefix correctly without total count when sources is an unsized generator."""
        mock_pipeline = MagicMock()
        valid_file = tmp_path / "gen.md"
        valid_file.write_text("Generator content", encoding="utf-8")

        def gen_sources():
            yield BatchSource(kind=SourceModality.FILE, target=str(valid_file))

        args = argparse.Namespace(
            manifest=None,
            no_scan_raw=False,
            passes=1,
            force_reprocess=False,
        )
        mock_pipeline.run_for_text_file.return_value = PipelineResult(
            content_id=ContentId("gen1"),
            success=True,
            synthesized_notes=(),
            reconciled_mocs=(),
        )

        with (
            patch("cresmo.presentation.commands.run._drain_telemetry_and_memory"),
            patch("cresmo.presentation.commands.run.build_concat_master_use_case"),
        ):
            code = execute_batch_run(mock_pipeline, gen_sources(), args)
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert "[1] [DONE] [gen1]: 0 atomic notes synthesized, 0 MOCs reconciled, 0 duplicate clusters unified.\n" in captured.out

    def test_execute_run_pipeline_batch_dry_run_with_sources(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify _execute_run_pipeline calls load_batch_sources and runs execute_batch_dry_run when dry_run=True."""
        from cresmo.presentation.commands.run import _execute_run_pipeline

        mock_pipeline = MagicMock()
        settings = CresmoSettings()
        args = argparse.Namespace(
            web_index=False,
            url=None,
            dry_run=True,
            manifest=None,
            no_scan_raw=False,
            no_crawl=False,
            channel_max_videos=50,
        )
        fake_source = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dryTest")

        with (
            patch("cresmo.presentation.commands.run.load_batch_sources", return_value=[fake_source]) as mock_load,
            patch("cresmo.presentation.commands.run.execute_batch_dry_run", return_value=EXIT_SUCCESS) as mock_dry,
        ):
            code = _execute_run_pipeline(args, settings, mock_pipeline)
            assert code == EXIT_SUCCESS
            mock_load.assert_called_once()
            assert mock_load.call_args.kwargs["settings"] is settings
            assert mock_load.call_args.kwargs["media_ingestion_port"] == mock_pipeline.media_ingestion_port
            mock_dry.assert_called_once_with(mock_pipeline, [fake_source])

    def test_build_batch_discovery_query_crawl_defaults(self) -> None:
        """Verify _build_batch_discovery_query respects enable_channel_crawler setting when no_crawl is False."""
        args = argparse.Namespace(
            manifest=None,
            no_scan_raw=False,
            channel_max_videos=50,
            no_crawl=False,
        )
        s_true = CresmoSettings(enable_channel_crawler=True)
        q_true = _build_batch_discovery_query(args, s_true)
        assert q_true.enable_channel_crawler is True

        s_false = CresmoSettings(enable_channel_crawler=False)
        q_false = _build_batch_discovery_query(args, s_false)
        assert q_false.enable_channel_crawler is False

    def test_drain_telemetry_and_memory_logs_debug_on_exception(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify _drain_telemetry_and_memory logs debug messages when flush or metrics fail."""
        import logging

        mock_pipeline = MagicMock()
        mock_pipeline.telemetry_port.flush.side_effect = RuntimeError("Telemetry offline")
        mock_pipeline.metrics_port.set_gauge.side_effect = RuntimeError("Metrics offline")

        with caplog.at_level(logging.DEBUG):
            _drain_telemetry_and_memory(mock_pipeline)

        assert "[run] Telemetry flush skipped or failed during cleanup: Telemetry offline" in caplog.text
        assert "[run] Process metrics emission failed during cleanup: Metrics offline" in caplog.text



