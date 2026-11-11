"""Phase 4 messaging + communities tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, *, email: str, username: str, name: str) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "display_name": name,
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_direct_messages_and_community_room(client: TestClient) -> None:
    token_a = _register(
        client, email="msg_a@example.com", username="msg_alice", name="Msg Alice"
    )
    token_b = _register(
        client, email="msg_b@example.com", username="msg_bob", name="Msg Bob"
    )
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    thread = client.post(
        "/messages/threads/direct",
        headers=headers_a,
        json={"username": "msg_bob"},
    )
    assert thread.status_code == 201, thread.text
    thread_id = thread.json()["id"]

    sent = client.post(
        f"/messages/threads/{thread_id}/messages",
        headers=headers_a,
        json={"body": "Salut Bob"},
    )
    assert sent.status_code == 201, sent.text

    inbox_b = client.get("/messages/threads", headers=headers_b)
    assert inbox_b.status_code == 200
    assert any(item["id"] == thread_id for item in inbox_b.json())

    messages = client.get(f"/messages/threads/{thread_id}/messages", headers=headers_b)
    assert messages.status_code == 200
    assert messages.json()[0]["body"] == "Salut Bob"

    reply = client.post(
        f"/messages/threads/{thread_id}/messages",
        headers=headers_b,
        json={"body": "Hello Alice"},
    )
    assert reply.status_code == 201

    community = client.post(
        "/communities",
        headers=headers_a,
        json={
            "name": "Demo Community",
            "slug": "demo-community",
            "description": "Phase 4 demo",
            "is_public": True,
        },
    )
    assert community.status_code == 201, community.text
    community_id = community.json()["id"]

    assert client.post(f"/communities/{community_id}/join", headers=headers_b).status_code == 204
    rooms = client.get(f"/communities/{community_id}/rooms", headers=headers_b)
    assert rooms.status_code == 200
    room_id = rooms.json()[0]["id"]

    room_msg = client.post(
        f"/communities/{community_id}/rooms/{room_id}/messages",
        headers=headers_b,
        json={"body": "Hello room"},
    )
    assert room_msg.status_code == 201
    listed = client.get(
        f"/communities/{community_id}/rooms/{room_id}/messages",
        headers=headers_a,
    )
    assert listed.status_code == 200
    assert listed.json()[0]["body"] == "Hello room"
