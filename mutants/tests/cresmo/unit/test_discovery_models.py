"""Unit tests for batch source discovery models, accumulators, and deduplication.

Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
Conforms to:
- ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
- ADR-012: Multi-Criteria Filtering & Alphabetical Feed Ordering
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cresmo.application.use_cases.discovery.models import (
    BatchDiscoveryQuery,
    BatchSource,
    _BatchSourceAccumulator,
    _is_already_seen,
    _record_seen_identifiers,
    _resolve_content_id,
)
from cresmo.domain.value_objects import (
    ContentId,
    SourceModality,
    SyncFilterCriteria,
)


class TestBatchSource:
    def test_instantiate_with_modality_enum(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        bs = BatchSource(kind=SourceModality.FILE, target="/path/to/transcript.md", content_id=cid)
        assert bs.kind is SourceModality.FILE
        assert bs.target == "/path/to/transcript.md"
        assert bs.content_id == cid
        assert bs.vid == "dQw4w9WgXcQ"
        assert bs.display_name == "transcript.md"

    def test_instantiate_with_string_modality_auto_converts(self) -> None:
        bs_file = BatchSource(kind="file", target="/path/to/video.mp4")  # type: ignore[arg-type]
        assert bs_file.kind is SourceModality.FILE

        bs_url = BatchSource(kind="url", target="https://youtube.com/watch?v=dQw4w9WgXcQ")  # type: ignore[arg-type]
        assert bs_url.kind is SourceModality.URL
        assert bs_url.display_name == "https://youtube.com/watch?v=dQw4w9WgXcQ"

    def test_invalid_modality_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid BatchSource modality"):
            BatchSource(kind="invalid_kind", target="/path/to/file")  # type: ignore[arg-type]

    def test_instantiate_with_string_content_id_auto_converts(self) -> None:
        bs = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dQw4w9WgXcQ", content_id="dQw4w9WgXcQ")  # type: ignore[arg-type]
        assert isinstance(bs.content_id, ContentId)
        assert bs.content_id.value == "dQw4w9WgXcQ"
        assert bs.vid == "dQw4w9WgXcQ"

    def test_vid_returns_none_when_content_id_none(self) -> None:
        bs = BatchSource(kind=SourceModality.FILE, target="/path/to/file.txt")
        assert bs.content_id is None
        assert bs.vid is None


class TestBatchDiscoveryQuery:
    def test_default_filter_criteria_instantiated(self) -> None:
        query = BatchDiscoveryQuery()
        assert query.filter_criteria is not None
        assert isinstance(query.filter_criteria, SyncFilterCriteria)
        assert query.scan_raw is True
        assert query.channel_max_videos == 50
        assert query.enable_channel_crawler is True

    def test_explicit_filter_criteria_preserved(self) -> None:
        criteria = SyncFilterCriteria(channels=("pes_channel",), categories=("philosophy",))
        query = BatchDiscoveryQuery(filter_criteria=criteria)
        assert query.filter_criteria == criteria


class TestResolveContentIdHelper:
    def test_explicit_content_id_returned_directly(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        assert _resolve_content_id("some_target", cid) == cid

    def test_explicit_raw_id_string_resolved(self) -> None:
        res = _resolve_content_id("target", "dQw4w9WgXcQ")
        assert res == ContentId("dQw4w9WgXcQ")

    def test_target_url_resolved(self) -> None:
        res = _resolve_content_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ", None)
        assert res == ContentId("dQw4w9WgXcQ")

    def test_target_filename_stem_resolved(self) -> None:
        res = _resolve_content_id("/data/vault/dQw4w9WgXcQ.md", None)
        assert res == ContentId("dQw4w9WgXcQ")

    def test_unresolvable_target_returns_none(self) -> None:
        res = _resolve_content_id("", None)
        assert res is None


class TestIsAlreadySeenHelper:
    def test_dedup_token_in_seen(self) -> None:
        seen = {"token_1"}
        assert _is_already_seen(seen, "token_1", None, None) is True
        assert _is_already_seen(seen, "token_2", None, None) is False

    def test_resolved_id_in_seen(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        seen = {cid}
        assert _is_already_seen(seen, "other", cid, None) is True

    def test_raw_id_in_seen(self) -> None:
        seen = {"raw_token"}
        assert _is_already_seen(seen, "other", None, "raw_token") is True


class TestRecordSeenIdentifiersHelper:
    def test_records_all_variants(self) -> None:
        seen: set[ContentId | str] = set()
        cid = ContentId("dQw4w9WgXcQ")
        _record_seen_identifiers(
            seen_vids=seen,
            dedup_token="dedup_token_1",
            resolved_id=cid,
            raw_id="raw_id_1",
            target="/path/to/my_stem.txt",
        )
        assert "dedup_token_1" in seen
        assert "raw_id_1" in seen
        assert cid in seen
        assert cid.value in seen
        assert "my_stem" in seen

    def test_records_with_content_id_raw_and_empty_stem(self) -> None:
        seen: set[ContentId | str] = set()
        cid_raw = ContentId("dQw4w9WgXcQ")
        _record_seen_identifiers(
            seen_vids=seen,
            dedup_token="token_2",
            resolved_id=None,
            raw_id=cid_raw,
            target="",
        )
        assert "token_2" in seen
        assert cid_raw.value in seen
        assert "" not in seen


class TestBatchSourceAccumulator:
    def test_add_source_deduplicates(self) -> None:
        added: list[BatchSource] = []
        acc = _BatchSourceAccumulator(on_source_added=added.append)

        src1 = acc.add_source(
            kind=SourceModality.FILE,
            target="/path/to/dQw4w9WgXcQ.md",
        )
        assert src1 is not None
        assert len(acc.sources) == 1
        assert len(added) == 1
        assert acc.sources[0] == src1

        # Duplicate attempt with same video ID target
        src2 = acc.add_source(
            kind=SourceModality.URL,
            target="https://youtube.com/watch?v=dQw4w9WgXcQ",
        )
        assert src2 is None
        assert len(acc.sources) == 1
        assert len(added) == 1

    def test_add_source_with_vid_and_raw_fallback(self) -> None:
        acc = _BatchSourceAccumulator(on_source_added=None)
        vid = ContentId("dQw4w9WgXcQ")
        src = acc.add_source(
            kind=SourceModality.FILE,
            target="/unknown/path/unparseable",
            vid=vid,
        )
        assert src is not None
        assert src.content_id == vid

        # Target with no id resolved and no raw_id: dedup uses stem
        acc2 = _BatchSourceAccumulator()
        src2 = acc2.add_source(
            kind=SourceModality.FILE,
            target="/some/random/unresolvable_stem",
        )
        assert src2 is not None
        assert "unresolvable_stem" in acc2.seen_vids
        # Second attempt with same stem is duplicate
        dup = acc2.add_source(
            kind=SourceModality.FILE,
            target="/another/folder/unresolvable_stem",
        )
        assert dup is None

    def test_register_identifier_and_has_seen(self) -> None:
        acc = _BatchSourceAccumulator()
        cid = ContentId("dQw4w9WgXcQ")

        assert acc.has_seen(cid) is False
        assert acc.has_seen("dQw4w9WgXcQ") is False

        acc.register_identifier(cid)
        assert acc.has_seen(cid) is True
        assert acc.has_seen("dQw4w9WgXcQ") is True

        acc.register_identifier("/path/to/stem_file.md")
        assert acc.has_seen("stem_file") is True
        assert acc.has_seen("/path/to/stem_file.md") is True
        assert acc.has_seen("nonexistent") is False

    def test_register_identifier_with_string_url_and_unparseable(self) -> None:
        acc = _BatchSourceAccumulator()
        acc.register_identifier("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert ContentId("dQw4w9WgXcQ") in acc.seen_vids
        assert "dQw4w9WgXcQ" in acc.seen_vids

        # Fresh accumulator has not seen empty token
        assert _BatchSourceAccumulator().has_seen("") is False

        # Register unparseable path
        acc.register_identifier("/path/to/custom_audio.opus")
        assert acc.has_seen("custom_audio") is True
        assert acc.has_seen("/path/to/custom_audio.opus") is True

    def test_has_seen_various_branches(self) -> None:
        acc = _BatchSourceAccumulator()
        cid = ContentId("dQw4w9WgXcQ")
        # Only add value string to seen_vids
        acc.seen_vids.add("dQw4w9WgXcQ")
        assert acc.has_seen(cid) is True

        # Unseen ContentId
        unseen_cid = ContentId("oHg5SJYRHA0")
        assert acc.has_seen(unseen_cid) is False

        # Valid URL whose resolved id is in seen_vids
        assert acc.has_seen("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

        # Stem branch
        acc.seen_vids.add("isolated_stem")
        assert acc.has_seen("/folder/sub/isolated_stem.txt") is True
        assert acc.has_seen("/folder/sub/unknown_stem.txt") is False
