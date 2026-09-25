"""Unit tests for Channel Sync and SQLite Ledger Value Objects and Exceptions.

Verifies construction invariants, immutability, and boundary conditions
defined in SPEC-003 and ADR-003.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from cresmo.domain.exceptions import (
    CresmoDomainError,
    CresmoInfrastructureError,
    DomainValidationError,
    PreflightError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ContentId,
    DiscoveredMediaItem,
    LedgerEntry,
    PipelineStatus,
    SyncFilterCriteria,
    SyncSummary,
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


class TestDiscoveredMediaItem:
    """Test suite for DiscoveredMediaItem value object."""

    def test_valid_construction(self) -> None:
        now = datetime.now(UTC)
        item = DiscoveredMediaItem(
            content_id=ContentId("dQw4w9WgXcQ"),
            title="Quantum Computation Lecture 1",
            published_at=now,
            media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            channel_name="QuantumHub",
        )
        assert item.content_id.value == "dQw4w9WgXcQ"
        assert item.title == "Quantum Computation Lecture 1"
        assert item.published_at == now
        assert item.media_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert item.channel_name == "QuantumHub"

    def test_empty_title_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(DomainValidationError, match="title cannot be empty"):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="   ",
                published_at=now,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                channel_name="QuantumHub",
            )

    def test_invalid_url_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(DomainValidationError, match="Must start with http:// or https://"):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="Quantum Physics",
                published_at=now,
                media_url="ftp://example.com/video.mp4",
                channel_name="QuantumHub",
            )

    def test_empty_channel_name_raises_validation_error(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(DomainValidationError, match="cannot be empty or whitespace"):
            DiscoveredMediaItem(
                content_id=ContentId("dQw4w9WgXcQ"),
                title="Quantum Physics",
                published_at=now,
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                channel_name="  ",
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

    def test_default_values(self) -> None:
        query = ChannelFeedQuery(channel_url="https://youtube.com/@QuantumHub")
        assert query.lookback_days == 7
        assert query.max_videos == 50

    def test_invalid_url_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="Must start with http:// or https://"):
            ChannelFeedQuery(channel_url="not_a_valid_url")

    def test_non_positive_lookback_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="lookback_days must be positive"):
            ChannelFeedQuery(
                channel_url="https://youtube.com/@QuantumHub",
                lookback_days=0,
            )

    def test_non_positive_max_videos_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="max_videos must be positive"):
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
            channel_name="QuantumHub",
            status=PipelineStatus.COMPLETED,
            notes_count=15,
            error_message=None,
            started_at=now,
            completed_at=now,
        )
        assert entry.content_id.value == "dQw4w9WgXcQ"
        assert entry.notes_count == 15
        assert entry.status == PipelineStatus.COMPLETED

    def test_negative_notes_count_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="notes_count cannot be negative"):
            LedgerEntry(
                content_id=ContentId("dQw4w9WgXcQ"),
                media_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                title="Quantum Computation",
                channel_name="QuantumHub",
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
        assert criteria.matches_channel("Ancapsu") is True
        assert criteria.matches_category("Ancapsu") is True
        assert criteria.matches_video("dQw4w9WgXcQ") is True

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
        with pytest.raises(DomainValidationError, match="Channel filter token cannot be empty"):
            SyncFilterCriteria(channels=("",))
        with pytest.raises(DomainValidationError, match="Category filter token cannot be empty"):
            SyncFilterCriteria(categories=("   ",))
        with pytest.raises(DomainValidationError, match="Video filter token cannot be empty"):
            SyncFilterCriteria(video_ids=("",))

    def test_from_comma_separated_strings(self) -> None:
        criteria = SyncFilterCriteria.from_strings(
            channels=["Ancapsu, 3Blue1Brown", "Veritasium"],
            categories=["politics_br, tech_ai", "perennial"],
            video_ids=["vid1, vid2"],
        )
        assert criteria.channels == ("ancapsu", "3blue1brown", "veritasium")
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
        assert criteria.matches_channel("Ancapsu") is True
        assert criteria.matches_channel("ancapsu") is True
        assert criteria.matches_channel("Veritasium", "https://youtube.com/@Veritasium") is True
        assert criteria.matches_channel("OtherChannel", "https://youtube.com/@ancapsu") is True
        assert criteria.matches_channel("3Blue1Brown") is False

    def test_matches_category_evaluates_domain_name_vs_volatility(self) -> None:
        # Category list has both domain name ("politics_br") and volatility type ("perennial")
        criteria = SyncFilterCriteria(categories=("politics_br", "perennial"))

        # Ancapsu -> domain='politics_br', category_type='volatile' -> MATCHES via domain!
        assert criteria.matches_category("ancapsu") is True

        # 3blue1brown -> domain='engineering', category_type='perennial' -> MATCHES via volatility!
        assert criteria.matches_category("3blue1brown") is True

        # Canal 90 -> domain='entertainment', category_type='volatile' -> REJECTED (neither matches)
        assert criteria.matches_category("canal 90") is False

    def test_matches_video_by_id_and_url(self) -> None:
        criteria = SyncFilterCriteria(video_ids=("vid12345", "dQw4w9WgXcQ"))
        assert criteria.matches_video("vid12345") is True
        assert criteria.matches_video("dQw4w9WgXcQ") is True
        assert criteria.matches_video(ContentId("dQw4w9WgXcQ")) is True
        assert criteria.matches_video(ContentId("vid12345")) is True
        assert criteria.matches_video("unknown", "https://youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert criteria.matches_video("unknown", "https://youtube.com/watch?v=other999") is False
