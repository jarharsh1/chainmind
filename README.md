# ⛓ ChainMind — Supply Chain Intelligence Engine

A GraphRAG-powered supply chain intelligence platform that lets you explore, filter, and query supply chain data using natural language.

## What is this?

ChainMind stores supply chain data (suppliers, components, products, warehouses, retailers) as a **knowledge graph** in Neo4j. Instead of writing SQL queries, you ask questions in plain English — the system converts them to Cypher queries, traverses the graph, and returns precise answers.

## Tech Stack

- **Backend:** FastAPI + Neo4j + LangChain
- **Frontend:** Next.js + react-force-graph-2d + Tailwind CSS
- **LLM:** NVIDIA NIM (Llama 3.1 70B Instruct)
- **Database:** Neo4j (Docker)

## Architecture

User Question → Schema Pruner → LLM (Cypher Generation) → Neo4j → LLM (Answer) → User

**Key Innovation — Schema Pruning:**
Instead of sending the full database schema to the LLM on every query (token bloat), ChainMind classifies the question and sends only the relevant schema subset. This reduces token usage by 70-85%.

## Features

- **Interactive Graph Visualization** — Explore the full supply chain as a force-directed graph
- **Click-to-Focus** — Click any node to see only its connections, hiding the rest
- **Filters** — Filter by node type, country, or category
- **Manual Traversal** — Click through connections to explore the graph step by step
- **GraphRAG Chatbot** — Ask natural language questions and get precise answers powered by graph traversal
- **Cypher Transparency** — View the generated Cypher query for every answer

## Sample Queries

- "Which components have only one supplier?"
- "If Taiwan Semiconductor Co goes down, which products are affected?"
- "What is the cheapest route to Flipkart India?"
- "How much Galaxy Ultra X stock is in Dubai?"
- "Compare shipping costs between air and sea routes"

## Setup

### Prerequisites
- Docker Desktop
- Python 3.10+
- Node.js 18+
- NVIDIA NIM API key (free at build.nvidia.com)

### Backend
```bash
# Start Neo4j
docker-compose up -d

# Create virtual environment
py -3.10 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env — add your NVIDIA_API_KEY

# Generate data and load graph
python data/generate_data.py
python graph/load_graph.py

# Start API
uvicorn api.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Project Structure

chainmind/
├── docker-compose.yml
├── .env
├── requirements.txt
├── data/
│   ├── generate_data.py
│   └── supply_chain_data.json
├── graph/
│   └── load_graph.py
├── pipeline/
│   ├── init.py
│   ├── schema_pruner.py
│   ├── cypher_chain.py
│   └── graphrag.py
├── api/
│   ├── init.py
│   └── main.py
├── main.py
└── frontend/
└── (Next.js app)

## How GraphRAG Works

1. **User asks:** "If Taiwan Semiconductor goes down, which products are affected?"
2. **Schema Pruner:** Classifies as "risk" → sends only Supplier, Component, Product schema
3. **LLM generates Cypher:**
```cypher
   MATCH (s:Supplier {name: "Taiwan Semiconductor Co"})-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product)
   RETURN DISTINCT p.name, c.name AS affected_component
```
4. **Neo4j executes:** Returns 7 affected products across smartphones, laptops, tablets, wearables
5. **LLM answers:** Natural language summary with categorized results

