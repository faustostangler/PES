"""End-to-End Integration tests for FastAPI Authentication API.

Tests registration, login, JWT bearer access, and Personal Access Token (PAT) dual-gate authentication.
"""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from identity.infrastructure.settings import IdentitySettings
from identity.presentation.composition import IdentityContainer, set_identity_container
from identity.presentation.routes import router as auth_router


@pytest.fixture
def app_client(tmp_path: Path) -> TestClient:
    test_db = tmp_path / "test_api_identity.db"
    settings = IdentitySettings(
        jwt_secret_key=SecretStr("super-secret-production-test-key-32-chars-long!"),
        identity_db_path=test_db,
        argon2_time_cost=2,
        argon2_memory_cost=19456,
        argon2_parallelism=1,
    )
    container = IdentityContainer(settings=settings)
    set_identity_container(container)

    app = FastAPI(title="PES IAM Test API")
    app.include_router(auth_router)

    return TestClient(app)


class TestAuthAPIEndpoints:
    def test_full_auth_and_pat_flow(self, app_client: TestClient) -> None:
        # 1. Register new user
        reg_resp = app_client.post(
            "/auth/register",
            json={
                "email": "architect@pes.ai",
                "password": "StrongPassword123!",
                "roles": ["admin", "user"],
            },
        )
        assert reg_resp.status_code == 201
        data = reg_resp.json()
        assert data["email"] == "architect@pes.ai"
        assert "admin" in data["roles"]

        # 2. Login with registered user
        login_resp = app_client.post(
            "/auth/login",
            json={
                "email": "architect@pes.ai",
                "password": "StrongPassword123!",
            },
        )
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        assert access_token is not None

        # 3. Access /auth/me without token -> 401
        unauth_resp = app_client.get("/auth/me")
        assert unauth_resp.status_code == 401

        # 4. Access /auth/me with Bearer JWT -> 200
        me_resp = app_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["email"] == "architect@pes.ai"
        assert "admin" in me_data["roles"]

        # 5. Create Personal Access Token (PAT) for CLI
        pat_resp = app_client.post(
            "/auth/tokens",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "CLI Ingestion Token",
                "scopes": ["cresmo:sync", "cresmo:read"],
                "expires_in_days": 30,
            },
        )
        assert pat_resp.status_code == 201
        pat_data = pat_resp.json()
        raw_pat = pat_data["raw_token"]
        pat_id = pat_data["id"]
        assert raw_pat.startswith("cresmo_pat_")

        # 6. Access /auth/me using X-Cresmo-PAT header -> 200
        me_pat_resp = app_client.get(
            "/auth/me",
            headers={"X-Cresmo-PAT": raw_pat},
        )
        assert me_pat_resp.status_code == 200
        me_pat_data = me_pat_resp.json()
        assert me_pat_data["email"] == "architect@pes.ai"
        assert "cresmo:sync" in me_pat_data["scopes"]

        # 7. List PATs
        list_resp = app_client.get(
            "/auth/tokens",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert list_resp.status_code == 200
        token_list = list_resp.json()
        assert len(token_list) == 1
        assert token_list[0]["id"] == pat_id

        # 8. Revoke PAT
        del_resp = app_client.delete(
            f"/auth/tokens/{pat_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert del_resp.status_code == 204

        # 9. Access with revoked PAT -> 401
        revoked_resp = app_client.get(
            "/auth/me",
            headers={"X-Cresmo-PAT": raw_pat},
        )
        assert revoked_resp.status_code == 401
