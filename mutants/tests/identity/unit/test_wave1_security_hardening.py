"""TDD Red: Wave 1 IAM Security Hardening & SSOT config.py.

Conforms to:
- ADR-048: Architectural Remediation and Comprehensive Mutation Blindage
- SPEC-048: IAM Security Hardening & Fail-Fast Settings
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from identity.application.dtos import LoginRequestDTO, RegisterUserRequestDTO
from identity.application.use_cases.authenticate_user import AuthenticateUserUseCase
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRoleError,
    InvalidTokenError,
)
from identity.domain.value_objects import (
    Email,
    Role,
    Scope,
    TokenHash,
    UserId,
)
from tests.identity.unit.test_use_cases import (
    InMemoryPasswordHasher,
    InMemoryTokenService,
    InMemoryUserRepository,
)


class TestWave1DomainInvariants:
    """Validate TokenHash 64-char hex invariants and PersonalAccessToken.is_active_at."""

    def test_token_hash_rejects_non_64_char_or_non_hex(self) -> None:
        """TokenHash must strictly be a 64-character lowercase hexadecimal string."""
        with pytest.raises(InvalidTokenError, match="64-character"):
            TokenHash("short_token_hash")

        with pytest.raises(InvalidTokenError, match="64-character"):
            TokenHash("Z" * 64)

        with pytest.raises(InvalidTokenError, match="64-character"):
            TokenHash("a" * 63)

        with pytest.raises(InvalidTokenError, match="64-character"):
            TokenHash("A" * 64)  # Lowercase hex required

    def test_token_hash_accepts_valid_sha256(self) -> None:
        valid_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        th = TokenHash(valid_hash)
        assert th.value == valid_hash

    def test_pat_is_active_at_supports_explicit_clock(self) -> None:
        """PersonalAccessToken.is_active_at allows deterministic clock injection."""
        now = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC)
        pat = PersonalAccessToken(
            id="pat_123",
            user_id=UserId("usr_123"),
            name="Clock Test",
            token_prefix="cresmo_pat_clk",
            token_hash=TokenHash.from_raw_token("cresmo_pat_clock_test_raw"),
            scopes=frozenset([Scope("read")]),
            created_at=now - timedelta(days=2),
            expires_at=now + timedelta(hours=1),
        )
        assert pat.is_active_at(now) is True
        assert pat.is_active_at(now + timedelta(hours=2)) is False

        pat.revoke()
        assert pat.is_active_at(now) is False


class TestWave1ApplicationSecurity:
    """Validate Role privilege escalation prevention and authentication timing protection."""

    def test_register_user_with_invalid_role_raises_invalid_role_error(self) -> None:
        """RegisterUserUseCase must raise InvalidRoleError rather than silently falling back to user."""
        user_repo = InMemoryUserRepository()
        hasher = InMemoryPasswordHasher()
        uc = RegisterUserUseCase(user_repo, hasher)

        dto = RegisterUserRequestDTO(
            email="victim@example.com",
            password="StrongPassword123!",
            roles=["super_admin_invalid_role"],
        )
        with pytest.raises(InvalidRoleError):
            uc.execute(dto)

    def test_authenticate_inactive_user_verifies_password_before_raising_inactive(self) -> None:
        """Verify password hash before checking user.is_active to prevent account enumeration."""
        user_repo = InMemoryUserRepository()
        hasher = InMemoryPasswordHasher()
        token_svc = InMemoryTokenService()
        uc = AuthenticateUserUseCase(user_repo, hasher, token_svc)

        # Deactivated user in repo
        user = User(
            id=UserId("usr_deactivated"),
            email=Email("deactivated@example.com"),
            hashed_password=hasher.hash("RealPassword123!"),
            roles=frozenset([Role.USER]),
            is_active=False,
        )
        user_repo.save(user)

        # 1. Wrong password on inactive user must raise InvalidCredentialsError (NOT InactiveUserError)
        with pytest.raises(InvalidCredentialsError):
            uc.execute(
                LoginRequestDTO(email="deactivated@example.com", password="WrongPassword999!")
            )

        # 2. Correct password on inactive user raises InactiveUserError WITHOUT leaking email in message
        with pytest.raises(InactiveUserError) as exc_info:
            uc.execute(
                LoginRequestDTO(email="deactivated@example.com", password="RealPassword123!")
            )
        assert "deactivated@example.com" not in str(exc_info.value)
