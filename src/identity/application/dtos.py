"""Data Transfer Objects (DTOs) for IAM Application Layer."""

from dataclasses import dataclass, field


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
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


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
class AuthenticatedUserDTO:
    """Contextual security principal passed to downstream controllers and contexts."""

    user_id: str
    tenant_id: str = "default"
    email: str = ""
    roles: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes or "admin" in self.roles
