# graph/nodes/generator_node.py
import asyncio
import re
from openai import AsyncOpenAI
from graph.state import SentinelState, Hypothesis
from config.settings import settings


# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

# --- Configuration ---
# Parallel swarm models
GENERATOR_MODELS = [
    "deepseek-v3.2",
    "mistral-7b",
]
ROUTER_MODEL = "llama-3.2-3b" # Fast classifier

GENERATOR_SYSTEM_PROMPT = """You are a Universal Cognitive Solver in a high-stakes swarm.
Your goal is to provide a comprehensive, logically-sound, and auditable solution to the user's request. 

THE UNIVERSAL REASONING PROCESS:
1. [INPUT ANALYSIS]: Extract all constraints, constants, and logical axioms from the prompt.
2. [LOGICAL MODELING]: Deconstruct the problem into a verifiable math or logic model.
3. [AUTONOMOUS VERIFICATION]: YOU ARE FORBIDDEN FROM DOING MATH IN RAW TEXT. If the problem involves numbers, weights, money, or logic, YOU MUST write a completely self-contained Python script inside a ```python block to calculate the exact numerical answer. Use print() to output the final result.
4. Provide a confidence score: "CONFIDENCE: <score>".

DEBATE ROLE: If you are the SKEPTIC, hunt for logical fallacies or hidden edge cases, and write your own contrasting Python script.
"""


# --- Logic ---
async def _call_single_model(model_id: str, user_query: str, retries: int = 3, is_skeptic: bool = False) -> Hypothesis:
    """
    Execute one Oxlo model with a built-in retry loop for 504/502 resilience.
    """
    system_prompt = GENERATOR_SYSTEM_PROMPT
    if is_skeptic:
        system_prompt += "\nSPECIAL ROLE: You are acting as the SKEPTIC. Hunt for logic traps."
        
    last_err = None
    for attempt in range(retries):
        try:
            response = await oxlo_client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                temperature=0.0, # Pure deterministic analytics
                max_tokens=1500,
            )
            
            content = response.choices[0].message.content or ""
            
            # 1. Extract Python code blocks (if any)
            code_match = re.search(r"```(?:python)?\s*\n(.*?)```", content, re.DOTALL)
            extracted_code = code_match.group(1).strip() if code_match else None
            
            # 2. Extract confidence score
            conf_match = re.search(r"CONFIDENCE:\s*([0-9.]+)", content)
            confidence = float(conf_match.group(1)) if conf_match else 0.5
            
            return Hypothesis(
                model_id=model_id,
                content=content,
                extracted_code=extracted_code,
                confidence=confidence
            )
        except Exception as e:
            last_err = e
            # Only retry on 504 (timeout) or 502 (bad gateway)
            if "504" in str(e) or "502" in str(e) or "Gateway Timeout" in str(e):
                backoff = 2 ** attempt
                await asyncio.sleep(backoff)
                continue
            else:
                # Other errors (429, 401) should fail fast to avoid infinite locks
                break

    # If we get here, all retries failed or it was a non-retriable error
    return Hypothesis(
        model_id=model_id,
        content=f"ERROR: Model failed — {str(last_err)}",
        extracted_code=None,
        confidence=0.0
    )


# --- Configuration ---
# Parallel swarm models
GENERATOR_MODELS = [
    "deepseek-v3.2", # Reverted to standard V3 to prevent <thought> token suffocation timeouts
    "llama-3.1-8b",    # High-performance parallel brain
]
ROUTER_MODEL = "llama-3.2-3b" # Fast classifier

# --- Logic ---
async def generator_node(state: SentinelState) -> dict:
    """
    Node 2 — Divergent Generator (True Parallel v4.5).
    Fires ALL models simultaneously using raw asyncio.gather.
    """
    user_query = state.get("user_query", "")
    status_messages = state.get("status_messages", [])
    
    # --- DEBATE INJECTION (The Fatal Flaw Fix) ---
    # If we are in a debate cycle, we MUST feed the models the Auditor's critique.
    # Otherwise, they will deterministically generate the exact same wrong answer forever.
    audit_cycles = state.get("audit_cycles", 0)
    audit_feedback = state.get("audit_reasoning", "")
    
    if audit_cycles > 0:
        actual_prompt = (
            f"ORIGINAL QUERY: {user_query}\n\n"
            f"--- DEBATE ROUND {audit_cycles} ---\n"
            f"AUDITOR CRITIQUE: {audit_feedback}\n"
            f"WARNING: The previous hypotheses disagreed or lacked Python proofs. "
            f"You MUST reconsider the logic, fix the flaws, and provide a verified Python script."
        )
    else:
        actual_prompt = user_query
    
    # 1. Prepare tasks for True Concurrency
    tasks = []
    
    async def _safe_call(model_id, is_skeptic=False):
        try:
            return await asyncio.wait_for(
                _call_single_model(model_id, actual_prompt, is_skeptic=is_skeptic),
                timeout=45.0
            )
        except Exception as e:
            return Hypothesis(
                model_id=model_id,
                content=f"ERROR: Model failed — {str(e)}",
                extracted_code=None,
                confidence=0.0
            )

    for i, mid in enumerate(GENERATOR_MODELS):
        is_skeptic = (i == 1) # SKEPTIC role to second model
        tasks.append(_safe_call(mid, is_skeptic))

    # 2. Fire and Wait for the slowest logic chain to finish
    results = await asyncio.gather(*tasks)

    # 3. Filter empty errors
    valid_hypotheses = [
        h for h in results 
        if "rate_limit_exceeded" not in h["content"] and "Concurrency limit" not in h["content"]
    ]

    return {
        "agent_hypotheses": valid_hypotheses,
        "status_messages": status_messages + [f"🧠 {len(valid_hypotheses)} hypotheses generated (True Swarm Async)"]
    }
