"""PostgreSQL Ledger Persistence Adapter for Cresmo.

Implements LedgerRepositoryPort with SQLAlchemy 2.0 Async and asyncpg,
providing transactional ACID guarantees, connection pooling, and multi-process
concurrency safety adhering to ADR-001, ADR-003, and the Doctor Stangler Method.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from collections.abc import Coroutine
from datetime import UTC, datetime
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from cresmo.application.ports import LedgerRepositoryPort
from cresmo.domain.value_objects import ChannelName, ContentId, LedgerEntry, PipelineStatus
from cresmo.infrastructure.database.models import Base, LedgerEntryRow

T = TypeVar("T")


class PostgresLedgerAdapter(LedgerRepositoryPort):
    """PostgreSQL ledger persistence adapter using SQLAlchemy 2.0 and asyncpg.

    Provides transactional persistence for processing audit trails, ensuring idempotency
    and preventing duplicate transcription/synthesis across distributed worker executions.

    Adheres to:
        - Hexagonal Architecture: Translates ORM LedgerEntryRow to/from domain LedgerEntry.
        - Fail-Fast & Zero Dual-Write: Operates inside atomic transaction boundaries.
    """

    def __init__(
        self,
        db_url: str | None = None,
        engine: AsyncEngine | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        echo: bool = False,
    ) -> None:
        """Initialize PostgreSQL ledger adapter.

        Args:
            db_url: Database connection URL (e.g. postgresql+asyncpg://user:pass@host:5432/dbname).
            engine: Optional pre-configured AsyncEngine.
            session_factory: Optional pre-configured async_sessionmaker.
            echo: Whether to enable SQLAlchemy query logging.
        """
        if session_factory is not None:
            self._session_factory = session_factory
            self._engine = engine
        elif engine is not None:
            self._engine = engine
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                autoflush=False,
            )
        elif db_url is not None:
            # Normalize PostgreSQL scheme to asyncpg driver if bare postgresql:// is provided
            normalized_url = db_url
            if normalized_url.startswith("postgresql://"):
                normalized_url = normalized_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif normalized_url.startswith("sqlite://"):
                normalized_url = normalized_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

            self._engine = create_async_engine(normalized_url, echo=echo)
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                autoflush=False,
            )
        else:
            raise ValueError("Either db_url, engine, or session_factory must be provided.")

    async def init_db(self) -> None:
        """Initialize database schema tables asynchronously if not present."""
        if self._engine is not None:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    # =========================================================================
    # Synchronous Port Interface Implementation (LedgerRepositoryPort)
    # =========================================================================

    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        return self._run_async(self.is_processed_async(content_id))

    def mark_processed(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        self._run_async(self.mark_processed_async(content_id))

    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        self._run_async(self.save_entry_async(entry))

    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        return self._run_async(self.get_entry_async(content_id))

    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        return self._run_async(self.list_entries_async(limit))

    # =========================================================================
    # Native Asynchronous Implementation
    # =========================================================================

    async def is_processed_async(self, content_id: ContentId) -> bool:
        """Asynchronously check whether a content item has already completed."""
        async with self._session_factory() as session:
            stmt = select(LedgerEntryRow.status).where(LedgerEntryRow.content_id == content_id.value)
            result = await session.execute(stmt)
            status = result.scalar_one_or_none()
            if status is None:
                return False
            return status == PipelineStatus.COMPLETED.value

    async def mark_processed_async(self, content_id: ContentId) -> None:
        """Asynchronously mark content item as completed."""
        now = datetime.now(UTC)
        async with self._session_factory() as session, session.begin():
            existing = await session.get(LedgerEntryRow, content_id.value)
            if existing is not None:
                existing.status = PipelineStatus.COMPLETED.value
                existing.completed_at = now
                existing.updated_at = now
            else:
                new_row = LedgerEntryRow(
                    content_id=content_id.value,
                    channel="DefaultChannel",
                    status=PipelineStatus.COMPLETED.value,
                    media_url=f"https://youtube.com/watch?v={content_id.value}",
                    title=f"Video {content_id.value}",
                    notes_count=0,
                    completed_at=now,
                    updated_at=now,
                )
                session.add(new_row)

    async def save_entry_async(self, entry: LedgerEntry) -> None:
        """Asynchronously persist or update an immutable LedgerEntry audit record."""
        now = datetime.now(UTC)
        async with self._session_factory() as session, session.begin():
            existing = await session.get(LedgerEntryRow, entry.content_id.value)
            if existing is not None:
                existing.channel = str(entry.channel_name)
                existing.status = entry.status.value
                existing.media_url = entry.media_url
                existing.title = entry.title
                existing.notes_count = entry.notes_count
                existing.error_message = entry.error_message
                if entry.started_at is not None:
                    existing.started_at = entry.started_at
                if entry.completed_at is not None:
                    existing.completed_at = entry.completed_at
                existing.updated_at = now
            else:
                new_row = LedgerEntryRow(
                    content_id=entry.content_id.value,
                    channel=str(entry.channel_name),
                    status=entry.status.value,
                    media_url=entry.media_url,
                    title=entry.title,
                    notes_count=entry.notes_count,
                    error_message=entry.error_message,
                    started_at=entry.started_at,
                    completed_at=entry.completed_at,
                    updated_at=now,
                )
                session.add(new_row)

    async def get_entry_async(self, content_id: ContentId) -> LedgerEntry | None:
        """Asynchronously retrieve the latest LedgerEntry for a given content ID."""
        async with self._session_factory() as session:
            row = await session.get(LedgerEntryRow, content_id.value)
            if row is None:
                return None
            return self._row_to_entry(row)

    async def list_entries_async(self, limit: int = 100) -> list[LedgerEntry]:
        """Asynchronously list recently recorded ledger entries."""
        async with self._session_factory() as session:
            stmt = (
                select(LedgerEntryRow)
                .order_by(LedgerEntryRow.updated_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_entry(row) for row in rows]

    # =========================================================================
    # Helpers & Mappers (ACL Translation Boundary)
    # =========================================================================

    @staticmethod
    def _row_to_entry(row: LedgerEntryRow) -> LedgerEntry:
        """Translate SQLAlchemy LedgerEntryRow ORM model to pure Domain LedgerEntry.

        Guarantees that Domain layer has zero knowledge of SQLAlchemy or ORM internals.
        """
        return LedgerEntry(
            content_id=ContentId(row.content_id),
            media_url=row.media_url,
            title=row.title,
            channel_name=ChannelName(row.channel),
            status=PipelineStatus(row.status),
            notes_count=row.notes_count,
            error_message=row.error_message if row.error_message else None,
            started_at=row.started_at,
            completed_at=row.completed_at,
        )

    def _run_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Execute an asynchronous coroutine safely from synchronous port callers."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
