"""SQLAlchemy 2.0 ORM persistence models for Cresmo.

Strictly segregated inside the Infrastructure layer adhering to Hexagonal Architecture.
Domain entities (e.g. LedgerEntry) NEVER inherit from DeclarativeBase.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class for all Cresmo persistence models."""


class LedgerEntryRow(Base):
    """PostgreSQL ORM model for cresmo_ledger tracking state and idempotency.

    Maps 1-to-1 with the PostgreSQL cresmo_ledger table.
    Translates to/from domain LedgerEntry value objects at the adapter boundary.
    """

    __tablename__ = "cresmo_ledger"

    content_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Detailed projection columns for fast indexing and query access
    media_url: Mapped[str] = mapped_column(String(512), default="")
    title: Mapped[str] = mapped_column(String(512), default="")
    notes_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OutboxRow(Base):
    """Transactional Outbox event store ensuring atomic eventual consistency.

    Conforms to Doctor Stangler Method Section 3 (Transactional Outbox Pattern).
    Ensures domain events are persisted in the same transaction as state updates,
    preventing dual-write distributed transaction failures.
    """

    __tablename__ = "cresmo_outbox"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
