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
    "mistral-7b-instruct",
    "llama-3.2-3b-instruct",
]

GENERATOR_SYSTEM_PROMPT = """You are a precise analytical solver in a swarm.
Your goal is to provide a comprehensive, step-by-step solution to the user's reasoning problem.

IMPORTANT RULES:
1. If your solution involves mathematics, logic, or data processing, you MUST write a self-contained Python script to verify your answer.
2. Put your Python code inside a ```python code block.
3. At the very end of your response, provide your self-assessed confidence score on exactly one line: "CONFIDENCE: <score>" (e.g., CONFIDENCE: 0.95).
"""


# --- Logic ---
async def _call_single_model(model_id: str, user_query: str) -> Hypothesis:
    """
    Execute one Oxlo model and parse its response.
    """
    response = await oxlo_client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    
    content = response.choices[0].message.content or ""
    
    # 1. Extract Python code blocks (if any)
    code_match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
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


async def generator_node(state: SentinelState) -> dict:
    """
    Node 2 — Divergent Generator.
    Parallel execution of the model swarm via asyncio.gather.
    """
    user_query = state.get("user_query", "")
    
    # 1. Parallel Dispatch
    tasks = [
        _call_single_model(mid, user_query)
        for mid in GENERATOR_MODELS
    ]
    
    # We use return_exceptions=True to ensure one failure doesn't kill the swarm
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 2. Parse Results
    valid_hypotheses: list[Hypothesis] = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            # Record the failure as a hypothesis for the Auditor to see
            valid_hypotheses.append(Hypothesis(
                model_id=GENERATOR_MODELS[i],
                content=f"[ERROR: Model failed — {str(res)}]",
                extracted_code=None,
                confidence=0.0
            ))
        else:
            valid_hypotheses.append(res)
            
    # 3. Telemetry
    status = "⚡ Parallel hypotheses generated (DeepSeek-V3.2, Mistral, Llama)"
    
    return {
        "agent_hypotheses": valid_hypotheses,
        "status_messages": state.get("status_messages", []) + [status]
    }
