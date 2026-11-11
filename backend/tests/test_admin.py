"""Phase 11 admin: bootstrap, TOTP, moderation, no private-message access."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import get_settings
from app.totp import current_code


def test_admin_requires_role_and_totp(client: TestClient, monkeypatch) -> None:
    blocked = client.post(
        "/admin/bootstrap",
        json={"username": "admin_demo", "token": "not-configured"},
    )
    assert blocked.status_code == 503

    registered = client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "username": "admin_demo",
            "display_name": "Admin Demo",
            "password": "securepass1",
        },
    )
    assert registered.status_code == 201, registered.text
    member_headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
    denied = client.get("/admin/dashboard", headers=member_headers)
    assert denied.status_code == 403
    assert "role" in denied.json()["detail"]

    monkeypatch.setenv("DOXAMI_ADMIN_BOOTSTRAP_TOKEN", "bootstrap-test-token")
    get_settings.cache_clear()
    try:
        promoted = client.post(
            "/admin/bootstrap",
            json={"username": "admin_demo", "token": "bootstrap-test-token"},
        )
        assert promoted.status_code == 200, promoted.text
        assert "email" not in promoted.json()
        assert promoted.json()["role"] == "admin"
        assert (
            client.post(
                "/admin/bootstrap",
                json={"username": "admin_demo", "token": "bootstrap-test-token"},
            ).status_code
            == 409
        )

        needs_mfa = client.get("/admin/dashboard", headers=member_headers)
        assert needs_mfa.status_code == 403
        assert "2FA" in needs_mfa.json()["detail"]

        enrolled = client.post("/admin/mfa/enroll", headers=member_headers)
        assert enrolled.status_code == 200, enrolled.text
        confirmed = client.post(
            "/admin/mfa/confirm",
            headers=member_headers,
            json={"code": current_code(enrolled.json()["secret"])},
        )
        assert confirmed.status_code == 200, confirmed.text
        admin_headers = {"Authorization": f"Bearer {confirmed.json()['access_token']}"}

        dashboard = client.get("/admin/dashboard", headers=admin_headers)
        assert dashboard.status_code == 200
        assert dashboard.json()["admins"] == 1

        created = client.post(
            "/posts",
            headers=admin_headers,
            json={"body": "public note to hide"},
        )
        assert created.status_code == 201, created.text
        post_id = created.json()["id"]
        hidden = client.post(f"/admin/moderation/posts/{post_id}/hide", headers=admin_headers)
        assert hidden.status_code == 200
        assert hidden.json()["hidden"] is True
        feed = client.get("/posts")
        assert all(item["id"] != post_id for item in feed.json())
        assert client.get(f"/posts/{post_id}").status_code == 404

        flag = client.patch(
            "/admin/flags/ads_enabled",
            headers=admin_headers,
            json={"enabled": True},
        )
        assert flag.status_code == 200
        assert flag.json()["checkout_unchanged"] is True

        logs = client.get("/admin/logs", headers=admin_headers)
        assert logs.status_code == 200
        actions = {row["action"] for row in logs.json()}
        assert "post.hide" in actions
        assert "email" not in logs.text.lower()
        assert client.get("/admin/messages", headers=admin_headers).status_code == 404

        users = client.get("/admin/users", headers=admin_headers)
        assert users.status_code == 200
        assert "email" not in users.text.lower()
        assert "phone" not in users.text.lower()
    finally:
        get_settings.cache_clear()
