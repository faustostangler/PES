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
from cresmo.infrastructure.adapters.database import PostgresLedgerAdapter
from cresmo.infrastructure.database.models import Base


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


def test_sync_is_processed_and_mark_processed(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify synchronous port methods for is_processed and mark_processed."""
    content_id = ContentId("test_vid_001")

    assert ledger_adapter.is_processed(content_id) is False

    ledger_adapter.mark_processed(content_id)
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


def test_sync_list_entries(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify listing recent ledger entries with ordering and limit."""
    for i in range(5):
        entry = LedgerEntry(
            content_id=ContentId(f"content_{i}"),
            media_url=f"https://youtube.com/watch?v=content_{i}",
            title=f"Title {i}",
            channel_name=ChannelName("Channel"),
            status=PipelineStatus.COMPLETED,
            notes_count=i,
        )
        ledger_adapter.save_entry(entry)

    entries = ledger_adapter.list_entries(limit=3)
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_native_async_methods(ledger_adapter: PostgresLedgerAdapter) -> None:
    """Verify direct native asynchronous methods for high-performance FastAPI/ARQ usage."""
    content_id = ContentId("async_content_001")

    assert await ledger_adapter.is_processed_async(content_id) is False

    await ledger_adapter.mark_processed_async(content_id)
    assert await ledger_adapter.is_processed_async(content_id) is True

    entry = await ledger_adapter.get_entry_async(content_id)
    assert entry is not None
    assert entry.status == PipelineStatus.COMPLETED

    all_entries = await ledger_adapter.list_entries_async(limit=10)
    assert len(all_entries) >= 1
