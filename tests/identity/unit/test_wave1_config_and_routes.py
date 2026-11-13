"""TDD Red: Wave 1 Config SSOT & Route Security.

Conforms to:
- ADR-048: Architectural Remediation and Comprehensive Mutation Blindage
- SPEC-048: Single config.py sourced from .env with fail-fast IAM_JWT_SECRET_KEY
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError


class TestWave1RootConfig:
    """Validate unified src/config.py SSOT."""

    def test_root_config_imports_cleanly_and_exposes_submodels(self) -> None:
        """Root src/config.py must provide unified AppConfig with iam and cresmo submodels."""
        from config import AppConfig, IamSettings

        settings = AppConfig(_env_file=None)
        assert isinstance(settings.iam, IamSettings)
        assert settings.iam.jwt_algorithm == "HS256"

    def test_iam_secret_key_fails_fast_when_under_32_characters(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """IAM_JWT_SECRET_KEY must be at least 32 characters or fail fast with ValidationError."""
        from config import IamSettings

        monkeypatch.setenv("IAM_JWT_SECRET_KEY", "too-short")
        with pytest.raises(ValidationError):
            IamSettings(_env_file=None)


class TestWave1PresentationRouteHardening:
    """Validate routes ignore payload roles and register only Role.USER."""

    def test_register_schema_does_not_permit_roles_injection(self) -> None:
        """Client cannot escalate role via RegisterSchema."""
        from unittest.mock import MagicMock

        from fastapi import FastAPI

        from identity.application.dtos import RegisterUserResponseDTO
        from identity.presentation.composition import get_identity_container
        from identity.presentation.routes import router

        app = FastAPI()
        app.include_router(router)
        mock_container = MagicMock()
        mock_container.register_user_uc.execute.return_value = RegisterUserResponseDTO(
            user_id="usr_test",
            email="hacker@example.com",
            roles=["user"],
            is_active=True,
            created_at="2026-10-31T00:00:00Z",
        )
        app.dependency_overrides[get_identity_container] = lambda: mock_container
        client = TestClient(app)

        client.post(
            "/auth/register",
            json={
                "email": "hacker@example.com",
                "password": "Password123!",
                "roles": ["admin"],  # Malicious injection attempt
            },
        )
        assert mock_container.register_user_uc.execute.called
        call_arg = mock_container.register_user_uc.execute.call_args[0][0]
        # Must only request 'user' role regardless of payload
        assert call_arg.roles == ["user"]
