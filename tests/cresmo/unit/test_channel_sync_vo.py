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
        with pytest.raises(DomainValidationError, match="channel_name cannot be empty"):
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
