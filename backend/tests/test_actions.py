"""Phase 8 ACTIONS — projects, tasks, real progress."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _token(client: TestClient, suffix: str = "a") -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": f"act{suffix}@example.com",
            "username": f"act_user_{suffix}",
            "display_name": f"Act User {suffix}",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_actions_flow_and_real_progress(client: TestClient) -> None:
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/actions",
        headers=headers,
        json={"title": "Projet Demo", "description": "Phase 8"},
    )
    assert created.status_code == 201, created.text
    project_id = created.json()["id"]
    assert created.json()["progress_percent"] == 0

    task = client.post(
        f"/actions/{project_id}/tasks",
        headers=headers,
        json={"title": "Étape 1"},
    )
    assert task.status_code == 201, task.text
    task_id = task.json()["id"]

    progress = client.get(f"/actions/{project_id}/progress", headers=headers)
    assert progress.status_code == 200
    assert progress.json()["task_total"] == 1
    assert progress.json()["progress_percent"] == 0

    updated = client.patch(
        f"/actions/{project_id}/tasks/{task_id}",
        headers=headers,
        json={"status": "done"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    progress2 = client.get(f"/actions/{project_id}/progress", headers=headers)
    assert progress2.json()["task_done"] == 1
    assert progress2.json()["progress_percent"] == 100

    post = client.post("/posts", headers=headers, json={"body": "Idée pour une action"})
    assert post.status_code == 201, post.text
    from_post = client.post(
        f"/actions/from-post/{post.json()['id']}",
        headers=headers,
    )
    assert from_post.status_code == 201, from_post.text
    assert from_post.json()["source_post_id"] == post.json()["id"]
    assert from_post.json()["task_total"] == 1
