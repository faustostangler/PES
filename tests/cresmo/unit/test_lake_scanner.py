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
        criteria = SyncFilterCriteria(channels=("pes_channel",), categories=("volatile",))
        # Matching channel name and classified volatile category
        assert _matches_channel_and_category(criteria, "pes_channel") is True
        assert _matches_channel_and_category(criteria, "other_channel") is False

    def test_matches_video_entry_empty_criteria(self) -> None:
        empty = SyncFilterCriteria()
        cid = ContentId("dQw4w9WgXcQ")
        assert _matches_video_entry(empty, cid, "https://youtube.com/watch?v=dQw4w9WgXcQ", "pes_chan") is True

    def test_matches_video_entry_video_ids_filter(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",))
        cid_match = ContentId("dQw4w9WgXcQ")
        cid_other = ContentId("oHg5SJYRHA0")

        assert _matches_video_entry(criteria, cid_match, "https://youtube.com/watch?v=dQw4w9WgXcQ", None) is True
        assert _matches_video_entry(criteria, cid_other, "https://youtube.com/watch?v=oHg5SJYRHA0", None) is False

    def test_matches_video_entry_channels_and_categories_filter(self) -> None:
        criteria = SyncFilterCriteria(channels=("target_chan",), categories=("volatile",))
        cid = ContentId("dQw4w9WgXcQ")
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

        # No local channel provided: fails channel filter
        assert _matches_video_entry(criteria, cid, url, None) is False
        # Wrong local channel: fails channel filter
        assert _matches_video_entry(criteria, cid, url, "wrong_chan") is False
        # Correct local channel
        assert _matches_video_entry(criteria, cid, url, "target_chan") is True

    def test_is_unresolved_video_candidate(self) -> None:
        empty = SyncFilterCriteria()
        cid = ContentId("dQw4w9WgXcQ")
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert _is_unresolved_video_candidate(empty, cid, url) is True

        # Video IDs only criteria matches
        vid_only = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",))
        assert _is_unresolved_video_candidate(vid_only, cid, url) is True
        assert _is_unresolved_video_candidate(vid_only, ContentId("oHg5SJYRHA0"), "https://youtube.com/watch?v=oHg5SJYRHA0") is False

        # If channels or categories criteria are set, unresolved candidate must be False
        with_chan = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",), channels=("some_chan",))
        assert _is_unresolved_video_candidate(with_chan, cid, url) is False

        with_cat = SyncFilterCriteria(video_ids=("dQw4w9WgXcQ",), categories=("some_cat",))
        assert _is_unresolved_video_candidate(with_cat, cid, url) is False


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
        channels = LakeScannerService.collect_priority_texts(priority_dir, acc, filter_criteria=criteria)

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
