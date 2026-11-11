"""Phase 9 creator profile + honest monetization (no payout)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _token(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": "creator@example.com",
            "username": "creator_demo",
            "display_name": "Creator Demo",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_creator_profile_and_blocked_money(client: TestClient) -> None:
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    missing = client.get("/creator/me", headers=headers)
    assert missing.status_code == 404

    saved = client.put(
        "/creator/me",
        headers=headers,
        json={"pitch": "Studio light", "focus": "texte", "accepting_collabs": True},
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["focus"] == "texte"
    assert saved.json()["user"]["username"] == "creator_demo"

    status = client.get("/monetization/status")
    assert status.status_code == 200
    body = status.json()
    assert body["ads_enabled"] is False
    assert body["premium_enabled"] is False
    assert body["psp_configured"] is False
    assert body["payouts_ready"] is False
    assert body["earnings_minor"] == 0

    plans = client.get("/monetization/plans")
    assert plans.status_code == 200
    assert plans.json()[0]["checkout_available"] is False

    checkout = client.post("/monetization/checkout", headers=headers)
    assert checkout.status_code == 503

    payout = client.post("/creator/payouts", headers=headers)
    assert payout.status_code == 503
