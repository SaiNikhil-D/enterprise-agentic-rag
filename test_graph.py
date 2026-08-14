from .graph import graph

from .rag_agent import close_rag_resources


# ============================================================
# USER QUESTION
# ============================================================

question = input(
    "\nAsk your enterprise AI assistant: "
)


# ============================================================
# INITIAL STATE
# ============================================================

initial_state = {

    "question":
        question,

    "retry_count":
        0

}


print(
    "\nStarting Agentic RAG..."
)


# ============================================================
# RUN GRAPH
# ============================================================

result = graph.invoke(
    initial_state
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "FINAL AGENTIC RAG RESULT"
)

print(
    "=" * 70
)


print(
    "\nQuestion:"
)

print(
    question
)


print(
    "\nSelected Agent:"
)

print(
    result.get(
        "next_agent",
        "UNKNOWN"
    )
)


print(
    "\nAnswer:"
)

print(
    result.get(
        "answer",
        "No answer generated."
    )
)


print(
    "\nVerification:"
)

print(
    result.get(
        "verification",
        "UNKNOWN"
    )
)


print(
    "\nConfidence:"
)

print(
    result.get(
        "confidence",
        0
    )
)


print(
    "\nRetry Count:"
)

print(
    result.get(
        "retry_count",
        0
    )
)


print(
    "\nCritic Feedback:"
)

print(
    result.get(
        "critique",
        "No critique."
    )
)


if result.get("sources"):

    print(
        "\nSources:"
    )

    for source in result["sources"]:

        print(
            "-",
            source
        )


# ============================================================
# CLOSE RESOURCES
# ============================================================

close_rag_resources()