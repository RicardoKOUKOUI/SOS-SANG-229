"""Phase 3 social-light tests (text posts, follow, like)."""

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


def test_create_feed_like_comment_follow_explore(client: TestClient) -> None:
    token_a = _register(
        client, email="alice@example.com", username="alice_demo", name="Alice Demo"
    )
    token_b = _register(
        client, email="bob@example.com", username="bob_demo", name="Bob Demo"
    )
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    created = client.post(
        "/posts",
        headers=headers_a,
        json={"body": "Hello DOXAMI social light"},
    )
    assert created.status_code == 201, created.text
    post_id = created.json()["id"]
    assert created.json()["author"]["username"] == "alice_demo"

    feed = client.get("/posts?tab=recent")
    assert feed.status_code == 200
    assert any(item["id"] == post_id for item in feed.json())

    assert client.post(f"/posts/{post_id}/likes", headers=headers_b).status_code == 204
    detail = client.get(f"/posts/{post_id}", headers=headers_b)
    assert detail.status_code == 200
    assert detail.json()["like_count"] == 1
    assert detail.json()["liked_by_me"] is True

    comment = client.post(
        f"/posts/{post_id}/comments",
        headers=headers_b,
        json={"body": "Nice post"},
    )
    assert comment.status_code == 201
    comments = client.get(f"/posts/{post_id}/comments")
    assert comments.status_code == 200
    assert len(comments.json()) == 1

    assert client.post("/users/alice_demo/follow", headers=headers_b).status_code == 204
    following_feed = client.get("/posts?tab=following", headers=headers_b)
    assert following_feed.status_code == 200
    assert any(item["id"] == post_id for item in following_feed.json())

    followers = client.get("/users/alice_demo/followers")
    assert followers.status_code == 200
    assert followers.json()[0]["user"]["username"] == "bob_demo"

    explore = client.get("/explore/search", params={"q": "DOXAMI"})
    assert explore.status_code == 200
    assert any(item["id"] == post_id for item in explore.json()["posts"])
    people = client.get("/explore/search", params={"q": "alice"})
    assert any(item["username"] == "alice_demo" for item in people.json()["people"])
