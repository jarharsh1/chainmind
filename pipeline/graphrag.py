"""
GraphRAG pipeline — ties the stages together.

schema_pruner (classify + prune) -> cypher_chain (generate + guard + execute +
answer). Import `ask()` from the API or the CLI.
"""

from pipeline.cypher_chain import query
from pipeline.schema_pruner import classify_question, get_pruned_schema

_GREETINGS = {"hello", "hi", "hey", "bye", "thanks", "thank you"}


def ask(question: str) -> dict:
    """Ask a natural-language question about the supply chain."""
    normalized = question.lower().strip()

    if normalized in _GREETINGS:
        return {
            "question": question,
            "category": "greeting",
            "cypher": "N/A",
            "results": [],
            "answer": (
                "Hey! I'm ChainMind — ask me anything about your supply chain. "
                "For example: 'Which components have only one supplier?'"
            ),
        }

    category = classify_question(question)
    pruned_schema = get_pruned_schema(question)

    result = query(question, pruned_schema)
    result["category"] = category
    return result


def print_result(result: dict) -> None:
    """Pretty-print a result for the CLI."""
    print(f"\n{'=' * 60}")
    print(f"Question:  {result['question']}")
    print(f"Category:  {result['category']}")
    print(f"Cypher:    {result['cypher']}")
    print(f"{'=' * 60}")
    print(f"\n{result['answer']}")
    print(f"\n{'=' * 60}")
