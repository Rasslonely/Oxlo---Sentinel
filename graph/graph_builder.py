# graph/graph_builder.py
"""
Oxlo-Sentinel LangGraph Topology.
Assembles the hivemind state machine with cyclic auditing and dual-path routing.
"""
from config.settings import settings
from langgraph.graph import StateGraph, END
from graph.state import SentinelState
from graph.nodes.router_node import router_node
from graph.nodes.pre_cognition_node import pre_cognition_node
from graph.nodes.generator_node import generator_node
from graph.nodes.mcp_node import mcp_node
from graph.nodes.auditor_node import auditor_node
from graph.nodes.synthesizer_node import synthesizer_node
from graph.nodes.memory_committer_node import memory_committer_node


# --- Configuration ---
MAX_AUDIT_CYCLES = 2 # Updated to cap endless debate loops


# --- Routing Functions ---
def _route_after_router(state: SentinelState) -> str:
    """
    Conditional edge: skip swarm for simple chat/flash queries.
    """
    if state.get("route") == "chat":
        return "synthesizer"
    return "pre_cognition"


def _route_after_mcp(state: SentinelState) -> str:
    """
    Budget Guard: If in Economy Mode and Sandbox is 100% successful,
    skip the expensive Auditor node to save API calls.
    """
    sandbox_success = state.get("sandbox_success", False)
    if settings.OXLO_ECONOMY_MODE and sandbox_success:
        return "synthesizer"
    return "auditor"


def _route_after_audit(state: SentinelState) -> str:
    """
    Conditional edge: decide next node after Auditor runs.
    Returns 'generator' to retry/debate, 'synthesizer' to finalize answer.
    """
    consensus = state.get("consensus_reached", False)
    cycles = state.get("audit_cycles", 0)

    if consensus or cycles >= MAX_AUDIT_CYCLES:
        return "synthesizer"
    return "generator"


# --- Graph Construction ---
def build_sentinel_graph() -> StateGraph:
    """
    Compile the Oxlo-Sentinel LangGraph topology v4.5 (True Parallel Swarm).
    """
    builder = StateGraph(SentinelState)

    # 1. Register Nodes
    builder.add_node("router", router_node)
    builder.add_node("pre_cognition", pre_cognition_node)
    builder.add_node("generator", generator_node)
    builder.add_node("mcp_tool", mcp_node)
    builder.add_node("auditor", auditor_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("memory_committer", memory_committer_node)

    # 2. Define Entry Point
    builder.set_entry_point("router")

    # 3. Define Edges (Nodes & Routing)
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "pre_cognition": "pre_cognition", 
            "synthesizer": "synthesizer"
        },
    )
    
    # 4. Cerebro Memory Integration
    builder.add_edge("pre_cognition", "generator")
    builder.add_edge("generator", "mcp_tool")
    
    # 4.5 Budget Guard: Conditional Audit
    builder.add_conditional_edges(
        "mcp_tool",
        _route_after_mcp,
        {
            "auditor": "auditor",
            "synthesizer": "synthesizer"
        }
    )

    # 5. The Audit Loop
    builder.add_conditional_edges(
        "auditor",
        _route_after_audit,
        {
            "generator": "generator", 
            "synthesizer": "synthesizer"
        },
    )

    # 6. Final Commitment Layer (LEARNING)
    builder.add_edge("synthesizer", "memory_committer")
    builder.add_edge("memory_committer", END)

    return builder.compile()


# --- Singleton Object ---
# Import this into your bot handlers to invoke the Hivemind
sentinel_graph = build_sentinel_graph()
