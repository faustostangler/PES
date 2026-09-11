"""SQLite Write-Ahead Logging (WAL) Ledger Adapter for Cresmo.

Implements LedgerRepositoryPort with ACID transactional durability,
WAL mode (PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;),
and multi-process concurrency safety adhering to ADR-003 and SPEC-003.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from cresmo.application.ports import LedgerRepositoryPort
from cresmo.domain.value_objects import ContentId, LedgerEntry, PipelineStatus


class SqliteLedgerAdapter(LedgerRepositoryPort):
    """ACID SQLite ledger persistence adapter in Write-Ahead Logging (WAL) mode."""

    def __init__(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        """Initialize database schema if not already present."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cresmo_ledger (
                    content_id TEXT PRIMARY KEY,
                    media_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    notes_count INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    started_at TEXT,
                    completed_at TEXT
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cresmo_ledger_status ON cresmo_ledger(status);"
            )

    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def mark_processed(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        now_iso = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO cresmo_ledger (
                    content_id, media_url, title, channel_name, status, notes_count, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(content_id) DO UPDATE SET
                    status = excluded.status,
                    completed_at = excluded.completed_at;
                """,
                (
                    content_id.value,
                    f"https://youtube.com/watch?v={content_id.value}",
                    f"Video {content_id.value}",
                    "DefaultChannel",
                    PipelineStatus.COMPLETED.value,
                    0,
                    now_iso,
                ),
            )

    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        started_iso = entry.started_at.isoformat() if entry.started_at else None
        completed_iso = entry.completed_at.isoformat() if entry.completed_at else None

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO cresmo_ledger (
                    content_id, media_url, title, channel_name, status,
                    notes_count, error_message, started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(content_id) DO UPDATE SET
                    media_url = excluded.media_url,
                    title = excluded.title,
                    channel_name = excluded.channel_name,
                    status = excluded.status,
                    notes_count = excluded.notes_count,
                    error_message = excluded.error_message,
                    started_at = COALESCE(excluded.started_at, cresmo_ledger.started_at),
                    completed_at = excluded.completed_at;
                """,
                (
                    entry.content_id.value,
                    entry.media_url,
                    entry.title,
                    entry.channel_name,
                    entry.status.value,
                    entry.notes_count,
                    entry.error_message,
                    started_iso,
                    completed_iso,
                ),
            )

    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )
