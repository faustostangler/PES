"""Unit tests for IAM Bounded Context Domain Layer (Value Objects and Entities).

Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
"""

from datetime import UTC, datetime, timedelta

import pytest

from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidEmailError,
    InvalidUserIdError,
)
from identity.domain.value_objects import (
    Email,
    HashedPassword,
    Role,
    Scope,
    TokenHash,
    UserId,
)


class TestUserIdValueObject:
    def test_valid_user_id(self) -> None:
        uid = UserId("usr_01hqz8b7m3e000000000000000")
        assert uid.value == "usr_01hqz8b7m3e000000000000000"
        assert str(uid) == "usr_01hqz8b7m3e000000000000000"

    def test_empty_or_whitespace_user_id_raises_error(self) -> None:
        with pytest.raises(InvalidUserIdError):
            UserId("")

        with pytest.raises(InvalidUserIdError):
            UserId("   ")


class TestEmailValueObject:
    def test_valid_email_normalizes_to_lowercase(self) -> None:
        email = Email("  Admin.User@Example.COM  ")
        assert email.value == "admin.user@example.com"
        assert str(email) == "admin.user@example.com"

    def test_invalid_email_format_raises_error(self) -> None:
        for invalid in ["not-an-email", "@example.com", "user@", "user @example.com", ""]:
            with pytest.raises(InvalidEmailError):
                Email(invalid)


class TestHashedPasswordValueObject:
    def test_valid_hashed_password(self) -> None:
        hash_str = "$argon2id$v=19$m=65536,t=3,p=4$some_salt$some_hash"
        hp = HashedPassword(hash_str)
        assert hp.value == hash_str

    def test_empty_hashed_password_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            HashedPassword("")


class TestPersonalAccessTokenEntity:
    def test_create_valid_pat(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_sec_random_string_1234567890")

        pat = PersonalAccessToken(
            id="pat_001",
            user_id=user_id,
            name="CLI Token",
            token_prefix="cresmo_pat_sec",
            token_hash=token_hash,
            scopes=frozenset([Scope("cresmo:read"), Scope("cresmo:sync")]),
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )

        assert pat.is_active is True
        assert pat.has_scope(Scope("cresmo:read")) is True
        assert pat.has_scope(Scope("cresmo:write")) is False

    def test_pat_expired_is_not_active(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_expired")
        past = datetime.now(UTC) - timedelta(days=1)

        pat = PersonalAccessToken(
            id="pat_002",
            user_id=user_id,
            name="Expired Token",
            token_prefix="cresmo_pat_exp",
            token_hash=token_hash,
            scopes=frozenset([Scope("cresmo:read")]),
            created_at=past - timedelta(days=10),
            expires_at=past,
        )
        assert pat.is_active is False

    def test_revoked_pat_is_not_active(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_revoked")

        pat = PersonalAccessToken(
            id="pat_003",
            user_id=user_id,
            name="Revoked Token",
            token_prefix="cresmo_pat_rev",
            token_hash=token_hash,
            scopes=frozenset([Scope("cresmo:read")]),
            created_at=datetime.now(UTC),
            is_revoked=True,
        )
        assert pat.is_active is False


class TestUserAggregate:
    def test_create_active_user(self) -> None:
        user = User(
            id=UserId("usr_999"),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.USER]),
        )
        assert user.is_active is True
        assert Role.USER in user.roles
        assert user.has_role(Role.USER) is True
        assert user.has_role(Role.ADMIN) is False

    def test_deactivate_and_activate_user(self) -> None:
        user = User(
            id=UserId("usr_999"),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.USER]),
        )
        user.deactivate()
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    def test_updating_password_on_inactive_user_raises_error(self) -> None:
        user = User(
            id=UserId("usr_999"),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.USER]),
            is_active=False,
        )
        with pytest.raises(InactiveUserError):
            user.change_password(HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$newsalt$newhash"))
