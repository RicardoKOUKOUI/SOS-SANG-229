"""MESH architecture-ready endpoints — must stay honest (no fake success)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient


def test_mesh_status_is_not_ready(api_client: TestClient) -> None:
    response = api_client.get("/mesh/status")
    assert response.status_code == 200
    body = response.json()
    assert body["mesh_transport_ready"] is False
    assert "ONLINE" in body["mode_supported"]
    assert "OFFLINE" in body["mode_supported"]
    assert "MESH" not in body["mode_supported"]


def test_mesh_envelope_not_implemented(api_client: TestClient) -> None:
    response = api_client.post(
        "/mesh/envelopes",
        json={
            "id": str(uuid4()),
            "ttl_hops": 3,
            "created_at": datetime.now(UTC).isoformat(),
            "kind": "chat",
            "payload_b64": "aGVsbG8=",
            "dedupe_key": "dedupe-key-demo-01",
        },
    )
    assert response.status_code == 501
