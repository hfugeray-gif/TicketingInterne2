# Ticketing App

Monorepo de l'application ticketing interne.

## Structure
- `frontend/streamlit_app` : interface Streamlit
- `backend` : API FastAPI
- `infra` : docker-compose et infra locale
- `docs` : documentation

## Lancer en local
1. Copier `.env.example` en `.env`
2. Lancer :
   ```bash
   docker compose -f infra/docker-compose.yml up --build