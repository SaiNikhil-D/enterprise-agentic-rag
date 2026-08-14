from langgraph.graph import StateGraph, END

from .state import AgentState

from .supervisor import supervisor_node

from .rag_agent import (
    rag_agent_node,
    close_rag_resources
)

from .sql_agent import sql_agent_node

from .web_agent import web_agent_node

from .critic_agent import critic_agent_node


# ============================================================
# CREATE WORKFLOW
# ============================================================

workflow = StateGraph(
    AgentState
)


# ============================================================
# ADD AGENTS / NODES
# ============================================================

workflow.add_node(
    "supervisor",
    supervisor_node
)


workflow.add_node(
    "rag_agent",
    rag_agent_node
)


workflow.add_node(
    "sql_agent",
    sql_agent_node
)


workflow.add_node(
    "web_agent",
    web_agent_node
)


workflow.add_node(
    "critic",
    critic_agent_node
)


# ============================================================
# RETRY NODE
# ============================================================

def retry_node(state):

    current_retry_count = state.get(
        "retry_count",
        0
    )

    new_retry_count = (
        current_retry_count + 1
    )

    print(
        "\n[RETRY SYSTEM]"
    )

    print(
        "Previous attempt:",
        current_retry_count + 1
    )

    print(
        "Starting retry:",
        new_retry_count + 1
    )

    return {

        "retry_count":
            new_retry_count

    }


workflow.add_node(
    "retry",
    retry_node
)


# ============================================================
# START
# ============================================================

workflow.set_entry_point(
    "supervisor"
)


# ============================================================
# SUPERVISOR ROUTING
# ============================================================

def route_from_supervisor(state):

    next_agent = state.get(
        "next_agent",
        "RAG"
    )


    if next_agent == "RAG":

        return "rag_agent"


    if next_agent == "SQL":

        return "sql_agent"


    if next_agent == "WEB":

        return "web_agent"


    # Default

    return "rag_agent"


workflow.add_conditional_edges(

    "supervisor",

    route_from_supervisor,

    {

        "rag_agent":
            "rag_agent",

        "sql_agent":
            "sql_agent",

        "web_agent":
            "web_agent"

    }

)


# ============================================================
# AGENTS → CRITIC
# ============================================================

workflow.add_edge(
    "rag_agent",
    "critic"
)


workflow.add_edge(
    "sql_agent",
    "critic"
)


workflow.add_edge(
    "web_agent",
    "critic"
)


# ============================================================
# CRITIC ROUTING
# ============================================================

def route_after_critic(state):

    verification = state.get(
        "verification",
        "FAIL"
    ).upper()


    retry_count = state.get(
        "retry_count",
        0
    )


    # --------------------------------------------------------
    # PASS
    # --------------------------------------------------------

    if verification == "PASS":

        print(
            "\n[CRITIC] Answer verified."
        )

        return "finish"


    # --------------------------------------------------------
    # Maximum retries reached
    # --------------------------------------------------------

    if retry_count >= 2:

        print(
            "\n[CRITIC] Maximum retries reached."
        )

        return "finish"


    # --------------------------------------------------------
    # Retry
    # --------------------------------------------------------

    print(
        "\n[CRITIC] Answer requires improvement."
    )

    return "retry"


workflow.add_conditional_edges(

    "critic",

    route_after_critic,

    {

        "finish":
            END,

        "retry":
            "retry"

    }

)


# ============================================================
# RETRY → SUPERVISOR
# ============================================================

workflow.add_edge(
    "retry",
    "supervisor"
)


# ============================================================
# COMPILE GRAPH
# ============================================================

graph = workflow.compile()