"""DOXAMI auth tests. Never assert raw emails/passwords in failure logs."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Ensure JWT works in tests before app settings are cached.
os.environ.setdefault("JWT_SECRET", "test-only-jwt-secret-not-for-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_register_login_me(client: TestClient) -> None:
    register = client.post(
        "/auth/register",
        json={
            "email": "demo.user@example.com",
            "username": "demo_user",
            "display_name": "Donneur Demo",
            "password": "securepass1",
        },
    )
    assert register.status_code == 201, register.text
    token = register.json()["access_token"]
    assert token

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["username"] == "demo_user"
    assert body["display_name"] == "Donneur Demo"
    assert "password" not in body
    assert "password_hash" not in body

    login = client.post(
        "/auth/login",
        json={"email": "demo.user@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_register_conflict(client: TestClient) -> None:
    payload = {
        "email": "dup@example.com",
        "username": "dup_user",
        "display_name": "Dup Demo",
        "password": "securepass1",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    again = client.post("/auth/register", json=payload)
    assert again.status_code == 409


def test_login_invalid(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "ok@example.com",
            "username": "ok_user",
            "display_name": "Ok Demo",
            "password": "securepass1",
        },
    )
    bad = client.post(
        "/auth/login",
        json={"email": "ok@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401


def test_update_and_public_profile(client: TestClient) -> None:
    reg = client.post(
        "/auth/register",
        json={
            "email": "prof@example.com",
            "username": "prof_user",
            "display_name": "Prof Demo",
            "password": "securepass1",
        },
    )
    token = reg.json()["access_token"]
    updated = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Prof Updated", "bio": "Hello DOXAMI"},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Prof Updated"
    assert updated.json()["bio"] == "Hello DOXAMI"

    public = client.get("/users/prof_user")
    assert public.status_code == 200
    assert public.json()["username"] == "prof_user"
    assert "email" not in public.json()


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401
