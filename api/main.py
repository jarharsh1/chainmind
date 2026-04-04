"""
ChainMind API — FastAPI Backend
Serves graph data, filters, and chatbot queries
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pipeline.graphrag import ask

load_dotenv()

app = FastAPI(title="ChainMind API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)


@app.get("/")
def root():
    return {"status": "ChainMind API running"}


@app.get("/api/graph")
def get_full_graph():
    """Return all nodes and relationships for visualization"""
    with driver.session() as session:
        nodes_result = session.run("""
            MATCH (n)
            RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props
        """)
        nodes = []
        for record in nodes_result:
            node = {
                "id": record["id"],
                "label": record["label"],
                **record["props"]
            }
            nodes.append(node)

        rels_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.id AS source, b.id AS target, type(r) AS type, properties(r) AS props
        """)
        links = []
        for record in rels_result:
            link = {
                "source": record["source"],
                "target": record["target"],
                "type": record["type"],
                **record["props"]
            }
            links.append(link)

    return {"nodes": nodes, "links": links}


@app.get("/api/graph/filtered")
def get_filtered_graph(
    node_type: str = None,
    country: str = None,
    category: str = None
):
    """Return filtered graph based on parameters"""
    with driver.session() as session:
        where_clauses = []
        params = {}

        if node_type:
            label_filter = f":{node_type}"
        else:
            label_filter = ""

        if country:
            where_clauses.append("n.country = $country")
            params["country"] = country

        if category:
            where_clauses.append("n.category = $category")
            params["category"] = category

        where_str = " AND ".join(where_clauses)
        where_str = f"WHERE {where_str}" if where_str else ""

        query = f"""
            MATCH (n{label_filter})
            {where_str}
            RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props
        """
        nodes_result = session.run(query, **params)
        node_ids = set()
        nodes = []
        for record in nodes_result:
            node_ids.add(record["id"])
            nodes.append({
                "id": record["id"],
                "label": record["label"],
                **record["props"]
            })

        links = []
        if node_ids:
            rels_result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE a.id IN $ids AND b.id IN $ids
                RETURN a.id AS source, b.id AS target, type(r) AS type, properties(r) AS props
            """, ids=list(node_ids))
            for record in rels_result:
                links.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"],
                    **record["props"]
                })

    return {"nodes": nodes, "links": links}


@app.get("/api/node/{node_id}")
def get_node_neighbors(node_id: str):
    """Get a node and all its direct connections — for manual traversal"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n {id: $node_id})
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN n.id AS center_id, labels(n)[0] AS center_label, properties(n) AS center_props,
                   collect({
                       id: m.id,
                       label: labels(m)[0],
                       props: properties(m),
                       rel_type: type(r),
                       rel_props: properties(r),
                       direction: CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END
                   }) AS neighbors
        """, node_id=node_id)

        record = result.single()
        if not record:
            return {"error": "Node not found"}

        return {
            "center": {
                "id": record["center_id"],
                "label": record["center_label"],
                **record["center_props"]
            },
            "neighbors": record["neighbors"]
        }


@app.get("/api/filters")
def get_filter_options():
    """Return available filter values for the UI dropdowns"""
    with driver.session() as session:
        labels = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels")
        node_types = labels.single()["labels"]

        countries = session.run("""
            MATCH (n) WHERE n.country IS NOT NULL
            RETURN collect(DISTINCT n.country) AS countries
        """).single()["countries"]

        categories = session.run("""
            MATCH (n) WHERE n.category IS NOT NULL
            RETURN collect(DISTINCT n.category) AS categories
        """).single()["categories"]

    return {
        "node_types": node_types,
        "countries": countries,
        "categories": categories
    }


@app.post("/api/chat")
def chat(payload: dict):
    """GraphRAG chatbot endpoint"""
    question = payload.get("question", "")
    if not question:
        return {"error": "No question provided"}

    result = ask(question)
    return result