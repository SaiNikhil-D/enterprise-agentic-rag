from typing import TypedDict, List


class AgentState(TypedDict, total=False):

    question: str

    intent: str

    rewritten_query: str

    keywords: List[str]

    next_agent: str

    retrieved_context: str

    answer: str

    sources: List[str]

    critique: str

    verification: str

    confidence: float

    retry_count: int