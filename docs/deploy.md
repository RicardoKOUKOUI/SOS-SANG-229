# Déploiement DOXAMI (Phase 13)

Ce fichier décrit comment brancher l’existant. Il ne contient pas de secret.
Aucun déploiement production n’est déclaré réussi par ce dépôt tant que
`/health/ready` ne répond pas 200 sur l’hôte réellement configuré.

## Hôtes

| Rôle | Où | Réglage |
| --- | --- | --- |
| Frontend | Vercel, projet déjà relié au dépôt | Root Directory `frontend` |
| API | Railway, image `backend/Dockerfile` | Root Directory **`backend`** |
| Postgres | Plugin Railway Postgres, ou Postgres 16 local | `DATABASE_URL` injecté par la plateforme |

Le frontend appelle l’API via le rewrite `/api` dans `frontend/vercel.json`.
L’URL qui y est écrite aujourd’hui a été interrogée le 11 novembre 2026
(14:45, heure de Porto-Novo) :

`GET https://sos-sang-229-production.up.railway.app/health` → **404**
`Application not found` (réponse Railway, pas l’API DOXAMI).

Tant que ce service n’existe pas, le preview Vercel sert le frontend et le
proxy `/api` ne joint pas cette API. Remplacer la destination du rewrite par
l’URL publique du service Railway une fois qu’il répond, sans committer de jeton.

Domaine custom : réglage Vercel / Railway, hors de ce dépôt.

## Variables (noms seulement)

Copier `.env.example`. Valeurs réelles uniquement dans le dashboard
(Vercel / Railway) ou dans un `.env` local non commité.

| Nom | Rôle |
| --- | --- |
| `DATABASE_URL` | Postgres. Requis pour `/health/ready` et les routes métier |
| `JWT_SECRET` | Signature des JWT. Requis pour `/auth` |
| `JWT_ALGORITHM` | Défaut `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée du jeton |
| `FRONTEND_ORIGIN` | Origines CORS, séparées par des virgules |
| `SEED_DEMO` | `1` lance le seed fictif après les migrations. `0` en base partagée |
| `DOXAMI_AI_API_KEY` | Vide = assistant indisponible |
| `DOXAMI_PSP_API_KEY` | Vide = pas de checkout ni de payout |
| `DOXAMI_ADMIN_BOOTSTRAP_TOKEN` | Vide = `/admin/bootstrap` répond 503 |
| `MATCH_RADIUS_METERS` | Rayon de matching legacy, pas un secret |

`PORT` est fourni par Railway. Ne pas le committer.

## Démarrage API

`backend/railway.toml` et l’image :

1. `alembic upgrade head`
2. `python scripts/seed_demo.py` seulement si `SEED_DEMO=1`
3. `uvicorn` sur `$PORT`

Santé :

- `GET /health` — le processus répond. Ne touche pas la base.
- `GET /health/ready` — `SELECT 1`. **503** si `DATABASE_URL` manque ou si la base ne répond pas. C’est le healthcheck Railway.

## Sauvegardes

Ce dépôt n’active pas les backups. Dans le projet Railway, activer les
sauvegardes du plugin Postgres et noter la rétention dans le dashboard.
Une copie logique locale éventuelle : `pg_dump` vers un stockage privé,
jamais dans git.

## Surveillance sans données personnelles

Surveiller le code HTTP de `/health` et `/health/ready`, le taux de 5xx,
et l’échec de `alembic upgrade`. Ne pas envoyer dans les logs : corps des
requêtes, en-tête `Authorization`, email, téléphone, GPS, groupe sanguin,
secret TOTP, `JWT_SECRET`.

Les journaux admin (`/admin/logs`) stockent une action et des identifiants,
pas ces champs.
