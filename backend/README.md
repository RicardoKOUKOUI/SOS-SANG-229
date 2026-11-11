# Backend — SOS Sang 229

API FastAPI : auth DOXAMI (JWT) + legacy SOS Sang (donors/alerts/matching haversine Text WKT,
donations, tracking). Point d’entrée : `app/main.py`.

## Lancer l’API

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Lancer ces commandes depuis le dossier `backend/`.

- Santé : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Docs OpenAPI : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

`GET /health` fonctionne sans base. Les routes métier exigent `DATABASE_URL`.

## Postgres + PostGIS et migrations

La base locale est le service `db` de `docker-compose.yml` (`postgis/postgis:16-3.4`).
Les locations sont stockées en Text WKT ; le matching utilise haversine Python (pas ST_DWithin). L’image Compose PostGIS reste compatible.

1. À la racine du dépôt, copier `.env.example` vers `.env` (jamais commité).
2. Définir un mot de passe local dans `.env`, par exemple :

   ```
   POSTGRES_PASSWORD=changeme_local_only
   DATABASE_URL=postgresql://sos_sang:changeme_local_only@127.0.0.1:5432/sos_sang_229
   MATCH_RADIUS_METERS=15000
   JWT_SECRET=local-dev-only-change-me
   ```

   Utiliser uniquement des identifiants locaux fictifs. Ne pas y mettre de secrets de production.

3. Démarrer Postgres :

   ```bash
   docker compose up -d
   ```

4. Depuis `backend/`, avec le venv activé :

   ```bash
   alembic upgrade head
   ```

Seed optionnel (données **clairement fictives** seulement : `Donneur Demo`, `+22900000000`, `Zone Demo`, `REQ-DEMO-*`) :

```bash
python scripts/seed_demo.py
```

Le script n’affiche jamais téléphone, GPS ni groupe sanguin.

Revenir en arrière (détruit les tables MVP, laisse l’extension PostGIS) :

```bash
alembic downgrade base
```

### Équivalent sans Docker

Une instance PostgreSQL 16 avec PostGIS et `DATABASE_URL` pointant dessus suffit.
Puis `alembic upgrade head` comme ci-dessus.

## Matching

Service : `app/matching.py`.

| Règle | Comportement |
| --- | --- |
| Compatibilité | ABO/Rh classique (ex. `O-` → tous ; un besoin `O+` accepte `O-` et `O+`) |
| Disponibilité | `donors.is_available = true` uniquement |
| GPS | Si l’hôpital **et** le donneur ont un `location` : `ST_DWithin` (geography, mètres) |
| Rayon par défaut | **15 000 m (15 km)**, via `MATCH_RADIUS_METERS` |
| Repli ville | Si le GPS manque d’un côté : même `city` (insensible à la casse) |
| Persistance | `urgency_matches` (`match_method` = `gps` \| `city`) + `alerted_donors_count` |

Aucun log de téléphone, GPS ou groupe sanguin. Twilio n’est **pas** appelé
(`app/notifications.py` = stub / TODO simulation).

Une urgence **doit** cibler `hospitals.is_recognized = true` (`app.rules.require_recognized_hospital`
+ trigger Postgres `trg_urgency_recognized_hospital`).

## Endpoints

| Méthode | Chemin | Rôle |
| --- | --- | --- |
| `GET` | `/health` | Santé |
| `GET` | `/hospitals` | Hôpitaux (`is_recognized=true` par défaut) |
| `GET` | `/hospitals/recognized` | Alias du select reconnu |
| `POST` | `/donors` | Inscription donneur |
| `POST` | `/alerts` | Créer une urgence + matching |
| `POST` | `/donations` | Confirmer un don |
| `GET` | `/requests` | Liste de suivi (compteurs) |
| `GET` | `/requests/{public_ref}` | Suivi d’une urgence |

Les réponses de suivi / liste **n’incluent pas** les numéros de téléphone ni le GPS.
`POST /donors` omet aussi le téléphone en réponse.

JWT n’est pas requis pour ce MVP (pas d’auth).

## Exemples curl (données fictives, sans secrets)

Après `alembic upgrade head` et éventuellement `python scripts/seed_demo.py`.

```bash
# Santé (sans base)
curl -s http://127.0.0.1:8000/health

# Hôpitaux reconnus (select)
curl -s http://127.0.0.1:8000/hospitals/recognized

# Inscription donneur fictif
curl -s -X POST http://127.0.0.1:8000/donors \
  -H 'Content-Type: application/json' \
  -d '{"display_name":"Donneur Demo","blood_group":"O+","phone":"+22900000000","city":"Zone Demo"}'

# Alerte : remplacer HOSPITAL_ID par un id renvoyé par /hospitals/recognized
curl -s -X POST http://127.0.0.1:8000/alerts \
  -H 'Content-Type: application/json' \
  -d '{"public_ref":"REQ-DEMO-API","blood_group_needed":"O+","patient_display_name":"Patient Demo","hospital_id":"HOSPITAL_ID","zone_label":"Zone Demo"}'

# Suivi (sans téléphone)
curl -s http://127.0.0.1:8000/requests/REQ-DEMO-API

# Confirmation : remplacer les UUID renvoyés
curl -s -X POST http://127.0.0.1:8000/donations \
  -H 'Content-Type: application/json' \
  -d '{"donor_id":"DONOR_ID","urgency_request_id":"URGENCY_ID"}'
```

Le seed expose `Hopital Demo` (`00000000-0000-4000-8000-000000000010`) et
`REQ-DEMO-001` s’il a déjà été inséré. `Clinique Demo Non Reconnue` doit être
refusée par `POST /alerts`.

## Tests

```bash
cd backend
python -m pytest
```

Pytest couvre le matching (compatibilité, rayon GPS, repli ville), la règle
hôpital reconnu, la chaîne Alembic, et les endpoints clés avec des données
fictives uniquement (SQLite en mémoire, sans secrets). Le chemin PostGIS
(`ST_DWithin`) est exercé en production / Docker ; les tests utilisent le
repli Python (mêmes règles GPS / ville).

## Schéma MVP

| Table | Rôle produit | Champs sensibles |
| --- | --- | --- |
| `donors` | User / Donneur | `phone`, `blood_group`, `location` (GPS PostGIS) |
| `hospitals` | Établissement | `contact_phone`, `location` |
| `urgency_requests` | Urgence / alerte (`hospital_id` FK uniquement) | `blood_group_needed`, `patient_display_name` (démo uniquement) |
| `urgency_matches` | Candidats matchés (`gps` / `city`) | — (pas de téléphone / GPS / groupe) |
| `donation_confirmations` | Confirmation de don | lie donneur + urgence (`confirmed_at`, `status`) |

### Hôpitaux reconnus

Une urgence ne peut cibler **que** un établissement avec `hospitals.is_recognized = true`.

- Défaut colonne : **`false`**.
- Pas de nom d’hôpital en texte libre sur `urgency_requests` : uniquement `hospital_id`.
- Le seed marque `Hopital Demo` comme reconnu et ajoute `Clinique Demo Non Reconnue`.
- Helper : `app.rules.require_recognized_hospital`. Trigger : `trg_urgency_recognized_hospital`.

## Dossiers

```
app/
  main.py           # application FastAPI
  config.py         # DATABASE_URL + MATCH_RADIUS_METERS
  matching.py       # compatibilité + PostGIS / repli ville
  notifications.py  # stub SMS (pas de Twilio)
  routers/          # health, hospitals, donors, alerts, donations, tracking
  models/           # ORM SQLAlchemy + PostGIS
  schemas/          # Pydantic create/read/public
alembic/            # migrations
scripts/seed_demo.py
tests/              # pytest
```

JWT et Twilio ne sont pas implémentés. Les variables correspondantes figurent uniquement dans `.env.example`.

**Ne jamais logger téléphone, GPS ou groupe sanguin en clair.**
