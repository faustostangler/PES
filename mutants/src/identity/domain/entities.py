"""Domain entities and aggregates for Identity & Access Management (IAM)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from identity.domain.exceptions import InactiveUserError
from identity.domain.value_objects import (
    Email,
    HashedPassword,
    Role,
    Scope,
    TokenHash,
    UserId,
)


@dataclass
class PersonalAccessToken:
    """Personal Access Token (PAT) entity for machine-to-machine authentication."""

    id: str
    user_id: UserId
    name: str
    token_prefix: str
    token_hash: TokenHash
    scopes: frozenset[Scope]
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    is_revoked: bool = False

    @property
    def is_active(self) -> bool:
        """Determines if the token is currently valid and unexpired."""
        if self.is_revoked:
            return False
        if self.expires_at is not None:
            now = datetime.now(UTC)
            # Ensure comparison timezone safety
            exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=UTC)
            if now >= exp:
                return False
        return True

    def has_scope(self, scope: Scope) -> bool:
        """Checks if the token grants a specific permission scope."""
        return scope in self.scopes

    def record_usage(self, timestamp: datetime | None = None) -> None:
        """Records token usage timestamp."""
        self.last_used_at = timestamp or datetime.now(UTC)

    def revoke(self) -> None:
        """Revokes the token permanently."""
        self.is_revoked = True


@dataclass
class User:
    """User Aggregate Root managing identity, credentials, and role assignments."""

    id: UserId
    email: Email
    hashed_password: HashedPassword
    roles: frozenset[Role] = field(default_factory=lambda: frozenset([Role.USER]))
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def has_role(self, role: Role) -> bool:
        """Verifies if the user is assigned a specific role."""
        return role in self.roles

    def deactivate(self) -> None:
        """Deactivates user account, preventing further authentication."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Re-activates a previously disabled user account."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def change_password(self, new_hashed_password: HashedPassword) -> None:
        """Updates user password hash while verifying active state."""
        if not self.is_active:
            raise InactiveUserError("Cannot change password for an inactive user account.")
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(UTC)
