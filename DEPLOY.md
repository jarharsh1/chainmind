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

## Backend on Railway

The repo ships a `railway.json` and `Dockerfile`, so the API service is
near one-click. You also need a Neo4j database — **Neo4j Aura Free** (managed
cloud) is the simplest; self-hosting Neo4j as a second Railway service also works.

### 1. Neo4j (recommended: Aura Free)
1. Create a free database at https://neo4j.com/cloud/aura-free/.
2. Save the **connection URI** (`neo4j+s://xxxx.databases.neo4j.io`), username
   (`neo4j`) and the generated password.

> Alternatively, on Railway: **New → Empty Service → Deploy a Docker image**
> `neo4j:5.18.0`, set `NEO4J_AUTH=neo4j/<password>` and `NEO4J_PLUGINS=["apoc"]`,
> add a volume at `/data`, and use its internal `bolt://` URL as `NEO4J_URI`.

### 2. API service on Railway
1. **New Project → Deploy from GitHub repo** → pick `jarharsh1/chainmind`.
   Railway reads `railway.json` and builds the `Dockerfile` automatically.
2. Add environment variables (Service → Variables):
   - `NEO4J_URI` = your Aura/Neo4j URI
   - `NEO4J_USERNAME` = `neo4j`
   - `NEO4J_PASSWORD` = your Neo4j password
   - `LLM_BASE_URL` = `https://api.groq.com/openai/v1`
   - `LLM_API_KEY` = your Groq key
   - `LLM_MODEL` = `llama-3.3-70b-versatile`
   - `CORS_ORIGINS` = your Vercel URL (e.g. `https://chainmind.vercel.app`) —
     pin it, don't use `*` in production
3. Deploy. Railway serves the API on a public domain and health-checks `/health`.

### 3. Load the graph (once)
From the Railway service shell (or locally with the same env vars pointing at Aura):
```bash
python data/generate_data.py && python graph/load_graph.py --reset
```

### 4. Point the frontend at it
Set `NEXT_PUBLIC_API_URL` in Vercel to the Railway API domain, then redeploy
the frontend.

## Local full stack

```bash
cp .env.example .env          # set NEO4J_PASSWORD + LLM_API_KEY
docker compose up -d          # Neo4j + API
python graph/load_graph.py --reset
cd frontend && npm install && npm run dev
```
