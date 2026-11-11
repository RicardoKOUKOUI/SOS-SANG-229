"""Phase 13 smoke: liveness, readiness, and one auth path. No production host."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_liveness_does_not_need_a_database(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_without_database_is_unavailable(api_client: TestClient) -> None:
    response = api_client.get("/health/ready")
    assert response.status_code == 503
    assert "DATABASE_URL" in response.json()["detail"]


def test_readiness_and_auth_on_app_database(client: TestClient) -> None:
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    body = ready.json()
    assert body == {"status": "ready", "database": "ok"}
    assert "postgresql" not in ready.text

    registered = client.post(
        "/auth/register",
        json={
            "email": "deploy-smoke@example.com",
            "username": "deploy_smoke",
            "display_name": "Deploy Smoke",
            "password": "securepass1",
        },
    )
    assert registered.status_code == 201, registered.text
    login = client.post(
        "/auth/login",
        json={"email": "deploy-smoke@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "deploy_smoke"
    assert "password" not in me.text.lower()
