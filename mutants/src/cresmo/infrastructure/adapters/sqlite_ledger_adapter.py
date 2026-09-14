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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut: MutantDict = {}  # type: ignore
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut: MutantDict = {}  # type: ignore


class SqliteLedgerAdapter(LedgerRepositoryPort):
    """ACID SQLite ledger persistence adapter in Write-Ahead Logging (WAL) mode."""

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁ__init____mutmut)
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

    def xǁSqliteLedgerAdapterǁ__init____mutmut_orig(self, db_path: Path | str, timeout: float = 5.0) -> None:
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

    def xǁSqliteLedgerAdapterǁ__init____mutmut_1(self, db_path: Path | str, timeout: float = 6.0) -> None:
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

    def xǁSqliteLedgerAdapterǁ__init____mutmut_2(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = None
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_3(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(None)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_4(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = None

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_5(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path == ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_6(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != "XX:memory:XX":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_7(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":MEMORY:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_8(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = None
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_9(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(None)
            target_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_10(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=None, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_11(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=None)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_12(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_13(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, )

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_14(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=False, exist_ok=True)

        self._init_db()

    def xǁSqliteLedgerAdapterǁ__init____mutmut_15(self, db_path: Path | str, timeout: float = 5.0) -> None:
        """Initialize SQLite ledger adapter and ensure WAL schema invariants.

        Args:
            db_path: Path to the SQLite database file or ':memory:'.
            timeout: Busy timeout in seconds before raising sqlite3.OperationalError.
        """
        self._db_path = str(db_path)
        self._timeout = timeout

        if self._db_path != ":memory:":
            target_path = Path(self._db_path)
            target_path.parent.mkdir(parents=True, exist_ok=False)

        self._init_db()

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut)
    def _get_connection(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_orig(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_1(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = None
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_2(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(None, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_3(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=None)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_4(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_5(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, )
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_6(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = None
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_7(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path == ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_8(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != "XX:memory:XX":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_9(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":MEMORY:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_10(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute(None)
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_11(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("XXPRAGMA journal_mode=WAL;XX")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_12(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("pragma journal_mode=wal;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_13(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA JOURNAL_MODE=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_14(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(None)
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_15(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("XXPRAGMA synchronous=NORMAL;XX")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_16(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("pragma synchronous=normal;")
        return conn

    def xǁSqliteLedgerAdapterǁ_get_connection__mutmut_17(self) -> sqlite3.Connection:
        """Create and configure a connection with standard pragmas."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        # Enforce WAL mode and NORMAL synchronous
        if self._db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA SYNCHRONOUS=NORMAL;")
        return conn

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut)
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

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_orig(self) -> None:
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

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_1(self) -> None:
        """Initialize database schema if not already present."""
        with self._get_connection() as conn:
            conn.execute(
                None
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cresmo_ledger_status ON cresmo_ledger(status);"
            )

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_2(self) -> None:
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
                None
            )

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_3(self) -> None:
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
                "XXCREATE INDEX IF NOT EXISTS idx_cresmo_ledger_status ON cresmo_ledger(status);XX"
            )

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_4(self) -> None:
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
                "create index if not exists idx_cresmo_ledger_status on cresmo_ledger(status);"
            )

    def xǁSqliteLedgerAdapterǁ_init_db__mutmut_5(self) -> None:
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
                "CREATE INDEX IF NOT EXISTS IDX_CRESMO_LEDGER_STATUS ON CRESMO_LEDGER(STATUS);"
            )

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut)
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

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_orig(self, content_id: ContentId) -> bool:
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

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_1(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = None
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_2(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                None,
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_3(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                None,
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_4(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_5(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_6(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "XXSELECT status FROM cresmo_ledger WHERE content_id = ?;XX",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_7(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "select status from cresmo_ledger where content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_8(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT STATUS FROM CRESMO_LEDGER WHERE CONTENT_ID = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_9(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = None
            if row is None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_10(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is not None:
                return False
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_11(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return True
            return str(row["status"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_12(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(None) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_13(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["XXstatusXX"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_14(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["STATUS"]) == PipelineStatus.COMPLETED.value

    def xǁSqliteLedgerAdapterǁis_processed__mutmut_15(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["status"]) != PipelineStatus.COMPLETED.value

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut)
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_orig(self, content_id: ContentId) -> None:
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_1(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        now_iso = None
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_2(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        now_iso = datetime.now(None).isoformat()
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_3(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        now_iso = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                None,
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_4(self, content_id: ContentId) -> None:
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
                None,
            )

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_5(self, content_id: ContentId) -> None:
        """Record content item as successfully processed."""
        now_iso = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            conn.execute(
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

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_6(self, content_id: ContentId) -> None:
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
                )

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_7(self, content_id: ContentId) -> None:
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
                    "XXDefaultChannelXX",
                    PipelineStatus.COMPLETED.value,
                    0,
                    now_iso,
                ),
            )

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_8(self, content_id: ContentId) -> None:
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
                    "defaultchannel",
                    PipelineStatus.COMPLETED.value,
                    0,
                    now_iso,
                ),
            )

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_9(self, content_id: ContentId) -> None:
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
                    "DEFAULTCHANNEL",
                    PipelineStatus.COMPLETED.value,
                    0,
                    now_iso,
                ),
            )

    def xǁSqliteLedgerAdapterǁmark_processed__mutmut_10(self, content_id: ContentId) -> None:
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
                    1,
                    now_iso,
                ),
            )

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut)
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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_orig(self, entry: LedgerEntry) -> None:
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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_1(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        started_iso = None
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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_2(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        started_iso = entry.started_at.isoformat() if entry.started_at else None
        completed_iso = None

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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_3(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        started_iso = entry.started_at.isoformat() if entry.started_at else None
        completed_iso = entry.completed_at.isoformat() if entry.completed_at else None

        with self._get_connection() as conn:
            conn.execute(
                None,
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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_4(self, entry: LedgerEntry) -> None:
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
                None,
            )

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_5(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically."""
        started_iso = entry.started_at.isoformat() if entry.started_at else None
        completed_iso = entry.completed_at.isoformat() if entry.completed_at else None

        with self._get_connection() as conn:
            conn.execute(
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

    def xǁSqliteLedgerAdapterǁsave_entry__mutmut_6(self, entry: LedgerEntry) -> None:
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
                )

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut)
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

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_orig(self, content_id: ContentId) -> LedgerEntry | None:
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

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_1(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = None
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_2(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                None,
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_3(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                None,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_4(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_5(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_6(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "XXSELECT * FROM cresmo_ledger WHERE content_id = ?;XX",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_7(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "select * from cresmo_ledger where content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_8(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM CRESMO_LEDGER WHERE CONTENT_ID = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_9(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = None
            if row is None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_10(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is not None:
                return None
            return self._row_to_entry(row)

    def xǁSqliteLedgerAdapterǁget_entry__mutmut_11(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger WHERE content_id = ?;",
                (content_id.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(None)

    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut)
    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_orig(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_1(self, limit: int = 101) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_2(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = None
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_3(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                None,
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_4(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                None,
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_5(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_6(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_7(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "XXSELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;XX",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_8(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "select * from cresmo_ledger order by rowid desc limit ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_9(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM CRESMO_LEDGER ORDER BY ROWID DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def xǁSqliteLedgerAdapterǁlist_entries__mutmut_10(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cresmo_ledger ORDER BY rowid DESC LIMIT ?;",
                (limit,),
            )
            return [self._row_to_entry(None) for row in cursor.fetchall()]

    @staticmethod
    @_mutmut_mutated(mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut)
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_orig(row: sqlite3.Row) -> LedgerEntry:
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_1(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_2(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(None) if row["started_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_3(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["XXstarted_atXX"]) if row["started_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_4(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["STARTED_AT"]) if row["started_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_5(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["XXstarted_atXX"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_6(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["STARTED_AT"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_7(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_8(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(None) if row["completed_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_9(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["XXcompleted_atXX"]) if row["completed_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_10(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["COMPLETED_AT"]) if row["completed_at"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_11(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["XXcompleted_atXX"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_12(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["COMPLETED_AT"] else None
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

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_13(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=None,
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_14(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=None,
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_15(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=None,
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_16(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=None,
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_17(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=None,
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_18(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=None,
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_19(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_20(row: sqlite3.Row) -> LedgerEntry:
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
            started_at=None,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_21(row: sqlite3.Row) -> LedgerEntry:
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
            completed_at=None,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_22(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_23(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_24(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_25(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_26(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_27(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_28(row: sqlite3.Row) -> LedgerEntry:
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
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_29(row: sqlite3.Row) -> LedgerEntry:
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
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_30(row: sqlite3.Row) -> LedgerEntry:
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
            )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_31(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(None),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_32(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(None)),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_33(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["XXcontent_idXX"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_34(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["CONTENT_ID"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_35(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(None),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_36(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["XXmedia_urlXX"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_37(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["MEDIA_URL"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_38(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(None),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_39(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["XXtitleXX"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_40(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["TITLE"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_41(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(None),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_42(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["XXchannel_nameXX"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_43(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["CHANNEL_NAME"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_44(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(None),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_45(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(None)),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_46(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["XXstatusXX"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_47(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["STATUS"])),
            notes_count=int(row["notes_count"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_48(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(None),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_49(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["XXnotes_countXX"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_50(row: sqlite3.Row) -> LedgerEntry:
        """Convert a sqlite3.Row to an immutable LedgerEntry."""
        started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return LedgerEntry(
            content_id=ContentId(str(row["content_id"])),
            media_url=str(row["media_url"]),
            title=str(row["title"]),
            channel_name=str(row["channel_name"]),
            status=PipelineStatus(str(row["status"])),
            notes_count=int(row["NOTES_COUNT"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_51(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=str(None) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_52(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=str(row["XXerror_messageXX"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_53(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=str(row["ERROR_MESSAGE"]) if row["error_message"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_54(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=str(row["error_message"]) if row["XXerror_messageXX"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_55(row: sqlite3.Row) -> LedgerEntry:
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
            error_message=str(row["error_message"]) if row["ERROR_MESSAGE"] else None,
            started_at=started_at,
            completed_at=completed_at,
        )

mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_11'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_12'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_13'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_14'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ__init____mutmut['xǁSqliteLedgerAdapterǁ__init____mutmut_15'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ__init____mutmut_15 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_11'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_12'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_13'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_14'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_15'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_16'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_get_connection__mutmut['xǁSqliteLedgerAdapterǁ_get_connection__mutmut_17'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_get_connection__mutmut_17 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['xǁSqliteLedgerAdapterǁ_init_db__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['xǁSqliteLedgerAdapterǁ_init_db__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['xǁSqliteLedgerAdapterǁ_init_db__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['xǁSqliteLedgerAdapterǁ_init_db__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_init_db__mutmut['xǁSqliteLedgerAdapterǁ_init_db__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_init_db__mutmut_5 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_11'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_12'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_13'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_14'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁis_processed__mutmut['xǁSqliteLedgerAdapterǁis_processed__mutmut_15'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁis_processed__mutmut_15 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁmark_processed__mutmut['xǁSqliteLedgerAdapterǁmark_processed__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁmark_processed__mutmut_10 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁsave_entry__mutmut['xǁSqliteLedgerAdapterǁsave_entry__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁsave_entry__mutmut_6 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁget_entry__mutmut['xǁSqliteLedgerAdapterǁget_entry__mutmut_11'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁget_entry__mutmut_11 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁlist_entries__mutmut['xǁSqliteLedgerAdapterǁlist_entries__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁlist_entries__mutmut_10 # type: ignore # mutmut generated

mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['_mutmut_orig'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_1'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_2'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_3'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_4'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_5'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_6'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_7'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_8'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_9'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_10'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_11'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_12'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_13'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_14'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_15'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_16'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_17'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_17 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_18'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_18 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_19'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_19 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_20'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_20 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_21'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_21 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_22'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_23'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_23 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_24'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_24 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_25'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_25 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_26'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_26 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_27'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_27 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_28'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_28 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_29'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_29 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_30'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_30 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_31'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_31 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_32'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_32 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_33'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_33 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_34'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_34 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_35'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_35 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_36'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_36 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_37'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_37 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_38'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_38 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_39'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_39 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_40'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_40 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_41'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_41 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_42'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_42 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_43'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_43 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_44'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_44 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_45'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_45 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_46'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_46 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_47'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_47 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_48'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_48 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_49'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_49 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_50'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_50 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_51'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_51 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_52'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_52 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_53'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_53 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_54'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_54 # type: ignore # mutmut generated
mutants_xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut['xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_55'] = SqliteLedgerAdapter.xǁSqliteLedgerAdapterǁ_row_to_entry__mutmut_55 # type: ignore # mutmut generated
