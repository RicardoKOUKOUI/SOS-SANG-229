from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.matching import DEFAULT_RADIUS_METERS
from app.routers import alerts, auth, donations, donors, health, hospitals, tracking, users

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
        "## Legacy SOS Sang\n"
        f"Matching radius default **{DEFAULT_RADIUS_METERS} m**. "
        "Twilio SMS: stub. JWT required for DOXAMI routes only; "
        "legacy blood endpoints remain open for the hackathon demo.\n\n"
        "Never log emails, phones, passwords, GPS, or blood groups in cleartext."
    ),
    version="0.3.0",
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
            "/hospitals",
            "/hospitals/recognized",
            "/donors",
            "/alerts",
            "/donations",
            "/requests",
            "/requests/{public_ref}",
        ],
    }
