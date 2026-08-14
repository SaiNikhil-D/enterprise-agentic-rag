import os

from dotenv import load_dotenv
from groq import Groq

from qdrant_client import QdrantClient

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

from rank_bm25 import BM25Okapi


# ============================================================
# CONFIGURATION
# ============================================================

QDRANT_PATH = "data/qdrant"

COLLECTION_NAME = "technova_documents"

TOP_K_CANDIDATES = 10

TOP_K_FINAL = 3


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


# ============================================================
# INITIALIZE MODELS
# ============================================================

print("Loading RAG models...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

llm = Groq(
    api_key=api_key
)

qdrant = QdrantClient(
    path=QDRANT_PATH
)

print("RAG models loaded.")


# ============================================================
# LOAD DOCUMENTS
# ============================================================

points, _ = qdrant.scroll(
    collection_name=COLLECTION_NAME,
    limit=100
)


documents = []

for point in points:

    documents.append({

        "id": point.id,

        "text": point.payload["text"],

        "chunk_id":
            point.payload["chunk_id"],

        "source":
            point.payload["source"],

        "page_number":
            point.payload["page_number"],

        "department":
            point.payload["department"]

    })


print(
    f"RAG Agent loaded {len(documents)} chunks."
)


# ============================================================
# BM25 INDEX
# ============================================================

tokenized_documents = [

    document["text"].lower().split()

    for document in documents

]

bm25 = BM25Okapi(
    tokenized_documents
)


# ============================================================
# RAG AGENT
# ============================================================

def rag_agent_node(state):

    # --------------------------------------------------------
    # Get information from shared state
    # --------------------------------------------------------

    question = state["question"]

    critique = state.get(
        "critique",
        ""
    )

    retry_count = state.get(
        "retry_count",
        0
    )


    print(
        "\n[RAG AGENT] Processing question..."
    )


    print(
        f"[RAG AGENT] Attempt: {retry_count + 1}"
    )


    if critique:

        print(
            "[RAG AGENT] Previous critic feedback:"
        )

        print(critique)


    # ========================================================
    # STEP 1 — Query Embedding
    # ========================================================

    query_embedding = embedding_model.encode(
        question
    )


    # ========================================================
    # STEP 2 — Dense Retrieval
    # ========================================================

    dense_results = qdrant.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding.tolist(),

        limit=len(documents)

    ).points


    dense_scores = {}


    for result in dense_results:

        dense_scores[
            result.payload["chunk_id"]
        ] = result.score


    # ========================================================
    # STEP 3 — BM25 Keyword Retrieval
    # ========================================================

    tokenized_query = question.lower().split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )


    # ========================================================
    # STEP 4 — Score Normalization
    # ========================================================

    def normalize(values):

        minimum = min(values)

        maximum = max(values)


        if maximum == minimum:

            return [
                1.0
                for _ in values
            ]


        return [

            (value - minimum)
            / (maximum - minimum)

            for value in values

        ]


    dense_list = []

    bm25_list = []


    for index, document in enumerate(
        documents
    ):

        dense_list.append(

            dense_scores.get(
                document["chunk_id"],
                0
            )

        )

        bm25_list.append(
            bm25_scores[index]
        )


    normalized_dense = normalize(
        dense_list
    )

    normalized_bm25 = normalize(
        bm25_list
    )


    # ========================================================
    # STEP 5 — Hybrid Retrieval
    # ========================================================

    candidates = []


    for index, document in enumerate(
        documents
    ):

        hybrid_score = (

            0.7
            * normalized_dense[index]

            +

            0.3
            * normalized_bm25[index]

        )


        candidates.append({

            "document": document,

            "hybrid_score":
                hybrid_score

        })


    candidates.sort(

        key=lambda x:
            x["hybrid_score"],

        reverse=True

    )


    candidates = candidates[
        :TOP_K_CANDIDATES
    ]


    # ========================================================
    # STEP 6 — Cross Encoder Reranking
    # ========================================================

    pairs = [

        [
            question,
            candidate["document"]["text"]
        ]

        for candidate in candidates

    ]


    reranker_scores = reranker.predict(
        pairs
    )


    for candidate, score in zip(
        candidates,
        reranker_scores
    ):

        candidate["reranker_score"] = float(
            score
        )


    candidates.sort(

        key=lambda x:
            x["reranker_score"],

        reverse=True

    )


    final_results = candidates[
        :TOP_K_FINAL
    ]


    # ========================================================
    # STEP 7 — Build Retrieved Context
    # ========================================================

    context_parts = []


    for result in final_results:

        document = result[
            "document"
        ]


        context_parts.append(

            f"""
Source: {document["source"]}
Page: {document["page_number"]}
Department: {document["department"]}

{document["text"]}
"""

        )


    context = "\n".join(
        context_parts
    )


    # ========================================================
    # STEP 8 — Generate Grounded Answer
    # ========================================================

    prompt = f"""
You are an Enterprise Knowledge Assistant.

This is retrieval attempt number:
{retry_count + 1}

The user asked:

{question}


Previous critic feedback:

{critique if critique else "No previous critic feedback."}


Use ONLY the provided company knowledge base
to answer the question.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Use the retrieved context as the source of truth.
4. If the context does not contain enough information,
   clearly say that there is insufficient information.
5. Give a concise and accurate answer.
6. Mention the relevant source and page.
7. If previous critic feedback exists, use it to
   improve the current answer.


Retrieved company knowledge:

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
        .strip()
    )


    # ========================================================
    # STEP 9 — Sources
    # ========================================================

    sources = []


    for result in final_results:

        document = result[
            "document"
        ]


        source = (

            f"{document['source']} "
            f"(Page {document['page_number']})"

        )


        sources.append(
            source
        )


    # ========================================================
    # STEP 10 — Return Updated State
    # ========================================================

    return {

        "retrieved_context":
            context,

        "answer":
            answer,

        "sources":
            sources,

        "next_agent":
            "RAG"

    }


# ============================================================
# CLOSE RESOURCES
# ============================================================

def close_rag_resources():

    qdrant.close()