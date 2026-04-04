# graph/nodes/router_node.py
import re
from openai import AsyncOpenAI
from graph.state import SentinelState
from config.settings import settings


# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

# --- Configuration ---
ROUTER_MODEL = "llama-3.2-3b-instruct" # Fast classifier

ROUTER_SYSTEM_PROMPT = """You are a classification engine for a Hivemind.
Classify the user's intent into exactly one of two categories:

1. "chat" - For simple greetings, small talk, general factual questions, or single-step requests.
2. "complex" - For math problems, logic puzzles, coding requests, multi-step analysis, or any query that requires verification.

Respond with exactly one word: "chat" or "complex".
"""

INJECTION_PATTERNS = [
    r"ignore (previous|prior|above) instructions",
    r"print (api|secret|key|token|password|env)",
    r"system prompt",
    r"you are now",
    r"<\|im_start\|>",
    r"</system>",
]


# --- Logic ---
def sanitize_user_input(text: str) -> str:
    """Check for prompt injection and truncate to safe limits."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("⚠️ Potentially malicious input detected. Request blocked.")
    return text[:2000].strip()


async def router_node(state: SentinelState) -> dict:
    """
    Node 1 — The Router.
    Classify the query to decide between 'Flash Response' and 'Cognitive Swarm'.
    """
    user_query = state.get("user_query", "")
    
    # 1. Sanitize
    try:
        clean_query = sanitize_user_input(user_query)
    except ValueError as e:
        # In a real app, this would be an error node, but here we just return the error
        return {
            "status_messages": state.get("status_messages", []) + [str(e)],
            "route": "chat"  # Default to chat for immediate error feedback
        }

    # 2. Classify
    response = await oxlo_client.chat.completions.create(
        model=ROUTER_MODEL,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": clean_query},
        ],
        temperature=0.0,
        max_tokens=10,
    )
    
    raw_route = (response.choices[0].message.content or "").strip().lower()
    route = "complex" if "complex" in raw_route else "chat"

    # 3. Telemetry
    status = f"[🧭 Router → {route.upper()}]"
    
    return {
        "route": route,
        "status_messages": state.get("status_messages", []) + [status],
        "user_query": clean_query
    }
