"""Shared security contracts consumed across Bounded Contexts (Cresmo, IAM, etc.)."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AuthenticatedUser:
    """Immutable security principal contract for cross-context authorization.

    Shields domain cores (such as Cresmo) from depending on IAM persistence
    or password hashing models.
    """

    user_id: str
    tenant_id: str = "default"
    email: str = ""
    roles: frozenset[str] = field(default_factory=frozenset)
    scopes: frozenset[str] = field(default_factory=frozenset)

    def has_role(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "admin" in self.roles

    def has_scope(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "admin" in self.roles
