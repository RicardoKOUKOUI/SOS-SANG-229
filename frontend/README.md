# Frontend — DOXAMI (+ legacy SOS Sang 229)

React (JavaScript) + Tailwind CSS + Vite.

## Lancer

```bash
npm install
npm run dev
```

App : [http://localhost:5173](http://localhost:5173)

Le proxy Vite `/api` → `http://127.0.0.1:8000` est configuré dans `vite.config.js`.

## Routes principales

| Chemin | Écran |
| --- | --- |
| `/` | Accueil DOXAMI (feed placeholder Phase 2) |
| `/auth/*` | Welcome, register, login, forgot, verify, logout |
| `/profile`, `/profile/edit` | Profil authentifié |
| `/u/:username` | Profil public |
| `/hub` | Hub + modules placeholder |
| `/legacy/sang/*` | Démo hackathon SOS Sang (branchée API) |

Anciennes URLs `/donneur/inscription`, `/alerte`, `/suivi` restent accessibles temporairement.
