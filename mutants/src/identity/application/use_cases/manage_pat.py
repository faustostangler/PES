"""Use Cases for managing Personal Access Tokens (PAT)."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from identity.application.dtos import (
    AuthenticatedUserDTO,
    CreatedPATResponseDTO,
    CreatePATRequestDTO,
)
from identity.application.ports import (
    PersonalAccessTokenRepositoryPort,
    UserRepositoryPort,
)
from identity.domain.entities import PersonalAccessToken
from identity.domain.exceptions import InvalidTokenError
from identity.domain.value_objects import Scope, TokenHash, UserId


class CreatePersonalAccessTokenUseCase:
    """Creates a high-entropy Personal Access Token, storing only its SHA-256 hash."""

    def __init__(self, pat_repo: PersonalAccessTokenRepositoryPort) -> None:
        self._pat_repo = pat_repo

    def execute(self, dto: CreatePATRequestDTO) -> CreatedPATResponseDTO:
        user_id = UserId(dto.user_id)
        # 32 bytes URL-safe random string -> ~43 chars
        random_secret = secrets.token_urlsafe(32)
        raw_token = f"cresmo_pat_{random_secret}"
        token_prefix = raw_token[:16]
        token_hash = TokenHash.from_raw_token(raw_token)

        scopes = frozenset([Scope(s) for s in dto.scopes])
        created_at = datetime.now(UTC)
        expires_at = (
            created_at + timedelta(days=dto.expires_in_days) if dto.expires_in_days else None
        )

        pat_id = f"pat_{uuid.uuid4().hex[:12]}"
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
            scopes=[s.value for s in pat.scopes],
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
        if not raw_token or not raw_token.startswith("cresmo_pat_"):
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
            tenant_id="default",
            email=user.email.value,
            roles=[r.value for r in user.roles],
            scopes=[s.value for s in pat.scopes],
        )
