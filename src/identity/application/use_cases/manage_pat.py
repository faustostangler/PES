"""Use Cases for managing Personal Access Tokens (PAT)."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Final

from identity.application.dtos import (
    AuthenticatedUserDTO,
    CreatedPATResponseDTO,
    CreatePATRequestDTO,
    PATItemDTO,
)
from identity.application.ports import (
    PersonalAccessTokenRepositoryPort,
    UserRepositoryPort,
)
from identity.domain.entities import PersonalAccessToken
from identity.domain.exceptions import InvalidTokenError
from identity.domain.value_objects import Scope, TokenHash, UserId
from shared_kernel.security import DEFAULT_TENANT_ID

PAT_SECRET_TOKEN_BYTES: Final[int] = 32
PAT_RAW_TOKEN_PREFIX: Final[str] = "cresmo_pat_"
PAT_TOKEN_PREFIX_LENGTH: Final[int] = 16
PAT_ID_PREFIX: Final[str] = "pat_"
PAT_ID_HEX_LENGTH: Final[int] = 12


class CreatePersonalAccessTokenUseCase:
    """Creates a high-entropy Personal Access Token, storing only its SHA-256 hash."""

    def __init__(self, pat_repo: PersonalAccessTokenRepositoryPort) -> None:
        self._pat_repo = pat_repo

    def execute(self, dto: CreatePATRequestDTO) -> CreatedPATResponseDTO:
        user_id = UserId(dto.user_id)
        # 32 bytes URL-safe random string -> ~43 chars
        random_secret = secrets.token_urlsafe(PAT_SECRET_TOKEN_BYTES)
        raw_token = f"{PAT_RAW_TOKEN_PREFIX}{random_secret}"
        token_prefix = raw_token[:PAT_TOKEN_PREFIX_LENGTH]
        token_hash = TokenHash.from_raw_token(raw_token)

        scopes = frozenset([Scope(s) for s in dto.scopes])
        created_at = datetime.now(UTC)
        expires_at = (
            created_at + timedelta(days=dto.expires_in_days) if dto.expires_in_days else None
        )

        pat_id = f"{PAT_ID_PREFIX}{uuid.uuid4().hex[:PAT_ID_HEX_LENGTH]}"
        pat = PersonalAccessToken(
            id=pat_id,
            user_id=user_id,
            name=dto.name,
            token_prefix=token_prefix,
            token_hash=token_hash,
            scopes=scopes,
            created_at=created_at,
            expires_at=expires_at,
        )

        self._pat_repo.save(pat)

        return CreatedPATResponseDTO(
            id=pat.id,
            raw_token=raw_token,
            token_prefix=pat.token_prefix,
            name=pat.name,
            scopes=sorted(s.value for s in pat.scopes),
            expires_at=pat.expires_at.isoformat() if pat.expires_at else None,
        )


class ValidatePersonalAccessTokenUseCase:
    """Validates raw Personal Access Token, checks revocation and expiry."""

    def __init__(
        self,
        pat_repo: PersonalAccessTokenRepositoryPort,
        user_repo: UserRepositoryPort,
    ) -> None:
        self._pat_repo = pat_repo
        self._user_repo = user_repo

    def execute(self, raw_token: str) -> AuthenticatedUserDTO:
        if not raw_token or not raw_token.startswith(PAT_RAW_TOKEN_PREFIX):
            raise InvalidTokenError("Invalid token format.")

        token_hash = TokenHash.from_raw_token(raw_token)
        pat = self._pat_repo.get_by_hash(token_hash)

        if pat is None or not pat.is_active:
            raise InvalidTokenError("Personal Access Token is invalid, revoked or expired.")

        user = self._user_repo.get_by_id(pat.user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError(
                "User account associated with this token is inactive or not found."
            )

        # Update last used timestamp
        pat.record_usage()
        self._pat_repo.save(pat)

        return AuthenticatedUserDTO(
            user_id=user.id.value,
            tenant_id=DEFAULT_TENANT_ID,
            email=user.email.value,
            roles=[r.value for r in user.roles],
            scopes=[s.value for s in pat.scopes],
        )


class ListPersonalAccessTokensUseCase:
    """Lists all Personal Access Tokens belonging to a specific user (ADR-048)."""

    def __init__(self, pat_repo: PersonalAccessTokenRepositoryPort) -> None:
        self._pat_repo = pat_repo

    def execute(self, user_id: UserId) -> list[PATItemDTO]:
        tokens = self._pat_repo.list_by_user(user_id)
        return [
            PATItemDTO(
                id=t.id,
                name=t.name,
                token_prefix=t.token_prefix,
                scopes=sorted(s.value for s in t.scopes),
                created_at=t.created_at.isoformat(),
                expires_at=t.expires_at.isoformat() if t.expires_at else None,
                last_used_at=t.last_used_at.isoformat() if t.last_used_at else None,
                is_active=t.is_active,
            )
            for t in tokens
        ]


class RevokePersonalAccessTokenUseCase:
    """Revokes a Personal Access Token belonging to a specific user (ADR-048)."""

    def __init__(self, pat_repo: PersonalAccessTokenRepositoryPort) -> None:
        self._pat_repo = pat_repo

    def execute(self, token_id: str, user_id: UserId) -> bool:
        return self._pat_repo.revoke(token_id, user_id)
