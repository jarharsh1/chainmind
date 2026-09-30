"""
Schema Pruner — Token Bloat Fix

Instead of sending the FULL schema (all nodes, relationships, properties)
to the LLM on every query, we classify the question and send only
the relevant subset. 70-85% token savings.
"""

# Full schema definition — this is what Neo4j has. Keep in sync with
# data/generate_data.py (the loader writes exactly these properties).
FULL_SCHEMA = {
    "nodes": {
        "Supplier": ["id", "name", "country", "region", "tier",
                     "on_time_delivery_pct", "lead_time_days", "lead_time_variance"],
        "Component": ["id", "name", "category", "unit_cost", "criticality", "alt_supplier_count"],
        "Product": ["id", "name", "category", "price"],
        "Warehouse": ["id", "name", "city", "country", "capacity", "utilization_pct"],
        "Retailer": ["id", "name", "city", "country", "type"],
    },
    "relationships": {
        "SUPPLIES": {"from": "Supplier", "to": "Component",
                     "properties": ["volume_per_month", "unit_price", "lead_time_days"]},
        "USED_IN": {"from": "Component", "to": "Product", "properties": ["quantity"]},
        "STORED_AT": {"from": "Product", "to": "Warehouse", "properties": ["stock_quantity"]},
        "SHIPS_TO": {"from": "Warehouse", "to": "Retailer",
                     "properties": ["mode", "cost_per_unit", "transit_days"]},
    }
}

# Question categories → relevant schema subsets
CATEGORY_SCHEMA_MAP = {
    "supplier": {
        "nodes": ["Supplier", "Component"],
        "relationships": ["SUPPLIES"]
    },
    "product": {
        "nodes": ["Product", "Component"],
        "relationships": ["USED_IN"]
    },
    "inventory": {
        "nodes": ["Product", "Warehouse"],
        "relationships": ["STORED_AT"]
    },
    "shipping": {
        "nodes": ["Warehouse", "Retailer"],
        "relationships": ["SHIPS_TO"]
    },
    "risk": {
        "nodes": ["Supplier", "Component", "Product"],
        "relationships": ["SUPPLIES", "USED_IN"]
    },
    "full_chain": {
        "nodes": ["Supplier", "Component", "Product", "Warehouse", "Retailer"],
        "relationships": ["SUPPLIES", "USED_IN", "STORED_AT", "SHIPS_TO"]
    },
}

# Keywords for classification
CATEGORY_KEYWORDS = {
    "supplier": ["supplier", "supplies", "vendor", "source", "deliver", "delivery", "lead time", "on time"],
    "product": ["product", "uses", "component", "bill of materials", "made of", "contains", "built with"],
    "inventory": ["stock", "inventory", "stored", "warehouse", "capacity", "storage"],
    "shipping": ["ship", "route", "transit", "cost", "transport", "retailer", "store", "deliver to"],
    "risk": ["risk", "single source", "failure", "backup", "alternate", "if.*goes down", "disruption", "only one"],
    "full_chain": ["full chain", "end to end", "supplier to retailer", "entire", "complete path", "whole chain"],
}


def classify_question(question: str) -> str:
    """Classify question into a category based on keyword matching"""
    question_lower = question.lower()

    # Check full_chain FIRST — these are multi-hop queries
    for keyword in CATEGORY_KEYWORDS.get("full_chain", []):
        if keyword in question_lower:
            return "full_chain"

    # Then score the rest
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "full_chain":
            continue
        score = 0
        for keyword in keywords:
            if keyword in question_lower:
                score += 1
        scores[category] = score

    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return "full_chain"

    return best_category


def get_pruned_schema(question: str) -> str:
    """Main function — takes a question, returns pruned schema as string"""
    category = classify_question(question)
    schema_subset = CATEGORY_SCHEMA_MAP[category]

    # Build schema string
    lines = []
    lines.append(f"Category: {category}")
    lines.append("\nNode types:")

    for node_name in schema_subset["nodes"]:
        props = FULL_SCHEMA["nodes"][node_name]
        lines.append(f"  {node_name}: {', '.join(props)}")

    lines.append("\nRelationships:")
    for rel_name in schema_subset["relationships"]:
        rel = FULL_SCHEMA["relationships"][rel_name]
        props_str = f" [{', '.join(rel['properties'])}]" if rel["properties"] else ""
        lines.append(f"  ({rel['from']})-[:{rel_name}{props_str}]->({rel['to']})")

    return "\n".join(lines)


# Test it
if __name__ == "__main__":
    test_questions = [
        "Which suppliers have on time delivery below 90%?",
        "What components are used in Galaxy Ultra X?",
        "How much stock of iPhone 16 Pro is in Dubai warehouse?",
        "What is the cheapest shipping route to BestBuy US?",
        "Which components have only one supplier?",
        "Show me the full supply chain from supplier to retailer for Pixel 9",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        print(f"Category: {classify_question(q)}")