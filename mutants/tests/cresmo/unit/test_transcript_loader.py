"""Unit tests for transcript_loader, is_subpath helper, and ensure_file_saved."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.pipeline.transcript_loader import (
    _derive_content_id,
    _extract_frontmatter,
    _resolve_metadata,
    ensure_transcript_saved,
    is_subpath,
    load_manifest_urls,
    load_transcript_from_file,
)
from cresmo.domain.entities import SourceTranscript
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId


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

    def test_relative_to_exception_returns_false(self) -> None:
        target = Path("/tmp/somewhere/file.txt")
        parent = Path("/tmp/other")
        with patch.object(Path, "is_relative_to", side_effect=ValueError("Different anchor")):
            assert is_subpath(target, parent) is False


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

    def test_file_inside_vault_raw_dir_skips_save_when_target_dir_none(
        self, tmp_path: Path
    ) -> None:
        vault_raw_dir = tmp_path / "vault_raw"
        vault_raw_dir.mkdir()
        file_path = vault_raw_dir / "sample.md"
        file_path.write_text("content", encoding="utf-8")

        mock_vault = MagicMock()
        mock_vault.raw_dir = vault_raw_dir
        mock_transcript = MagicMock(spec=SourceTranscript)

        ensure_transcript_saved(mock_vault, file_path, mock_transcript, target_dir=None)

        mock_vault.save_transcript.assert_not_called()

    def test_file_outside_vault_raw_dir_and_target_none_saves(self, tmp_path: Path) -> None:
        vault_raw_dir = tmp_path / "vault_raw"
        vault_raw_dir.mkdir()
        external_dir = tmp_path / "other"
        external_dir.mkdir()
        file_path = external_dir / "sample.md"
        file_path.write_text("content", encoding="utf-8")

        mock_vault = MagicMock()
        mock_vault.raw_dir = vault_raw_dir
        mock_transcript = MagicMock(spec=SourceTranscript)

        ensure_transcript_saved(mock_vault, file_path, mock_transcript, target_dir=None)

        mock_vault.save_transcript.assert_called_once_with(mock_transcript)


class TestContentIdDerivation:
    """Verifies deterministic and compliant ContentId derivation."""

    def test_valid_stem_exact_boundaries(self) -> None:
        # Minimum valid length = 8
        stem_8 = "12345678"
        cid_8 = _derive_content_id(stem_8, "body")
        assert cid_8.value == "12345678"

        # Maximum valid length = 64
        stem_64 = "a" * 64
        cid_64 = _derive_content_id(stem_64, "body")
        assert cid_64.value == "a" * 64

    def test_short_stem_triggers_fallback_hash(self) -> None:
        stem_7 = "1234567"
        raw_body = "sample body"
        expected_suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
        cid = _derive_content_id(stem_7, raw_body)
        assert cid.value == f"1234567_{expected_suffix}"

    def test_long_stem_triggers_fallback_hash_with_prefix_truncation(self) -> None:
        stem_65 = "b" * 65
        raw_body = "another body"
        expected_suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
        cid = _derive_content_id(stem_65, raw_body)
        assert cid.value == f"{'b' * 24}_{expected_suffix}"

    def test_empty_or_all_symbol_stem_uses_text_prefix(self) -> None:
        raw_body = "content text"
        expected_suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
        cid = _derive_content_id("!@#$%^&*()", raw_body)
        assert cid.value == f"text_{expected_suffix}"

    def test_stem_cleaning_filters_disallowed_characters(self) -> None:
        # Stem with spaces and special chars, but valid length when cleaned
        stem = "clean-stem_with.special@chars!"
        cid = _derive_content_id(stem, "body")
        assert cid.value == "clean-stem_withspecialchars"


class TestFrontmatterParsing:
    """Verifies frontmatter extraction and parsing."""

    def test_raw_body_without_frontmatter(self) -> None:
        body = "Just plain text without headers."
        parsed_body, meta = _extract_frontmatter(body, "sample.md")
        assert parsed_body == body
        assert meta == {}

    def test_raw_body_with_unclosed_frontmatter(self) -> None:
        body = "---\ntitle: unclosed\nno end delimiter here"
        parsed_body, meta = _extract_frontmatter(body, "sample.md")
        assert parsed_body == body
        assert meta == {}

    def test_empty_frontmatter(self) -> None:
        body = "---\n\n---\nActual content"
        parsed_body, meta = _extract_frontmatter(body, "sample.md")
        assert parsed_body == "Actual content"
        assert meta == {}

    def test_malformed_yaml_frontmatter_logs_debug_and_returns_empty(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        body = "---\nkey: : [unbalanced yaml\n---\nActual content"
        with caplog.at_level(logging.DEBUG):
            parsed_body, meta = _extract_frontmatter(body, "malformed.md")
        assert parsed_body == "Actual content"
        assert meta == {}
        record = next(
            r
            for r in caplog.records
            if r.levelno == logging.DEBUG and "malformed.md" in r.getMessage()
        )
        assert record.msg == "[pipeline] Malformed YAML frontmatter in '%s', retaining defaults: %s"
        args = record.args
        assert isinstance(args, tuple)
        assert args[0] == "malformed.md"
        assert isinstance(args[1], Exception)


class TestMetadataResolution:
    """Verifies metadata resolution hierarchy and fallbacks."""

    def test_video_title_precedence_over_title(self, tmp_path: Path) -> None:
        meta = {"video_title": "Primary Video Title", "title": "Secondary Title"}
        title, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert title == "Primary Video Title"

    def test_title_precedence_over_stem(self, tmp_path: Path) -> None:
        meta = {"title": "Secondary Title"}
        title, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert title == "Secondary Title"

    def test_stem_fallback_formatting(self, tmp_path: Path) -> None:
        meta: dict[str, str] = {}
        title, *_, _ = _resolve_metadata(meta, tmp_path / "my_cool-lecture.md", "my_cool-lecture")
        assert title == "My Cool Lecture"

    def test_channel_name_precedence_over_channel(self, tmp_path: Path) -> None:
        meta = {"channel_name": "Main Channel", "channel": "Alt Channel"}
        _, ch_name, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert ch_name.value == "Main Channel"

    def test_channel_fallback_over_parent_dir(self, tmp_path: Path) -> None:
        meta = {"channel": "Alt Channel"}
        _, ch_name, *_, _ = _resolve_metadata(meta, tmp_path / "parent_dir" / "test.md", "test")
        assert ch_name.value == "Alt Channel"

    def test_parent_dir_fallback(self, tmp_path: Path) -> None:
        meta: dict[str, str] = {}
        file_path = tmp_path / "recorded_podcasts" / "ep1.md"
        _, ch_name, *_, _ = _resolve_metadata(meta, file_path, "ep1")
        assert ch_name.value == "recorded_podcasts"

    def test_empty_parent_dir_fallback_to_text(self) -> None:
        meta: dict[str, str] = {}
        file_path = Path("/ep1.md")
        _, ch_name, *_, _ = _resolve_metadata(meta, file_path, "ep1")
        assert ch_name.value == "text"

    def test_explicit_channel_id(self, tmp_path: Path) -> None:
        meta = {"channel_id": "UC_987654321"}
        _, _, ch_id, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert ch_id is not None
        assert ch_id.value == "UC_987654321"

    def test_absent_channel_id_defaults_to_priority_text(self, tmp_path: Path) -> None:
        meta: dict[str, str] = {}
        _, _, ch_id, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert ch_id is not None
        assert ch_id.value == "priority_text"

    def test_channel_category_precedence_over_domain(self, tmp_path: Path) -> None:
        meta = {"channel_category": "technology", "domain": "science"}
        _, _, _, category, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert category == "technology"

    def test_domain_precedence_over_taxonomy(self, tmp_path: Path) -> None:
        meta = {"domain": "philosophy"}
        _, _, _, category, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert category == "philosophy"

    def test_taxonomy_fallback_for_category(self, tmp_path: Path) -> None:
        meta: dict[str, str] = {}
        file_path = tmp_path / "brasil paralelo" / "test.md"
        _, ch_name, _, category, *_, _ = _resolve_metadata(meta, file_path, "test")
        assert ch_name.value == "brasil paralelo"
        assert category == "politics_br"

    def test_explicit_source_url(self, tmp_path: Path) -> None:
        meta = {"url": "https://youtube.com/watch?v=12345"}
        _, _, _, _, source_url, *_, _ = _resolve_metadata(meta, tmp_path / "test.md", "test")
        assert source_url == "https://youtube.com/watch?v=12345"

    def test_fallback_file_source_url(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test.md"
        meta: dict[str, str] = {}
        _, _, _, _, source_url, *_, _ = _resolve_metadata(meta, file_path, "test")
        assert source_url == f"file://{file_path.resolve()}"

    def test_video_description_present_and_absent(self, tmp_path: Path) -> None:
        meta_with_desc = {"video_description": "Summary of the video."}
        _, _, _, _, _, desc1, _ = _resolve_metadata(meta_with_desc, tmp_path / "test.md", "test")
        assert desc1 == "Summary of the video."

        meta_empty: dict[str, str] = {}
        _, _, _, _, _, desc2, _ = _resolve_metadata(meta_empty, tmp_path / "test.md", "test")
        assert desc2 == ""

    def test_publication_date_and_published_at_resolution(self, tmp_path: Path) -> None:
        meta_pub = {"publication_date": "2026-04-10"}
        *_, pub1 = _resolve_metadata(meta_pub, tmp_path / "test.md", "test")
        assert pub1 == "2026-04-10"

        meta_at = {"published_at": "2026-05-20"}
        *_, pub2 = _resolve_metadata(meta_at, tmp_path / "test.md", "test")
        assert pub2 == "2026-05-20"


class TestLoadTranscriptFromFile:
    """Verifies load_transcript_from_file parsing, validation, and domain invariants."""

    def test_load_valid_file(self, tmp_path: Path) -> None:
        from datetime import date

        file_path = tmp_path / "test_video.md"
        content = (
            "---\n"
            "title: 'My Video Title'\n"
            "channel: 'Tech Channel'\n"
            "channel_id: 'UC_custom123'\n"
            "channel_category: 'computing'\n"
            "video_description: 'A deep dive into architecture.'\n"
            "publication_date: '2026-06-15'\n"
            "---\n\n"
            "This is the spoken transcript body."
        )
        file_path.write_text(content, encoding="utf-8")

        transcript = load_transcript_from_file(file_path)

        assert isinstance(transcript, SourceTranscript)
        assert transcript.content.title == "My Video Title"
        assert transcript.channel.name == "Tech Channel"
        assert transcript.channel.id is not None
        assert transcript.channel.id.value == "UC_custom123"
        assert transcript.channel.category == "computing"
        assert transcript.provenance.description == "A deep dive into architecture."
        assert transcript.provenance.publication_date == date(2026, 6, 15)
        assert transcript.content.body == "This is the spoken transcript body."
        assert isinstance(transcript.content.id, ContentId)
        assert transcript.content.id.value == "test_video"
        assert transcript.provenance.url == f"file://{file_path.resolve()}"

    def test_load_transcript_without_title_uses_stem(self, tmp_path: Path) -> None:
        file_path = tmp_path / "inferred_title_file.md"
        file_path.write_text("Body text with enough length.", encoding="utf-8")
        transcript = load_transcript_from_file(file_path)
        assert transcript.content.title == "Inferred Title File"
        assert transcript.content.id.value == "inferred_title_file"
        assert transcript.provenance.publication_date is None

    def test_load_transcript_with_malformed_yaml_logs_with_filename(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        file_path = tmp_path / "bad_yaml.md"
        file_path.write_text(
            "---\nfoo: : [bad\n---\nBody text with enough length.", encoding="utf-8"
        )
        with caplog.at_level(logging.DEBUG):
            transcript = load_transcript_from_file(file_path)
        assert transcript.content.body == "Body text with enough length."
        record = next(
            r
            for r in caplog.records
            if r.levelno == logging.DEBUG and "bad_yaml.md" in r.getMessage()
        )
        args = record.args
        assert isinstance(args, tuple)
        assert args[0] == "bad_yaml.md"

    def test_load_transcript_enforces_utf8_encoding(self, tmp_path: Path) -> None:
        file_path = tmp_path / "encoding_test.md"
        file_path.write_text("Valid body with length over eight chars", encoding="utf-8")
        with patch.object(Path, "read_text", wraps=file_path.read_text) as mock_read:
            load_transcript_from_file(file_path)
            assert mock_read.call_args[1].get("encoding") == "utf-8"

    def test_derive_content_id_enforces_utf8_encoding(self) -> None:
        mock_body = MagicMock()
        mock_body.encode.return_value = b"sample body"
        _derive_content_id("short", mock_body)
        mock_body.encode.assert_called_once_with("utf-8")

    def test_internal_cresmo_system_file_raises_error(self, tmp_path: Path) -> None:
        system_file = tmp_path / "_index.md"
        system_file.write_text("index content")

        with pytest.raises(
            CresmoDomainError,
            match="is an internal Cresmo artifact or system index and cannot be processed as a transcript.",
        ):
            load_transcript_from_file(system_file)

    def test_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "nonexistent.md"

        with pytest.raises(CresmoDomainError, match="Priority text file not found:"):
            load_transcript_from_file(nonexistent)

    def test_empty_file_raises_error(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("   \n   \t \n", encoding="utf-8")

        with pytest.raises(CresmoDomainError, match="Priority text file is empty:"):
            load_transcript_from_file(empty_file)


class TestLoadManifestUrls:
    """Verifies load_manifest_urls parsing and error handling."""

    def test_load_manifest_urls_success(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "urls.txt"
        manifest_content = (
            "# This is a comment\n"
            "\n"
            "https://youtube.com/watch?v=aaa111\n"
            "   \n"
            "# Another comment\n"
            "  https://youtube.com/watch?v=bbb222  \n"
        )
        manifest_file.write_text(manifest_content, encoding="utf-8")

        urls = load_manifest_urls(manifest_file)
        assert urls == [
            "https://youtube.com/watch?v=aaa111",
            "https://youtube.com/watch?v=bbb222",
        ]

    def test_load_manifest_urls_enforces_utf8_encoding(self, tmp_path: Path) -> None:
        manifest = tmp_path / "urls_enc.txt"
        manifest.write_text("https://example.com/item\n", encoding="utf-8")
        with patch.object(Path, "read_text", wraps=manifest.read_text) as mock_read:
            load_manifest_urls(manifest)
            assert mock_read.call_args[1].get("encoding") == "utf-8"

    def test_nonexistent_manifest_raises_error(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "missing_urls.txt"

        with pytest.raises(CresmoDomainError, match="Manifest file not found:"):
            load_manifest_urls(nonexistent)


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
