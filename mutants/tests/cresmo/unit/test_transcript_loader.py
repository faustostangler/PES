"""Unit tests for transcript_loader, is_subpath helper, and ensure_file_saved."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.pipeline.transcript_loader import (
    ensure_transcript_saved,
    is_subpath,
    load_transcript_from_file,
)
from cresmo.domain.entities import SourceTranscript
from cresmo.domain.value_objects import ChannelName, ContentId


class TestIsSubpath:
    """Verifies filesystem containment predicate is_subpath."""

    def test_direct_child_is_subpath(self, tmp_path: Path) -> None:
        parent = tmp_path / "data" / "raw"
        parent.mkdir(parents=True)
        child = parent / "transcript.md"
        child.write_text("test")

        assert is_subpath(child, parent) is True

    def test_nested_child_is_subpath(self, tmp_path: Path) -> None:
        parent = tmp_path / "data"
        parent.mkdir(parents=True)
        nested = parent / "raw" / "channel" / "transcript.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("test")

        assert is_subpath(nested, parent) is True

    def test_outside_path_is_not_subpath(self, tmp_path: Path) -> None:
        parent = tmp_path / "data" / "raw"
        parent.mkdir(parents=True)
        outside = tmp_path / "other_dir" / "transcript.md"
        outside.parent.mkdir(parents=True)
        outside.write_text("test")

        assert is_subpath(outside, parent) is False

    def test_none_parent_returns_false(self, tmp_path: Path) -> None:
        target = tmp_path / "transcript.md"
        assert is_subpath(target, None) is False

    def test_same_directory_is_subpath(self, tmp_path: Path) -> None:
        assert is_subpath(tmp_path, tmp_path) is True


class TestEnsureTranscriptSaved:
    """Verifies transcript persistence delegation to VaultRepositoryPort without disk I/O."""

    def test_file_inside_target_dir_skips_save(self, tmp_path: Path) -> None:
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        file_path = target_dir / "sample.md"
        file_path.write_text("content", encoding="utf-8")

        mock_vault = MagicMock()
        mock_transcript = MagicMock(spec=SourceTranscript)

        ensure_transcript_saved(mock_vault, file_path, mock_transcript, target_dir)

        mock_vault.save_transcript.assert_not_called()

    def test_file_outside_target_dir_is_saved_via_vault_port(self, tmp_path: Path) -> None:
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        external_dir = tmp_path / "external"
        external_dir.mkdir()
        file_path = external_dir / "sample.md"
        file_path.write_text("content", encoding="utf-8")

        mock_vault = MagicMock()
        mock_transcript = MagicMock(spec=SourceTranscript)

        ensure_transcript_saved(mock_vault, file_path, mock_transcript, target_dir)

        mock_vault.save_transcript.assert_called_once_with(mock_transcript)


class TestLoadTranscriptFromFile:
    """Verifies load_transcript_from_file parsing and SourceTranscript creation."""

    def test_load_valid_file(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test_video.md"
        content = (
            "---\n"
            "title: 'My Video Title'\n"
            "channel: 'Tech Channel'\n"
            "---\n\n"
            "This is the spoken transcript body."
        )
        file_path.write_text(content, encoding="utf-8")

        transcript = load_transcript_from_file(file_path)

        assert isinstance(transcript, SourceTranscript)
        assert transcript.content.title == "My Video Title"
        assert transcript.content.content_title == "My Video Title"
        assert transcript.channel.channel_name == ChannelName("Tech Channel")
        assert transcript.content.body == "This is the spoken transcript body."
        assert isinstance(transcript.content.id, ContentId)
        # ADR-038: Pure Triad Composition & Parity
        assert transcript.channel.name == "Tech Channel"
        assert transcript.content.title == "My Video Title"
        assert transcript.content.body == "This is the spoken transcript body."
        assert transcript.provenance.url == f"file://{file_path.resolve()}"


def test_coordinator_run_for_text_file_passes_raw_dir(tmp_path: Path) -> None:
    from cresmo.application.pipeline import CresmoPipeline
    from cresmo.application.pipeline.stage_runner import PipelineStageRunner
    from cresmo.application.ports import DefaultPipelineSettings
    from cresmo.application.ports.storage import VaultRepositoryPort

    file_path = tmp_path / "incoming" / "sample.md"
    file_path.parent.mkdir()
    file_path.write_text("---\ntitle: 'Title'\nchannel: 'Chan'\n---\nBody text.", encoding="utf-8")

    mock_vault = MagicMock(spec=VaultRepositoryPort)
    mock_runner = MagicMock(spec=PipelineStageRunner)
    mock_runner.telemetry_port = None
    mock_runner.metrics_port = None
    mock_runner.llm_transformation_port = MagicMock()

    custom_raw_dir = tmp_path / "custom_raw"
    custom_raw_dir.mkdir()
    settings = DefaultPipelineSettings(raw_dir=custom_raw_dir)

    pipeline = CresmoPipeline(
        media_ingestion_port=MagicMock(),
        vault_port=mock_vault,
        stage_runner=mock_runner,
        settings=settings,
    )
    pipeline.execute = MagicMock()

    pipeline.run_for_text_file(file_path)

    # Since file_path is in incoming/ and not in custom_raw/, it must be persisted via vault_port mock
    mock_vault.save_transcript.assert_called_once()
