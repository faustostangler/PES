"""Unit tests for IAM Infrastructure Adapters.

Tests Argon2PasswordHasherAdapter and JwtTokenServiceAdapter.
"""

from datetime import timedelta

import pytest
from pydantic import SecretStr

from identity.domain.entities import User
from identity.domain.exceptions import InvalidTokenError
from identity.domain.value_objects import Email, HashedPassword, Role, UserId
from identity.infrastructure.adapters.argon2_hasher_adapter import Argon2PasswordHasherAdapter
from identity.infrastructure.adapters.jwt_token_adapter import JwtTokenServiceAdapter
from identity.infrastructure.settings import IdentitySettings


@pytest.fixture
def identity_settings() -> IdentitySettings:
    return IdentitySettings(
        jwt_secret_key=SecretStr("super-secret-production-test-key-32-chars-long!"),
        jwt_algorithm="HS256",
        access_token_expire_minutes=15,
        argon2_time_cost=2,
        argon2_memory_cost=19456,  # 19 MiB for quick tests
        argon2_parallelism=1,
    )


class TestArgon2PasswordHasherAdapter:
    def test_hash_and_verify_success(self, identity_settings: IdentitySettings) -> None:
        hasher = Argon2PasswordHasherAdapter(settings=identity_settings)
        plain = "CorrectHorseBatteryStaple123!"

        hashed = hasher.hash(plain)
        assert hashed.value.startswith("$argon2id$")

        # Verify correct password
        assert hasher.verify(plain, hashed) is True

        # Verify wrong password
        assert hasher.verify("WrongPassword!", hashed) is False


class TestJwtTokenServiceAdapter:
    def test_create_and_decode_token_success(self, identity_settings: IdentitySettings) -> None:
        service = JwtTokenServiceAdapter(settings=identity_settings)
        user = User(
            id=UserId("usr_jwt_test"),
            email=Email("jwt@example.com"),
            hashed_password=HashedPassword("$dummy$hash"),
            roles=frozenset([Role.ADMIN, Role.USER]),
        )

        token = service.create_access_token(user, expires_delta=timedelta(minutes=5))
        assert isinstance(token, str)

        claims = service.decode_access_token(token)
        assert claims["sub"] == "usr_jwt_test"
        assert claims["email"] == "jwt@example.com"
        assert "admin" in claims["roles"]
        assert "user" in claims["roles"]

    def test_decode_tampered_token_raises_error(self, identity_settings: IdentitySettings) -> None:
        service = JwtTokenServiceAdapter(settings=identity_settings)
        user = User(
            id=UserId("usr_jwt_test"),
            email=Email("jwt@example.com"),
            hashed_password="$dummy$hash",  # type: ignore[arg-type]
        )
        token = service.create_access_token(user)

        # Tamper signature
        tampered = token[:-5] + "xxxxx"
        with pytest.raises(InvalidTokenError, match="Signature verification failed|Invalid token"):
            service.decode_access_token(tampered)

    def test_decode_expired_token_raises_error(self, identity_settings: IdentitySettings) -> None:
        service = JwtTokenServiceAdapter(settings=identity_settings)
        user = User(
            id=UserId("usr_jwt_test"),
            email=Email("jwt@example.com"),
            hashed_password="$dummy$hash",  # type: ignore[arg-type]
        )
        # Create token expired in past
        token = service.create_access_token(user, expires_delta=timedelta(seconds=-10))

        with pytest.raises(InvalidTokenError, match="Token has expired"):
            service.decode_access_token(token)
