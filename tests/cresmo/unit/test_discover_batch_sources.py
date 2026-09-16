"""Unit tests for DiscoverBatchSourcesUseCase.

Verifies raw transcript lake scanning, frontmatter parsing, concurrent channel resolution,
and channel feed discovery per ADR-003 and Clean Hexagonal Architecture.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
    _BatchSourceAccumulator,
    extract_raw_file_metadata,
    is_channel_or_playlist_feed,
    load_transcript_files,
    read_manifest_lines,
)
from cresmo.domain.value_objects import ContentId, DiscoveredMediaItem
from cresmo.infrastructure.config import CresmoSettings


def _create_mock_media_item(
    content_id_str: str,
    media_url: str,
    title: str = "Test Video",
    channel_name: str = "Test Channel",
) -> DiscoveredMediaItem:
    return DiscoveredMediaItem(
        content_id=ContentId(content_id_str),
        title=title,
        published_at=datetime.now(UTC),
        media_url=media_url,
        channel_name=channel_name,
    )


class TestDiscoverBatchSourcesUseCase:
    """Test suite for DiscoverBatchSourcesUseCase."""

    def test_extract_raw_file_metadata_parses_frontmatter(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.md"
        file.write_text(
            "---\ntitle: Sample Video\nchannel: https://www.youtube.com/@channel1\nvideo_id: abc12345\n---\nBody",
            encoding="utf-8",
        )
        meta = extract_raw_file_metadata(file)
        assert meta["title"] == "Sample Video"
        assert meta["channel"] == "https://www.youtube.com/@channel1"
        assert meta["video_id"] == "abc12345"

    def test_discover_sources_from_raw_lake(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        (raw_dir / "vid1.md").write_text(
            "---\ntitle: Video 1\nchannel: https://www.youtube.com/@chan1\nvideo_id: 11111111\n---\nText",
            encoding="utf-8",
        )
        (raw_dir / "vid2.md").write_text(
            "---\ntitle: Video 2\nchannel: https://www.youtube.com/@chan1\nvideo_id: 22222222\n---\nText",
            encoding="utf-8",
        )
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.discover_channel_feed.return_value = []

        settings = CresmoSettings()
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=settings,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=raw_dir,
            scan_raw=True,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert all(s.kind == "file" for s in sources)
        # Channel was discovered from frontmatter and queried exactly once
        assert mock_ingestion.discover_channel_feed.call_count == 1

    def test_discover_sources_resolves_channel_from_video_and_discovers_feed(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://www.youtube.com/watch?v=seed12345\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCDiscovered"
        )
        new_item = _create_mock_media_item(
            content_id_str="disc99999",
            media_url="https://www.youtube.com/watch?v=disc99999",
        )
        mock_ingestion.discover_channel_feed.return_value = [new_item]

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=True,
            lookback_days=365,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        mock_ingestion.extract_channel_url_from_video.assert_called_once_with(
            "https://www.youtube.com/watch?v=seed12345"
        )
        feed_query = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert feed_query.channel_url == "https://www.youtube.com/channel/UCDiscovered"
        assert feed_query.lookback_days == 365

        targets = [s.target for s in sources]
        assert "https://www.youtube.com/watch?v=seed12345" in targets
        assert "https://www.youtube.com/watch?v=disc99999" in targets

    def test_discover_sources_deduplicates_channels_across_multiple_videos(
        self, tmp_path: Path
    ) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text(
            "https://www.youtube.com/watch?v=video11111\nhttps://www.youtube.com/watch?v=video22222\n",
            encoding="utf-8",
        )

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/channel/UCSameChannel"
        )
        mock_ingestion.discover_channel_feed.return_value = []

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=True,
            playlist_priority_path=tmp_path / "empty_priority.txt",
            priority_texts_dir=tmp_path / "empty_priority_dir",
        )
        sources = use_case.execute(query)

        assert mock_ingestion.extract_channel_url_from_video.call_count == 2
        assert mock_ingestion.discover_channel_feed.call_count == 1
        assert len(sources) == 2

    def test_batch_source_display_name(self) -> None:
        file_source = BatchSource(kind="file", target="/lake/transcripts/lecture1.md")
        assert file_source.display_name == "lecture1.md"
        url_source = BatchSource(kind="url", target="https://youtube.com/watch?v=12345")
        assert url_source.display_name == "https://youtube.com/watch?v=12345"

    def test_extract_raw_file_metadata_channel_formats_and_error(self, tmp_path: Path) -> None:
        # Test @handle channel format
        f_handle = tmp_path / "handle.md"
        f_handle.write_text("---\nchannel: @TheoryCraft\n---\nBody", encoding="utf-8")
        meta_handle = extract_raw_file_metadata(f_handle)
        assert meta_handle["channel"] == "https://www.youtube.com/@TheoryCraft"

        # Test bare channel ID format
        f_bare = tmp_path / "bare.md"
        f_bare.write_text("---\nchannel_id: UCxyz123\n---\nBody", encoding="utf-8")
        meta_bare = extract_raw_file_metadata(f_bare)
        assert meta_bare["channel"] == "https://www.youtube.com/channel/UCxyz123"

        # Test unreadable / non-existent file returns empty dict
        assert extract_raw_file_metadata(tmp_path / "non_existent.md") == {}

    def test_explicit_manifest_override_and_progress_callback(self, tmp_path: Path) -> None:
        manifest = tmp_path / "custom_manifest.txt"
        manifest.write_text(
            "https://youtube.com/watch?v=explicit1\n# Comment\nhttps://youtube.com/watch?v=explicit2\n",
            encoding="utf-8",
        )

        notifications: list[str] = []
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=MagicMock(),
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(explicit_manifest=manifest)
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert [s.target for s in sources] == [
            "https://youtube.com/watch?v=explicit1",
            "https://youtube.com/watch?v=explicit2",
        ]
        assert any("Loaded 2 URLs" in msg for msg in notifications)

    def test_priority_sources(self, tmp_path: Path) -> None:
        priority_dir = tmp_path / "priority_texts"
        priority_dir.mkdir()
        (priority_dir / "prio1.md").write_text("# Priority doc", encoding="utf-8")

        priority_txt = tmp_path / "playlist-priority.txt"
        priority_txt.write_text("https://youtube.com/watch?v=prioUrl1\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        query = BatchDiscoveryQuery(
            priority_texts_dir=priority_dir,
            playlist_priority_path=priority_txt,
            playlist_path=tmp_path / "empty_playlist.txt",
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
        )
        sources = use_case.execute(query)

        assert len(sources) == 2
        assert sources[0].kind == "file"
        assert "prio1.md" in sources[0].target
        assert sources[1].kind == "url"
        assert sources[1].target == "https://youtube.com/watch?v=prioUrl1"

    def test_channel_feed_in_playlist_and_naive_datetime_filtering(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text(
            "https://www.youtube.com/@ExplicitChannel\nhttps://youtube.com/watch?v=videoWithRawMatch\n",
            encoding="utf-8",
        )

        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        (raw_dir / "videoWithRawMatch.md").write_text(
            "---\nvideo_id: videoWithRawMatch\nchannel: https://www.youtube.com/@RawChannel\n---\nContent",
            encoding="utf-8",
        )

        mock_ingestion = MagicMock()
        now_naive = datetime.now(UTC).replace(tzinfo=None)
        old_naive = (datetime.now(UTC) - timedelta(days=400)).replace(tzinfo=None)
        mock_ingestion.discover_channel_feed.return_value = [
            DiscoveredMediaItem(
                content_id=ContentId("fresh111"),
                title="Fresh Naive Date Video",
                published_at=now_naive,
                media_url="https://youtube.com/watch?v=fresh111",
                channel_name="ExplicitChannel",
            ),
            DiscoveredMediaItem(
                content_id=ContentId("old22222"),
                title="Old Video",
                published_at=old_naive,
                media_url="https://youtube.com/watch?v=old22222",
                channel_name="ExplicitChannel",
            ),
        ]

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=raw_dir,
            scan_raw=False,
            lookback_days=30,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        targets = [s.target for s in sources]
        assert "https://youtube.com/watch?v=fresh111" in targets
        assert "https://youtube.com/watch?v=old22222" not in targets

    def test_channel_lookup_and_probe_exception_resilience(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://youtube.com/watch?v=failLookup\n", encoding="utf-8")

        notifications: list[str] = []
        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.side_effect = RuntimeError(
            "Extraction failed"
        )

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 1
        assert sources[0].target == "https://youtube.com/watch?v=failLookup"
        assert any("Warning: Failed to resolve channel" in msg for msg in notifications)

    def test_probe_single_channel_exception_handling(self, tmp_path: Path) -> None:
        manifest = tmp_path / "playlist.txt"
        manifest.write_text("https://www.youtube.com/@CrashingChannel\n", encoding="utf-8")

        notifications: list[str] = []
        mock_ingestion = MagicMock()
        mock_ingestion.discover_channel_feed.side_effect = ConnectionError("Channel feed down")

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(
            manifest_path=manifest,
            raw_dir=tmp_path / "empty_raw",
            scan_raw=False,
            playlist_priority_path=tmp_path / "empty_prio.txt",
            priority_texts_dir=tmp_path / "empty_prio_dir",
        )
        sources = use_case.execute(query)

        assert len(sources) == 0
        assert any("Warning: Failed to probe" in msg for msg in notifications)

    def test_is_channel_or_playlist_feed_patterns(self) -> None:
        # Channel prefixes
        assert is_channel_or_playlist_feed("https://youtube.com/channel/UC123") is True
        assert is_channel_or_playlist_feed("https://youtube.com/c/CreatorName") is True
        assert is_channel_or_playlist_feed("https://youtube.com/user/UserName") is True
        assert is_channel_or_playlist_feed("https://youtube.com/@ChannelHandle") is True
        assert is_channel_or_playlist_feed("https://youtube.com/playlist?list=PL12345") is True

        # Case-insensitivity check (kills .lower() -> .upper() mutants)
        assert is_channel_or_playlist_feed("HTTPS://YOUTUBE.COM/@UPPERCASE") is True
        assert is_channel_or_playlist_feed("HTTPS://YOUTUBE.COM/CHANNEL/UC_UPPER") is True

        # Watch URLs: plain watch URL must be False
        assert is_channel_or_playlist_feed("https://youtube.com/watch?v=abcd1234") is False
        # Channel URL with watch?v but without list must be False
        assert (
            is_channel_or_playlist_feed("https://youtube.com/channel/UC123?watch?v=abcd") is False
        )
        # Channel URL with watch?v AND list must be True
        assert (
            is_channel_or_playlist_feed("https://youtube.com/channel/UC123?watch?v=abcd&list=PL123")
            is True
        )
        # Playlist feed URL
        assert is_channel_or_playlist_feed("https://youtube.com/playlist?list=PL999") is True
        # Watch URL with query param containing 'channel' must be False
        assert (
            is_channel_or_playlist_feed("https://youtube.com/watch?v=abcd1234&name=channel")
            is False
        )
        # Non-matching URL
        assert is_channel_or_playlist_feed("https://example.com/blog/article") is False

    def test_load_transcript_files_and_manifest_reading(self, tmp_path: Path) -> None:
        # Directory is None or non-existent
        assert load_transcript_files(None) == []
        assert load_transcript_files(tmp_path / "non_existent_folder") == []

        # Target is a file, not a directory
        reg_file = tmp_path / "regular_file.txt"
        reg_file.write_text("content", encoding="utf-8")
        assert load_transcript_files(reg_file) == []

        # Directory with multiple extensions
        folder = tmp_path / "transcripts"
        folder.mkdir()
        (folder / "b.txt").write_text("txt2", encoding="utf-8")
        (folder / "a.md").write_text("md1", encoding="utf-8")
        (folder / "c.MD").write_text("md2", encoding="utf-8")
        (folder / "d.TXT").write_text("txt1", encoding="utf-8")
        (folder / "e.pdf").write_text("pdf", encoding="utf-8")
        (folder / "f.doc").write_text("doc", encoding="utf-8")

        found = load_transcript_files(folder)
        assert [f.name for f in found] == ["a.md", "b.txt", "c.MD", "d.TXT"]

        # read_manifest_lines
        assert read_manifest_lines(None) == []
        assert read_manifest_lines(tmp_path / "missing_mf.txt") == []

        mf = tmp_path / "test_manifest.txt"
        mf.write_text(
            "# Section comment\n\n  https://yt.com/1  \n# Inline\nhttps://yt.com/2\n\n",
            encoding="utf-8",
        )
        lines = read_manifest_lines(mf)
        assert lines == ["https://yt.com/1", "https://yt.com/2"]

    def test_extract_raw_file_metadata_edge_cases(self, tmp_path: Path) -> None:
        # File without frontmatter
        plain = tmp_path / "plain.md"
        plain.write_text("Regular content without any YAML frontmatter header.", encoding="utf-8")
        assert extract_raw_file_metadata(plain) == {}

        # Incomplete frontmatter without closing ---
        unclosed = tmp_path / "unclosed.md"
        unclosed.write_text(
            "---\ntitle: Unclosed\nchannel: https://yt.com/@test\n", encoding="utf-8"
        )
        assert extract_raw_file_metadata(unclosed) == {}

        # Multiple --- horizontal dividers in body (kills rsplit or unsplit mutations)
        multi = tmp_path / "multi_delim.md"
        multi.write_text(
            '---\ntitle: "Quoted Title"\nchannel: http://youtube.com/@httpchannel\n---\nPart 1\n---\nPart 2\n---\nPart 3',
            encoding="utf-8",
        )
        meta_multi = extract_raw_file_metadata(multi)
        assert meta_multi["title"] == "Quoted Title"
        assert meta_multi["channel"] == "http://youtube.com/@httpchannel"

        # Colons in frontmatter value and single quotes
        colon_f = tmp_path / "colon_val.md"
        colon_f.write_text(
            "---\ntitle: 'Volume 1: The Historical Palimpsest: Section A'\nchannel_id: 'UCbare123'\n---\nBody",
            encoding="utf-8",
        )
        meta_colon = extract_raw_file_metadata(colon_f)
        assert meta_colon["title"] == "Volume 1: The Historical Palimpsest: Section A"
        assert meta_colon["channel"] == "https://www.youtube.com/channel/UCbare123"

        # Frontmatter with title only (no channel or channel_id)
        no_chan = tmp_path / "no_chan.md"
        no_chan.write_text("---\ntitle: Sole Title\n---\nBody", encoding="utf-8")
        meta_no_chan = extract_raw_file_metadata(no_chan)
        assert meta_no_chan["title"] == "Sole Title"
        assert "channel" not in meta_no_chan

    def test_batch_source_accumulator_deduplication(self) -> None:
        acc = _BatchSourceAccumulator()
        # Add with explicit vid
        acc.add_source(kind="file", target="/lake/explicit_vid.md", vid="exp_vid_1")
        assert acc.has_seen("exp_vid_1") is True
        assert acc.has_seen("non_existent") is False

        # Add URL matching video ID regex
        acc.add_source(kind="url", target="https://www.youtube.com/watch?v=vidRegex123")
        assert acc.has_seen("vidRegex123") is True

        # Add target without video regex (uses stem)
        acc.add_source(kind="file", target="/lake/transcripts/lecture_notes.md")
        assert acc.has_seen("lecture_notes") is True

    def test_scan_raw_lake_edge_cases(self, tmp_path: Path) -> None:
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=MagicMock(),
            settings=CresmoSettings(_env_file=None),
        )
        acc = _BatchSourceAccumulator()

        # Non-directory / invalid path inputs
        assert use_case._scan_raw_lake(None, scan_raw=True, acc=acc) == {}
        assert use_case._scan_raw_lake(tmp_path / "not_a_dir", scan_raw=True, acc=acc) == {}
        f = tmp_path / "file_not_dir.txt"
        f.write_text("hi", encoding="utf-8")
        assert use_case._scan_raw_lake(f, scan_raw=True, acc=acc) == {}

        # Directory with files
        raw_dir = tmp_path / "raw_lake_tests"
        raw_dir.mkdir()
        (raw_dir / "vid_with_front.md").write_text(
            "---\nvideo_id: explicit_vid_456\nchannel: https://youtube.com/@ChannelOne\n---\nBody",
            encoding="utf-8",
        )
        (raw_dir / "vid_without_front_id.md").write_text(
            "---\nchannel: https://youtube.com/@ChannelTwo\n---\nBody",
            encoding="utf-8",
        )
        (raw_dir / "vid_no_channel.md").write_text(
            "---\ntitle: No Channel\n---\nBody",
            encoding="utf-8",
        )

        # scan_raw = False: registers channels in dict, but does NOT add to acc.sources
        acc_no_scan = _BatchSourceAccumulator()
        chan_map = use_case._scan_raw_lake(raw_dir, scan_raw=False, acc=acc_no_scan)
        assert chan_map["explicit_vid_456"] == "https://youtube.com/@ChannelOne"
        assert chan_map["vid_with_front"] == "https://youtube.com/@ChannelOne"
        assert chan_map["vid_without_front_id"] == "https://youtube.com/@ChannelTwo"
        assert len(acc_no_scan.sources) == 0

        # scan_raw = True: adds to acc.sources and registers seen_vids
        acc_scan = _BatchSourceAccumulator()
        use_case._scan_raw_lake(raw_dir, scan_raw=True, acc=acc_scan)
        assert len(acc_scan.sources) == 3
        assert acc_scan.has_seen("vid_with_front") is True
        assert acc_scan.has_seen("explicit_vid_456") is True
        assert acc_scan.has_seen("vid_without_front_id") is True

        # Pre-seen file is skipped
        acc_pre = _BatchSourceAccumulator()
        acc_pre.seen_vids.add("explicit_vid_456")
        use_case._scan_raw_lake(raw_dir, scan_raw=True, acc=acc_pre)
        assert not any("vid_with_front" in s.target for s in acc_pre.sources)

    def test_classify_seeds_deduplication_and_routing(self, tmp_path: Path) -> None:
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=MagicMock(),
            settings=CresmoSettings(_env_file=None),
        )
        acc = _BatchSourceAccumulator()
        acc.seen_vids.add("already_seen_vid123")

        manifest = tmp_path / "test_seeds_playlist.txt"
        manifest.write_text(
            "https://www.youtube.com/@RawChan\n"  # already in local_channels
            "https://www.youtube.com/@NewChan\n"  # new channel feed
            "https://youtube.com/watch?v=already_seen_vid123\n"  # already seen -> skipped
            "https://youtube.com/watch?v=knownLocalVid\n"  # vid matches local_channels -> routes to channels_to_probe
            "https://youtube.com/watch?v=remoteUnknownVid\n"  # not in local -> remote_videos
            "https://some.domain.com/unparseable_url\n",  # no video ID regex -> still added as url source
            encoding="utf-8",
        )

        local_channels = {
            "vid1": "https://www.youtube.com/@RawChan",
            "vid2": "https://www.youtube.com/@RawChan",  # duplicate channel in local_channels
            "knownLocalVid": "https://www.youtube.com/@KnownLocalChan",
        }

        channels_to_probe, remote_videos, _probed_channels = use_case._classify_seeds(
            manifest, local_channels, acc
        )

        # @RawChan only probed once
        assert channels_to_probe.count("https://www.youtube.com/@RawChan") == 1
        assert "https://www.youtube.com/@NewChan" in channels_to_probe
        assert "https://www.youtube.com/@KnownLocalChan" in channels_to_probe
        assert "https://youtube.com/watch?v=remoteUnknownVid" in remote_videos
        assert "https://youtube.com/watch?v=knownLocalVid" not in remote_videos

        # Check accumulator sources
        targets = [s.target for s in acc.sources]
        assert "https://youtube.com/watch?v=already_seen_vid123" not in targets
        assert "https://youtube.com/watch?v=knownLocalVid" in targets
        assert "https://youtube.com/watch?v=remoteUnknownVid" in targets
        assert "https://some.domain.com/unparseable_url" in targets

    def test_probe_single_channel_feed_variations(self) -> None:
        mock_ingestion = MagicMock()
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        now = datetime.now(UTC)
        cutoff = now - timedelta(days=7)

        # Discovered items with various attributes
        item_fresh = MagicMock()
        item_fresh.published_at = now
        item_fresh.media_url = "https://yt.com/watch?v=fresh123"

        item_old = MagicMock()
        item_old.published_at = now - timedelta(days=14)
        item_old.media_url = "https://yt.com/watch?v=old123"

        item_none_pub = MagicMock()
        item_none_pub.published_at = None
        item_none_pub.media_url = "https://yt.com/watch?v=nonepub123"

        item_fallback_url = MagicMock(spec=["url"])
        item_fallback_url.url = "https://yt.com/watch?v=fallbackUrl123"

        item_empty_url = MagicMock()
        item_empty_url.published_at = now
        item_empty_url.media_url = ""
        item_empty_url.url = ""

        mock_ingestion.discover_channel_feed.return_value = [
            item_fresh,
            item_old,
            item_none_pub,
            item_fallback_url,
            item_empty_url,
        ]

        # Test bare URL format prepending https://
        urls = use_case._probe_single_channel_feed(
            chan_url="youtube.com/@barechannel",
            lookback_days=7,
            max_videos=25,
            cutoff=cutoff,
        )

        feed_q = mock_ingestion.discover_channel_feed.call_args[0][0]
        assert feed_q.channel_url == "https://youtube.com/@barechannel"
        assert feed_q.lookback_days == 7
        assert feed_q.max_videos == 25

        assert "https://yt.com/watch?v=fresh123" in urls
        assert "https://yt.com/watch?v=nonepub123" in urls
        assert "https://yt.com/watch?v=fallbackUrl123" in urls
        assert "https://yt.com/watch?v=old123" not in urls

    def test_execute_settings_fallbacks(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "data"
        raw_dir = data_dir / "raw"
        raw_dir.mkdir(parents=True)
        priority_dir = data_dir / "priority"
        priority_dir.mkdir(parents=True)
        (priority_dir / "prio_note.md").write_text("# Priority Doc", encoding="utf-8")

        prio_txt = data_dir / "playlist-priority.txt"
        prio_txt.write_text("https://yt.com/watch?v=fallbackPrio\n", encoding="utf-8")

        playlist_txt = data_dir / "playlist.txt"
        playlist_txt.write_text("https://yt.com/watch?v=fallbackMain\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = None
        mock_ingestion.discover_channel_feed.return_value = []

        settings = CresmoSettings(
            _env_file=None,
            data_dir=data_dir,
            channel_discovery_workers=2,
            days_lookback=10,
        )

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=settings,
        )

        # Execute with completely empty BatchDiscoveryQuery (defaults trigger all settings fallbacks)
        sources = use_case.execute(BatchDiscoveryQuery())
        targets = [s.target for s in sources]

        assert any("prio_note.md" in t for t in targets)
        assert "https://yt.com/watch?v=fallbackPrio" in targets
        assert "https://yt.com/watch?v=fallbackMain" in targets

    def test_resolve_remote_channels_and_probe_feeds_worker_bounds(self) -> None:
        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://youtube.com/@ResolvedChan"
        )
        mock_ingestion.discover_channel_feed.return_value = [
            DiscoveredMediaItem(
                content_id=ContentId("disc_item_1"),
                title="Discovered 1",
                published_at=datetime.now(UTC),
                media_url="https://youtube.com/watch?v=disc_item_1",
                channel_name="ResolvedChan",
            ),
            DiscoveredMediaItem(
                content_id=ContentId("disc_item_2"),
                title="Discovered 2",
                published_at=datetime.now(UTC),
                media_url="https://nonstandard.url/disc_no_id",
                channel_name="ResolvedChan",
            ),
        ]

        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
        )

        # Test empty videos list returns immediately
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        use_case._resolve_remote_channels(
            [], workers=4, probed_channels=probed_channels, channels_to_probe=channels_to_probe
        )
        assert channels_to_probe == []

        # Test resolve with 2 videos
        use_case._resolve_remote_channels(
            ["https://yt.com/watch?v=v1", "https://yt.com/watch?v=v2"],
            workers=4,
            probed_channels=probed_channels,
            channels_to_probe=channels_to_probe,
        )
        assert channels_to_probe == ["https://youtube.com/@ResolvedChan"]

        # Test probe feeds with empty channels returns immediately
        acc = _BatchSourceAccumulator()
        use_case._probe_channel_feeds([], lookback_days=7, max_videos=10, workers=2, acc=acc)
        assert len(acc.sources) == 0

        # Test probe feeds populates acc and handles items without standard video ID
        use_case._probe_channel_feeds(
            ["https://youtube.com/@ResolvedChan"],
            lookback_days=7,
            max_videos=10,
            workers=2,
            acc=acc,
        )
        assert len(acc.sources) == 2
        assert acc.has_seen("disc_item_1") is True
        assert acc.has_seen("https://nonstandard.url/disc_no_id") is True

    def test_two_stage_channel_discovery_with_uploads_playlist_and_lake_filter(
        self, tmp_path: Path
    ) -> None:
        """Verify two-stage channel discovery: A (unify channels) and B (filter raw lake videos)."""
        # A1: Priority folder
        pri_dir = tmp_path / "priority_folder"
        pri_dir.mkdir()
        (pri_dir / "pri_note.md").write_text(
            "---\ntitle: Priority Note\nchannel_id: UCPriority12345678901234\n---\nBody",
            encoding="utf-8",
        )

        # A2: Local raw lake
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        (raw_dir / "lake_vid1.md").write_text(
            "---\nvideo_id: lake_vid1\nchannel_id: UCLakeChan12345678901234\n---\nBody",
            encoding="utf-8",
        )

        # A3: Seed playlist with a new seed video
        playlist_file = tmp_path / "playlist.txt"
        playlist_file.write_text("https://www.youtube.com/watch?v=seed_new_video\n", encoding="utf-8")

        mock_ingestion = MagicMock()
        mock_ingestion.extract_channel_url_from_video.return_value = (
            "https://www.youtube.com/playlist?list=UUSeedChan12345678901234"
        )

        # In Stage B, channel feed returns 2 videos:
        # - "lake_vid1" (already in raw lake -> MUST BE SKIPPED)
        # - "brand_new_vid" (not in raw lake -> MUST BE ADDED)
        already_in_lake_item = _create_mock_media_item(
            content_id_str="lake_vid1",
            media_url="https://www.youtube.com/watch?v=lake_vid1",
            title="Already in Lake",
        )
        new_discovered_item = _create_mock_media_item(
            content_id_str="brand_new_vid",
            media_url="https://www.youtube.com/watch?v=brand_new_vid",
            title="Brand New Upload",
        )
        mock_ingestion.discover_channel_feed.return_value = [already_in_lake_item, new_discovered_item]

        notifications: list[str] = []
        use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=mock_ingestion,
            settings=CresmoSettings(_env_file=None),
            progress_callback=notifications.append,
        )

        query = BatchDiscoveryQuery(
            manifest_path=playlist_file,
            raw_dir=raw_dir,
            priority_texts_dir=pri_dir,
            playlist_priority_path=tmp_path / "empty_pri_urls.txt",
            scan_raw=False,  # Don't add raw files to sources, only scan for lake filtering
            enable_channel_crawler=True,
            discovery_workers=2,
            lookback_days=365,
        )

        sources = use_case.execute(query)

        # Targets in sources must include:
        # 1. pri_note.md (file)
        # 2. seed_new_video (url)
        # 3. brand_new_vid (url from Stage B)
        # MUST NOT include lake_vid1 as URL because it was already in the raw lake!
        targets = [s.target for s in sources]
        assert str((pri_dir / "pri_note.md").resolve()) in targets
        assert "https://www.youtube.com/watch?v=seed_new_video" in targets
        assert "https://www.youtube.com/watch?v=brand_new_vid" in targets
        assert "https://www.youtube.com/watch?v=lake_vid1" not in targets

        # Check that discover_channel_feed was called for channels
        assert mock_ingestion.discover_channel_feed.called

        # Check progress notifications contain Stage A and Stage B logs
        combined_notifications = "".join(notifications)
        assert "Stage A complete" in combined_notifications
        assert "Stage B:" in combined_notifications
        assert "Stage B complete" in combined_notifications
