"""
Cypher Chain — LLM-powered Cypher generation + guarded execution.

Flow:
1. Take pruned schema + few-shot examples + user question -> LLM writes Cypher.
2. The Cypher is validated read-only BEFORE it touches the database. A write
   query is never executed; we make one repair attempt, then refuse safely.
3. The (safe) Cypher runs on Neo4j in a READ session with a per-query timeout.
4. The LLM turns the rows into a natural-language answer.
"""

from config import get_settings
from db import read_session
from pipeline.guards import UnsafeCypherError, assert_read_only
from pipeline.llm import get_llm_client

# Few-shot examples — helps the model write accurate Cypher for this schema.
FEW_SHOT_EXAMPLES = """
Example 1:
Question: Which suppliers are from China?
Cypher: MATCH (s:Supplier) WHERE toLower(s.country) = "china" RETURN s.name, s.on_time_delivery_pct

Example 2:
Question: What components are used in iPhone 16 Pro?
Cypher: MATCH (c:Component)-[:USED_IN]->(p:Product) WHERE toLower(p.name) CONTAINS "iphone 16 pro" RETURN c.name, c.category, c.unit_cost

Example 3:
Question: Which components have only one supplier?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(c:Component) WITH c, COUNT(s) AS supplier_count WHERE supplier_count = 1 MATCH (s2:Supplier)-[:SUPPLIES]->(c) RETURN c.name, c.category, s2.name AS only_supplier

Example 4:
Question: How much stock of Galaxy Ultra X is in each warehouse?
Cypher: MATCH (p:Product)-[r:STORED_AT]->(w:Warehouse) WHERE toLower(p.name) CONTAINS "galaxy ultra x" RETURN w.name, w.city, r.stock_quantity

Example 5:
Question: What is the cheapest shipping route to BestBuy US?
Cypher: MATCH (w:Warehouse)-[r:SHIPS_TO]->(ret:Retailer) WHERE toLower(ret.name) CONTAINS "bestbuy us" RETURN w.name, r.mode, r.cost_per_unit, r.transit_days ORDER BY r.cost_per_unit ASC

Example 6:
Question: If Taiwan Semiconductor Co goes down, which products are affected?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product) WHERE toLower(s.name) CONTAINS "taiwan semiconductor" RETURN DISTINCT p.name, p.category, c.name AS affected_component

Example 7:
Question: Who supplies components for iPhone?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product) WHERE toLower(p.name) CONTAINS "iphone" RETURN s.name, c.name, s.on_time_delivery_pct ORDER BY s.on_time_delivery_pct DESC
"""

_CYPHER_RULES = """Rules:
- Return ONLY the Cypher query, nothing else.
- No explanations, no markdown, no backticks.
- The query MUST be read-only: only MATCH / OPTIONAL MATCH / WHERE / WITH /
  RETURN / ORDER BY / LIMIT / aggregations. NEVER use CREATE, MERGE, SET,
  DELETE, REMOVE, DROP, or any write/admin clause.
- Use exact property names from the schema.
- Always use RETURN to show results.
- When matching names, prefer toLower() with CONTAINS instead of exact match.
- When comparing string values, use toLower() on both sides."""


def _clean_cypher(raw: str) -> str:
    """Strip markdown fences / stray labels the model sometimes adds."""
    cypher = raw.strip()
    cypher = cypher.replace("```cypher", "").replace("```", "").strip()
    # Drop a leading "Cypher:" label if the model echoes it.
    if cypher.lower().startswith("cypher:"):
        cypher = cypher[len("cypher:"):].strip()
    return cypher


def generate_cypher(question: str, pruned_schema: str, feedback: str | None = None) -> str:
    """LLM call #1 — generate Cypher from the question.

    `feedback` is passed on a repair attempt to tell the model why its previous
    query was rejected.
    """
    repair_note = ""
    if feedback:
        repair_note = (
            f"\nYour previous attempt was rejected because: {feedback}\n"
            "Return a corrected, strictly READ-ONLY query.\n"
        )

    prompt = f"""You are a Neo4j Cypher expert. Generate a Cypher query to answer the user's question.

SCHEMA:
{pruned_schema}

{FEW_SHOT_EXAMPLES}

{_CYPHER_RULES}
{repair_note}
Question: {question}
Cypher:"""

    raw = get_llm_client().complete(prompt, temperature=0.0, max_tokens=500)
    return _clean_cypher(raw)


def execute_cypher(cypher: str) -> tuple[list[dict], str | None]:
    """Run read-only Cypher with a per-query timeout. Returns (rows, error)."""
    s = get_settings()
    try:
        with read_session() as session:
            with session.begin_transaction(timeout=s.query_timeout_seconds) as tx:
                result = tx.run(cypher)
                rows = [dict(record) for record in result]
        return rows, None
    except Exception as e:  # noqa: BLE001 — surface any driver/query error cleanly
        return [], str(e)


def generate_answer(question: str, cypher: str, results: list[dict]) -> str:
    """LLM call #2 — turn graph rows into a natural-language answer."""
    prompt = f"""You are a supply chain analyst. Answer the user's question based on the data provided.

Question: {question}

Cypher query used: {cypher}

Results from database:
{results}

Rules:
- Answer in clear, concise language.
- If results are empty, say the data was not found.
- Include specific numbers and names from the results.
- Keep it brief but complete.

Answer:"""
    return get_llm_client().complete(prompt, temperature=0.3, max_tokens=500)


_REFUSAL = (
    "I can only answer read-only questions about the supply chain — I can't run "
    "queries that modify the database. Try rephrasing as a question about the data."
)


def query(question: str, pruned_schema: str) -> dict:
    """Full pipeline for one question: Cypher -> guard -> execute -> answer."""
    cypher = generate_cypher(question, pruned_schema)

    # Guard: reject writes before execution. Allow one repair attempt.
    try:
        assert_read_only(cypher)
    except UnsafeCypherError as first_error:
        cypher = generate_cypher(question, pruned_schema, feedback=str(first_error))
        try:
            assert_read_only(cypher)
        except UnsafeCypherError:
            return {
                "question": question,
                "cypher": cypher,
                "results": [],
                "answer": _REFUSAL,
            }

    rows, error = execute_cypher(cypher)
    if error is not None:
        answer = f"The query could not be completed: {error}"
    else:
        answer = generate_answer(question, cypher, rows)

    return {
        "question": question,
        "cypher": cypher,
        "results": rows,
        "answer": answer,
    }
