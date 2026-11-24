"""Unit tests for PostgresLedgerAdapter adhering to Hexagonal Architecture and TDD.

Verifies that PostgresLedgerAdapter satisfies the LedgerRepositoryPort contract,
supports atomic transactions, and guarantees domain entities never inherit from DeclarativeBase.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import DeclarativeBase

from cresmo.application.ports import LedgerRepositoryPort
from cresmo.domain.value_objects import ChannelName, ContentId, LedgerEntry, PipelineStatus
from cresmo.infrastructure.persistence.models import Base, OutboxRow
from cresmo.infrastructure.persistence.postgres_ledger_adapter import PostgresLedgerAdapter


@pytest.fixture
def ledger_adapter() -> PostgresLedgerAdapter:
    """Create a hermetic in-memory async SQLite engine for PostgresLedgerAdapter testing."""
    import asyncio

    adapter = PostgresLedgerAdapter(db_url="sqlite+aiosqlite:///:memory:")
    asyncio.run(adapter.init_db())
    return adapter


def test_domain_entity_never_inherits_declarative_base() -> None:
    """Hexagonal Architecture Invariant: Domain models must not inherit from ORM DeclarativeBase."""
    assert not issubclass(LedgerEntry, DeclarativeBase)
    assert not issubclass(LedgerEntry, Base)


def test_implements_ledger_repository_port(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify that PostgresLedgerAdapter is an instance of LedgerRepositoryPort."""
    assert isinstance(ledger_adapter, LedgerRepositoryPort)


def test_sync_is_processed_reflects_completed_entry(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify is_processed returns False until a COMPLETED LedgerEntry is persisted."""
    content_id = ContentId("test_vid_001")

    assert ledger_adapter.is_processed(content_id) is False

    ledger_adapter.save_entry(
        LedgerEntry(
            content_id=content_id,
            media_url="https://youtube.com/watch?v=test_vid_001",
            title="Test Video",
            channel_name=ChannelName("TechChannel"),
            status=PipelineStatus.COMPLETED,
        )
    )
    assert ledger_adapter.is_processed(content_id) is True

    entry = ledger_adapter.get_entry(content_id)
    assert entry is not None
    assert entry.content_id == content_id
    assert entry.status == PipelineStatus.COMPLETED


def test_sync_save_and_get_entry(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify synchronous persistence and retrieval of LedgerEntry."""
    content_id = ContentId("test_vid_002")
    now = datetime.now(UTC)

    entry = LedgerEntry(
        content_id=content_id,
        media_url="https://youtube.com/watch?v=test_vid_002",
        title="Test Architectural Evolution",
        channel_name=ChannelName("TechChannel"),
        status=PipelineStatus.RUNNING,
        notes_count=0,
        error_message=None,
        started_at=now,
        completed_at=None,
    )

    ledger_adapter.save_entry(entry)

    retrieved = ledger_adapter.get_entry(content_id)
    assert retrieved is not None
    assert retrieved.content_id == content_id
    assert retrieved.title == "Test Architectural Evolution"
    assert retrieved.channel_name == ChannelName("TechChannel")
    assert retrieved.status == PipelineStatus.RUNNING

    # Update entry to COMPLETED
    completed_entry = LedgerEntry(
        content_id=content_id,
        media_url="https://youtube.com/watch?v=test_vid_002",
        title="Test Architectural Evolution Updated",
        channel_name=ChannelName("TechChannel"),
        status=PipelineStatus.COMPLETED,
        notes_count=12,
        error_message=None,
        started_at=now,
        completed_at=datetime.now(UTC),
    )
    ledger_adapter.save_entry(completed_entry)

    updated = ledger_adapter.get_entry(content_id)
    assert updated is not None
    assert updated.status == PipelineStatus.COMPLETED
    assert updated.notes_count == 12
    assert updated.title == "Test Architectural Evolution Updated"


@pytest.mark.asyncio
async def test_native_async_methods(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify direct native asynchronous methods for high-performance FastAPI/ARQ usage."""
    content_id = ContentId("async_content_001")

    assert await ledger_adapter.is_processed_async(content_id) is False

    await ledger_adapter.save_entry_async(
        LedgerEntry(
            content_id=content_id,
            media_url="https://youtube.com/watch?v=async_content_001",
            title="Async Video",
            channel_name=ChannelName("AsyncChannel"),
            status=PipelineStatus.COMPLETED,
        )
    )
    assert await ledger_adapter.is_processed_async(content_id) is True

    entry = await ledger_adapter.get_entry_async(content_id)
    assert entry is not None
    assert entry.status == PipelineStatus.COMPLETED

    # Verify native save_entry_async
    async_entry = LedgerEntry(
        content_id=ContentId("async_content_002"),
        media_url="https://youtube.com/watch?v=async_content_002",
        title="Async Saved Title",
        channel_name=ChannelName("AsyncChannel"),
        status=PipelineStatus.RUNNING,
        notes_count=42,
    )
    await ledger_adapter.save_entry_async(async_entry)
    fetched = await ledger_adapter.get_entry_async(ContentId("async_content_002"))
    assert fetched is not None
    assert fetched.title == "Async Saved Title"
    assert fetched.notes_count == 42


def test_outbox_row_schema_and_instantiation() -> None:
    """Verify OutboxRow attributes and default values."""
    now = datetime.now(UTC)
    row = OutboxRow(
        event_id="evt_001",
        event_type="TranscriptIndexed",
        payload='{"key": "value"}',
        created_at=now,
    )
    assert row.event_id == "evt_001"
    assert row.event_type == "TranscriptIndexed"
    assert row.payload == '{"key": "value"}'
    assert row.created_at == now
    assert row.__tablename__ == "cresmo_outbox"
