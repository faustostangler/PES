"""Unit tests for IAM presentation dependencies and HTTP route boundaries.

Conforms to:
- ADR-018: IAM Bounded Context & SvelteKit BFF
- ADR-048: Comprehensive Mutation Blindage (Identity Presentation Gate)
- SPEC-007: Identity and Access Management Specification
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from identity.application.dtos import AuthenticatedUserDTO
from identity.domain.exceptions import InactiveUserError, InvalidTokenError
from identity.presentation.dependencies import (
    get_current_user,
    require_role,
    require_scope,
)
from identity.presentation.routes import router


class TestSecurityDependencies:
    """Tests for get_current_user, require_role, and require_scope dependencies."""

    @pytest.mark.asyncio
    async def test_get_current_user_via_valid_pat(self) -> None:
        mock_container = MagicMock()
        expected_user = AuthenticatedUserDTO(
            user_id="usr_pat",
            roles=["operator"],
            scopes=["cresmo:sync"],
        )
        mock_container.validate_pat_uc.execute.return_value = expected_user

        user = await get_current_user(
            authorization=None,
            x_cresmo_pat="cresmo_pat_valid_123",
            container=mock_container,
        )
        assert user == expected_user
        mock_container.validate_pat_uc.execute.assert_called_once_with("cresmo_pat_valid_123")

    @pytest.mark.asyncio
    async def test_get_current_user_via_invalid_pat_raises_401(self) -> None:
        mock_container = MagicMock()
        mock_container.validate_pat_uc.execute.side_effect = InvalidTokenError("Revoked")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization=None,
                x_cresmo_pat="cresmo_pat_revoked",
                container=mock_container,
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Personal Access Token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_via_valid_bearer_jwt(self) -> None:
        mock_container = MagicMock()
        expected_user = AuthenticatedUserDTO(
            user_id="usr_jwt",
            roles=["user"],
        )
        mock_container.validate_token_uc.execute.return_value = expected_user

        user = await get_current_user(
            authorization="Bearer valid.jwt.token",
            x_cresmo_pat=None,
            container=mock_container,
        )
        assert user == expected_user
        mock_container.validate_token_uc.execute.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    async def test_get_current_user_via_invalid_jwt_raises_401(self) -> None:
        mock_container = MagicMock()
        mock_container.validate_token_uc.execute.side_effect = InactiveUserError("User inactive")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization="Bearer expired.jwt.token",
                x_cresmo_pat=None,
                container=mock_container,
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid access token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_missing_credentials_raises_401(self) -> None:
        mock_container = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization=None,
                x_cresmo_pat=None,
                container=mock_container,
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing authentication credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_malformed_auth_header_raises_401(self) -> None:
        mock_container = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization="Basic invalid_credentials",
                x_cresmo_pat=None,
                container=mock_container,
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_require_role_matching_passes(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_1", roles=["editor"])
        checker = require_role("editor")
        assert checker(user) == user

    def test_require_role_admin_override_passes(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_admin", roles=["admin"])
        checker = require_role("editor")
        assert checker(user) == user

    def test_require_role_missing_raises_403(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_viewer", roles=["viewer"])
        checker = require_role("admin")
        with pytest.raises(HTTPException) as exc_info:
            checker(user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "requires role 'admin'" in exc_info.value.detail

    def test_require_scope_matching_passes(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_1", scopes=["cresmo:sync"])
        checker = require_scope("cresmo:sync")
        assert checker(user) == user

    def test_require_scope_admin_override_passes(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_admin", roles=["admin"])
        checker = require_scope("cresmo:sync")
        assert checker(user) == user

    def test_require_scope_missing_raises_403(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_1", scopes=["cresmo:read"])
        checker = require_scope("cresmo:sync")
        with pytest.raises(HTTPException) as exc_info:
            checker(user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "requires scope 'cresmo:sync'" in exc_info.value.detail


class TestIdentityRoutes:
    """Integration/unit tests for FastAPI route error responses and use case wiring."""

    @pytest.fixture
    def test_app(self) -> tuple[TestClient, MagicMock]:
        from fastapi import FastAPI

        from identity.presentation.composition import get_identity_container

        app = FastAPI()
        app.include_router(router)
        mock_container = MagicMock()
        app.dependency_overrides[get_identity_container] = lambda: mock_container
        client = TestClient(app)
        return client, mock_container

    def test_register_duplicate_email_returns_409(self, test_app: tuple[TestClient, MagicMock]) -> None:
        from identity.domain.exceptions import UserAlreadyExistsError

        client, mock_container = test_app
        mock_container.register_user_uc.execute.side_effect = UserAlreadyExistsError(
            "User with email 'dup@example.com' already exists."
        )

        response = client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "SecurePassword123!"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_login_invalid_credentials_returns_401(self, test_app: tuple[TestClient, MagicMock]) -> None:
        from identity.domain.exceptions import InvalidCredentialsError

        client, mock_container = test_app
        mock_container.authenticate_user_uc.execute.side_effect = InvalidCredentialsError(
            "Invalid email or password."
        )

        response = client.post(
            "/auth/login",
            json={"email": "wrong@example.com", "password": "WrongPassword123!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_inactive_user_returns_403(self, test_app: tuple[TestClient, MagicMock]) -> None:
        from identity.domain.exceptions import InactiveUserError

        client, mock_container = test_app
        mock_container.authenticate_user_uc.execute.side_effect = InactiveUserError(
            "Account is deactivated."
        )

        response = client.post(
            "/auth/login",
            json={"email": "inactive@example.com", "password": "Password123!"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "deactivated" in response.json()["detail"]

    def test_revoke_nonexistent_pat_returns_404(self, test_app: tuple[TestClient, MagicMock]) -> None:
        client, mock_container = test_app
        mock_user = AuthenticatedUserDTO(user_id="usr_owner")
        mock_container.validate_token_uc.execute.return_value = mock_user
        mock_container.revoke_pat_uc.execute.return_value = False

        response = client.delete(
            "/auth/tokens/pat_nonexistent",
            headers={"Authorization": "Bearer valid.token"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
