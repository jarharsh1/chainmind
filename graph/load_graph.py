import json
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def clear_database(session):
    """Pehle purana data delete karo — clean start"""
    session.run("MATCH (n) DETACH DELETE n")
    print("Database cleared.")

def create_constraints(session):
    """Unique constraints — duplicate nodes na bane"""
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Supplier) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Component) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (w:Warehouse) REQUIRE w.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Retailer) REQUIRE r.id IS UNIQUE",
    ]
    for c in constraints:
        session.run(c)
    print("Constraints created.")

def load_nodes(session, data):
    """Saare nodes create karo"""

    # Suppliers
    for s in data["suppliers"]:
        session.run(
            """CREATE (s:Supplier {
                id: $id, name: $name, country: $country,
                on_time_delivery_pct: $on_time_delivery_pct,
                lead_time_days: $lead_time_days
            })""",
            **s
        )
    print(f"  Suppliers loaded: {len(data['suppliers'])}")

    # Components
    for c in data["components"]:
        session.run(
            """CREATE (c:Component {
                id: $id, name: $name, category: $category,
                unit_cost: $unit_cost, criticality: $criticality
            })""",
            **c
        )
    print(f"  Components loaded: {len(data['components'])}")

    # Products
    for p in data["products"]:
        session.run(
            """CREATE (p:Product {
                id: $id, name: $name, category: $category,
                price: $price
            })""",
            **p
        )
    print(f"  Products loaded: {len(data['products'])}")

    # Warehouses
    for w in data["warehouses"]:
        session.run(
            """CREATE (w:Warehouse {
                id: $id, name: $name, city: $city,
                country: $country, capacity: $capacity
            })""",
            **w
        )
    print(f"  Warehouses loaded: {len(data['warehouses'])}")

    # Retailers
    for r in data["retailers"]:
        session.run(
            """CREATE (r:Retailer {
                id: $id, name: $name, city: $city,
                country: $country, type: $type
            })""",
            **r
        )
    print(f"  Retailers loaded: {len(data['retailers'])}")

def load_relationships(session, data):
    """Saare relationships create karo"""

    # SUPPLIES: Supplier → Component
    for rel in data["supplies"]:
        session.run(
            """MATCH (s:Supplier {id: $supplier_id})
               MATCH (c:Component {id: $component_id})
               CREATE (s)-[:SUPPLIES {volume_per_month: $volume_per_month}]->(c)""",
            **rel
        )
    print(f"  SUPPLIES relationships: {len(data['supplies'])}")

    # USED_IN: Component → Product
    for rel in data["used_in"]:
        session.run(
            """MATCH (c:Component {id: $component_id})
               MATCH (p:Product {id: $product_id})
               CREATE (c)-[:USED_IN {quantity: $quantity}]->(p)""",
            **rel
        )
    print(f"  USED_IN relationships: {len(data['used_in'])}")

    # STORED_AT: Product → Warehouse
    for rel in data["stored_at"]:
        session.run(
            """MATCH (p:Product {id: $product_id})
               MATCH (w:Warehouse {id: $warehouse_id})
               CREATE (p)-[:STORED_AT {stock_quantity: $stock_quantity}]->(w)""",
            **rel
        )
    print(f"  STORED_AT relationships: {len(data['stored_at'])}")

    # SHIPS_TO: Warehouse → Retailer
    for rel in data["ships_to"]:
        session.run(
            """MATCH (w:Warehouse {id: $warehouse_id})
               MATCH (r:Retailer {id: $retailer_id})
               CREATE (w)-[:SHIPS_TO {
                   mode: $mode, cost_per_unit: $cost_per_unit,
                   transit_days: $transit_days
               }]->(r)""",
            **rel
        )
    print(f"  SHIPS_TO relationships: {len(data['ships_to'])}")

def verify_graph(session):
    """Check ki sab sahi load hua"""
    result = session.run("""
        MATCH (n)
        RETURN labels(n)[0] AS label, COUNT(n) AS count
        ORDER BY label
    """)
    print("\nGraph summary:")
    for record in result:
        print(f"  {record['label']}: {record['count']} nodes")

    result = session.run("""
        MATCH ()-[r]->()
        RETURN TYPE(r) AS type, COUNT(r) AS count
        ORDER BY type
    """)
    for record in result:
        print(f"  {record['type']}: {record['count']} relationships")

def main():
    # Load JSON data
    with open("data/supply_chain_data.json", "r") as f:
        data = json.load(f)

    with driver.session() as session:
        print("Loading supply chain graph into Neo4j...\n")
        clear_database(session)
        create_constraints(session)
        print("\nLoading nodes:")
        load_nodes(session, data)
        print("\nLoading relationships:")
        load_relationships(session, data)
        verify_graph(session)
        print("\nDone! Open http://localhost:7474 to explore your graph.")

    driver.close()

if __name__ == "__main__":
    main()