from .rag_agent import (
    rag_agent_node,
    close_rag_resources
)


question = (
    "How many annual leave days do employees receive?"
)


state = {
    "question": question
}


result = rag_agent_node(state)


print("\n" + "=" * 70)

print("RAG AGENT RESULT")

print("=" * 70)

print("\nAnswer:")

print(result["answer"])


print("\nSources:")

for source in result["sources"]:

    print("-", source)


close_rag_resources()