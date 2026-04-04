# graph/nodes/synthesizer_node.py
from langchain_core.messages import AIMessage
from graph.state import SentinelState


# --- Configuration ---
SYNTH_MODEL = "deepseek-v3.2"  # Flagship for composition


# --- Logic ---
async def synthesizer_node(state: SentinelState) -> dict:
    """
    Node 5 — The Synthesizer.
    Composes the final markdown answer with attribution and verification status.
    """
    route = state.get("route", "chat")
    user_query = state.get("user_query", "")
    
    # --- PATH A: FLASH RESPONSE (< 1s) ---
    # Bypass the swarm and just return the AI message
    if route == "chat":
        # In this simple path, we can just return the AIMessage directly
        # The AI (Llama-3.2-3B) would have responded in the router or a simple chat node
        return {
            "status_messages": state.get("status_messages", []) + ["⚡ Flash Response complete"],
        }

    # --- PATH B: COGNITIVE SWARM (~8s) ---
    # High-level composition of all swarm data
    hypotheses = state.get("agent_hypotheses", [])
    sandbox_logs = state.get("sandbox_logs", "")
    audit_reasoning = state.get("audit_reasoning", "No detailed audit available.")
    consensus = state.get("consensus_reached", False)
    cycles = state.get("audit_cycles", 0)

    # 1. Determine Verification Status
    if consensus:
        header = "✅ **VERIFIED ANSWER** (Hivemind Consensus)"
    elif cycles >= 5:
        header = "⚠️ **UNVERIFIED ANSWER** (Max Audit Cycles Reached)"
    else:
        header = "💡 **PROPOSED ANSWER** (Limited Audit)"

    # 2. Extract Best Answer (if available)
    # Note: In a production app, we would use another Oxlo call to clean up the final answer
    # For now, we take the lead model (DeepSeek-V3.2) as the base
    lead_hypothesis = hypotheses[0] if hypotheses else None
    base_content = lead_hypothesis["content"] if lead_hypothesis else "No answer generated."

    # 3. Format Attribution
    attribution = "\n\n---\n📊 **Verification Report**\n"
    attribution += f"- **Consensus**: {'YES' if consensus else 'NO'}\n"
    attribution += f"- **Models**: {', '.join(h['model_id'] for h in hypotheses)}\n"
    attribution += f"- **Cycles**: {cycles}/5\n"
    attribution += f"- **Sandbox**: {'✅ Success' if state.get('sandbox_success') else '❌ Failed/Skipped'}\n"
    
    if audit_reasoning:
        attribution += f"\n**Reasoning**: {audit_reasoning}\n"

    # 4. Final Final Message
    final_text = f"{header}\n\n{base_content}\n{attribution}"

    return {
        "status_messages": state.get("status_messages", []) + [header],
        "messages": [AIMessage(content=final_text)]  # Append to message history
    }
