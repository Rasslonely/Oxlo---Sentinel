# graph/nodes/auditor_node.py
import json
from openai import AsyncOpenAI
from graph.state import SentinelState
from config.settings import settings


# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

# --- Configuration ---
# Auditor Model (Reasoning Model)
AUDITOR_MODEL = "deepseek-r1-8b"
MAX_AUDIT_CYCLES = 5  # User requested better performance


AUDITOR_SYSTEM_PROMPT = f"""You are a ruthless scientific auditor for a cognitive hivemind.
Your goal is to reach a correct, verified answer by evaluating multiple model hypotheses 
and their corresponding Python sandbox execution results.

Ground Truth Priority:
1. If Python sandbox outputs exist, they are the HIGHEST priority (Ground Truth).
2. If multiple models agree and their confidence is high, consider it a consensus.
3. If sandbox results contradict model reasoning, the sandbox WINS.

Evaluation Logic:
- If consensus is reached on the correct answer, set "consensus_reached": true.
- If models disagree and no code was run, or code failed, set "consensus_reached": false.
- Explain your judgment in "reasoning".

CRITICAL: Respond ONLY with a standard JSON object.
JSON Format:
{{
    "consensus_reached": true/false,
    "reasoning": "<short analysis of disagreement/consensus>",
    "best_answer": "<the final correct answer string or null>"
}}
"""


# --- Logic ---
async def auditor_node(state: SentinelState) -> dict:
    """
    Node 4 — The Auditor.
    Checks for consensus and verified truth. Controls the retry loop.
    """
    # 1. Prepare Audit Context
    hypotheses_text = "\n\n".join([
        f"--- Model: {h['model_id']} (Confidence: {h['confidence']}) ---\n{h['content']}"
        for h in state.get("agent_hypotheses", [])
    ])
    
    sandbox_text = state.get("sandbox_logs", "")
    if sandbox_text:
        audit_input = f"MODEL HYPOTHESES:\n{hypotheses_text}\n\nGROUND TRUTH SANDBOX LOGS:\n{sandbox_text}"
    else:
        audit_input = f"MODEL HYPOTHESES:\n{hypotheses_text}\n\nNO SANDBOX DATA AVAILABLE."

    # 2. Invoke DeepSeek-R1-8B
    response = await oxlo_client.chat.completions.create(
        model=AUDITOR_MODEL,
        messages=[
            {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": audit_input},
        ],
        temperature=0.0,
        max_tokens=600,
        # Force JSON response via system prompt + formatting
        response_format={"type": "json_object"}
    )
    
    # 3. Parse JSON Response
    raw_content = (response.choices[0].message.content or "").strip()
    
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        # Fallback for parsing errors
        parsed = {
            "consensus_reached": False,
            "reasoning": f"INTERNAL ERROR: Auditor produced invalid JSON: {raw_content[:100]}",
            "best_answer": None
        }

    consensus = parsed.get("consensus_reached", False)
    
    # 4. Increment Cycles & Guard the Loop
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
