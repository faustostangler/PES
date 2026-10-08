"""SQLite WAL implementations of UserRepositoryPort and PersonalAccessTokenRepositoryPort."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from identity.application.ports import PersonalAccessTokenRepositoryPort, UserRepositoryPort
from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import UserAlreadyExistsError
from identity.domain.value_objects import Email, HashedPassword, Role, Scope, TokenHash, UserId


def get_sqlite_connection(db_path: Path | str) -> sqlite3.Connection:
    """Returns an optimized SQLite WAL connection with foreign keys enabled."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_identity_database(db_path: Path | str) -> None:
    """Initializes users and personal_access_tokens schema."""
    with get_sqlite_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                roles TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        conn.execute("""
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
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_pat_token_hash ON personal_access_tokens(token_hash);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_pat_user_id ON personal_access_tokens(user_id);"
        )


class SqliteUserRepositoryAdapter(UserRepositoryPort):
    """Hermetic SQLite storage for Users with WAL mode."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        init_identity_database(self._db_path)

    def save(self, user: User) -> None:
        roles_str = ",".join(r.value for r in user.roles)
        query = """
            INSERT INTO users (id, email, hashed_password, roles, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                email=excluded.email,
                hashed_password=excluded.hashed_password,
                roles=excluded.roles,
                is_active=excluded.is_active,
                updated_at=excluded.updated_at
        """
        try:
            with get_sqlite_connection(self._db_path) as conn:
                conn.execute(
                    query,
                    (
                        user.id.value,
                        user.email.value,
                        user.hashed_password.value,
                        roles_str,
                        1 if user.is_active else 0,
                        user.created_at.isoformat(),
                        user.updated_at.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                raise UserAlreadyExistsError(
                    f"User with email '{user.email.value}' already exists."
                ) from e
            raise

    def get_by_id(self, user_id: UserId) -> User | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id.value,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def get_by_email(self, email: Email) -> User | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email.value,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def update(self, user: User) -> None:
        self.save(user)

    def _row_to_user(self, row: sqlite3.Row) -> User:
        roles = frozenset(Role(r) for r in row["roles"].split(",") if r)
        return User(
            id=UserId(row["id"]),
            email=Email(row["email"]),
            hashed_password=HashedPassword(row["hashed_password"]),
            roles=roles,
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class SqlitePersonalAccessTokenRepositoryAdapter(PersonalAccessTokenRepositoryPort):
    """Hermetic SQLite storage for Personal Access Tokens with WAL mode."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        init_identity_database(self._db_path)

    def save(self, pat: PersonalAccessToken) -> None:
        scopes_str = ",".join(s.value for s in pat.scopes)
        query = """
            INSERT INTO personal_access_tokens (
                id, user_id, name, token_prefix, token_hash, scopes, created_at, expires_at, last_used_at, is_revoked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                last_used_at=excluded.last_used_at,
                is_revoked=excluded.is_revoked
        """
        with get_sqlite_connection(self._db_path) as conn:
            conn.execute(
                query,
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
                    1 if pat.is_revoked else 0,
                ),
            )

    def get_by_hash(self, token_hash: TokenHash) -> PersonalAccessToken | None:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM personal_access_tokens WHERE token_hash = ?",
                (token_hash.value,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_pat(row)

    def list_by_user(self, user_id: UserId) -> list[PersonalAccessToken]:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM personal_access_tokens WHERE user_id = ? ORDER BY created_at DESC",
                (user_id.value,),
            )
            return [self._row_to_pat(r) for r in cursor.fetchall()]

    def revoke(self, token_id: str, user_id: UserId) -> bool:
        with get_sqlite_connection(self._db_path) as conn:
            cursor = conn.execute(
                "UPDATE personal_access_tokens SET is_revoked = 1 WHERE id = ? AND user_id = ?",
                (token_id, user_id.value),
            )
            return cursor.rowcount > 0

    def _row_to_pat(self, row: sqlite3.Row) -> PersonalAccessToken:
        scopes = frozenset(Scope(s) for s in row["scopes"].split(",") if s)
        return PersonalAccessToken(
            id=row["id"],
            user_id=UserId(row["user_id"]),
            name=row["name"],
            token_prefix=row["token_prefix"],
            token_hash=TokenHash(row["token_hash"]),
            scopes=scopes,
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            last_used_at=datetime.fromisoformat(row["last_used_at"])
            if row["last_used_at"]
            else None,
            is_revoked=bool(row["is_revoked"]),
        )
