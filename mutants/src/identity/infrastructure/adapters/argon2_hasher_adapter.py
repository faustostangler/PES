"""Argon2id implementation of PasswordHasherPort using argon2-cffi."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from identity.application.ports import PasswordHasherPort
from identity.domain.value_objects import HashedPassword
from identity.infrastructure.settings import IdentitySettings


class Argon2PasswordHasherAdapter(PasswordHasherPort):
    """Secure password hashing adapter compliant with RFC 9106 / OWASP."""

    def __init__(self, settings: IdentitySettings | None = None) -> None:
        cfg = settings or IdentitySettings()
        self._hasher = PasswordHasher(
            time_cost=cfg.argon2_time_cost,
            memory_cost=cfg.argon2_memory_cost,
            parallelism=cfg.argon2_parallelism,
        )

    def hash(self, plain_password: str) -> HashedPassword:
        hashed_str = self._hasher.hash(plain_password)
        return HashedPassword(hashed_str)

    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        try:
            return self._hasher.verify(hashed.value, plain_password)
        except (VerifyMismatchError, InvalidHashError):
            return False
