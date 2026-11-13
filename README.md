# Dukaan-Voice (DukaanAI Foundation)

Production-oriented foundation for a multilingual voice-first Kirana assistant.

## Stack
- Backend: FastAPI (Python)
- Frontend: Streamlit
- DB: Supabase PostgreSQL (migration included)
- Testing: Pytest
- Deployment: Docker + Render-ready structure

## Structure
- `backend/app/api` routes
- `backend/app/services` business + orchestration
- `backend/app/repositories` repository layer
- `backend/app/integrations` gnani/llm/supabase adapters
- `database/migrations` SQL schema + RLS
- `frontend` Streamlit app

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Run tests:
```bash
cd backend
pytest tests -q
```

Run with Docker:
```bash
docker compose up --build
```

## External credentials required
Set these in `.env` (see `.env.example`):
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `GNANI_PRISMA_URL`, `GNANI_PRISMA_API_KEY`
- `GNANI_TIMBRE_URL`, `GNANI_TIMBRE_API_KEY`

Gnani adapters are intentionally documented placeholders until verified API docs are integrated.
