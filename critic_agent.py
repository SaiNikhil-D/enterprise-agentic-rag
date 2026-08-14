import os
import json

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# Environment
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


# ============================================================
# LLM
# ============================================================

llm = Groq(
    api_key=api_key
)


# ============================================================
# Critic Agent
# ============================================================

def critic_agent_node(state):

    question = state.get(
        "question",
        ""
    )

    answer = state.get(
        "answer",
        ""
    )

    context = state.get(
        "retrieved_context",
        ""
    )

    sources = state.get(
        "sources",
        []
    )


    prompt = f"""
You are a strict verification agent
for an enterprise AI system.

Your job is to determine whether the
generated answer is sufficiently supported
by the available evidence.

User question:

{question}

Generated answer:

{answer}

Available evidence:

{context}

Sources:

{sources}

Evaluate:

1. Is the answer relevant to the question?
2. Is the answer supported by the evidence?
3. Does the answer contain invented information?
4. Is the answer sufficiently clear?

Return ONLY valid JSON:

{{
    "verdict": "PASS" or "FAIL",
    "reason": "short explanation",
    "confidence": 0.0
}}

Do not add markdown.
"""


    response = llm.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    content = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    # Remove markdown fences if necessary

    if content.startswith("```"):

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()


    try:

        result = json.loads(
            content
        )

    except json.JSONDecodeError:

        result = {

            "verdict": "FAIL",

            "reason":
                "Critic returned invalid JSON.",

            "confidence": 0.0

        }


    verdict = result.get(
        "verdict",
        "FAIL"
    ).upper()


    if verdict not in {
        "PASS",
        "FAIL"
    }:

        verdict = "FAIL"


    print(
        "\n[CRITIC AGENT]"
    )

    print(
        "Verdict:",
        verdict
    )

    print(
        "Reason:",
        result.get(
            "reason",
            ""
        )
    )

    print(
        "Confidence:",
        result.get(
            "confidence",
            0
        )
    )


    return {

        "critique":
            result.get(
                "reason",
                ""
            ),

        "verification":
            verdict,

        "confidence":
            result.get(
                "confidence",
                0
            )

    }