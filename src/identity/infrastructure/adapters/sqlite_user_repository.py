"""SQLite WAL implementations of UserRepositoryPort and PersonalAccessTokenRepositoryPort."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Final

from identity.application.ports import PersonalAccessTokenRepositoryPort, UserRepositoryPort
from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import UserAlreadyExistsError
from identity.domain.value_objects import Email, HashedPassword, Role, Scope, TokenHash, UserId

DEFAULT_SQLITE_TIMEOUT_SECONDS: Final[float] = 10.0

_CSV_COLLECTION_DELIMITER: Final[str] = ","
_SQLITE_BOOL_TRUE: Final[int] = 1
_SQLITE_BOOL_FALSE: Final[int] = 0
_SQLITE_UNIQUE_EMAIL_ERROR_MARKER: Final[str] = "UNIQUE constraint failed: users.email"

_COL_ID: Final[str] = "id"
_COL_EMAIL: Final[str] = "email"
_COL_HASHED_PASSWORD: Final[str] = "hashed_password"
_COL_ROLES: Final[str] = "roles"
_COL_IS_ACTIVE: Final[str] = "is_active"
_COL_CREATED_AT: Final[str] = "created_at"
_COL_UPDATED_AT: Final[str] = "updated_at"
_COL_USER_ID: Final[str] = "user_id"
_COL_NAME: Final[str] = "name"
_COL_TOKEN_PREFIX: Final[str] = "token_prefix"
_COL_TOKEN_HASH: Final[str] = "token_hash"
_COL_SCOPES: Final[str] = "scopes"
_COL_EXPIRES_AT: Final[str] = "expires_at"
_COL_LAST_USED_AT: Final[str] = "last_used_at"
_COL_IS_REVOKED: Final[str] = "is_revoked"

_SQL_PRAGMA_JOURNAL_WAL: Final[str] = "PRAGMA journal_mode=WAL;"
_SQL_PRAGMA_SYNCHRONOUS_NORMAL: Final[str] = "PRAGMA synchronous=NORMAL;"
_SQL_PRAGMA_FOREIGN_KEYS_ON: Final[str] = "PRAGMA foreign_keys=ON;"

_SQL_CREATE_USERS_TABLE: Final[str] = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        roles TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
"""
_SQL_CREATE_PATS_TABLE: Final[str] = """
    CREATE TABLE IF NOT EXISTS personal_access_tokens (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        token_prefix TEXT NOT NULL,
        token_hash TEXT UNIQUE NOT NULL,
        scopes TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT,
        last_used_at TEXT,
        is_revoked INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
"""
_SQL_CREATE_USERS_EMAIL_INDEX: Final[str] = "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
_SQL_CREATE_PAT_HASH_INDEX: Final[str] = (
    "CREATE INDEX IF NOT EXISTS idx_pat_token_hash ON personal_access_tokens(token_hash);"
)
_SQL_CREATE_PAT_USER_INDEX: Final[str] = (
    "CREATE INDEX IF NOT EXISTS idx_pat_user_id ON personal_access_tokens(user_id);"
)
_SQL_UPSERT_USER: Final[str] = """
    INSERT INTO users (id, email, hashed_password, roles, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        email=excluded.email,
        hashed_password=excluded.hashed_password,
        roles=excluded.roles,
        is_active=excluded.is_active,
        updated_at=excluded.updated_at
"""
_SQL_SELECT_USER_BY_ID: Final[str] = "SELECT * FROM users WHERE id = ?"
_SQL_SELECT_USER_BY_EMAIL: Final[str] = "SELECT * FROM users WHERE email = ?"
_SQL_INSERT_PAT: Final[str] = """
    INSERT INTO personal_access_tokens (
        id, user_id, name, token_prefix, token_hash, scopes, created_at, expires_at, last_used_at, is_revoked
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        last_used_at=excluded.last_used_at,
        is_revoked=excluded.is_revoked
"""
_SQL_SELECT_PAT_BY_HASH: Final[str] = "SELECT * FROM personal_access_tokens WHERE token_hash = ?"
_SQL_LIST_PATS_BY_USER: Final[str] = (
    "SELECT * FROM personal_access_tokens WHERE user_id = ? ORDER BY created_at DESC"
)
_SQL_REVOKE_PAT: Final[str] = (
    "UPDATE personal_access_tokens SET is_revoked = 1 WHERE id = ? AND user_id = ?"
)


def get_sqlite_connection(db_path: Path | str) -> sqlite3.Connection:
    """Returns an optimized SQLite WAL connection with foreign keys enabled."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=DEFAULT_SQLITE_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    conn.execute(_SQL_PRAGMA_JOURNAL_WAL)
    conn.execute(_SQL_PRAGMA_SYNCHRONOUS_NORMAL)
    conn.execute(_SQL_PRAGMA_FOREIGN_KEYS_ON)
    return conn


def init_identity_database(db_path: Path | str) -> None:
    """Initializes users and personal_access_tokens schema."""
    with get_sqlite_connection(db_path) as conn:
        conn.execute(_SQL_CREATE_USERS_TABLE)
        conn.execute(_SQL_CREATE_PATS_TABLE)
        conn.execute(_SQL_CREATE_USERS_EMAIL_INDEX)
        conn.execute(_SQL_CREATE_PAT_HASH_INDEX)
        conn.execute(_SQL_CREATE_PAT_USER_INDEX)


class SqliteUserRepositoryAdapter(UserRepositoryPort):
    """Hermetic SQLite storage for Users with WAL mode."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        init_identity_database(self._db_path)

    def save(self, user: User) -> None:
        roles_str = _CSV_COLLECTION_DELIMITER.join(r.value for r in user.roles)
        try:
            with get_sqlite_connection(self._db_path) as conn:
                conn.execute(
                    _SQL_UPSERT_USER,
                    (
                        user.id.value,
                        user.email.value,
                        user.hashed_password.value,
                        roles_str,
                        _SQLITE_BOOL_TRUE if user.is_active else _SQLITE_BOOL_FALSE,
                        user.created_at.isoformat(),
                        user.updated_at.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as e:
            if _SQLITE_UNIQUE_EMAIL_ERROR_MARKER in str(e):
                raise UserAlreadyExistsError(
                    f"User with email '{user.email.value}' already exists."
                ) from e
            raise

    def get_by_id(self, user_id: UserId) -> User | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(_SQL_SELECT_USER_BY_ID, (user_id.value,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def get_by_email(self, email: Email) -> User | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(_SQL_SELECT_USER_BY_EMAIL, (email.value,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def update(self, user: User) -> None:
        self.save(user)

    def _row_to_user(self, row: sqlite3.Row) -> User:
        roles = frozenset(
            Role(r) for r in row[_COL_ROLES].split(_CSV_COLLECTION_DELIMITER) if r
        )
        return User(
            id=UserId(row[_COL_ID]),
            email=Email(row[_COL_EMAIL]),
            hashed_password=HashedPassword(row[_COL_HASHED_PASSWORD]),
            roles=roles,
            is_active=bool(row[_COL_IS_ACTIVE]),
            created_at=datetime.fromisoformat(row[_COL_CREATED_AT]),
            updated_at=datetime.fromisoformat(row[_COL_UPDATED_AT]),
        )


class SqlitePersonalAccessTokenRepositoryAdapter(PersonalAccessTokenRepositoryPort):
    """Hermetic SQLite storage for Personal Access Tokens with WAL mode."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        init_identity_database(self._db_path)

    def save(self, pat: PersonalAccessToken) -> None:
        scopes_str = _CSV_COLLECTION_DELIMITER.join(s.value for s in pat.scopes)
        with get_sqlite_connection(self._db_path) as conn:
            conn.execute(
                _SQL_INSERT_PAT,
                (
                    pat.id,
                    pat.user_id.value,
                    pat.name,
                    pat.token_prefix,
                    pat.token_hash.value,
                    scopes_str,
                    pat.created_at.isoformat(),
                    pat.expires_at.isoformat() if pat.expires_at else None,
                    pat.last_used_at.isoformat() if pat.last_used_at else None,
                    _SQLITE_BOOL_TRUE if pat.is_revoked else _SQLITE_BOOL_FALSE,
                ),
            )

    def get_by_hash(self, token_hash: TokenHash) -> PersonalAccessToken | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(_SQL_SELECT_PAT_BY_HASH, (token_hash.value,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_pat(row)

    def list_by_user(self, user_id: UserId) -> list[PersonalAccessToken]:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(_SQL_LIST_PATS_BY_USER, (user_id.value,))
            return [self._row_to_pat(r) for r in cursor.fetchall()]

    def revoke(self, token_id: str, user_id: UserId) -> bool:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(_SQL_REVOKE_PAT, (token_id, user_id.value))
            return cursor.rowcount > 0

    def _row_to_pat(self, row: sqlite3.Row) -> PersonalAccessToken:
        scopes = frozenset(
            Scope(s) for s in row[_COL_SCOPES].split(_CSV_COLLECTION_DELIMITER) if s
        )
        return PersonalAccessToken(
            id=row[_COL_ID],
            user_id=UserId(row[_COL_USER_ID]),
            name=row[_COL_NAME],
            token_prefix=row[_COL_TOKEN_PREFIX],
            token_hash=TokenHash(row[_COL_TOKEN_HASH]),
            scopes=scopes,
            created_at=datetime.fromisoformat(row[_COL_CREATED_AT]),
            expires_at=datetime.fromisoformat(row[_COL_EXPIRES_AT])
            if row[_COL_EXPIRES_AT]
            else None,
            last_used_at=datetime.fromisoformat(row[_COL_LAST_USED_AT])
            if row[_COL_LAST_USED_AT]
            else None,
            is_revoked=bool(row[_COL_IS_REVOKED]),
        )
