from .supervisor import supervisor_node


questions = [
    "How many annual leave days do employees receive?",
    "Show me the total sales for 2025.",
    "What is the latest AI news?"
]


for question in questions:

    state = {
        "question": question
    }

    result = supervisor_node(state)

    print("\nQuestion:")
    print(question)

    print("Selected Agent:")
    print(result["next_agent"])

    print("-" * 60)