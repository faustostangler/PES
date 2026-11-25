"""Unit tests for LakeScannerService and seed classification.

Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

from pathlib import Path

from cresmo.application.use_cases.discovery.lake_scanner import (
    LakeScannerService,
    _is_unresolved_video_candidate,
    _matches_channel_and_category,
    _matches_video_entry,
)
from cresmo.application.use_cases.discovery.models import (
    _BatchSourceAccumulator,
)
from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    SyncFilterCriteria,
)


class TestLakeScannerHelpers:
    def test_matches_channel_and_category_empty_criteria(self) -> None:
        empty = SyncFilterCriteria()
        assert _matches_channel_and_category(empty, "https://youtube.com/@pes_channel") is True

    def test_matches_channel_and_category_with_matching_and_unmatching(self) -> None:
        from unittest.mock import MagicMock

        mock_taxonomy = MagicMock()
        mock_taxonomy.classify.return_value = ("science", "volatile")
        criteria = SyncFilterCriteria(channels=("pes_channel",), categories=("volatile",))
        # Matching channel name and classified volatile category
        assert (
            _matches_channel_and_category(criteria, "pes_channel", taxonomy_port=mock_taxonomy)
            is True
        )
        assert (
            _matches_channel_and_category(criteria, "other_channel", taxonomy_port=mock_taxonomy)
            is False
        )

    def test_matches_video_entry_empty_criteria(self) -> None:
        empty = SyncFilterCriteria()
        cid = ContentId("dQw4w9WgXcQ")
        assert (
            _matches_video_entry(empty, cid, "https://youtube.com/watch?v=dQw4w9WgXcQ", "pes_chan")
            is True
        )

    def test_matches_video_entry_video_ids_filter(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",))
        cid_match = ContentId("dQw4w9WgXcQ")
        cid_other = ContentId("oHg5SJYRHA0")

        assert (
            _matches_video_entry(
                criteria, cid_match, "https://youtube.com/watch?v=dQw4w9WgXcQ", None
            )
            is True
        )
        assert (
            _matches_video_entry(
                criteria, cid_other, "https://youtube.com/watch?v=oHg5SJYRHA0", None
            )
            is False
        )

    def test_matches_video_entry_channels_and_categories_filter(self) -> None:
        from unittest.mock import MagicMock

        mock_taxonomy = MagicMock()
        mock_taxonomy.classify.return_value = ("science", "volatile")
        criteria = SyncFilterCriteria(channels=("target_chan",), categories=("volatile",))
        cid = ContentId("dQw4w9WgXcQ")
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

        # No local channel provided: fails channel filter
        assert _matches_video_entry(criteria, cid, url, None, taxonomy_port=mock_taxonomy) is False
        # Wrong local channel: fails channel filter
        assert (
            _matches_video_entry(criteria, cid, url, "wrong_chan", taxonomy_port=mock_taxonomy)
            is False
        )
        # Correct local channel
        assert (
            _matches_video_entry(criteria, cid, url, "target_chan", taxonomy_port=mock_taxonomy)
            is True
        )

    def test_is_unresolved_video_candidate(self) -> None:
        empty = SyncFilterCriteria()
        cid = ContentId("dQw4w9WgXcQ")
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert _is_unresolved_video_candidate(empty, cid, url) is True

        # Video IDs only criteria matches
        vid_only = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",))
        assert _is_unresolved_video_candidate(vid_only, cid, url) is True
        assert (
            _is_unresolved_video_candidate(
                vid_only, ContentId("oHg5SJYRHA0"), "https://youtube.com/watch?v=oHg5SJYRHA0"
            )
            is False
        )

        # If channels or categories criteria are set, unresolved candidate must be False
        with_chan = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",), channels=("some_chan",))
        assert _is_unresolved_video_candidate(with_chan, cid, url) is False

        with_cat = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",), categories=("some_cat",))
        assert _is_unresolved_video_candidate(with_cat, cid, url) is False

        # Cross-host cid vs url_fallback coverage for both helpers
        cross_host = SyncFilterCriteria(video_ids=("https://youtu.be/dQw4w9WgXcQ",))
        assert _matches_video_entry(cross_host, cid, url, None) is True
        assert _is_unresolved_video_candidate(cross_host, cid, url) is True

        list_only = SyncFilterCriteria(video_ids=("list=PL888",))
        url_with_list = "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL888"
        cid_other = ContentId("oHg5SJYRHA0")
        assert _matches_video_entry(list_only, cid_other, url_with_list, None) is True
        assert _is_unresolved_video_candidate(list_only, cid_other, url_with_list) is True


class TestLakeScannerService:
    def test_collect_priority_texts(self, tmp_path: Path) -> None:
        priority_dir = tmp_path / "priority_texts"
        priority_dir.mkdir()

        # Valid markdown transcript file with frontmatter
        md1 = priority_dir / "dQw4w9WgXcQ.md"
        md1.write_text(
            "---\nvideo_id: dQw4w9WgXcQ\nchannel: https://www.youtube.com/@philosophy_chan\n---\nTranscript text content here.",
            encoding="utf-8",
        )

        # Non-transcript file (ignored)
        ignored = priority_dir / "notes.log"
        ignored.write_text("random log", encoding="utf-8")

        acc = _BatchSourceAccumulator()
        channels = LakeScannerService.collect_priority_texts(priority_dir, acc)

        assert len(acc.sources) == 1
        assert acc.sources[0].kind is SourceModality.FILE
        assert acc.sources[0].target == str(md1.absolute())
        assert len(channels) == 1
        assert "uploads" in channels[0] or "philosophy_chan" in channels[0]

    def test_collect_priority_texts_with_filter_criteria(self, tmp_path: Path) -> None:
        priority_dir = tmp_path / "priority_texts"
        priority_dir.mkdir()

        md_matched = priority_dir / "match_vid.md"
        md_matched.write_text(
            "---\nvideo_id: match_vid\nchannel: allowed_chan\n---\nContent",
            encoding="utf-8",
        )

        md_unmatched = priority_dir / "other_vid.md"
        md_unmatched.write_text(
            "---\nvideo_id: other_vid\nchannel: rejected_chan\n---\nContent",
            encoding="utf-8",
        )

        criteria = SyncFilterCriteria(channels=("allowed_chan",))
        acc = _BatchSourceAccumulator()
        channels = LakeScannerService.collect_priority_texts(
            priority_dir, acc, filter_criteria=criteria
        )

        assert len(acc.sources) == 1
        assert acc.sources[0].target == str(md_matched.absolute())
        assert len(channels) == 1

    def test_collect_priority_urls(self, tmp_path: Path) -> None:
        priority_file = tmp_path / "priority_urls.txt"
        priority_file.write_text(
            "https://www.youtube.com/@test_channel\n"
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "https://www.youtube.com/watch?v=unresolved123\n",
            encoding="utf-8",
        )

        local_map = {"dQw4w9WgXcQ": "https://www.youtube.com/@test_channel"}
        acc = _BatchSourceAccumulator()

        channels, unresolved = LakeScannerService.collect_priority_urls(
            priority_file,
            local_video_channel_map=local_map,
            acc=acc,
        )

        assert len(channels) >= 1
        assert "unresolved123" in unresolved[0]
        assert len(acc.sources) == 2
        assert any(s.target == "https://www.youtube.com/watch?v=dQw4w9WgXcQ" for s in acc.sources)

    def test_scan_raw_lake_and_deduplication(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw_lake"
        raw_dir.mkdir()

        f1 = raw_dir / "video_one.md"
        f1.write_text(
            "---\nvideo_id: video_one\nchannel: https://www.youtube.com/@science_channel\n---\nTranscript 1",
            encoding="utf-8",
        )

        f2 = raw_dir / "video_two.md"
        f2.write_text(
            "---\nvideo_id: video_two\nchannel: https://www.youtube.com/@math_channel\n---\nTranscript 2",
            encoding="utf-8",
        )

        acc = _BatchSourceAccumulator()
        mapping = LakeScannerService.scan_raw_lake(
            raw_dir=raw_dir,
            scan_raw=True,
            acc=acc,
        )

        assert mapping["video_one"] == "https://www.youtube.com/@science_channel"
        assert mapping["video_two"] == "https://www.youtube.com/@math_channel"
        assert len(acc.sources) == 2

        # Second scan does not re-add already seen sources
        LakeScannerService.scan_raw_lake(
            raw_dir=raw_dir,
            scan_raw=True,
            acc=acc,
        )
        assert len(acc.sources) == 2

    def test_scan_raw_lake_with_criteria(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw_lake"
        raw_dir.mkdir()

        f1 = raw_dir / "allowed.md"
        f1.write_text(
            "---\nvideo_id: allowed\nchannel: allowed_channel\n---\nTranscript",
            encoding="utf-8",
        )

        f2 = raw_dir / "blocked.md"
        f2.write_text(
            "---\nvideo_id: blocked\nchannel: blocked_channel\n---\nTranscript",
            encoding="utf-8",
        )

        criteria = SyncFilterCriteria(channels=("allowed_channel",))
        acc = _BatchSourceAccumulator()
        mapping = LakeScannerService.scan_raw_lake(
            raw_dir=raw_dir,
            scan_raw=True,
            acc=acc,
            filter_criteria=criteria,
        )

        assert len(acc.sources) == 1
        assert "allowed" in acc.sources[0].target
        assert mapping["allowed"] == "allowed_channel"

    def test_classify_seeds_alphabetical_order_and_categorization(self, tmp_path: Path) -> None:
        seeds_file = tmp_path / "seeds.txt"
        seeds_file.write_text(
            "https://www.youtube.com/@zebra_channel\n"
            "https://www.youtube.com/@alpha_channel\n"
            "https://www.youtube.com/watch?v=remote_video_1\n",
            encoding="utf-8",
        )

        local_map = {
            "mapped_vid": "https://www.youtube.com/@beta_channel",
        }

        acc = _BatchSourceAccumulator()
        channels, remote_videos, _probed = LakeScannerService.classify_seeds(
            playlist_path=seeds_file,
            local_video_channel_map=local_map,
            acc=acc,
        )

        # ADR-012 alphabetical sort verification
        assert channels == sorted(channels, key=lambda c: c.lower())
        assert any("alpha_channel" in c for c in channels)
        assert any("beta_channel" in c for c in channels)
        assert any("zebra_channel" in c for c in channels)
        assert len(remote_videos) == 1
        assert "remote_video_1" in remote_videos[0]

    def test_collect_priority_texts_taxonomy_video_id_and_stem_fallback(
        self, tmp_path: Path
    ) -> None:
        from unittest.mock import MagicMock

        priority_dir = tmp_path / "priority_texts"
        priority_dir.mkdir()

        # File with frontmatter video_id != stem + channel classified by taxonomy
        f_custom = priority_dir / "stem_custom.md"
        f_custom.write_text(
            "---\nvideo_id: front_vid_99\nchannel: kept_chan\n---\nBody",
            encoding="utf-8",
        )
        # File without video_id frontmatter (falls back to stem)
        f_stem = priority_dir / "stem_only_77.md"
        f_stem.write_text(
            "---\nchannel: kept_chan\n---\nBody",
            encoding="utf-8",
        )
        # File rejected by category taxonomy
        f_other_cat = priority_dir / "other_cat.md"
        f_other_cat.write_text(
            "---\nvideo_id: front_vid_99\nchannel: volatile_chan\n---\nBody",
            encoding="utf-8",
        )

        taxonomy = MagicMock()
        taxonomy.classify.side_effect = lambda target: (
            ("science", "perennial")
            if "kept_chan" in str(target)
            else ("news", "volatile")
        )

        acc1 = _BatchSourceAccumulator()
        chans1 = LakeScannerService.collect_priority_texts(
            priority_dir,
            acc1,
            filter_criteria=SyncFilterCriteria(
                video_ids=("front_vid_99",),
                categories=("perennial",),
            ),
            taxonomy_port=taxonomy,
        )
        assert [s.target for s in acc1.sources] == [str(f_custom.absolute())]
        assert len(chans1) == 1
        assert "kept_chan" in chans1[0]

        acc2 = _BatchSourceAccumulator()
        LakeScannerService.collect_priority_texts(
            priority_dir,
            acc2,
            filter_criteria=SyncFilterCriteria(video_ids=("stem_only_77",)),
            taxonomy_port=taxonomy,
        )
        assert [s.target for s in acc2.sources] == [str(f_stem.absolute())]

    def test_collect_priority_urls_dedup_criteria_taxonomy_and_unresolved(
        self, tmp_path: Path
    ) -> None:
        from unittest.mock import MagicMock

        priority_file = tmp_path / "priority_urls.txt"
        priority_file.write_text(
            "https://www.youtube.com/@kept_chan\n"
            "https://www.youtube.com/@kept_chan\n"
            "https://www.youtube.com/@dropped_chan\n"
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL777\n"
            "https://www.youtube.com/watch?v=seenVid0001\n"
            "https://www.youtube.com/watch?v=unres000001\n"
            "https://www.youtube.com/watch?v=unres000001\n"
            "https://www.youtube.com/watch?v=unres000002&list=PL777\n",
            encoding="utf-8",
        )
        local_map = {
            "dQw4w9WgXcQ": "https://www.youtube.com/@kept_chan",
            "oHg5SJYRHA0": "https://www.youtube.com/@kept_chan",
            "seenVid0001": "https://www.youtube.com/@kept_chan",
        }
        taxonomy = MagicMock()
        taxonomy.classify.side_effect = lambda target: (
            ("science", "perennial")
            if "kept_chan" in str(target)
            else ("news", "volatile")
        )

        # 1. Cross-host video_id + category + taxonomy filter + seen video dedup
        acc = _BatchSourceAccumulator()
        acc.mark_seen("seenVid0001")
        criteria = SyncFilterCriteria(
            channels=("kept_chan",),
            categories=("perennial",),
            video_ids=("https://youtu.be/dQw4w9WgXcQ", "list=PL777", "seenVid0001"),
        )
        chans, unres = LakeScannerService.collect_priority_urls(
            priority_file,
            local_video_channel_map=local_map,
            acc=acc,
            filter_criteria=criteria,
            taxonomy_port=taxonomy,
        )
        assert chans == ["https://www.youtube.com/@kept_chan/videos"]
        assert None not in chans
        assert len(acc.sources) == 2
        assert {s.content_id for s in acc.sources} == {
            ContentId("dQw4w9WgXcQ"),
            ContentId("oHg5SJYRHA0"),
        }
        assert unres == []

        # 2. Unresolved videos with video_ids-only criteria deduplicate and respect cross-host/list
        acc_unres = _BatchSourceAccumulator()
        _, unres_only = LakeScannerService.collect_priority_urls(
            priority_file,
            local_video_channel_map={},
            acc=acc_unres,
            filter_criteria=SyncFilterCriteria(
                video_ids=("https://youtu.be/unres000001", "list=PL777")
            ),
        )
        assert unres_only == [
            "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL777",
            "https://www.youtube.com/watch?v=unres000001",
            "https://www.youtube.com/watch?v=unres000002&list=PL777",
        ]

        # 3. Feed URL taxonomy filtering without local_map, and local_chan taxonomy filtering without feed URL
        feed_only = tmp_path / "feed_only.txt"
        feed_only.write_text(
            "https://www.youtube.com/@kept_chan\n"
            "https://www.youtube.com/@kept_chan\n"
            "https://www.youtube.com/@dropped_chan\n",
            encoding="utf-8",
        )
        chans_feed_only, _ = LakeScannerService.collect_priority_urls(
            feed_only,
            local_video_channel_map={},
            acc=_BatchSourceAccumulator(),
            filter_criteria=SyncFilterCriteria(categories=("perennial",)),
            taxonomy_port=taxonomy,
        )
        assert chans_feed_only == ["https://www.youtube.com/@kept_chan/videos"]

        vid_only = tmp_path / "vid_only.txt"
        vid_only.write_text(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "https://www.youtube.com/watch?v=dropVid0001\n",
            encoding="utf-8",
        )
        chans_local_only, _ = LakeScannerService.collect_priority_urls(
            vid_only,
            local_video_channel_map={
                "dQw4w9WgXcQ": "https://www.youtube.com/@kept_chan",
                "dropVid0001": "https://www.youtube.com/@dropped_chan",
            },
            acc=_BatchSourceAccumulator(),
            filter_criteria=SyncFilterCriteria(categories=("perennial",)),
            taxonomy_port=taxonomy,
        )
        assert chans_local_only == ["https://www.youtube.com/@kept_chan/videos"]

    def test_scan_raw_lake_nested_same_name_stem_marking_and_video_id_filter(
        self, tmp_path: Path
    ) -> None:
        raw_dir = tmp_path / "raw_lake"
        same_name_subdir = raw_dir / "raw_lake"
        same_name_subdir.mkdir(parents=True)
        (same_name_subdir / "nested_vid.md").write_text("Body", encoding="utf-8")

        acc_no_fm = _BatchSourceAccumulator()
        mapping_no_fm = LakeScannerService.scan_raw_lake(
            raw_dir=raw_dir,
            scan_raw=True,
            acc=acc_no_fm,
            extract_frontmatter=False,
        )
        # parent_dir != raw_dir but parent_dir.name == raw_dir.name -> no channel inferred
        assert mapping_no_fm == {}

        # Frontmatter video_id != stem: stem must still be marked seen, no None in seen_vids,
        # and video_ids criteria filters on canonical_vid
        raw_fm = tmp_path / "raw_fm"
        raw_fm.mkdir()
        (raw_fm / "local_stem_alpha.md").write_text(
            "---\nvideo_id: canonical_alpha\nchannel: chan_a\n---\nBody",
            encoding="utf-8",
        )
        (raw_fm / "local_stem_beta.md").write_text(
            "---\nvideo_id: canonical_beta\nchannel: chan_b\n---\nBody",
            encoding="utf-8",
        )
        acc_fm = _BatchSourceAccumulator()
        LakeScannerService.scan_raw_lake(
            raw_dir=raw_fm,
            scan_raw=True,
            acc=acc_fm,
            filter_criteria=SyncFilterCriteria(video_ids=("canonical_alpha",)),
        )
        assert [s.target for s in acc_fm.sources] == [
            str((raw_fm / "local_stem_alpha.md").absolute())
        ]
        assert acc_fm.has_seen("local_stem_alpha") is True
        assert acc_fm.has_seen("local_stem_beta") is True
        assert acc_fm.has_seen("canonical_beta") is True
        assert None not in acc_fm.seen_vids

    def test_classify_seeds_criteria_taxonomy_dedup_and_case_insensitive_sort(
        self, tmp_path: Path
    ) -> None:
        from unittest.mock import MagicMock

        seeds_file = tmp_path / "seeds.txt"
        seeds_file.write_text(
            "https://www.youtube.com/@alpha\n"
            "https://www.youtube.com/@alpha\n"
            "https://www.youtube.com/@_under\n"
            "https://www.youtube.com/@dropped_feed\n"
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL777\n"
            "https://www.youtube.com/watch?v=seenVid0001\n"
            "https://www.youtube.com/watch?v=unres000001\n"
            "https://www.youtube.com/watch?v=unres000001\n",
            encoding="utf-8",
        )
        local_map = {
            "dQw4w9WgXcQ": "https://www.youtube.com/@alpha",
            "oHg5SJYRHA0": "https://www.youtube.com/@dropped_local",
            "seenVid0001": "https://www.youtube.com/@alpha",
        }
        taxonomy = MagicMock()
        taxonomy.classify.side_effect = lambda target: (
            ("science", "perennial")
            if ("alpha" in str(target) or "_under" in str(target) or "Zebra" in str(target))
            else ("news", "volatile")
        )

        # 1. Mixed-case + underscore sorting (lambda c: c.lower() puts _under, alpha, Zebra;
        # key=None puts Zebra before _under and alpha!)
        acc_sort = _BatchSourceAccumulator()
        chans_sort, _, probed_sort = LakeScannerService.classify_seeds(
            playlist_path=seeds_file,
            local_video_channel_map={"x": "https://www.youtube.com/@Zebra"},
            acc=acc_sort,
            filter_criteria=SyncFilterCriteria(categories=("perennial",)),
            taxonomy_port=taxonomy,
        )
        assert chans_sort == [
            "https://www.youtube.com/@_under",
            "https://www.youtube.com/@alpha",
            "https://www.youtube.com/@Zebra",
        ]
        assert None not in probed_sort
        assert None not in chans_sort

        # Local-only channel map with empty playlist verifies Loop 1 taxonomy_port forwarding
        empty_seeds = tmp_path / "empty_seeds.txt"
        empty_seeds.write_text("", encoding="utf-8")
        chans_local_map, _, _ = LakeScannerService.classify_seeds(
            playlist_path=empty_seeds,
            local_video_channel_map={
                "v1": "https://www.youtube.com/@alpha",
                "v2": "https://www.youtube.com/@dropped_local",
            },
            acc=_BatchSourceAccumulator(),
            filter_criteria=SyncFilterCriteria(categories=("perennial",)),
            taxonomy_port=taxonomy,
        )
        assert chans_local_map == ["https://www.youtube.com/@alpha"]

        # 2. Combined channel + category + cross-host video_id filtering with local_chan
        acc_filt = _BatchSourceAccumulator()
        acc_filt.mark_seen("seenVid0001")
        chans_filt, remote_filt, _ = LakeScannerService.classify_seeds(
            playlist_path=seeds_file,
            local_video_channel_map=local_map,
            acc=acc_filt,
            filter_criteria=SyncFilterCriteria(
                channels=("alpha", "dropped_local"),
                categories=("perennial",),
                video_ids=("https://youtu.be/dQw4w9WgXcQ", "list=PL777", "seenVid0001"),
            ),
            taxonomy_port=taxonomy,
        )
        assert chans_filt == ["https://www.youtube.com/@alpha"]
        assert len(acc_filt.sources) == 1
        assert acc_filt.sources[0].content_id == ContentId("dQw4w9WgXcQ")
        assert remote_filt == []

        # 3. Unresolved remote_videos deduplication and video_ids-only filtering
        acc_rem = _BatchSourceAccumulator()
        _, remote_only, _ = LakeScannerService.classify_seeds(
            playlist_path=seeds_file,
            local_video_channel_map={},
            acc=acc_rem,
            filter_criteria=SyncFilterCriteria(
                video_ids=("https://youtu.be/unres000001", "list=PL777")
            ),
        )
        assert remote_only == [
            "https://www.youtube.com/watch?v=oHg5SJYRHA0&list=PL777",
            "https://www.youtube.com/watch?v=unres000001",
        ]
        assert len(acc_rem.sources) == 2
