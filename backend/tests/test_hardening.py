"""Phase 12: headers, list caps, private threads, and honest failures."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, suffix: str) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": f"{suffix}@example.com",
            "username": f"user_{suffix}",
            "display_name": f"User {suffix}",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_security_headers_and_no_store(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["referrer-policy"] == "no-referrer"
    assert health.headers["x-frame-options"] == "DENY"

    token = _register(client, "headers")
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.headers["cache-control"] == "no-store"
    assert "password" not in me.text.lower()


def test_mesh_query_cannot_force_ready(client: TestClient) -> None:
    forced = client.get("/mesh/status?simulate=1&mesh_transport_ready=true")
    assert forced.status_code == 200
    body = forced.json()
    assert body["mesh_transport_ready"] is False
    assert "cannot enable" in body["notes"]
    envelope = client.post(
        "/mesh/envelopes",
        json={
            "id": "00000000-0000-4000-8000-000000000001",
            "ttl_hops": 1,
            "created_at": "2026-11-11T12:00:00Z",
            "kind": "chat",
            "payload_b64": "aGVsbG8=",
            "dedupe_key": "demo-key1",
        },
    )
    assert envelope.status_code == 501


def test_feed_stays_capped_for_low_bandwidth(client: TestClient) -> None:
    token = _register(client, "feedcap")
    headers = {"Authorization": f"Bearer {token}"}
    for index in range(55):
        created = client.post("/posts", headers=headers, json={"body": f"note {index}"})
        assert created.status_code == 201, created.text
    listed = client.get("/posts")
    assert listed.status_code == 200
    assert len(listed.json()) == 50


def test_private_thread_and_money_stay_closed(client: TestClient) -> None:
    alice = _register(client, "aliceh")
    bob = _register(client, "bobh")
    cara = _register(client, "carah")
    alice_headers = {"Authorization": f"Bearer {alice}"}
    bob_headers = {"Authorization": f"Bearer {bob}"}
    cara_headers = {"Authorization": f"Bearer {cara}"}

    thread = client.post(
        "/messages/threads/direct",
        headers=alice_headers,
        json={"username": "user_bobh"},
    )
    assert thread.status_code == 201, thread.text
    thread_id = thread.json()["id"]
    sent = client.post(
        f"/messages/threads/{thread_id}/messages",
        headers=alice_headers,
        json={"body": "secret hello"},
    )
    assert sent.status_code == 201, sent.text
    assert client.get(f"/messages/threads/{thread_id}", headers=bob_headers).status_code == 200
    outsider = client.get(f"/messages/threads/{thread_id}", headers=cara_headers)
    assert outsider.status_code == 403
    outsider_msgs = client.get(
        f"/messages/threads/{thread_id}/messages",
        headers=cara_headers,
    )
    assert outsider_msgs.status_code == 403
    assert "secret hello" not in outsider_msgs.text

    assert client.get("/actions", headers=alice_headers).status_code == 200
    assert client.post("/ai/chat", headers=alice_headers, json={"message": "hi"}).status_code == 503
    assert client.post("/creator/payouts", headers=alice_headers).status_code == 503
    assert client.post("/monetization/checkout", headers=alice_headers).status_code == 503
    assert client.get("/admin/dashboard", headers=alice_headers).status_code == 403
    assert client.get("/admin/messages", headers=alice_headers).status_code == 404
