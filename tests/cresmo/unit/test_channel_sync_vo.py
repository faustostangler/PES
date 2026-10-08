"""Unit tests for Channel Sync and SQLite Ledger Value Objects and Exceptions.

Verifies construction invariants, immutability, and boundary conditions
defined in SPEC-003 and ADR-003.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from cresmo.domain.exceptions import (
    CresmoDomainError,
    CresmoInfrastructureError,
    DomainValidationError,
    PreflightError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    Channel,
    ChannelFeedQuery,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    DiscoveredMediaItem,
    LedgerEntry,
    MediaProvenance,
    PipelineStatus,
    SyncFilterCriteria,
    SyncSummary,
    normalize_to_uploads_playlist_url,
)
from cresmo.domain.value_objects.media import (
    DEFAULT_FEED_LOOKBACK_DAYS,
    DEFAULT_FEED_MAX_VIDEOS,
)


class TestPipelineStatus:
    """Test suite for PipelineStatus enumeration."""

    def test_pipeline_status_canonical_members(self) -> None:
        assert PipelineStatus.COMPLETED.value == "COMPLETED"
        assert PipelineStatus.SKIPPED_IDEMPOTENT.value == "SKIPPED_IDEMPOTENT"
        assert PipelineStatus.FAILED_INGESTION.value == "FAILED_INGESTION"
        assert PipelineStatus.FAILED_TRANSFORMATION.value == "FAILED_TRANSFORMATION"
        assert PipelineStatus.RUNNING.value == "RUNNING"
        assert PipelineStatus.PAUSED_BUDGET.value == "PAUSED_BUDGET"
        assert PipelineStatus.QUARANTINED.value == "QUARANTINED"


class TestMediaProvenance:
    """Test suite for MediaProvenance value object."""

    def test_construction_and_string_cleaning(self) -> None:
        prov = MediaProvenance(
            url="  https://youtube.com/watch?v=dQw4w9WgXcQ  ",
            description="  Video Description  ",
            publication_date=datetime(2024, 6, 15, 12, 0, 0),
        )
        assert prov.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert prov.description == "Video Description"
        assert prov.publication_date == date(2024, 6, 15)

    def test_create_factory_variants(self) -> None:
        p1 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date=datetime(2024, 6, 15, 12, 0),
        )
        assert p1.publication_date == date(2024, 6, 15)

        p2 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date=date(2024, 6, 15),
        )
        assert p2.publication_date == date(2024, 6, 15)

        p3 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date="2024-06-15",
        )
        assert p3.publication_date == date(2024, 6, 15)

        p4 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date="not-an-iso-date",
        )
        assert p4.publication_date is None

        p5 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date="",
        )
        assert p5.publication_date is None

        p6 = MediaProvenance.create(
            url="https://youtube.com",
            description="Test",
            publication_date=None,
        )
        assert p6.publication_date is None

    def test_create_default_parameters(self) -> None:
        p_default = MediaProvenance.create()
        assert p_default.url == ""
        assert p_default.description == ""
        assert p_default.publication_date is None

        p_vals = MediaProvenance.create(url="https://u.com", description="custom desc")
        assert p_vals.url == "https://u.com"
        assert p_vals.description == "custom desc"

    def test_empty_factory(self) -> None:
        empty = MediaProvenance.empty()
        assert empty.url == ""
        assert empty.description == ""
        assert empty.publication_date is None


class TestDiscoveredMediaItem:
    """Test suite for DiscoveredMediaItem value object."""

    def test_valid_construction(self) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("dQw4w9WgXcQ"),
            title="Quantum Computation Lecture 1",
            published_at=now,
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            channel_name=ChannelName("QuantumHub"),
        )
        assert item.content_id.value == "dQw4w9WgXcQ"
        assert item.title == "Quantum Computation Lecture 1"
        assert item.published_at == now
        assert item.media_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert item.channel_name == ChannelName("QuantumHub")

    def test_valid_http_url(self) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("dQw4w9WgXcQ"),
            title="Quantum Computation",
            published_at=now,
            media_url="http://youtube.com/watch?v=dQw4w9WgXcQ",
            channel_name=ChannelName("QuantumHub"),
        )
        assert item.media_url == "http://youtube.com/watch?v=dQw4w9WgXcQ"

    def test_composite_properties(self) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("dQw4w9WgXcQ"),
            title="Quantum Computation Lecture 1",
            published_at=now,
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            channel_name=ChannelName("QuantumHub"),
        )
        channel = item.channel
        assert isinstance(channel, Channel)
        assert channel.name == ChannelName("QuantumHub")

        prov = item.provenance
        assert isinstance(prov, MediaProvenance)
        assert prov.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert prov.publication_date == now.date()

        content = item.content
        assert isinstance(content, Content)
        assert content.id == ContentId("dQw4w9WgXcQ")
        assert content.title == "Quantum Computation Lecture 1"

    def test_construction_normalizes_and_coerces_fields(self) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id="  dQw4w9WgXcQ  ",  # type: ignore[arg-type]
            title="  Quantum Computation Lecture 1  ",
            published_at=now,
            media_url="  https://youtube.com/watch?v=dQw4w9WgXcQ  ",
            channel_name="  QuantumHub  ",  # type: ignore[arg-type]
        )
        assert item.title == "Quantum Computation Lecture 1"
        assert item.media_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert isinstance(item.channel_name, ChannelName)
        assert item.channel_name.value == "QuantumHub"
        assert isinstance(item.content_id, ContentId)
        assert item.content_id.value == "dQw4w9WgXcQ"

    def test_empty_title_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(
            DomainValidationError,
            match=r"^DiscoveredMediaItem title cannot be empty\.$",
        ):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="   ",
                published_at=now,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                channel_name=ChannelName("QuantumHub"),
            )

    def test_invalid_url_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(DomainValidationError, match="Must start with http:// or https://"):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="Quantum Physics",
                published_at=now,
                media_url="ftp://example.com/video.mp4",
                channel_name=ChannelName("QuantumHub"),
            )

    def test_empty_channel_name_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(DomainValidationError, match="ChannelName cannot be empty"):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="Quantum Physics",
                published_at=now,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                channel_name=ChannelName("  "),
            )


class TestChannelFeedQuery:
    """Test suite for ChannelFeedQuery command / value object."""

    def test_valid_query(self) -> None:
        query = ChannelFeedQuery(
            channel_url="https://youtube.com/@QuantumHub",
            lookback_days=14,
            max_videos=25,
        )
        assert query.channel_url == "https://youtube.com/@QuantumHub"
        assert query.lookback_days == 14
        assert query.max_videos == 25

    def test_valid_http_and_whitespace_stripped(self) -> None:
        query = ChannelFeedQuery(channel_url="  http://youtube.com/@QuantumHub  ")
        assert query.channel_url == "http://youtube.com/@QuantumHub"

    def test_boundary_values(self) -> None:
        q_days = ChannelFeedQuery(channel_url="https://youtube.com/@QuantumHub", lookback_days=1)
        assert q_days.lookback_days == 1

        q_max = ChannelFeedQuery(channel_url="https://youtube.com/@QuantumHub", max_videos=1)
        assert q_max.max_videos == 1

    def test_default_values(self) -> None:
        query = ChannelFeedQuery(channel_url="https://youtube.com/@QuantumHub")
        assert query.lookback_days == 7
        assert query.max_videos == 50

    def test_invalid_url_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="Must start with http:// or https://"):
            ChannelFeedQuery(channel_url="not_a_valid_url")

    def test_non_positive_lookback_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^lookback_days must be positive\. Got: 0$"):
            ChannelFeedQuery(
                channel_url="https://youtube.com/@QuantumHub",
                lookback_days=0,
            )

    def test_non_positive_max_videos_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^max_videos must be positive\. Got: 0$"):
            ChannelFeedQuery(
                channel_url="https://youtube.com/@QuantumHub",
                max_videos=0,
            )
        with pytest.raises(DomainValidationError, match=r"^max_videos must be positive\. Got: -5$"):
            ChannelFeedQuery(
                channel_url="https://youtube.com/@QuantumHub",
                max_videos=-5,
            )


class TestSyncSummary:
    """Test suite for SyncSummary execution report."""

    def test_valid_summary(self) -> None:
        summary = SyncSummary(
            channel_url="https://youtube.com/@QuantumHub",
            total_discovered=10,
            processed_count=5,
            skipped_count=4,
            failed_count=1,
            duration_seconds=12.4,
            status=PipelineStatus.COMPLETED,
        )
        assert summary.channel_url == "https://youtube.com/@QuantumHub"
        assert summary.total_discovered == 10
        assert summary.processed_count == 5
        assert summary.skipped_count == 4
        assert summary.failed_count == 1
        assert summary.duration_seconds == 12.4
        assert summary.status == PipelineStatus.COMPLETED


class TestLedgerEntry:
    """Test suite for LedgerEntry audit record."""

    def test_valid_ledger_entry(self) -> None:
        now = datetime.now(UTC)
        entry = LedgerEntry(
            content_id=ContentId("dQw4w9WgXcQ"),
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Quantum Computation",
            channel_name=ChannelName("QuantumHub"),
            status=PipelineStatus.COMPLETED,
            notes_count=15,
            error_message=None,
            started_at=now,
            completed_at=now,
        )
        assert entry.content_id.value == "dQw4w9WgXcQ"
        assert entry.notes_count == 15
        assert entry.status == PipelineStatus.COMPLETED

    def test_valid_http_media_url(self) -> None:
        entry = LedgerEntry(
            content_id=ContentId("dQw4w9WgXcQ"),
            media_url="http://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Quantum Computation",
            channel_name=ChannelName("QuantumHub"),
            status=PipelineStatus.COMPLETED,
        )
        assert entry.media_url == "http://youtube.com/watch?v=dQw4w9WgXcQ"

    def test_construction_normalizes_and_coerces_fields(self) -> None:
        entry = LedgerEntry(
            content_id="  dQw4w9WgXcQ  ",  # type: ignore[arg-type]
            media_url="  https://youtube.com/watch?v=dQw4w9WgXcQ  ",
            title="  Quantum Computation  ",
            channel_name="  QuantumHub  ",  # type: ignore[arg-type]
            status=PipelineStatus.COMPLETED,
        )
        assert isinstance(entry.content_id, ContentId)
        assert entry.content_id.value == "dQw4w9WgXcQ"
        assert isinstance(entry.channel_name, ChannelName)
        assert entry.channel_name.value == "QuantumHub"
        assert entry.media_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert entry.title == "Quantum Computation"

    def test_invalid_media_url_exact_message(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^Invalid LedgerEntry media_url 'ftp://example\.com'\. Must start with http:// or https://$",
        ):
            LedgerEntry(
                content_id=ContentId("dQw4w9WgXcQ"),
                media_url="ftp://example.com",
                title="Quantum Computation",
                channel_name=ChannelName("QuantumHub"),
                status=PipelineStatus.COMPLETED,
            )

    def test_empty_title_exact_message(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^LedgerEntry title cannot be empty\.$",
        ):
            LedgerEntry(
                content_id=ContentId("dQw4w9WgXcQ"),
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="   ",
                channel_name=ChannelName("QuantumHub"),
                status=PipelineStatus.COMPLETED,
            )

    def test_notes_count_boundaries(self) -> None:
        entry0 = LedgerEntry(
            content_id=ContentId("dQw4w9WgXcQ"),
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            title="Quantum Computation",
            channel_name=ChannelName("QuantumHub"),
            status=PipelineStatus.COMPLETED,
            notes_count=0,
        )
        assert entry0.notes_count == 0

        with pytest.raises(
            DomainValidationError,
            match=r"^LedgerEntry notes_count cannot be negative\. Got: -1$",
        ):
            LedgerEntry(
                content_id=ContentId("dQw4w9WgXcQ"),
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Quantum Computation",
                channel_name=ChannelName("QuantumHub"),
                status=PipelineStatus.COMPLETED,
                notes_count=-1,
            )


class TestExceptionsHierarchy:
    """Test suite verifying segregation of infrastructure vs domain exceptions."""

    def test_infrastructure_exceptions_inherit_base(self) -> None:
        preflight = PreflightError("Missing credentials")
        assert isinstance(preflight, CresmoInfrastructureError)
        assert not isinstance(preflight, CresmoDomainError)

        security = SecurityViolationError("Path traversal escape")
        assert isinstance(security, CresmoInfrastructureError)
        assert not isinstance(security, CresmoDomainError)


class TestSyncFilterCriteria:
    """Test suite for SyncFilterCriteria Value Object enforcing ADR-012."""

    def test_default_empty_criteria_matches_all(self) -> None:
        criteria = SyncFilterCriteria()
        assert criteria.is_empty() is True
        assert criteria.channels == ()
        assert criteria.categories == ()
        assert criteria.video_ids == ()
        assert criteria.matches_channel(ChannelName("Ancapsu")) is True
        assert criteria.matches_category(ChannelName("Ancapsu")) is True
        assert criteria.matches_video(ContentId("dQw4w9WgXcQ")) is True

    @pytest.mark.parametrize(
        "channels,categories,video_ids,expected_empty",
        [
            ((), (), (), True),
            (("ch",), (), (), False),
            ((), ("cat",), (), False),
            ((), (), ("vid",), False),
            (("ch",), ("cat",), ("vid",), False),
        ],
    )
    def test_is_empty_matrix(
        self,
        channels: tuple[str, ...],
        categories: tuple[str, ...],
        video_ids: tuple[str, ...],
        expected_empty: bool,
    ) -> None:
        criteria = SyncFilterCriteria(channels=channels, categories=categories, video_ids=video_ids)
        assert criteria.is_empty() is expected_empty

    def test_construction_sanitizes_and_normalizes(self) -> None:
        criteria = SyncFilterCriteria(
            channels=(" Ancapsu ", "3blue1brown"),
            categories=(" POLITICS_BR ", "Perennial "),
            video_ids=(" dQw4w9WgXcQ ",),
        )
        assert criteria.channels == ("ancapsu", "3blue1brown")
        assert criteria.categories == ("politics_br", "perennial")
        assert criteria.video_ids == ("dQw4w9WgXcQ",)
        assert criteria.is_empty() is False

    def test_empty_tokens_raise_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^Channel filter token cannot be empty\.$"):
            SyncFilterCriteria(channels=("",))
        with pytest.raises(DomainValidationError, match=r"^Category filter token cannot be empty\.$"):
            SyncFilterCriteria(categories=("   ",))
        with pytest.raises(DomainValidationError, match=r"^Video filter token cannot be empty\.$"):
            SyncFilterCriteria(video_ids=("",))

    def test_from_comma_separated_strings(self) -> None:
        criteria = SyncFilterCriteria.from_strings(
            channels=["Ancapsu, 3Blue1Brown", "", None, "Veritasium", "  ,  extra  "],
            categories=["politics_br, tech_ai", None, "perennial"],
            video_ids=["vid1, vid2", ""],
        )
        assert criteria.channels == ("ancapsu", "3blue1brown", "veritasium", "extra")
        assert criteria.categories == ("politics_br", "tech_ai", "perennial")
        assert criteria.video_ids == ("vid1", "vid2")

    def test_from_strings_none_or_empty_yields_empty_criteria(self) -> None:
        criteria = SyncFilterCriteria.from_strings(
            channels=None,
            categories=[],
            video_ids=None,
        )
        assert criteria.is_empty() is True

    def test_matches_channel_by_name_handle_and_url(self) -> None:
        criteria = SyncFilterCriteria(channels=("ancapsu", "veritasium"))
        assert criteria.matches_channel(ChannelName("Ancapsu")) is True
        assert criteria.matches_channel(ChannelName("ancapsu")) is True
        assert (
            criteria.matches_channel(ChannelName("Veritasium"), "https://youtube.com/@Veritasium")
            is True
        )
        assert (
            criteria.matches_channel(ChannelName("OtherChannel"), "https://youtube.com/@ancapsu")
            is True
        )
        assert criteria.matches_channel(ChannelName("3Blue1Brown")) is False

    def test_matches_channel_subsets_and_prefixes(self) -> None:
        # Target in channel_name (target is proper subset of name)
        c1 = SyncFilterCriteria(channels=("ancap",))
        assert c1.matches_channel(ChannelName("ancapsu")) is True
        assert c1.matches_channel(ChannelName("other")) is False

        # Channel_name in target (name is proper subset of target)
        c2 = SyncFilterCriteria(channels=("superancapsu",))
        assert c2.matches_channel(ChannelName("ancapsu")) is True
        assert c2.matches_channel(ChannelName("other")) is False

        # Target starting with '@'
        c3 = SyncFilterCriteria(channels=("@ancapsu",))
        assert c3.matches_channel(ChannelName("ancapsu")) is True
        assert c3.matches_channel(channel_name=None, channel_url="https://youtube.com/channel/ancapsu") is True
        assert c3.matches_channel(ChannelName("other")) is False

        # Target being only '@' without bare target
        c_at_only = SyncFilterCriteria(channels=("@",))
        assert c_at_only.matches_channel(ChannelName("ancapsu")) is False

        # Target starting with '@X' to kill lstrip character set mutant
        c_x = SyncFilterCriteria(channels=("@X",))
        assert c_x.matches_channel(ChannelName("X")) is True

        # Channel URL with @target
        c4 = SyncFilterCriteria(channels=("mychan",))
        assert c4.matches_channel(channel_name=None, channel_url="https://youtube.com/@mychan") is True
        assert c4.matches_channel(channel_name=None, channel_url="https://youtube.com/@other") is False

        # Channel name containing @target
        c5 = SyncFilterCriteria(channels=("myhandle",))
        assert c5.matches_channel(ChannelName("Follow @myhandle daily")) is True

    def test_resolve_channel_name_and_url_variations(self) -> None:
        # Raw string channel_name containing URL or handle
        c = SyncFilterCriteria(channels=("mychan",))
        assert c.matches_channel(channel_name="https://youtube.com/@mychan", channel_url=None) is True
        assert c.matches_channel(channel_name="/mychan/videos", channel_url=None) is True
        assert c.matches_channel(channel_name="@mychan", channel_url=None) is True
        assert c.matches_channel(channel_name="MYCHAN", channel_url=None) is True

        # When channel_url is already provided, it takes precedence over embedded string url
        assert c.matches_channel(channel_name="http://embedded", channel_url="https://youtube.com/@mychan") is True

        # When channel_name is None, do not match dummy "XXXX" or "xxxx"
        c_dummy = SyncFilterCriteria(channels=("xxxx",))
        assert c_dummy.matches_channel(channel_name=None, channel_url=None) is False
        assert c_dummy.matches_channel(channel_name=ChannelName("other"), channel_url=None) is False
        assert c_dummy.matches_channel(channel_name=None, channel_url="https://youtube.com/@other") is False

    def test_matches_category_evaluates_domain_name_vs_volatility(self) -> None:
        # Category list has both domain name ("politics_br") and volatility type ("perennial")
        criteria = SyncFilterCriteria(categories=("politics_br", "perennial"))

        # Ancapsu -> domain='politics_br', category_type='volatile' -> MATCHES via domain!
        assert criteria.matches_category(ChannelName("ancapsu")) is True

        # 3blue1brown -> domain='engineering', category_type='perennial' -> MATCHES via volatility!
        assert criteria.matches_category(ChannelName("3blue1brown")) is True

        # Canal 90 -> domain='entertainment', category_type='volatile' -> REJECTED (neither matches)
        assert criteria.matches_category(ChannelName("canal 90")) is False

        # Fallback with channel_url when channel_name is None
        assert criteria.matches_category(channel_name=None, channel_url="https://youtube.com/@ancapsu") is True
        assert criteria.matches_category(channel_name=None, channel_url=None) is False
        c_dummy_cat = SyncFilterCriteria(categories=("XXXX",))
        assert c_dummy_cat.matches_category(channel_name=None, channel_url=None) is False

    def test_matches_video_by_id_and_url(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("vid12345", "dQw4w9WgXcQ"))
        assert criteria.matches_video(ContentId("vid12345")) is True
        assert criteria.matches_video(ContentId("dQw4w9WgXcQ")) is True
        assert criteria.matches_video(video_id="vid12345") is True
        assert (
            criteria.matches_video(ContentId("unknown"), "https://youtube.com/watch?v=dQw4w9WgXcQ")
            is True
        )
        assert (
            criteria.matches_video(ContentId("unknown"), "https://youtube.com/watch?v=other999")
            is False
        )

    def test_matches_video_subsets_and_url_inference(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("12345",))

        # Target is substring of video_id (target != video_id)
        assert criteria.matches_video(video_id=ContentId("vid12345")) is True
        assert criteria.matches_video(video_id="vid12345") is True

        # video_id is substring of target
        c_long = SyncFilterCriteria(video_ids=("long_target_vid12345_suffix",))
        assert c_long.matches_video(video_id="vid12345") is True

        # Raw string video_id containing URL with http or slash
        assert criteria.matches_video(video_id="https://youtu.be/12345", video_url=None) is True
        assert criteria.matches_video(video_id="path/12345", video_url=None) is True

        # Target is substring of video_url
        assert criteria.matches_video(video_id=None, video_url="https://youtube.com/watch?v=12345") is True

        # video_url is substring of Target
        c_url = SyncFilterCriteria(video_ids=("https://youtu.be/12345?t=42",))
        assert c_url.matches_video(video_id=None, video_url="https://youtu.be/12345") is True

        # Non-matching and dummy check
        c_dummy = SyncFilterCriteria(video_ids=("XXXX",))
        assert c_dummy.matches_video(video_id=None, video_url=None) is False
        assert c_dummy.matches_video(video_id=ContentId("other"), video_url=None) is False
        assert c_dummy.matches_video(video_id=None, video_url="https://youtu.be/other") is False


class TestNormalizeToUploadsPlaylistUrl:
    """Test suite for normalize_to_uploads_playlist_url function."""

    def test_channel_id_instance(self) -> None:
        cid = ChannelId("UC1234567890123456789012")
        expected = "https://www.youtube.com/playlist?list=UU1234567890123456789012"
        assert normalize_to_uploads_playlist_url(cid) == expected

        # ChannelId without uploads playlist URL falls back to canonical URL
        cid_no_uploads = ChannelId("custom_channel")
        assert (
            normalize_to_uploads_playlist_url(cid_no_uploads)
            == cid_no_uploads.canonical_url
        )

    def test_empty_and_whitespace(self) -> None:
        assert normalize_to_uploads_playlist_url("") == ""
        assert normalize_to_uploads_playlist_url("   ") == ""

    def test_already_playlist_urls(self) -> None:
        # Standard playlist parameter
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/playlist?list=CUSTOM_ID")
            == "https://youtube.com/playlist?list=CUSTOM_ID"
        )
        assert (
            normalize_to_uploads_playlist_url("http://youtube.com/playlist?list=CUSTOM_ID")
            == "http://youtube.com/playlist?list=CUSTOM_ID"
        )
        assert (
            normalize_to_uploads_playlist_url("youtube.com/playlist?list=CUSTOM_ID")
            == "https://youtube.com/playlist?list=CUSTOM_ID"
        )
        # UU playlist parameter
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/watch?v=1&list=UU123")
            == "https://youtube.com/watch?v=1&list=UU123"
        )
        assert (
            normalize_to_uploads_playlist_url("http://youtube.com/watch?v=1&list=UU123")
            == "http://youtube.com/watch?v=1&list=UU123"
        )
        assert (
            normalize_to_uploads_playlist_url("youtube.com/watch?v=1&list=UU123")
            == "https://youtube.com/watch?v=1&list=UU123"
        )
        # PL playlist parameter
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/watch?v=1&list=PL123")
            == "https://youtube.com/watch?v=1&list=PL123"
        )
        assert (
            normalize_to_uploads_playlist_url("http://youtube.com/watch?v=1&list=PL123")
            == "http://youtube.com/watch?v=1&list=PL123"
        )
        assert (
            normalize_to_uploads_playlist_url("youtube.com/watch?v=1&list=PL123")
            == "https://youtube.com/watch?v=1&list=PL123"
        )

        # Playlist parameter with @ handle (prevents fall-through to /@ check appending /videos)
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu?list=PL123")
            == "https://youtube.com/@ancapsu?list=PL123"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu?list=UU123")
            == "https://youtube.com/@ancapsu?list=UU123"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/playlist?list=CUSTOM")
            == "https://youtube.com/@ancapsu/playlist?list=CUSTOM"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu?list=PL123")
            == "https://@ancapsu?list=PL123"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu?list=UU123")
            == "https://@ancapsu?list=UU123"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu/playlist?list=CUSTOM")
            == "https://@ancapsu/playlist?list=CUSTOM"
        )

    def test_handle_urls_and_tab_suffixes(self) -> None:
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu")
            == "https://youtube.com/@ancapsu/videos"
        )
        # Handle ending in 'X' to ensure rstrip('/') does not strip non-slash trailing characters
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@channelX")
            == "https://youtube.com/@channelX/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/")
            == "https://youtube.com/@ancapsu/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/videos")
            == "https://youtube.com/@ancapsu/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/videos/")
            == "https://youtube.com/@ancapsu/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/shorts")
            == "https://youtube.com/@ancapsu/shorts"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/streams")
            == "https://youtube.com/@ancapsu/streams"
        )
        assert (
            normalize_to_uploads_playlist_url("https://youtube.com/@ancapsu/playlists")
            == "https://youtube.com/@ancapsu/playlists"
        )
        assert (
            normalize_to_uploads_playlist_url("https://@ancapsu")
            == "https://www.youtube.com/@ancapsu/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu/videos")
            == "https://www.youtube.com/@ancapsu/videos"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu/shorts")
            == "https://www.youtube.com/@ancapsu/shorts"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu/streams")
            == "https://www.youtube.com/@ancapsu/streams"
        )
        assert (
            normalize_to_uploads_playlist_url("@ancapsu/playlists")
            == "https://www.youtube.com/@ancapsu/playlists"
        )

    def test_custom_urls(self) -> None:
        assert (
            normalize_to_uploads_playlist_url("http://example.com/custom")
            == "http://example.com/custom"
        )

