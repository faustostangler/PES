"""Unit tests for discovery manifests and file reading utilities.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.use_cases.discovery.manifests import (
    extract_raw_file_metadata,
    is_channel_or_playlist_feed,
    load_transcript_files,
    matches_category_target,
    matches_channel_target,
    matches_video_target,
    read_manifest_lines,
)
from cresmo.domain.value_objects import (
    ContentId,
    SyncFilterCriteria,
)


class TestIsChannelOrPlaylistFeed:
    def test_identifies_channel_and_playlist_urls(self) -> None:
        assert is_channel_or_playlist_feed("https://www.youtube.com/@some_user") is True
        assert is_channel_or_playlist_feed("https://www.youtube.com/playlist?list=PL123") is True
        assert is_channel_or_playlist_feed("https://www.youtube.com/channel/UC1234567890") is True

    def test_identifies_individual_video_urls(self) -> None:
        assert is_channel_or_playlist_feed("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is False


class TestLoadTranscriptFiles:
    def test_empty_or_nonexistent_directory(self, tmp_path: Path) -> None:
        assert load_transcript_files(None) == []
        assert load_transcript_files(tmp_path / "nonexistent") == []

    def test_filters_valid_transcript_files(self, tmp_path: Path) -> None:
        (tmp_path / "video1.md").write_text("Valid content", encoding="utf-8")
        (tmp_path / "video2.txt").write_text("Valid text", encoding="utf-8")
        (tmp_path / "ignore.json").write_text("{}", encoding="utf-8")
        (tmp_path / ".DS_Store").write_bytes(b"")

        files = load_transcript_files(tmp_path)
        names = [f.name for f in files]
        assert "video1.md" in names
        assert "video2.txt" in names
        assert "ignore.json" not in names
        assert ".DS_Store" not in names


class TestReadManifestLines:
    def test_none_or_missing_file(self, tmp_path: Path) -> None:
        assert read_manifest_lines(None) == []
        assert read_manifest_lines(tmp_path / "missing.txt") == []

    def test_strips_comments_and_whitespace(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest.txt"
        manifest.write_text(
            "# Comment at top\n"
            "https://www.youtube.com/watch?v=111\n"
            "   \n"
            "   https://www.youtube.com/watch?v=222   \n"
            "# Another comment\n"
            "https://www.youtube.com/watch?v=333\n",
            encoding="utf-8",
        )
        lines = read_manifest_lines(manifest)
        assert lines == [
            "https://www.youtube.com/watch?v=111",
            "https://www.youtube.com/watch?v=222",
            "https://www.youtube.com/watch?v=333",
        ]


class TestExtractRawFileMetadata:
    def test_valid_yaml_frontmatter_with_http_channel(self, tmp_path: Path) -> None:
        f = tmp_path / "test1.md"
        f.write_text(
            "---\nvideo_id: vid_123\nchannel: https://youtube.com/@my_chan\n---\nTranscript body",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(f)
        assert meta["video_id"] == "vid_123"
        assert meta["channel"] == "https://youtube.com/@my_chan"

    def test_at_handle_channel_expansion(self, tmp_path: Path) -> None:
        f = tmp_path / "test2.md"
        f.write_text(
            "---\nchannel: @pes_science\n---\n",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(f)
        assert meta["channel"] == "https://www.youtube.com/@pes_science"

    def test_uc_channel_id_expansion(self, tmp_path: Path) -> None:
        f = tmp_path / "test3.md"
        f.write_text(
            "---\nchannel_id: UC1234567890abcdef\n---\n",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(f)
        assert meta["channel"] == "https://www.youtube.com/channel/UC1234567890abcdef"

    def test_plain_channel_name_preserved(self, tmp_path: Path) -> None:
        f = tmp_path / "test4.md"
        f.write_text(
            "---\nchannel_name: PlainChannel\n---\n",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(f)
        assert meta["channel"] == "PlainChannel"

    def test_missing_opening_fence_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "no_fence.md"
        f.write_text("No frontmatter at all\nvideo_id: 123", encoding="utf-8")
        assert extract_raw_file_metadata(f) == {}

    def test_unclosed_frontmatter_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "unclosed.md"
        f.write_text(
            "---\nvideo_id: 123\nchannel: test\nLine 3 without closing fence", encoding="utf-8"
        )
        assert extract_raw_file_metadata(f) == {}

    def test_frontmatter_exceeding_50_lines_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "too_long.md"
        # 1 opening fence + 49 keys + 1 closing fence = 51 lines -> exceeds max_lines=50
        lines_51 = ["---"] + [f"key_{i}: value_{i}" for i in range(49)] + ["---"]
        f.write_text("\n".join(lines_51), encoding="utf-8")
        assert extract_raw_file_metadata(f) == {}

        f_50 = tmp_path / "exact_50.md"
        lines_50 = ["---"] + [f"key_{i}: value_{i}" for i in range(48)] + ["---"]
        f_50.write_text("\n".join(lines_50), encoding="utf-8")
        assert extract_raw_file_metadata(f_50)["key_0"] == "value_0"

    def test_strips_nested_quotes_and_preserves_channel_id_urls(self, tmp_path: Path) -> None:
        f_http = tmp_path / "http_chan.md"
        f_http.write_text(
            '---\nvideo_title: "\'X_Nested_X\'"\nchannel_id: http://youtube.com/@http_chan\n---\n',
            encoding="utf-8",
        )
        meta_http = extract_raw_file_metadata(f_http)
        assert meta_http["video_title"] == "X_Nested_X"
        assert meta_http["channel"] == "http://youtube.com/@http_chan"

        f_https = tmp_path / "https_chan.md"
        f_https.write_text(
            "---\nchannel_id: https://youtube.com/@https_chan\n---\n",
            encoding="utf-8",
        )
        meta_https = extract_raw_file_metadata(f_https)
        assert meta_https["channel"] == "https://youtube.com/@https_chan"


class TestTargetMatchingFunctions:
    def test_matches_channel_target(self) -> None:
        criteria = SyncFilterCriteria(channels=("pes_chan",))
        assert matches_channel_target(criteria, "pes_chan") is True
        assert matches_channel_target(criteria, "@pes_chan") is True
        assert matches_channel_target(criteria, "https://youtube.com/@pes_chan") is True
        assert matches_channel_target(criteria, "other_chan") is False

        # @handle must route via channel_url (str), not ChannelName("@pes_chan")
        url_only_criteria = SyncFilterCriteria(channels=("youtube.com/@pes_chan",))
        assert matches_channel_target(url_only_criteria, "@pes_chan") is False

    def test_matches_category_target(self) -> None:
        from unittest.mock import MagicMock

        from cresmo.domain.value_objects import ChannelName

        seen_targets: list[ChannelName | str] = []

        def _classify(target: ChannelName | str) -> tuple[str, str]:
            seen_targets.append(target)
            return "science", "volatile"

        mock_taxonomy = MagicMock()
        mock_taxonomy.classify.side_effect = _classify
        criteria = SyncFilterCriteria(categories=("volatile",))
        assert matches_category_target(criteria, "pes_chan", taxonomy_port=mock_taxonomy) is True
        assert (
            matches_category_target(
                criteria, "https://youtube.com/@pes_chan", taxonomy_port=mock_taxonomy
            )
            is True
        )
        assert matches_category_target(criteria, "@pes_chan", taxonomy_port=mock_taxonomy) is True
        assert isinstance(seen_targets[0], ChannelName)
        assert seen_targets[1] == "https://youtube.com/@pes_chan"
        assert seen_targets[2] == "@pes_chan"
        assert type(seen_targets[2]) is str

    def test_matches_video_target_variations(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",))
        cid = ContentId("dQw4w9WgXcQ")

        assert matches_video_target(criteria, cid) is True
        assert matches_video_target(criteria, "dQw4w9WgXcQ") is True
        assert matches_video_target(criteria, "https://youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert (
            matches_video_target(
                criteria, None, url_fallback="https://youtube.com/watch?v=dQw4w9WgXcQ"
            )
            is True
        )
        assert matches_video_target(criteria, "oHg5SJYRHA0") is False

        # url_fallback forwarded for both ContentId and str token when id alone doesn't match
        list_criteria = SyncFilterCriteria(video_ids=("list=PL999",))
        other_cid = ContentId("oHg5SJYRHA0")
        assert (
            matches_video_target(
                list_criteria,
                other_cid,
                url_fallback="https://youtube.com/watch?v=oHg5SJYRHA0&list=PL999",
            )
            is True
        )
        assert (
            matches_video_target(
                list_criteria,
                "oHg5SJYRHA0",
                url_fallback="https://youtube.com/watch?v=oHg5SJYRHA0&list=PL999",
            )
            is True
        )

        # Empty criteria always matches
        empty = SyncFilterCriteria()
        assert matches_video_target(empty, None) is True
