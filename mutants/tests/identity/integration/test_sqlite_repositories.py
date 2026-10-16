"""Integration tests for SQLite IAM repository adapters.

Tests SqliteUserRepositoryAdapter and SqlitePersonalAccessTokenRepositoryAdapter.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import UserAlreadyExistsError
from identity.domain.value_objects import Email, HashedPassword, Role, Scope, TokenHash, UserId
from identity.infrastructure.adapters.sqlite_user_repository import (
    SqlitePersonalAccessTokenRepositoryAdapter,
    SqliteUserRepositoryAdapter,
)


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_identity.db"


class TestSqliteUserRepositoryAdapter:
    def test_save_and_retrieve_user(self, temp_db_path: Path) -> None:
        repo = SqliteUserRepositoryAdapter(temp_db_path)
        user = User(
            id=UserId("usr_integration_1"),
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.ADMIN, Role.USER]),
        )

        repo.save(user)

        retrieved = repo.get_by_id(UserId("usr_integration_1"))
        assert retrieved is not None
        assert retrieved.id.value == "usr_integration_1"
        assert retrieved.email.value == "test@example.com"
        assert Role.ADMIN in retrieved.roles
        assert Role.USER in retrieved.roles

        by_email = repo.get_by_email(Email("TEST@example.COM"))
        assert by_email is not None
        assert by_email.id == user.id

    def test_save_duplicate_email_raises_user_already_exists(self, temp_db_path: Path) -> None:
        repo = SqliteUserRepositoryAdapter(temp_db_path)
        user1 = User(
            id=UserId("usr_1"),
            email=Email("dupe@example.com"),
            hashed_password=HashedPassword("$argon2id$1"),
        )
        user2 = User(
            id=UserId("usr_2"),
            email=Email("dupe@example.com"),
            hashed_password=HashedPassword("$argon2id$2"),
        )

        repo.save(user1)
        with pytest.raises(UserAlreadyExistsError):
            repo.save(user2)


class TestSqlitePersonalAccessTokenRepositoryAdapter:
    def test_save_and_retrieve_pat(self, temp_db_path: Path) -> None:
        user_repo = SqliteUserRepositoryAdapter(temp_db_path)
        pat_repo = SqlitePersonalAccessTokenRepositoryAdapter(temp_db_path)

        user = User(
            id=UserId("usr_pat_owner"),
            email=Email("pat_owner@example.com"),
            hashed_password=HashedPassword("$argon2id$hash"),
        )
        user_repo.save(user)

        token_hash = TokenHash.from_raw_token("cresmo_pat_1234567890abcdef")
        pat = PersonalAccessToken(
            id="pat_int_01",
            user_id=user.id,
            name="Deploy Key",
            token_prefix="cresmo_pat_1234",
            token_hash=token_hash,
            scopes=frozenset([Scope("cresmo:sync")]),
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        pat_repo.save(pat)

        retrieved = pat_repo.get_by_hash(token_hash)
        assert retrieved is not None
        assert retrieved.id == "pat_int_01"
        assert retrieved.name == "Deploy Key"
        assert retrieved.has_scope(Scope("cresmo:sync")) is True

        # Test listing by user
        tokens = pat_repo.list_by_user(user.id)
        assert len(tokens) == 1
        assert tokens[0].id == "pat_int_01"

        # Test revocation
        revoked = pat_repo.revoke("pat_int_01", user.id)
        assert revoked is True

        re_retrieved = pat_repo.get_by_hash(token_hash)
        assert re_retrieved is not None
        assert re_retrieved.is_revoked is True
        assert re_retrieved.is_active is False
