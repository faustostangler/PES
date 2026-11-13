"""Unit tests for IAM Bounded Context Domain Layer (Value Objects and Entities).

Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
Conforms to:
- ADR-048: Comprehensive Mutation Blindage
- SPEC-048: Identity Domain Invariants & Mutation Blindage
"""

import hashlib
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
        with pytest.raises(InvalidUserIdError) as exc_empty:
            UserId("")
        assert exc_empty.value.args[0] == "UserId cannot be empty or whitespace."

        with pytest.raises(InvalidUserIdError) as exc_ws:
            UserId("   ")
        assert exc_ws.value.args[0] == "UserId cannot be empty or whitespace."


class TestEmailValueObject:
    def test_valid_email_normalizes_to_lowercase(self) -> None:
        email = Email("  Admin.User@Example.COM  ")
        assert email.value == "admin.user@example.com"
        assert str(email) == "admin.user@example.com"

    def test_invalid_email_format_raises_error(self) -> None:
        for invalid in ["not-an-email", "@example.com", "user@", "user @example.com"]:
            with pytest.raises(InvalidEmailError) as exc_info:
                Email(invalid)
            assert exc_info.value.args[0] == f"Invalid email address format: '{invalid}'"

    def test_non_string_or_empty_email_raises_error(self) -> None:
        with pytest.raises(InvalidEmailError) as exc_none:
            Email(None)  # type: ignore[arg-type]
        assert exc_none.value.args[0] == "Email must be a non-empty string."

        with pytest.raises(InvalidEmailError) as exc_int:
            Email(12345)  # type: ignore[arg-type]
        assert exc_int.value.args[0] == "Email must be a non-empty string."

        with pytest.raises(InvalidEmailError) as exc_empty:
            Email("")
        assert exc_empty.value.args[0] == "Email must be a non-empty string."

        with pytest.raises(InvalidEmailError) as exc_ws:
            Email("   ")
        assert exc_ws.value.args[0] == "Invalid email address format: '   '"


class TestHashedPasswordValueObject:
    def test_valid_hashed_password(self) -> None:
        hash_str = "$argon2id$v=19$m=65536,t=3,p=4$some_salt$some_hash"
        hp = HashedPassword(hash_str)
        assert hp.value == hash_str
        assert str(hp) == hash_str

    def test_empty_or_whitespace_hashed_password_raises_error(self) -> None:
        with pytest.raises(ValueError) as exc_empty:
            HashedPassword("")
        assert exc_empty.value.args[0] == "Hashed password cannot be empty."

        with pytest.raises(ValueError) as exc_ws:
            HashedPassword("   ")
        assert exc_ws.value.args[0] == "Hashed password cannot be empty."


class TestScopeValueObject:
    def test_valid_scope(self) -> None:
        scope = Scope("cresmo:sync")
        assert scope.value == "cresmo:sync"
        assert str(scope) == "cresmo:sync"

    def test_empty_or_whitespace_scope_raises_error(self) -> None:
        with pytest.raises(ValueError) as exc_empty:
            Scope("")
        assert exc_empty.value.args[0] == "Scope cannot be empty."

        with pytest.raises(ValueError) as exc_ws:
            Scope("   ")
        assert exc_ws.value.args[0] == "Scope cannot be empty."


class TestTokenHashValueObject:
    def test_valid_direct_token_hash(self) -> None:
        valid_hex = "a" * 64
        th = TokenHash(valid_hex)
        assert th.value == valid_hex
        assert str(th) == valid_hex

    def test_invalid_token_hash_direct_instantiation(self) -> None:
        with pytest.raises(Exception) as exc_empty:
            TokenHash("")
        assert (
            exc_empty.value.args[0]
            == "TokenHash must be a 64-character lowercase hexadecimal string."
        )

        with pytest.raises(Exception) as exc_int:
            TokenHash(12345)  # type: ignore[arg-type]
        assert (
            exc_int.value.args[0]
            == "TokenHash must be a 64-character lowercase hexadecimal string."
        )

        with pytest.raises(Exception) as exc_short:
            TokenHash("abc")
        assert (
            exc_short.value.args[0]
            == "TokenHash must be a 64-character lowercase hexadecimal string."
        )

        with pytest.raises(Exception) as exc_upper:
            TokenHash("A" * 64)
        assert (
            exc_upper.value.args[0]
            == "TokenHash must be a 64-character lowercase hexadecimal string."
        )

    def test_from_raw_token_derives_sha256(self) -> None:
        raw = "cresmo_pat_sample_secret_key_12345"
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        th = TokenHash.from_raw_token(raw)
        assert th.value == expected
        assert str(th) == expected

    def test_from_raw_token_empty_or_whitespace_raises_error(self) -> None:
        with pytest.raises(ValueError) as exc_empty:
            TokenHash.from_raw_token("")
        assert exc_empty.value.args[0] == "Raw token cannot be empty."

        with pytest.raises(ValueError) as exc_ws:
            TokenHash.from_raw_token("   ")
        assert exc_ws.value.args[0] == "Raw token cannot be empty."


class TestRoleEnum:
    def test_roles_membership(self) -> None:
        assert Role.ADMIN.value == "admin"
        assert Role.USER.value == "user"
        assert Role.SERVICE_ACCOUNT.value == "service_account"
        assert Role.VIEWER.value == "viewer"


class TestPersonalAccessTokenEntity:
    def test_create_valid_pat_without_expiration(self) -> None:
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
            expires_at=None,
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

    def test_pat_exact_expiration_boundary_and_naive_now(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_boundary")
        exp_time = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC)

        pat = PersonalAccessToken(
            id="pat_boundary",
            user_id=user_id,
            name="Boundary Token",
            token_prefix="cresmo_pat_bou",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime(2026, 10, 30, 12, 0, 0, tzinfo=UTC),
            expires_at=exp_time,
        )
        # Exactly at expiration moment (chk >= exp) -> must be False (expired)
        assert pat.is_active_at(exp_time) is False

        # One microsecond after expiration -> must be False
        assert pat.is_active_at(exp_time + timedelta(microseconds=1)) is False

        # One microsecond before expiration -> must be True
        assert pat.is_active_at(exp_time - timedelta(microseconds=1)) is True

        # Naive datetime comparisons (ensure naive check replaces with UTC)
        naive_at_exp = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC).replace(tzinfo=None)
        assert pat.is_active_at(naive_at_exp) is False

        naive_before_exp = datetime(2026, 10, 31, 11, 59, 59, tzinfo=UTC).replace(tzinfo=None)
        assert pat.is_active_at(naive_before_exp) is True

    def test_pat_timezone_naive_expiry_converted_to_utc(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_naive")
        # Timezone-naive past datetime
        naive_past = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=2)
        pat = PersonalAccessToken(
            id="pat_003",
            user_id=user_id,
            name="Naive Expired Token",
            token_prefix="cresmo_pat_nai",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime.now(UTC) - timedelta(days=1),
            expires_at=naive_past,
        )
        assert pat.is_active is False

        # Timezone-naive future datetime
        naive_future = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=2)
        pat_active = PersonalAccessToken(
            id="pat_004",
            user_id=user_id,
            name="Naive Active Token",
            token_prefix="cresmo_pat_nai",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime.now(UTC),
            expires_at=naive_future,
        )
        assert pat_active.is_active is True

    def test_revoked_pat_is_not_active(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_revoked")

        pat = PersonalAccessToken(
            id="pat_005",
            user_id=user_id,
            name="Revoked Token",
            token_prefix="cresmo_pat_rev",
            token_hash=token_hash,
            scopes=frozenset([Scope("cresmo:read")]),
            created_at=datetime.now(UTC),
            is_revoked=True,
        )
        assert pat.is_active is False

    def test_record_usage_default_timestamp(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_record_usage")
        pat = PersonalAccessToken(
            id="pat_006",
            user_id=user_id,
            name="Record Usage Token",
            token_prefix="cresmo_pat_rec",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime.now(UTC),
        )
        assert pat.last_used_at is None
        before = datetime.now(UTC)
        pat.record_usage()
        assert pat.last_used_at is not None
        assert isinstance(pat.last_used_at, datetime)
        assert pat.last_used_at.tzinfo is UTC
        assert pat.last_used_at >= before

    def test_record_usage_explicit_timestamp(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_record_usage_explicit")
        pat = PersonalAccessToken(
            id="pat_007",
            user_id=user_id,
            name="Record Usage Token",
            token_prefix="cresmo_pat_rec",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime.now(UTC),
        )
        target = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC)
        pat.record_usage(target)
        assert pat.last_used_at == target

    def test_revoke_method(self) -> None:
        user_id = UserId("usr_123")
        token_hash = TokenHash.from_raw_token("cresmo_pat_revoke_method")
        pat = PersonalAccessToken(
            id="pat_008",
            user_id=user_id,
            name="Revoke Method Token",
            token_prefix="cresmo_pat_rev",
            token_hash=token_hash,
            scopes=frozenset(),
            created_at=datetime.now(UTC),
        )
        assert pat.is_active is True
        assert pat.is_revoked is False
        pat.revoke()
        assert pat.is_revoked is True
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
        before_deact = datetime.now(UTC)
        user.deactivate()
        assert user.is_active is False
        assert user.updated_at is not None
        assert user.updated_at.tzinfo is UTC
        assert user.updated_at >= before_deact

        before_act = datetime.now(UTC)
        user.activate()
        assert user.is_active is True
        assert user.updated_at is not None
        assert user.updated_at.tzinfo is UTC
        assert user.updated_at >= before_act

    def test_updating_password_on_inactive_user_raises_error(self) -> None:
        user = User(
            id=UserId("usr_999"),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.USER]),
            is_active=False,
        )
        with pytest.raises(InactiveUserError) as exc_info:
            user.change_password(HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$newsalt$newhash"))
        assert exc_info.value.args[0] == "Cannot change password for an inactive user account."

    def test_updating_password_on_active_user_success(self) -> None:
        user = User(
            id=UserId("usr_999"),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$salt$hash"),
            roles=frozenset([Role.USER]),
            is_active=True,
        )
        new_pwd = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$newsalt$newhash")
        before_update = datetime.now(UTC)
        user.change_password(new_pwd)
        assert user.hashed_password == new_pwd
        assert user.updated_at is not None
        assert user.updated_at.tzinfo is UTC
        assert user.updated_at >= before_update
