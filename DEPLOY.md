# Deployment

ChainMind has two parts that deploy separately:

- **Frontend** (Next.js in `frontend/`) → **Vercel**
- **Backend** (FastAPI + Neo4j) → a host that runs a Python server + a database
  (Railway, Render, Fly.io, …). Vercel **cannot** run the FastAPI/Neo4j
  backend, so it must live elsewhere and the frontend points at it.

## Frontend on Vercel

1. Push this repo to GitHub (done).
2. In Vercel: **Add New → Project → import this repo.**
3. **Set Root Directory to `frontend`** (Settings → General → Root Directory).
   Vercel auto-detects Next.js from there.
4. Add an environment variable:
   - `NEXT_PUBLIC_API_URL` = the public URL of your deployed backend
     (e.g. `https://chainmind-api.up.railway.app`).
5. **Deploy.** Every push to `main` then redeploys automatically.

> The frontend needs the backend URL at **build time** (it's a
> `NEXT_PUBLIC_*` var), so set it before deploying and redeploy after changing it.

## Backend (example: Railway)

1. New project → Deploy from this repo.
2. Add a **Neo4j** database (Railway plugin, Neo4j Aura, or a Neo4j container).
3. Set env vars from `.env.example`:
   - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
   - `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
   - `CORS_ORIGINS` = your Vercel frontend URL (pin it, don't use `*` in prod)
4. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   (a `Dockerfile` is included if you prefer container deploys).
5. Load the graph once the DB is up:
   `python data/generate_data.py && python graph/load_graph.py --reset`

## Local full stack

```bash
cp .env.example .env          # set NEO4J_PASSWORD + LLM_API_KEY
docker compose up -d          # Neo4j + API
python graph/load_graph.py --reset
cd frontend && npm install && npm run dev
```
