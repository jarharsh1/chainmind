"""
Cypher Chain — LLM-powered Cypher generation + execution

Flow:
1. Takes pruned schema + few-shot examples + user question
2. LLM generates Cypher query
3. Cypher runs on Neo4j
4. LLM converts results to natural language answer
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI

load_dotenv()

# Neo4j connection
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# NVIDIA NIM client (OpenAI-compatible)
client = OpenAI(
    base_url=os.getenv("NVIDIA_BASE_URL"),
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "meta/llama-3.1-70b-instruct"

# Few-shot examples — helps LLM write accurate Cypher
FEW_SHOT_EXAMPLES = """
Example 1:
Question: Which suppliers are from China?
Cypher: MATCH (s:Supplier) WHERE s.country = "China" RETURN s.name, s.on_time_delivery_pct

Example 2:
Question: What components are used in iPhone 16 Pro?
Cypher: MATCH (c:Component)-[:USED_IN]->(p:Product {name: "iPhone 16 Pro"}) RETURN c.name, c.category, c.unit_cost

Example 3:
Question: Which components have only one supplier?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(c:Component) WITH c, COUNT(s) AS supplier_count WHERE supplier_count = 1 MATCH (s2:Supplier)-[:SUPPLIES]->(c) RETURN c.name, c.category, s2.name AS only_supplier

Example 4:
Question: How much stock of Galaxy Ultra X is in each warehouse?
Cypher: MATCH (p:Product {name: "Galaxy Ultra X"})-[r:STORED_AT]->(w:Warehouse) RETURN w.name, w.city, r.stock_quantity

Example 5:
Question: What is the cheapest shipping route to BestBuy US?
Cypher: MATCH (w:Warehouse)-[r:SHIPS_TO]->(ret:Retailer {name: "BestBuy US"}) RETURN w.name, r.mode, r.cost_per_unit, r.transit_days ORDER BY r.cost_per_unit ASC

Example 6:
Question: If Taiwan Semiconductor Co goes down, which products are affected?
Cypher: MATCH (s:Supplier {name: "Taiwan Semiconductor Co"})-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product) RETURN DISTINCT p.name, p.category, c.name AS affected_component

Example 7:
Question: Who supplies components for iPhone?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product) WHERE toLower(p.name) CONTAINS "iphone" RETURN s.name, c.name, s.on_time_delivery_pct ORDER BY s.on_time_delivery_pct DESC
"""


def generate_cypher(question: str, pruned_schema: str) -> str:
    """LLM Call #1 — Generate Cypher from question"""

    prompt = f"""You are a Neo4j Cypher expert. Generate a Cypher query to answer the user's question.

SCHEMA:
{pruned_schema}

{FEW_SHOT_EXAMPLES}

Rules:
- Return ONLY the Cypher query, nothing else
- No explanations, no markdown, no backticks
- Use exact property names from the schema
- Always use RETURN to show results
- When matching names, use toLower() and CONTAINS instead of exact match
- When comparing string values, always use toLower() for both sides

Question: {question}
Cypher:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500
    )

    cypher = response.choices[0].message.content.strip()

    # Clean up — remove backticks or markdown if LLM adds them
    cypher = cypher.replace("```cypher", "").replace("```", "").strip()

    return cypher


def execute_cypher(cypher: str) -> list:
    """Run Cypher on Neo4j and return results"""
    try:
        with driver.session() as session:
            result = session.run(cypher)
            records = [dict(record) for record in result]
            return records
    except Exception as e:
        return [{"error": str(e)}]


def generate_answer(question: str, cypher: str, results: list) -> str:
    """LLM Call #2 — Convert graph results to natural language"""

    prompt = f"""You are a supply chain analyst. Answer the user's question based on the data provided.

Question: {question}

Cypher query used: {cypher}

Results from database:
{results}

Rules:
- Answer in clear, concise language
- If results are empty, say the data was not found
- Include specific numbers and names from the results
- Keep it brief but complete

Answer:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()


def query(question: str, pruned_schema: str) -> dict:
    """Full pipeline — question in, answer out"""

    # Step 1: Generate Cypher
    cypher = generate_cypher(question, pruned_schema)

    # Step 2: Execute on Neo4j
    results = execute_cypher(cypher)

    # Step 3: Generate answer
    if results and "error" in results[0]:
        answer = f"Cypher query failed: {results[0]['error']}"
    else:
        answer = generate_answer(question, cypher, results)

    return {
        "question": question,
        "cypher": cypher,
        "results": results,
        "answer": answer
    }


if __name__ == "__main__":
    from schema_pruner import get_pruned_schema

    test_q = "Which suppliers have on time delivery below 90%?"
    schema = get_pruned_schema(test_q)

    print(f"Question: {test_q}")
    print(f"\nPruned Schema:\n{schema}")

    result = query(test_q, schema)
    print(f"\nGenerated Cypher:\n{result['cypher']}")
    print(f"\nRaw Results:\n{result['results']}")
    print(f"\nAnswer:\n{result['answer']}")