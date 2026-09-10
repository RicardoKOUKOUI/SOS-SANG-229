from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.matching import DEFAULT_RADIUS_METERS
from app.routers import alerts, donations, donors, health, hospitals, tracking

app = FastAPI(
    title="SOS Sang 229 API",
    description=(
        "MVP d’alerte et de matching donneur de sang — Hackathon Cursor Bénin.\n\n"
        "## Endpoints métier\n"
        "- `GET /health` — santé de l’API (sans base)\n"
        "- `GET /hospitals` / `GET /hospitals/recognized` — établissements reconnus "
        "(sans téléphone ni GPS)\n"
        "- `POST /donors` — inscription donneur (téléphone / GPS omis en réponse)\n"
        "- `POST /alerts` — créer une urgence (`hospital_id` reconnu obligatoire), "
        "lancer le matching, enregistrer `alerted_donors_count`\n"
        "- `POST /donations` — confirmer un don\n"
        "- `GET /requests` et `GET /requests/{public_ref}` — suivi (compteurs / statut, "
        "sans numéro de téléphone)\n\n"
        "## Matching\n"
        f"Rayon GPS par défaut : **{DEFAULT_RADIUS_METERS} m (15 km)**, "
        "configurable via `MATCH_RADIUS_METERS`. "
        "Si l'hôpital et le donneur ont un point GPS (WKT) : distance haversine (mètres). "
        "Sinon : même ville (comparaison insensible à la casse). "
        "Groupes compatibles ABO/Rh. Donneurs `is_available=true` uniquement.\n\n"
        "Twilio / SMS réel : non branché (stub). JWT : non requis pour ce MVP. "
        "Ne jamais logger téléphone, GPS ou groupe sanguin en clair."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(hospitals.router)
app.include_router(donors.router)
app.include_router(alerts.router)
app.include_router(donations.router)
app.include_router(tracking.router)


@app.get("/")
def root():
    return {
        "service": "sos-sang-229",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/health",
            "/hospitals",
            "/hospitals/recognized",
            "/donors",
            "/alerts",
            "/donations",
            "/requests",
            "/requests/{public_ref}",
        ],
    }
