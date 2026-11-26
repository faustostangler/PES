"""SQLite Write-Ahead Logging (WAL) Ledger Adapter for Cresmo.

Implements LedgerRepositoryPort with ACID transactional durability,
WAL mode (PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;),
and multi-process concurrency safety adhering to ADR-003 and SPEC-003.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Final

from cresmo.application.ports import LedgerRepositoryPort
from cresmo.domain.value_objects import ChannelName, ContentId, LedgerEntry, PipelineStatus

DEFAULT_SQLITE_TIMEOUT_SECONDS: Final[float] = 5.0
_SQLITE_MEMORY_DB: Final[str] = ":memory:"
_SQL_PRAGMA_WAL: Final[str] = "PRAGMA journal_mode=WAL;"
_SQL_PRAGMA_SYNC_NORMAL: Final[str] = "PRAGMA synchronous=NORMAL;"
_SQL_CREATE_LEDGER_TABLE: Final[str] = """
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
_SQL_CREATE_STATUS_INDEX: Final[str] = (
    "CREATE INDEX IF NOT EXISTS idx_cresmo_ledger_status ON cresmo_ledger(status);"
)
_SQL_SELECT_STATUS: Final[str] = "SELECT status FROM cresmo_ledger WHERE content_id = ?;"
_SQL_UPSERT_ENTRY: Final[str] = """
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
"""
_SQL_SELECT_ENTRY: Final[str] = "SELECT * FROM cresmo_ledger WHERE content_id = ?;"
_COL_CONTENT_ID: Final[str] = "content_id"
_COL_MEDIA_URL: Final[str] = "media_url"
_COL_TITLE: Final[str] = "title"
_COL_CHANNEL_NAME: Final[str] = "channel_name"
_COL_STATUS: Final[str] = "status"
_COL_NOTES_COUNT: Final[str] = "notes_count"
_COL_ERROR_MESSAGE: Final[str] = "error_message"
_COL_STARTED_AT: Final[str] = "started_at"
_COL_COMPLETED_AT: Final[str] = "completed_at"


class SqliteLedgerAdapter(LedgerRepositoryPort):
    """ACID SQLite ledger persistence adapter in Write-Ahead Logging (WAL) mode.

    Provides transactional persistence for processing audit trails, ensuring idempotency
    and preventing duplicate transcription/synthesis across multi-worker executions.

    Conforms to:
        - ADR-003: PES Production Architecture & Telemetry
        - SPEC-003: Channel Synchronization Specifications
    """

    def __init__(
        self,
        db_path: Path | str,
        timeout: float = DEFAULT_SQLITE_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != _SQLITE_MEMORY_DB:
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection]:
        """Create, configure, and safely close a connection with standard pragmas.

        Yields:
            Configured sqlite3.Connection with Row row_factory and WAL journal mode.
        """
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        try:
            conn.row_factory = sqlite3.Row
            # Enforce WAL mode and NORMAL synchronous to maximize write throughput without data corruption
            if self._db_path != _SQLITE_MEMORY_DB:
                conn.execute(_SQL_PRAGMA_WAL)
            conn.execute(_SQL_PRAGMA_SYNC_NORMAL)
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema and indices if not already present."""
        with self._get_connection() as conn:
            conn.execute(_SQL_CREATE_LEDGER_TABLE)
            conn.execute(_SQL_CREATE_STATUS_INDEX)

    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages.

        Args:
            content_id: Video or media identifier to check.

        Returns:
            True if status is COMPLETED; False otherwise.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(_SQL_SELECT_STATUS, (content_id.value,))
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row[_COL_STATUS]) == PipelineStatus.COMPLETED.value

    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically.

        Args:
            entry: LedgerEntry domain value object representing the processing state.
        """
        started_iso = entry.started_at.isoformat() if entry.started_at else None
        completed_iso = entry.completed_at.isoformat() if entry.completed_at else None

        with self._get_connection() as conn:
            conn.execute(
                _SQL_UPSERT_ENTRY,
                (
                    entry.content_id.value,
                    entry.media_url,
                    entry.title,
                    str(entry.channel_name),
                    entry.status.value,
                    entry.notes_count,
                    entry.error_message,
                    started_iso,
                    completed_iso,
                ),
            )

    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID.

        Args:
            content_id: Video or media identifier to look up.

        Returns:
            LedgerEntry if record exists, or None.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(_SQL_SELECT_ENTRY, (content_id.value,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry.

        Args:
            row: SQLite row containing ledger table columns.

        Returns:
            Hydrated immutable LedgerEntry value object.
        """
        started_at = datetime.fromisoformat(row[_COL_STARTED_AT]) if row[_COL_STARTED_AT] else None
        completed_at = (
            datetime.fromisoformat(row[_COL_COMPLETED_AT]) if row[_COL_COMPLETED_AT] else None
        )
        return LedgerEntry(
            content_id=ContentId(str(row[_COL_CONTENT_ID])),
            media_url=str(row[_COL_MEDIA_URL]),
            title=str(row[_COL_TITLE]),
            channel_name=ChannelName(str(row[_COL_CHANNEL_NAME])),
            status=PipelineStatus(str(row[_COL_STATUS])),
            notes_count=int(row[_COL_NOTES_COUNT]),
            error_message=str(row[_COL_ERROR_MESSAGE]) if row[_COL_ERROR_MESSAGE] else None,
            started_at=started_at,
            completed_at=completed_at,
        )
