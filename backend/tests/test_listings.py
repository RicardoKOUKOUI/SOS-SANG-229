"""Phase 10 listings — profiles, jobs, market. Checkout stays refused."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _token(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={
            "email": "pro@example.com",
            "username": "pro_demo",
            "display_name": "Pro Demo",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def test_professional_jobs_and_blocked_checkout(client: TestClient) -> None:
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    saved = client.put(
        "/professional/me",
        headers=headers,
        json={
            "headline": "Atelier demo",
            "organization": "Studio Demo",
            "city_label": "Cotonou Demo",
            "summary": "Profil professionnel fictif.",
        },
    )
    assert saved.status_code == 200, saved.text
    listed = client.get("/professionals")
    assert listed.status_code == 200
    assert any(item["headline"] == "Atelier demo" for item in listed.json())

    job = client.post(
        "/jobs",
        headers=headers,
        json={"title": "Mission demo", "description": "Texte seulement", "city_label": "Zone Demo"},
    )
    assert job.status_code == 201, job.text
    jobs = client.get("/jobs")
    assert any(item["title"] == "Mission demo" for item in jobs.json())

    listing = client.post(
        "/marketplace",
        headers=headers,
        json={"title": "Objet demo", "description": "Pas à vendre", "price_minor": 1500},
    )
    assert listing.status_code == 201, listing.text
    body = listing.json()
    assert body["checkout_available"] is False
    assert body["currency"] == "XOF"
    listing_id = body["id"]

    checkout = client.post(f"/marketplace/{listing_id}/checkout", headers=headers)
    assert checkout.status_code == 503
    assert "no charge" in checkout.json()["detail"]
