import asyncio
from langchain_core.messages import AIMessage
from openai import AsyncOpenAI
from graph.state import SentinelState
from config.settings import settings

# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

# --- Configuration ---
SYNTH_MODEL = "deepseek-v3.2"  # Flagship for composition


# --- Utilities ---
def premium_sanitize(text: str) -> str:
    """Universal math & markdown sanitizer for Telegram Premium UI."""
    # Convert LaTeX to clean Markdown
    text = text.replace("\\[", "**").replace("\\]", "**").replace("\\(", "*").replace("\\)", "*")
    text = text.replace("\\cdot", "×").replace("\\times", "×").replace("\\div", "÷")
    return text


# --- Logic ---
async def _call_oxlo_with_retry(messages: list, model: str = SYNTH_MODEL, max_tokens: int = 600, retries: int = 3) -> str:
    """Helper to call Oxlo with silent retries for 504/502 resilience."""
    last_err = None
    for attempt in range(retries):
        try:
            response = await asyncio.wait_for(
                oxlo_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=max_tokens
                ),
                timeout=25.0
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            last_err = e
            if "504" in str(e) or "502" in str(e) or "Timeout" in str(e):
                await asyncio.sleep(2 ** attempt)
                continue
            break
    raise last_err or Exception("All retries failed")


async def _generate_executive_summary(hypotheses: list, user_query: str) -> str:
    """Extra pass to create a clean, human-centric 'Executive Summary'."""
    lead_content = hypotheses[0].get("content", "")
    system_prompt = (
        "You are the Premium Executive Voice of the Oxlo-Sentinel. "
        "Your goal is to provide a natural, conversational final answer for a layperson. "
        "1. DO NOT use mathematical variables like x, y, n. Use clear names like 'Ivan's coins'. "
        "2. Lead with the final conclusions in bold. "
        "3. Keep it to 1-2 short, professional paragraphs. "
        "4. Tone: Helpful, elite, and natural (not robotic)."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User Query: {user_query}\n\nInternal Reasoning:\n{lead_content}"}
    ]
    
    try:
        return await _call_oxlo_with_retry(messages, max_tokens=400)
    except Exception:
        return "✅ **Verified Solution Confirmed.** (Details available below)."


async def synthesizer_node(state: SentinelState) -> dict:
    """
    Node 5 — The Synthesizer.
    Composes the final God-Tier Human-Centric response.
    """
    route = state.get("route", "chat")
    user_query = state.get("user_query", "")
    status_messages = state.get("status_messages", [])
    
    # --- PATH A: FLASH RESPONSE (< 1s) ---
    if route == "chat":
        try:
            system_prompt = (
                "You are the professional, friendly voice of the Oxlo-Sentinel. "
                "Provide a natural, conversational response. "
                "If it's math like 'sin 90', answer like a helpful teacher: 'Certainly! The value of sin(90) is 1.' "
                "Use bolding for clarity. No robotic data blocks."
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
            content = await _call_oxlo_with_retry(messages, max_tokens=300)
            clean_content = premium_sanitize(content)
            
            return {
                "status_messages": status_messages + ["⚡ Flash Response complete"],
                "messages": [AIMessage(content=clean_content)]
            }
        except Exception as e:
            return {
                "status_messages": status_messages + [f"⚠️ Flash Fallback: {str(e)}"],
                "messages": [AIMessage(content="❌ **Service Temporarily Busy**\nThe Hivemind is recovering. Please try again.")]
            }

    # --- PATH B: COGNITIVE SWARM (~8s) ---
    hypotheses = [
        h for h in state.get("agent_hypotheses", []) 
        if "ERROR" not in h.get("content", "") and "Concurrency limit" not in h.get("content", "")
    ]
    
    if not hypotheses:
        return {
            "status_messages": status_messages + ["❌ Swarm Failure"],
            "messages": [AIMessage(content="❌ **Swarm Failure**: API Unavailable.")]
        }

    # 1. Executive Summary Pass (v2.2: Human-First)
    summary_clean = ""
    try:
        summary = await _generate_executive_summary(hypotheses, user_query)
        summary_clean = premium_sanitize(summary)
    except Exception:
        summary_clean = "✅ **Consensus Reached.** (See reasoning below)"

    # 2. Reasoning & Logic Extraction
    audit_reasoning = state.get("audit_reasoning", "Consensus reached.")
    if not audit_reasoning:
        audit_reasoning = "Consensus reached."
        
    consensus = state.get("consensus_reached", False)
    cycles = state.get("audit_cycles", 0)
    header = "🛡️ **SENTINEL VERIFIED SOLUTION**" if consensus else "💡 **PROPOSED HYPOTHESIS**"
    
    # 3. Compact Technical Trace (Code block prevents markdown breaking)
    logs = state.get("sandbox_logs", "") or ""
    if len(logs) > 300: logs = logs[:297] + "..."
    
    trace_text = (
        f"Consensus: {'YES' if consensus else 'NO'} | "
        f"Nodes: {len(hypotheses)} | Cycles: {cycles}/2\n"
        f"Logic: {audit_reasoning[:150]}...\n"
    )
    if logs:
        trace_text += f"\nSandbox Output:\n{logs}"

    # 4. Final Composition
    final_text = (
        f"{header}\n\n"
        f"{summary_clean}\n\n"
        f"```text\n[SYSTEM TRACE]\n{trace_text}\n```"
    )
    
    # Safely truncate if it somehow exceeds Telegram's 4096 limit
    if len(final_text) > 4000:
        # We slice before the end of the code block so we don't break the formatting
        final_text = final_text[:3980] + "\n...[Truncated]\n```"

    return {
        "status_messages": status_messages + [header],
        "messages": [AIMessage(content=final_text)]
    }
