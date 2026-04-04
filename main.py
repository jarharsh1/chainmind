"""
ChainMind — Supply Chain Intelligence Engine
Ask natural language questions about your supply chain.
"""

from pipeline.graphrag import ask, print_result


def main():
    print("\n" + "="*60)
    print("  ChainMind — Supply Chain Intelligence Engine")
    print("  Type 'quit' to exit")
    print("="*60)

    while True:
        question = input("\nAsk: ").strip()

        if question.lower() in ["quit", "exit", "q"]:
            print("Bye!")
            break

        if not question:
            continue

        try:
            result = ask(question)
            print_result(result)
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()