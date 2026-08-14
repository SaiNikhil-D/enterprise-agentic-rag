from .critic_agent import critic_agent_node


state = {

    "question":
        "How many annual leave days do employees receive?",

    "answer":
        "Full-time employees receive 20 days of paid annual leave.",

    "retrieved_context":
        """
        Full-time employees are entitled to
        20 days of paid annual leave per calendar year.
        """,

    "sources":
        [
            "company_policy.pdf Page 1"
        ]

}


result = critic_agent_node(
    state
)


print("\n" + "=" * 70)

print("CRITIC RESULT")

print("=" * 70)

print(
    "\nVerification:",
    result["verification"]
)

print(
    "Confidence:",
    result["confidence"]
)

print(
    "Reason:",
    result["critique"]
)