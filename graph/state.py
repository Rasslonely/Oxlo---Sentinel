# graph/state.py
from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class Hypothesis(TypedDict):
    """
    A single model's attempt at solving the user's problem.
    Used in the Divergent Generator node.
    """
    model_id: str                    # e.g. "deepseek-v3.2"
    content: str                     # The hypothesis text
    extracted_code: Optional[str]    # Python code block if present
    confidence: float                # 0.0–1.0 self-reported score


class SentinelState(TypedDict):
    """
    The single source of truth for one LangGraph execution.
    All nodes read from and write to this state dict.
    """
    # --- Core Conversation ---
    # Messages are managed by LangGraph's add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    telegram_chat_id: int
    telegram_message_id: int         # The "live" message to edit in place

    # --- Routing ---
    # "chat" = Flash Response (< 1s)
    # "complex" = Cognitive Swarm (~8s)
    route: Literal["chat", "complex"]

    # --- Swarm Outputs (Cognitive Swarm ONLY) ---
    agent_hypotheses: list[Hypothesis]
    sandbox_logs: Optional[str]      # Combined stdout from E2B
    sandbox_success: bool

    # --- Auditor Control ---
    consensus_reached: bool
    audit_cycles: int                # Hard cap at MAX_AUDIT_CYCLES=5
    audit_reasoning: Optional[str]   # Auditor's explanation (DeepSeek-R1-8B)

    # --- UI Streaming ---
    # Ordered log of progress messages for the live Telegram edit queue
    user_mode: Optional[str]  # 'think' or 'fast'
    # --- Cerebro Core (v3.0 Logic Memory) ---
    retrieved_logic: Optional[str]  # Past "Golden Logic" retrieved from Vector DB
    debug_attempts: int             # Internal sandbox loop counter
    short_circuit: bool             # GPT-Speed Path: Skip Swarm if primary is confident
    status_messages: list[str]

    # --- Persistence ---
    session_id: str
