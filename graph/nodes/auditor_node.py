# graph/nodes/auditor_node.py
import json
import asyncio
from openai import AsyncOpenAI
from graph.state import SentinelState
from config.settings import settings
from graph.concurrency import oxlo_concurrency_semaphore


# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

# --- Configuration ---
# Auditor Model (Reasoning Model)
AUDITOR_MODEL = "deepseek-r1-8b"
MAX_AUDIT_CYCLES = 2 


AUDITOR_SYSTEM_PROMPT = """You are an elite Scientific Arbiter in a cognitive hivemind.
Your goal is to evaluate the swarm's answers for consensus, factual truth, and logical soundness.

YOUR VERIFICATION CRITERIA:
1. CONSENSUS: Do the models logically agree on the final conclusion/answer?
2. GROUND TRUTH: If MCP sandbox logs are present, evaluate if they support the claims. Sandbox results are absolute TRUTH.
3. LOGICAL SOUNDNESS: Is the reasoning free of fallacies?
4. SKEPTICISM: Pay close attention to the model marked 'SKEPTIC'. If they find a trap or a misreading, prioritize their warning.

RESPONSE FORMAT (JSON ONLY):
{
    "consensus_reached": true/false, 
    "reasoning": "<analysis focusing on consensus vs sandbox truth>", 
    "best_answer": "<the final verified answer or null>"
}
"""


# --- Logic ---
async def auditor_node(state: SentinelState) -> dict:
    """
    Node 4 — The Auditor.
    Checks for consensus and verified truth. Controls the retry loop.
    """
    # 1. Prepare Audit Context
    hypotheses = state.get("agent_hypotheses", [])
    hypotheses_text = "\n\n".join([
        f"--- Model: {h['model_id']} (Confidence: {h['confidence']}) ---\n{h['content']}"
        for h in hypotheses
    ])
    
    sandbox_text = state.get("sandbox_logs", "")
    if sandbox_text:
        audit_input = f"MODEL HYPOTHESES:\n{hypotheses_text}\n\nGROUND TRUTH SANDBOX LOGS:\n{sandbox_text}"
    else:
        audit_input = f"MODEL HYPOTHESES:\n{hypotheses_text}\n\nNO SANDBOX DATA AVAILABLE."

    # 2. Invoke DeepSeek with Concurrency Shield
    for attempt in range(3):
        try:
            # First, wait for a slot (unlimited patience for the queue)
            async with oxlo_concurrency_semaphore:
                # Second, execute the reasoning with a robust timeout
                coro = oxlo_client.chat.completions.create(
                    model=AUDITOR_MODEL,
                    messages=[
                        {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
                        {"role": "user", "content": audit_input},
                    ],
                    temperature=0.0,
                    max_tokens=800,
                    response_format={"type": "json_object"}
                )
                response = await asyncio.wait_for(coro, timeout=90.0)
            
            # 3. Parse JSON Response
            raw_content = (response.choices[0].message.content or "").strip()
            parsed = json.loads(raw_content)
            break # Success
        except Exception as e:
            if any(x in str(e) for x in ["429", "504", "502", "limit"]) and attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            # Fallback for parsing or API errors
            parsed = {
                "consensus_reached": False,
                "reasoning": f"AUDITOR FAILED/TIMEOUT: {str(e)}",
                "best_answer": None
            }
            break

    consensus = parsed.get("consensus_reached", False)
    
    # 4. Increment Cycles
    current_cycles = state.get("audit_cycles", 0) + 1
    
    # Telemetry
    if consensus:
        status = f"⚖️ Hivemind Consensus reached (Cycle {current_cycles}/{MAX_AUDIT_CYCLES})"
    else:
        status = f"🔄 Disagreement detected — Starting Hivemind Debate ({current_cycles}/{MAX_AUDIT_CYCLES})"

    return {
        "consensus_reached": consensus,
        "audit_cycles": current_cycles,
        "audit_reasoning": parsed.get("reasoning"),
        "status_messages": state.get("status_messages", []) + [status]
    }
