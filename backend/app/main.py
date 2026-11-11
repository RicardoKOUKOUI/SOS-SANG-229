from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.matching import DEFAULT_RADIUS_METERS
from app.routers import (
    actions,
    ai,
    alerts,
    auth,
    communities,
    creator,
    donations,
    donors,
    events,
    health,
    hospitals,
    mesh,
    messaging,
    posts,
    social,
    tracking,
    users,
)

settings = get_settings()
_cors_origins = [
    origin.strip()
    for origin in settings.frontend_origin.split(",")
    if origin.strip()
]
if "http://localhost:5173" not in _cors_origins:
    _cors_origins.append("http://localhost:5173")
if "http://127.0.0.1:5173" not in _cors_origins:
    _cors_origins.append("http://127.0.0.1:5173")

app = FastAPI(
    title="DOXAMI API (via SOS Sang 229 stack)",
    description=(
        "Phase 2 foundations: DOXAMI auth/profiles + legacy SOS Sang 229 blood MVP.\n\n"
        "## DOXAMI auth\n"
        "- `POST /auth/register` — create account + JWT\n"
        "- `POST /auth/login` — JWT\n"
        "- `GET /auth/me` — current user\n"
        "- `POST /auth/logout` — client discard (stateless)\n"
        "- `PATCH /users/me` — update profile\n"
        "- `GET /users/{username}` — public profile\n\n"
        "## DOXAMI social light (Phase 3)\n"
        "- `POST/GET /posts`, `GET /posts/{id}`\n"
        "- likes + comments on posts\n"
        "- follow/unfollow + followers/following\n"
        "- `GET /explore/search?q=`\n"
        "Media upload: not enabled (text-only).\n\n"
        "## DOXAMI messaging & communities (Phase 4)\n"
        "- `/messages/threads*` — 1:1 + group text (polling, no WebRTC)\n"
        "- `/communities*` — public communities, rooms, text chat\n\n"
        "## DOXAMI MESH (Phase 6 — architecture-ready)\n"
        "- `GET /mesh/status` — honest readiness (no fake P2P)\n"
        "- `POST /mesh/envelopes` — 501 until native transport exists\n"
        "Offline IndexedDB sync is NOT MESH.\n\n"
        "## DOXAMI HUB services (Phase 7)\n"
        "- `/events` — DB events CRUD list/create\n"
        "- `/ai/status`, `/ai/chat` — requires DOXAMI_AI_API_KEY (else unavailable)\n"
        "- Meet/Live remain UI placeholders without WebRTC infra\n\n"
        "## DOXAMI ACTIONS (Phase 8)\n"
        "- `/actions` — projects, tasks (todo/doing/done), team, progress réel\n\n"
        "## DOXAMI creators (Phase 9)\n"
        "- `/creator/me` — studio profile\n"
        "- `/monetization/status` — ads/premium flags; payouts_ready stays false\n"
        "- checkout and payouts return 503 (no PSP adapter, earnings 0)\n\n"
        "## Legacy SOS Sang\n"
        f"Matching radius default **{DEFAULT_RADIUS_METERS} m**. "
        "Twilio SMS: stub. JWT required for DOXAMI routes only; "
        "legacy blood endpoints remain open for the hackathon demo.\n\n"
        "Never log emails, phones, passwords, GPS, or blood groups in cleartext."
    ),
    version="0.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(social.router)
app.include_router(messaging.router)
app.include_router(communities.router)
app.include_router(mesh.router)
app.include_router(events.router)
app.include_router(ai.router)
app.include_router(actions.router)
app.include_router(creator.router)
app.include_router(hospitals.router)
app.include_router(donors.router)
app.include_router(alerts.router)
app.include_router(donations.router)
app.include_router(tracking.router)


@app.get("/")
def root():
    return {
        "service": "doxami",
        "legacy": "sos-sang-229",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/health",
            "/auth/register",
            "/auth/login",
            "/auth/me",
            "/auth/logout",
            "/users/me",
            "/users/{username}",
            "/posts",
            "/explore/search",
            "/messages/threads",
            "/communities",
            "/mesh/status",
            "/events",
            "/ai/status",
            "/actions",
            "/creator/me",
            "/monetization/status",
            "/hospitals",
            "/hospitals/recognized",
            "/donors",
            "/alerts",
            "/donations",
            "/requests",
            "/requests/{public_ref}",
        ],
    }
