import os

from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv()


api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found."
    )


client = Groq(
    api_key=api_key
)


def supervisor_node(state):

    question = state["question"]


    prompt = f"""
You are the supervisor of an enterprise AI system.

Decide which agent should handle the user's request.

Available agents:

RAG:
Use for questions about company documents,
policies, employee information, internal knowledge,
and uploaded documents.

SQL:
Use for structured database questions,
numbers, tables, transactions, reports,
and business analytics.

WEB:
Use for current external information,
news, recent events, public information,
or information not contained in company documents.

Return ONLY one word:

RAG

SQL

WEB


User question:

{question}
"""


    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    decision = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .upper()
    )


    if decision not in {
        "RAG",
        "SQL",
        "WEB"
    }:

        decision = "RAG"


    return {
        "next_agent": decision
    }