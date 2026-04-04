# graph/graph_builder.py
"""
Oxlo-Sentinel LangGraph Topology.
Assembles the hivemind state machine with cyclic auditing and dual-path routing.
"""
from langgraph.graph import StateGraph, END
from graph.state import SentinelState
from graph.nodes.router_node import router_node
from graph.nodes.generator_node import generator_node
from graph.nodes.mcp_node import mcp_node
from graph.nodes.auditor_node import auditor_node
from graph.nodes.synthesizer_node import synthesizer_node


# --- Configuration ---
MAX_AUDIT_CYCLES = 5


# --- Routing Functions ---
def _route_after_router(state: SentinelState) -> str:
    """
    Conditional edge: skip swarm for simple chat/flash queries.
    """
    # Using 'route' literal from SentinelState
    return "synthesizer" if state.get("route") == "chat" else "generator"


def _route_after_audit(state: SentinelState) -> str:
    """
    Conditional edge: decide next node after Auditor runs.
    Returns 'generator' to retry/debate, 'synthesizer' to finalize answer.
    """
    consensus = state.get("consensus_reached", False)
    cycles = state.get("audit_cycles", 0)

    # 1. Consensus reached -> Exit to synthesizer
    if consensus:
        return "synthesizer"
        
    # 2. Hard Cap reached -> Exit to synthesizer (marked as Unverified)
    if cycles >= MAX_AUDIT_CYCLES:
        return "synthesizer"
        
    # 3. Disagreement -> Loop back to generator for another attempt
    return "generator"


# --- Graph Construction ---
def build_sentinel_graph() -> StateGraph:
    """
    Compile the Oxlo-Sentinel LangGraph topology.
    Returns a compiled graph ready for .astream_events() invocation.
    """
    # 1. Initialize Graph with State Definition
    builder = StateGraph(SentinelState)

    # 2. Register Nodes
    builder.add_node("router", router_node)
    builder.add_node("generator", generator_node)
    builder.add_node("mcp_tool", mcp_node)
    builder.add_node("auditor", auditor_node)
    builder.add_node("synthesizer", synthesizer_node)

    # 3. Define Entry Point
    builder.set_entry_point("router")

    # 4. Define Edges (Nodes & Routing)
    # A. Initial Routing (Fast Response vs Swarm)
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "generator": "generator", 
            "synthesizer": "synthesizer"
        },
    )

    # B. The Cognitive Core Flow
    builder.add_edge("generator", "mcp_tool")
    builder.add_edge("mcp_tool", "auditor")

    # C. The Audit Loop (Cyclic Routing)
    builder.add_conditional_edges(
        "auditor",
        _route_after_audit,
        {
            "generator": "generator", 
            "synthesizer": "synthesizer"
        },
    )

    # D. Exit Node
    builder.add_edge("synthesizer", END)

    # 5. Compile the Graph
    return builder.compile()


# --- Singleton Object ---
# Import this into your bot handlers to invoke the Hivemind
sentinel_graph = build_sentinel_graph()
