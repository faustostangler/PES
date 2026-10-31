"""Data Transfer Objects (DTOs) for IAM Application Layer."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from shared_kernel.security import AuthenticatedUser


@dataclass(frozen=True)
class RegisterUserRequestDTO:
    """Input payload for registering a new user."""

    email: str
    password: str
    roles: list[str] = field(default_factory=lambda: ["user"])


@dataclass(frozen=True)
class RegisterUserResponseDTO:
    """Output payload after user registration."""

    user_id: str
    email: str
    roles: list[str]
    is_active: bool
    created_at: str


@dataclass(frozen=True)
class LoginRequestDTO:
    """Input payload for password-based authentication."""

    email: str
    password: str


@dataclass(frozen=True)
class TokenResponseDTO:
    """Output payload containing authentication token."""

    access_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class CreatePATRequestDTO:
    """Input payload for creating a Personal Access Token."""

    user_id: str
    name: str
    scopes: list[str] = field(default_factory=list)
    expires_in_days: int | None = None


@dataclass(frozen=True)
class CreatedPATResponseDTO:
    """Output payload revealing raw token once at creation time."""

    id: str
    raw_token: str
    token_prefix: str
    name: str
    scopes: list[str]
    expires_at: str | None


@dataclass(frozen=True)
class PATItemDTO:
    """Read-only view of a Personal Access Token for listing."""

    id: str
    name: str
    token_prefix: str
    scopes: list[str]
    created_at: str
    expires_at: str | None
    last_used_at: str | None
    is_active: bool


@dataclass(frozen=True)
class AuthenticatedUserDTO(AuthenticatedUser):
    """Contextual security principal conforming to Shared Kernel contract (ADR-048)."""

    def __init__(
        self,
        user_id: str,
        tenant_id: str = "default",
        email: str = "",
        roles: Iterable[str] = (),
        scopes: Iterable[str] = (),
    ) -> None:
        object.__setattr__(self, "user_id", user_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "email", email)
        object.__setattr__(self, "roles", frozenset(roles))
        object.__setattr__(self, "scopes", frozenset(scopes))
