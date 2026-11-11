# DOXAMI (stack issue de SOS Sang 229)

Écosystème DOXAMI en construction (**Phase 5 — offline-first web**) sur le dépôt hackathon **SOS Sang 229** (Option A : évoluer en place, démo sang préservée sous `/legacy/sang`).

| Couche | Stack | Statut Phase 2 |
| --- | --- | --- |
| Frontend | React + Vite + Tailwind | Shell DOXAMI, auth, feed/create/explore, follow/like, Hub placeholders |
| Backend | FastAPI | auth + `/posts`, follow/like, `/explore/search` + legacy sang |
| Base | PostgreSQL (+ image PostGIS en local) | Migration `004_users` ; matching sang = haversine Text WKT (pas ST_DWithin) |
| SMS | Twilio | Stub uniquement |
| CI | GitHub Actions | `pytest` + `npm run build` |

## Structure

```
frontend/          # App DOXAMI + legacy SOS Sang
backend/           # API FastAPI
docker-compose.yml # Postgres local
.env.example       # noms de variables uniquement
```

## Lancer en local

Prérequis : Node.js 18+, Python 3.11+, (optionnel) Docker.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Ouvre [http://localhost:5173](http://localhost:5173).

Routes DOXAMI (extrait) :

- `/` — accueil / feed placeholder
- `/auth`, `/auth/register`, `/auth/login`, `/auth/logout`
- `/profile`, `/profile/edit`, `/u/:username`
- `/hub` — tuiles Hub (placeholders honnêtes)
- `/legacy/sang` — démo SOS Sang 229

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# .env avec DATABASE_URL + JWT_SECRET (voir .env.example)
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Santé : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Docs : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Auth : `POST /auth/register`, `POST /auth/login`, `GET /auth/me`

### Postgres

```bash
docker compose up -d
cd backend && alembic upgrade head
# optionnel legacy démo :
python scripts/seed_demo.py
```

## Sécurité

Ne jamais committer de secrets (`.env`). Ne pas logger email, téléphone, GPS, groupe sanguin ou mots de passe en clair. Seeds fictifs uniquement.

## Branches

- Cloud agents : `cursor/<name>-xxxx`
- Convention équipe : `<type>/<nom-court>`
- Pas de commit direct sur `main` : ouvrir une PR.
