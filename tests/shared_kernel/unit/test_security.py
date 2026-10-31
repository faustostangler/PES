"""Unit tests for shared security principal contracts.

Conforms to:
- ADR-048: Shared Kernel Security Contract Parity
- SPEC-048: AuthenticatedUser Domain Invariants & Role/Scope Verification
"""

from __future__ import annotations

import dataclasses

import pytest

from shared_kernel.security import AuthenticatedUser


class TestAuthenticatedUser:
    """Hermetic unit tests for AuthenticatedUser immutable security principal."""

    def test_default_attributes(self) -> None:
        user = AuthenticatedUser(user_id="usr_001")
        assert user.user_id == "usr_001"
        assert user.tenant_id == "default"
        assert user.email == ""
        assert user.roles == frozenset()
        assert user.scopes == frozenset()

    def test_immutability(self) -> None:
        user = AuthenticatedUser(user_id="usr_001")
        with pytest.raises(dataclasses.FrozenInstanceError):
            user.user_id = "usr_002"  # type: ignore[misc]

    def test_has_role_direct_match(self) -> None:
        user = AuthenticatedUser(
            user_id="usr_001",
            roles=frozenset(["operator", "viewer"]),
        )
        assert user.has_role("operator") is True
        assert user.has_role("viewer") is True
        assert user.has_role("admin") is False
        assert user.has_role("editor") is False

    def test_has_role_admin_override(self) -> None:
        user = AuthenticatedUser(
            user_id="usr_admin",
            roles=frozenset(["admin"]),
        )
        assert user.has_role("admin") is True
        assert user.has_role("operator") is True
        assert user.has_role("any_arbitrary_role") is True

    def test_has_scope_direct_match(self) -> None:
        user = AuthenticatedUser(
            user_id="usr_001",
            scopes=frozenset(["cresmo:sync", "cresmo:read"]),
        )
        assert user.has_scope("cresmo:sync") is True
        assert user.has_scope("cresmo:read") is True
        assert user.has_scope("cresmo:write") is False

    def test_has_scope_admin_role_override(self) -> None:
        user = AuthenticatedUser(
            user_id="usr_admin",
            roles=frozenset(["admin"]),
            scopes=frozenset(),
        )
        assert user.has_scope("cresmo:sync") is True
        assert user.has_scope("cresmo:admin") is True
        assert user.has_scope("arbitrary:scope") is True

    def test_equality_and_hash(self) -> None:
        user1 = AuthenticatedUser(
            user_id="usr_001",
            tenant_id="t1",
            roles=frozenset(["user"]),
            scopes=frozenset(["read"]),
        )
        user2 = AuthenticatedUser(
            user_id="usr_001",
            tenant_id="t1",
            roles=frozenset(["user"]),
            scopes=frozenset(["read"]),
        )
        user3 = AuthenticatedUser(
            user_id="usr_002",
            tenant_id="t1",
        )
        assert user1 == user2
        assert hash(user1) == hash(user2)
        assert user1 != user3

