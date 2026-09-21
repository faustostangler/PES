"""Abstract Application Ports (Interfaces) for IAM Bounded Context."""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

from identity.domain.entities import PersonalAccessToken, User
from identity.domain.value_objects import Email, HashedPassword, TokenHash, UserId


class UserRepositoryPort(ABC):
    """Port for User persistence and query operations."""

    @abstractmethod
    def save(self, user: User) -> None:
        """Saves a new user entity. Raises UserAlreadyExistsError if email exists."""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User | None:
        """Retrieves user by unique UserId."""

    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        """Retrieves user by normalized Email."""

    @abstractmethod
    def update(self, user: User) -> None:
        """Updates an existing user entity."""


class PasswordHasherPort(ABC):
    """Port for secure cryptographic password hashing and verification."""

    @abstractmethod
    def hash(self, plain_password: str) -> HashedPassword:
        """Generates a secure cryptographic hash from a plain password string."""

    @abstractmethod
    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        """Verifies if a plain password matches the cryptographic hash."""


class TokenServicePort(ABC):
    """Port for issuing and verifying JWT access tokens."""

    @abstractmethod
    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        """Creates a signed JWT access token for an authenticated user."""

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decodes and validates a JWT token, returning its claims payload."""


class PersonalAccessTokenRepositoryPort(ABC):
    """Port for Personal Access Token (PAT) persistence and management."""

    @abstractmethod
    def save(self, pat: PersonalAccessToken) -> None:
        """Persists a new Personal Access Token."""

    @abstractmethod
    def get_by_hash(self, token_hash: TokenHash) -> PersonalAccessToken | None:
        """Retrieves a PAT by its cryptographic SHA-256 hash."""

    @abstractmethod
    def list_by_user(self, user_id: UserId) -> list[PersonalAccessToken]:
        """Lists all PATs belonging to a specific user."""

    @abstractmethod
    def revoke(self, token_id: str, user_id: UserId) -> bool:
        """Revokes a PAT by ID for a specific user. Returns True if revoked."""
