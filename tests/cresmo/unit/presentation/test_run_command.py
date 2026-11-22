"""Hermetic unit tests for Humble Object 'cresmo run' command, AST purity, and purged flags.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cresmo.application.use_cases.run_synthesis import (
    BatchItemEvent,
    BatchItemEventKind,
    RunExitStatus,
    RunSynthesisOutcome,
    RunSynthesisRequest,
)
from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    QuotaPoolExhaustedError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import BatchId
from cresmo.presentation.cli import app, main
from cresmo.presentation.commands.run import _render_event, _render_outcome, handle_run
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


class TestRunHumbleCommand:
    """Unit tests verifying Humble Object rendering, option binding, and purity."""

    def test_handle_run_delegates_to_use_case_and_propagates_overrides(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_uc = MagicMock()
        batch_id = BatchId.generate()
        mock_uc.execute.return_value = RunSynthesisOutcome(
            status=RunExitStatus.SUCCESS,
            mode="batch",
            batch_id=batch_id,
            completed=2,
            skipped=1,
            failed=0,
            total_items=3,
        )

        req = RunSynthesisRequest(
            passes=4,
            batch_size=8,
            lookback=14,
            web_index=True,
            crawl=True,
        )
        with patch(
            "cresmo.presentation.commands.run.build_run_synthesis_use_case",
            return_value=mock_uc,
        ) as mock_builder:
            code = handle_run(req)

        assert code == EXIT_SUCCESS
        mock_builder.assert_called_once_with(
            lookback_override=14,
            batch_size_override=8,
            web_index=True,
            check_ffmpeg=True,
        )
        mock_uc.execute.assert_called_once()
        assert mock_uc.execute.call_args.args[0] == req
        captured = capsys.readouterr()
        assert f"Batch Synthesis Summary [Batch: {batch_id.value}]:" in captured.out
        assert "- Completed: 2" in captured.out
        assert "- Skipped (Idempotent): 1" in captured.out
        assert "- Failed: 0" in captured.out

    @pytest.mark.parametrize(
        ("exc", "expected_code"),
        [
            (
                QuotaPoolExhaustedError("cooldown", retry_after_seconds=30.0),
                EXIT_RATE_LIMIT_EXCEEDED,
            ),
            (RateLimitExceededError("429"), EXIT_RATE_LIMIT_EXCEEDED),
            (IngestionNetworkError("net error"), EXIT_INGESTION_ERROR),
            (PreflightError("missing ffmpeg"), EXIT_CONFIG_OR_USAGE_ERROR),
            (DomainValidationError("bad value"), EXIT_DOMAIN_VALIDATION_ERROR),
            (RuntimeError("crash"), EXIT_INTERNAL_ERROR),
        ],
    )
    def test_handle_run_maps_exceptions_via_error_handler(
        self, exc: BaseException, expected_code: int
    ) -> None:
        with patch(
            "cresmo.presentation.commands.run.build_run_synthesis_use_case",
            side_effect=exc,
        ):
            assert handle_run(RunSynthesisRequest()) == expected_code

    def test_render_event_routes_stdout_and_stderr(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _render_event(BatchItemEvent(BatchItemEventKind.PREFLIGHT_WARNING, "warn"))
        _render_event(BatchItemEvent(BatchItemEventKind.DISCOVERY_PROGRESS, "Found 1 "))
        _render_event(BatchItemEvent(BatchItemEventKind.COMPLETED, "[1/1] [DONE]"))
        _render_event(BatchItemEvent(BatchItemEventKind.MASTER_CONSOLIDATED, "Master done: 1"))
        _render_event(BatchItemEvent(BatchItemEventKind.QUOTA_ABORT, "Cooldown abort"))

        captured = capsys.readouterr()
        assert "[preflight warning] warn\n" in captured.err
        assert "Cooldown abort\n" in captured.err
        assert "Found 1 [1/1] [DONE]\n" in captured.out
        assert "Consolidating master compendiums for RAG..." in captured.out

    def test_render_outcome_covers_single_and_batch_variants(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.INGESTION_ERROR,
                    mode="single",
                    dry_run=True,
                    single_dry_run_url="https://youtube.com/watch?v=12345678901",
                )
            )
            == EXIT_INGESTION_ERROR
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.SUCCESS,
                    mode="single",
                    dry_run=True,
                    single_content_id="12345678901",
                    single_dry_run_chars=500,
                )
            )
            == EXIT_SUCCESS
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.SUCCESS,
                    mode="single",
                    skipped=1,
                    single_content_id="12345678901",
                )
            )
            == EXIT_SUCCESS
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.SUCCESS,
                    mode="single",
                    completed=1,
                    single_content_id="12345678901",
                    single_notes_count=4,
                    single_mocs_count=1,
                    single_duplicates_unified=2,
                )
            )
            == EXIT_SUCCESS
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.INTERNAL_ERROR,
                    mode="single",
                    failed=1,
                    error_message="Stage error",
                )
            )
            == EXIT_INTERNAL_ERROR
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.SUCCESS,
                    mode="batch",
                    empty_sources=True,
                    manifest_display="m.txt",
                    scan_raw=True,
                )
            )
            == EXIT_SUCCESS
        )
        assert (
            _render_outcome(
                RunSynthesisOutcome(
                    status=RunExitStatus.SUCCESS,
                    mode="batch",
                    dry_run=True,
                    dry_run_validated=2,
                    dry_run_total=3,
                )
            )
            == EXIT_SUCCESS
        )
        captured = capsys.readouterr()
        assert "Dry-run completed: 2/3 items validated.\n" in captured.out
        assert (
            "No sources found to process (manifest: m.txt, raw lake scan: True).\n" in captured.out
        )
        assert "Pipeline error: Stage error\n" in captured.err

    def test_typer_run_builds_request_without_dead_flags(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("", encoding="utf-8")
        with patch(
            "cresmo.presentation.commands.run.handle_run", return_value=EXIT_SUCCESS
        ) as mock_handle:
            code = main(
                [
                    "run",
                    "--manifest",
                    str(manifest),
                    "--passes",
                    "2",
                    "--scan-raw",
                    "--crawl",
                    "--web-index",
                    "--channel",
                    "Mises",
                    "--category",
                    "Economics",
                    "--video",
                    "dQw4w9WgXcQ",
                ]
            )
        assert code == EXIT_SUCCESS
        req = mock_handle.call_args.args[0]
        assert isinstance(req, RunSynthesisRequest)
        assert req.manifest == manifest.resolve()
        assert req.passes == 2
        assert req.scan_raw is True
        assert req.crawl is True
        assert req.web_index is True
        assert req.channels == ("Mises",)
        assert req.categories == ("Economics",)
        assert req.video_ids == ("dQw4w9WgXcQ",)


class TestHexagonalPurityAndPurgedDeadFlags:
    """AST import-purity enforcement and CLI rejection of all 12 purged dead flags."""

    @pytest.mark.parametrize(
        "argv",
        [
            ["run", "--all"],
            ["run", "--device", "cpu"],
            ["run", "--concurrency", "2"],
            ["run", "--verbose"],
            ["run", "-v"],
            ["run", "--no-crawl"],
            ["sync", "--verbose"],
            ["check-config", "--verbose"],
            ["concat-master", "--verbose"],
            ["export-cookies", "--verbose"],
            ["seed-prompts", "--verbose"],
            ["worker", "--channel", "https://youtube.com/@test", "--verbose"],
            ["dedupe", "--dry-run"],
        ],
    )
    def test_purged_dead_cli_flags_rejected_with_usage_error(self, argv: list[str]) -> None:
        runner = CliRunner()
        result = runner.invoke(app, argv)
        assert result.exit_code != 0

    @pytest.mark.parametrize(
        ("rel_path", "forbidden_prefixes"),
        [
            (
                "src/cresmo/presentation/commands/run.py",
                ("cresmo.infrastructure", "opentelemetry", "gc"),
            ),
            (
                "src/cresmo/presentation/commands/sync.py",
                ("cresmo.infrastructure", "opentelemetry", "gc"),
            ),
            (
                "src/cresmo/presentation/commands/check_config.py",
                ("cresmo.infrastructure", "opentelemetry", "gc"),
            ),
            (
                "src/cresmo/application/use_cases/run_synthesis.py",
                ("cresmo.infrastructure", "opentelemetry", "sys", "gc"),
            ),
            (
                "src/cresmo/application/use_cases/sync_batch.py",
                ("cresmo.infrastructure", "opentelemetry", "sys", "gc"),
            ),
        ],
    )
    def test_ast_import_purity_enforced(
        self, rel_path: str, forbidden_prefixes: tuple[str, ...]
    ) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        tree = ast.parse((repo_root / rel_path).read_text(encoding="utf-8"), filename=rel_path)
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        violations = [
            mod
            for mod in imported_modules
            if any(mod == prefix or mod.startswith(f"{prefix}.") for prefix in forbidden_prefixes)
        ]
        assert not violations, f"Forbidden imports in {rel_path}: {violations}"
