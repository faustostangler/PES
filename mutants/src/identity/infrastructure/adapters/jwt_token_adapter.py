"""JWT implementation of TokenServicePort using PyJWT."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from identity.application.ports import TokenServicePort
from identity.domain.entities import User
from identity.domain.exceptions import InvalidTokenError
from identity.infrastructure.settings import IdentitySettings


class JwtTokenServiceAdapter(TokenServicePort):
    """Issues and cryptographically validates JWT access tokens."""

    def __init__(self, settings: IdentitySettings | None = None) -> None:
        self._settings = settings or IdentitySettings()
        self._secret = self._settings.jwt_secret_key.get_secret_value()
        self._algorithm = self._settings.jwt_algorithm

    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        now = datetime.now(UTC)
        lifetime = expires_delta or timedelta(minutes=self._settings.access_token_expire_minutes)
        expire = now + lifetime

        payload: dict[str, Any] = {
            "sub": user.id.value,
            "email": user.email.value,
            "roles": [r.value for r in user.roles],
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "tenant_id": "default",
        }

        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError as e:
            raise InvalidTokenError("Token has expired.") from e
        except jwt.PyJWTError as e:
            raise InvalidTokenError(f"Invalid token: {e}") from e
