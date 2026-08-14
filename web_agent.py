import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

tavily_key = os.getenv("TAVILY_API_KEY")


if not groq_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


if not tavily_key:
    raise ValueError(
        "TAVILY_API_KEY was not found in .env"
    )


# ============================================================
# Initialize clients
# ============================================================

llm = Groq(
    api_key=groq_key
)

search_client = TavilyClient(
    api_key=tavily_key
)


# ============================================================
# Web Agent
# ============================================================

def web_agent_node(state):

    question = state["question"]

    print(
        "\n[WEB AGENT] Searching the web..."
    )


    # --------------------------------------------------------
    # Search web
    # --------------------------------------------------------

    search_response = search_client.search(
        query=question,
        max_results=5,
        search_depth="advanced"
    )


    results = search_response.get(
        "results",
        []
    )


    if not results:

        return {
            "answer":
                "No reliable web results were found.",

            "sources": [],

            "next_agent": "WEB"
        }


    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    sources = []


    for result in results:

        title = result.get(
            "title",
            ""
        )

        content = result.get(
            "content",
            ""
        )

        url = result.get(
            "url",
            ""
        )


        context_parts.append(
            f"""
Title:
{title}

URL:
{url}

Content:
{content}
"""
        )


        if url:

            sources.append(url)


    context = "\n".join(
        context_parts
    )


    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    prompt = f"""
You are an enterprise web research assistant.

Answer the user's question using ONLY
the web search results provided below.

Rules:

1. Do not invent facts.
2. Prefer information supported by multiple sources.
3. If sources disagree, mention the disagreement.
4. Give a concise answer.
5. Mention the important sources.

User question:

{question}

Web search results:

{context}
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


    answer = (
        response
        .choices[0]
        .message
        .content
    )


    return {

        "answer": answer,

        "sources": sources,

        "next_agent": "WEB"
    }