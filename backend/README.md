# CyberPulse Backend (MVP)

Backend FastAPI pour CyberPulse — veille, analyse et reporting cybersécurité.

Stack : Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic, MySQL 8, Redis, JWT (access + refresh), bcrypt, APScheduler, python-socketio (WebSocket), ReportLab (PDF).

## Architecture

```
app/
  api/v1/        routers (auth, users, cves, watchlists, alerts, reports, articles, health)
  core/          config, security (JWT/bcrypt), logging, exceptions
  db/            SQLAlchemy base + async session
  models/        ORM models (users, cves, watchlists, alerts, reports, scraped_articles)
  schemas/       Pydantic request/response models
  repositories/  DB access layer
  services/      business logic (auth, cve, watchlist, alert, report, scraping, report engine)
  tasks/         APScheduler jobs (CVE sync, scraping pipeline)
  websocket/     python-socketio connection manager + ASGI mount
alembic/         migrations
tests/           pytest suite (auth, health) using an in-memory SQLite DB
```

## Prérequis

- Python 3.11+
- MySQL 8 en cours d'exécution
- Redis en cours d'exécution

## Installation

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/macOS
```

Éditez `.env` avec vos identifiants MySQL/Redis et un `JWT_SECRET_KEY` fort.

Créez la base de données MySQL :

```sql
CREATE DATABASE cyberpulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Migrations

```bash
alembic upgrade head
```

## Lancer le serveur

```bash
uvicorn app.main:socket_app --reload --port 8000
```

> Important : pointez uvicorn sur `app.main:socket_app` (et non `app.main:app`) pour que le WebSocket (python-socketio, monté sur `/socket.io`) fonctionne. `socket_app` enveloppe l'application FastAPI complète.

- Documentation interactive : http://localhost:8000/docs
- Health check : http://localhost:8000/api/v1/health

## Tests

```bash
pytest
```

Les tests utilisent une base SQLite en mémoire (aucune dépendance à MySQL/Redis n'est nécessaire pour les lancer).

## Modules implémentés

- **Auth** : register / login / refresh / logout, JWT access (15 min) + refresh (7 jours) avec révocation en base, hachage bcrypt, rôles ADMIN / ANALYST / READER.
- **CVE Engine** : CRUD CVE, filtres (CVSS, sévérité, produit, dates, recherche), endpoint `/cves/sync` qui alimente la base depuis NVD/CISA (génération de données structurellement valides en l'absence d'accès réseau sortant — à remplacer par de vrais appels HTTP dans `CVEService.sync_from_sources`).
- **Watchlists** : CRUD scopé à l'utilisateur connecté.
- **Alerts** : création, listing, acknowledgement ; diffusion temps réel via WebSocket.
- **Reports** : génération de rapports PDF (ReportLab) filtrés sur les CVE, téléchargement.
- **Scraping Engine** : pipeline fetch → parse (BeautifulSoup) → déduplication (hash) → enrichissement (résumé, catégorisation par mots-clés, score de pertinence, extraction de CVE mentionnées) → stockage → notification WebSocket. Source réelle tentée via HTTP, repli sur contenu structurellement valide si la source est inaccessible.
- **WebSocket** : `python-socketio`, événements `alert` et `new_article` diffusés en broadcast.
- **Scheduler** : APScheduler exécute la synchronisation CVE et le pipeline de scraping à intervalles configurables (`.env`).

## Variables d'environnement clés

Voir `.env.example`. Notamment :
- `DATABASE_URL` (async, runtime) / `DATABASE_URL_SYNC` (Alembic)
- `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`
- `SCRAPING_INTERVAL_MINUTES`, `CVE_SYNC_INTERVAL_MINUTES`
- `REPORTS_DIR` (dossier de sortie des PDF générés)
