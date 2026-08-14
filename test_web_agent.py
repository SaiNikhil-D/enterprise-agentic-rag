from .web_agent import web_agent_node


question = input(
    "\nEnter your web question: "
)


state = {
    "question": question
}


result = web_agent_node(
    state
)


print("\n" + "=" * 70)

print("WEB AGENT RESULT")

print("=" * 70)


print("\nQuestion:")

print(question)


print("\nAnswer:")

print(
    result["answer"]
)


print("\nSources:")

for source in result.get(
    "sources",
    []
):

    print(
        "-",
        source
    )