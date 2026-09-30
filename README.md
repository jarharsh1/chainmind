# ⛓ ChainMind — Supply Chain Intelligence Engine

A GraphRAG-powered supply chain platform. Supply chain data (suppliers,
components, products, warehouses, retailers) lives as a **knowledge graph** in
Neo4j. Instead of writing Cypher, you ask questions in plain English — ChainMind
classifies the question, generates a **read-only** Cypher query, runs it against
the graph, and turns the results into an answer.

## Tech Stack

- **Backend:** FastAPI + Neo4j (official driver)
- **Frontend:** Next.js + react-force-graph-2d + Tailwind CSS
- **LLM:** any OpenAI-compatible endpoint (Groq by default)
- **Database:** Neo4j (Docker)

## Architecture

```
Question → Schema Pruner → LLM (Cypher) → read-only guard → Neo4j → LLM (answer)
```

**Schema pruning:** rather than sending the full schema to the LLM on every
query (token bloat), ChainMind classifies the question and sends only the
relevant subset — a large token saving on each call.

**Read-only guard:** every LLM-generated query is validated before it runs. Any
write/DDL/admin clause is rejected, so the chat path can never modify the graph.
The query also runs in a session opened with READ access — defense in depth.

## Features

- Interactive force-directed graph of the whole supply chain
- Click-to-focus: click a node to see only it and its connections
- Filters by node type, country, and category
- GraphRAG chat with loading / empty / error states
- Cypher transparency: the generated query is shown (and copyable) per answer

## Sample Questions

- "Which components have only one supplier?"
- "If Taiwan Semiconductor Co goes down, which products are affected?"
- "What is the cheapest route to Flipkart India?"
- "Which suppliers have on-time delivery below 90%?"
- "Which warehouse is closest to full capacity?"
- "What components are used in Galaxy Ultra X?"

## LLM Provider (pure configuration)

The provider is entirely config-driven — point these three env vars at any
OpenAI-compatible endpoint, no code change:

| Provider   | `LLM_BASE_URL`                        | `LLM_MODEL` (example)         |
|------------|---------------------------------------|-------------------------------|
| **Groq**   | `https://api.groq.com/openai/v1`      | `llama-3.3-70b-versatile`     |
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.1-70b-instruct` |
| Ollama     | `http://localhost:11434/v1`           | `llama3.1:8b`                 |
| OpenAI     | `https://api.openai.com/v1`           | `gpt-4o-mini`                 |

Set `LLM_API_KEY` for hosted providers (any non-empty string works for Ollama).

## Setup

### Prerequisites
- Docker, Python 3.11+, Node.js 18+
- An API key for your chosen LLM provider (Groq: https://console.groq.com)

### 1. Environment
```bash
cp .env.example .env
# edit .env — set NEO4J_PASSWORD and LLM_API_KEY (never commit .env)
```

### 2. Backend
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt      # or requirements.txt for runtime only

docker compose up -d neo4j               # start Neo4j
python data/generate_data.py             # generate the dataset
python graph/load_graph.py --reset       # load it into Neo4j

uvicorn api.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
cp .env.example .env.local               # set NEXT_PUBLIC_API_URL if not localhost
npm install
npm run dev
```
Open http://localhost:3000

### Full stack with Docker
```bash
docker compose up -d          # Neo4j + API (set .env first)
# then load data once the DB is healthy:
python graph/load_graph.py --reset
```

## Project Structure

```
chainmind/
├── config.py              # pydantic-settings; all env access
├── db.py                  # shared driver + read_session()
├── main.py                # CLI entry point
├── api/
│   ├── main.py            # FastAPI app
│   └── schemas.py         # typed request/response models
├── pipeline/
│   ├── schema_pruner.py   # classify_question, get_pruned_schema
│   ├── guards.py          # read-only Cypher validation
│   ├── llm.py             # OpenAI-compatible client (timeout + retry)
│   ├── cypher_chain.py    # generate → guard → execute → answer
│   └── graphrag.py        # orchestration
├── data/generate_data.py  # deterministic synthetic data generator
├── graph/load_graph.py    # idempotent batched loader (--reset)
├── tests/                 # pytest suite (no live services needed)
└── frontend/              # Next.js app (component-based)
```

## Testing

```bash
ruff check .      # lint
pytest -q         # 37 tests; LLM + Neo4j are mocked, no services required
```

The suite includes the key security check: a prompt-injected write request is
refused by the guard and never reaches the database.

## Deployment

Frontend deploys to Vercel (root directory `frontend`, set `NEXT_PUBLIC_API_URL`);
the FastAPI + Neo4j backend deploys separately (Railway/Render/etc.). Full
step-by-step in [DEPLOY.md](DEPLOY.md).

## Security Notes

- The chat path uses a read-only Cypher guard **and** a READ-access session.
- Configure a dedicated read-only Neo4j user via `NEO4J_READ_USERNAME` /
  `NEO4J_READ_PASSWORD` for the query path (falls back to the main user).
- Secrets live only in `.env` (gitignored). `.env.example` holds placeholders.
- Pin `CORS_ORIGINS` to your frontend origin in production.
