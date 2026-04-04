"""
GraphRAG Pipeline — Ties everything together

schema_pruner → cypher_chain → answer
"""

from pipeline.schema_pruner import get_pruned_schema, classify_question
from pipeline.cypher_chain import query


def ask(question: str) -> dict:
    """Ask a natural language question about the supply chain"""
    
    # Handle non-questions
    greetings = ["hello", "hi", "hey", "bye", "thanks", "thank you"]
    if question.lower().strip() in greetings:
        return {
            "question": question,
            "category": "greeting",
            "cypher": "N/A",
            "results": [],
            "answer": "Hey! I'm ChainMind — ask me anything about your supply chain. For example: 'Which components have only one supplier?'"
        }
    
    # Step 1: Prune schema
    category = classify_question(question)
    pruned_schema = get_pruned_schema(question)

    # Step 2: Run full pipeline
    result = query(question, pruned_schema)
    result["category"] = category

    return result


def print_result(result: dict):
    """Pretty print the result"""
    print(f"\n{'='*60}")
    print(f"Question:  {result['question']}")
    print(f"Category:  {result['category']}")
    print(f"Cypher:    {result['cypher']}")
    print(f"{'='*60}")
    print(f"\n{result['answer']}")
    print(f"\n{'='*60}")