"""
ChainMind API — FastAPI backend.

Serves graph data for the visualization, filter options, single-node traversal,
and the GraphRAG chat endpoint. All Neo4j access goes through the shared
read-only session helper in db.py; config comes from config.py.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ChatRequest,
    ChatResponse,
    GraphResponse,
    HealthResponse,
)
from config import get_settings
from db import close_driver, read_session
from pipeline.graphrag import ask

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_driver()


app = FastAPI(title="ChainMind API", version="2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _node_from_record(record) -> dict:
    return {"id": record["id"], "label": record["label"], **record["props"]}


def _link_from_record(record) -> dict:
    return {
        "source": record["source"],
        "target": record["target"],
        "type": record["type"],
        **record["props"],
    }


@app.get("/")
def root():
    return {"status": "ChainMind API running"}


@app.get("/health", response_model=HealthResponse)
def health():
    """Liveness + Neo4j connectivity check."""
    neo4j_status = "connected"
    try:
        with read_session() as session:
            session.run("RETURN 1").consume()
    except Exception:  # noqa: BLE001 — report unavailability, don't crash
        neo4j_status = "unavailable"
    return HealthResponse(status="ok", neo4j=neo4j_status)


@app.get("/api/graph", response_model=GraphResponse)
def get_full_graph():
    """Return nodes + relationships for visualization, capped at the node limit."""
    limit = settings.graph_node_limit
    with read_session() as session:
        total = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]

        nodes_result = session.run(
            """
            MATCH (n)
            RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props
            LIMIT $limit
            """,
            limit=limit,
        )
        nodes = [_node_from_record(r) for r in nodes_result]
        node_ids = [n["id"] for n in nodes]

        links = []
        if node_ids:
            rels_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.id IN $ids AND b.id IN $ids
                RETURN a.id AS source, b.id AS target, type(r) AS type,
                       properties(r) AS props
                """,
                ids=node_ids,
            )
            links = [_link_from_record(r) for r in rels_result]

    return GraphResponse(nodes=nodes, links=links, truncated=total > len(nodes))


@app.get("/api/graph/filtered", response_model=GraphResponse)
def get_filtered_graph(
    node_type: str | None = None,
    country: str | None = None,
    category: str | None = None,
):
    """Return a filtered subgraph (by node type / country / category)."""
    limit = settings.graph_node_limit
    label_filter = f":{node_type}" if node_type and node_type.isalnum() else ""

    where_clauses = []
    params: dict = {"limit": limit}
    if country:
        where_clauses.append("n.country = $country")
        params["country"] = country
    if category:
        where_clauses.append("n.category = $category")
        params["category"] = category
    where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with read_session() as session:
        nodes_result = session.run(
            f"""
            MATCH (n{label_filter})
            {where_str}
            RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props
            LIMIT $limit
            """,
            **params,
        )
        nodes = [_node_from_record(r) for r in nodes_result]
        node_ids = [n["id"] for n in nodes]

        links = []
        if node_ids:
            rels_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.id IN $ids AND b.id IN $ids
                RETURN a.id AS source, b.id AS target, type(r) AS type,
                       properties(r) AS props
                """,
                ids=node_ids,
            )
            links = [_link_from_record(r) for r in rels_result]

    return GraphResponse(nodes=nodes, links=links, truncated=len(nodes) >= limit)


@app.get("/api/node/{node_id}")
def get_node_neighbors(node_id: str):
    """Return a node and its direct connections — for manual traversal."""
    with read_session() as session:
        result = session.run(
            """
            MATCH (n {id: $node_id})
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN n.id AS center_id, labels(n)[0] AS center_label,
                   properties(n) AS center_props,
                   collect({
                       id: m.id,
                       label: labels(m)[0],
                       props: properties(m),
                       rel_type: type(r),
                       rel_props: properties(r),
                       direction: CASE WHEN startNode(r) = n THEN 'outgoing'
                                       ELSE 'incoming' END
                   }) AS neighbors
            """,
            node_id=node_id,
        )
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        "center": {
            "id": record["center_id"],
            "label": record["center_label"],
            **record["center_props"],
        },
        # collect() yields one {id: null, ...} entry when there are no neighbors.
        "neighbors": [n for n in record["neighbors"] if n["id"] is not None],
    }


@app.get("/api/filters")
def get_filter_options():
    """Return available filter values for the UI dropdowns."""
    with read_session() as session:
        node_types = session.run(
            "CALL db.labels() YIELD label RETURN collect(label) AS labels"
        ).single()["labels"]
        countries = session.run(
            """
            MATCH (n) WHERE n.country IS NOT NULL
            RETURN collect(DISTINCT n.country) AS countries
            """
        ).single()["countries"]
        categories = session.run(
            """
            MATCH (n) WHERE n.category IS NOT NULL
            RETURN collect(DISTINCT n.category) AS categories
            """
        ).single()["categories"]

    return {
        "node_types": node_types,
        "countries": sorted(countries),
        "categories": sorted(categories),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """GraphRAG chat endpoint."""
    try:
        result = ask(req.question)
    except Exception as e:  # noqa: BLE001 — bounded by LLM/query timeouts
        raise HTTPException(
            status_code=502,
            detail=f"Chat pipeline failed: {e}",
        ) from e
    return ChatResponse(**result)
