"""Phase 7 HUB events + AI status honesty."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def _token(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": "hub@example.com",
            "username": "hub_user",
            "display_name": "Hub User",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_events_crud_and_ai_unavailable(client: TestClient) -> None:
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    starts = datetime.now(UTC) + timedelta(days=1)
    created = client.post(
        "/events",
        headers=headers,
        json={
            "title": "Demo Meetup",
            "description": "Phase 7 event",
            "location_label": "Cotonou Demo",
            "starts_at": starts.isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    listed = client.get("/events")
    assert listed.status_code == 200
    assert any(item["title"] == "Demo Meetup" for item in listed.json())

    status = client.get("/ai/status")
    assert status.status_code == 200
    assert status.json()["configured"] is False

    chat = client.post(
        "/ai/chat",
        headers=headers,
        json={"message": "Bonjour"},
    )
    assert chat.status_code == 503
