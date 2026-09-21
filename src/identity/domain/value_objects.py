"""Value Objects for the Identity & Access Management (IAM) Bounded Context."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum

from identity.domain.exceptions import (
    InvalidEmailError,
    InvalidUserIdError,
)

# Standard RFC 5322 simplified email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True)
class UserId:
    """Strongly-typed unique identifier for a User."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidUserIdError("UserId cannot be empty or whitespace.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email:
    """Normalized, RFC 5322 validated email address."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise InvalidEmailError("Email must be a non-empty string.")

        normalized = self.value.strip().lower()
        if not EMAIL_REGEX.match(normalized):
            raise InvalidEmailError(f"Invalid email address format: '{self.value}'")

        # Override value with normalized string
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HashedPassword:
    """Encapsulates a cryptographically hashed password (Argon2id format)."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Hashed password cannot be empty.")

    def __str__(self) -> str:
        return self.value


class Role(str, Enum):
    """Authorization role hierarchy."""

    ADMIN = "admin"
    USER = "user"
    SERVICE_ACCOUNT = "service_account"
    VIEWER = "viewer"


@dataclass(frozen=True)
class Scope:
    """Fine-grained permission scope."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Scope cannot be empty.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TokenHash:
    """Cryptographic SHA-256 hash of a Personal Access Token or secret."""

    value: str

    @classmethod
    def from_raw_token(cls, raw_token: str) -> TokenHash:
        """Derives a hexadecimal SHA-256 hash from a raw plaintext token."""
        if not raw_token or not raw_token.strip():
            raise ValueError("Raw token cannot be empty.")
        computed = hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()
        return cls(value=computed)

    def __str__(self) -> str:
        return self.value
