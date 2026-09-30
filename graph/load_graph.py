"""
Idempotent, batched Neo4j loader.

Loads data/supply_chain_data.json into Neo4j. Nodes and relationships are MERGEd
(re-running never duplicates), attributes are applied generically with `SET += `
(so new properties in the generator load with no change here), and writes are
batched with UNWIND. Pass --reset to clear the database first.
"""

import argparse
import json
import os
import sys

# Allow running directly (`python graph/load_graph.py`) as well as `-m`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase  # noqa: E402

from config import get_settings  # noqa: E402

BATCH_SIZE = 1000

# (label, json key) — the label whitelist also makes the f-strings below safe.
NODE_SPECS = [
    ("Supplier", "suppliers"),
    ("Component", "components"),
    ("Product", "products"),
    ("Warehouse", "warehouses"),
    ("Retailer", "retailers"),
]

# (rel type, json key, from label, from key, to label, to key)
REL_SPECS = [
    ("SUPPLIES", "supplies", "Supplier", "supplier_id", "Component", "component_id"),
    ("USED_IN", "used_in", "Component", "component_id", "Product", "product_id"),
    ("STORED_AT", "stored_at", "Product", "product_id", "Warehouse", "warehouse_id"),
    ("SHIPS_TO", "ships_to", "Warehouse", "warehouse_id", "Retailer", "retailer_id"),
]


def clear_database(session) -> None:
    session.run("MATCH (n) DETACH DELETE n")
    print("Database cleared.")


def create_constraints(session) -> None:
    for label, _ in NODE_SPECS:
        session.run(
            f"CREATE CONSTRAINT IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.id IS UNIQUE"
        )
    print("Constraints ensured.")


def _batched(rows: list) -> list:
    for i in range(0, len(rows), BATCH_SIZE):
        yield rows[i:i + BATCH_SIZE]


def load_nodes(session, label: str, rows: list[dict]) -> None:
    for batch in _batched(rows):
        session.run(
            f"UNWIND $rows AS row MERGE (n:{label} {{id: row.id}}) SET n += row",
            rows=batch,
        )
    print(f"  {label}: {len(rows)}")


def load_relationships(session, spec: tuple, rows: list[dict]) -> None:
    rel_type, _, from_label, from_key, to_label, to_key = spec
    payload = [
        {
            "from": r[from_key],
            "to": r[to_key],
            "props": {k: v for k, v in r.items() if k not in (from_key, to_key)},
        }
        for r in rows
    ]
    for batch in _batched(payload):
        session.run(
            f"UNWIND $rows AS row "
            f"MATCH (a:{from_label} {{id: row.from}}) "
            f"MATCH (b:{to_label} {{id: row.to}}) "
            f"MERGE (a)-[rel:{rel_type}]->(b) SET rel += row.props",
            rows=batch,
        )
    print(f"  {rel_type}: {len(rows)}")


def verify_graph(session) -> None:
    print("\nGraph summary:")
    for record in session.run(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS c ORDER BY label"
    ):
        print(f"  {record['label']}: {record['c']} nodes")
    for record in session.run(
        "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY t"
    ):
        print(f"  {record['t']}: {record['c']} relationships")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the supply-chain graph into Neo4j.")
    parser.add_argument("--reset", action="store_true", help="Clear the database first.")
    args = parser.parse_args()

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "supply_chain_data.json")
    with open(data_path) as f:
        data = json.load(f)

    s = get_settings()
    driver = GraphDatabase.driver(
        s.neo4j_uri, auth=(s.neo4j_username, s.neo4j_password)
    )
    try:
        with driver.session() as session:
            print("Loading supply chain graph into Neo4j...\n")
            if args.reset:
                clear_database(session)
            create_constraints(session)

            print("\nLoading nodes:")
            for label, key in NODE_SPECS:
                load_nodes(session, label, data[key])

            print("\nLoading relationships:")
            for spec in REL_SPECS:
                load_relationships(session, spec, data[spec[1]])

            verify_graph(session)
            print("\nDone! Open http://localhost:7474 to explore your graph.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
