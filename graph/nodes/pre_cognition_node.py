# graph/nodes/pre_cognition_node.py
import asyncio
from openai import AsyncOpenAI
from graph.state import SentinelState
from db.client import supabase
from config.settings import settings

# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

EMBEDDING_MODEL = "bge-large"

async def pre_cognition_node(state: SentinelState) -> dict:
    """
    Node 0 — Pre-Cognitive Logic Retrieval (RAG).
    Searches the Vector DB for similar past problems to retrieve 'Golden Logic'.
    """
    user_query = state.get("user_query", "")
    
    # 1. Generate Embedding for the query
    try:
        coro = oxlo_client.embeddings.create(
            input=[user_query],
            model=EMBEDDING_MODEL
        )
        response = await asyncio.wait_for(coro, timeout=10.0)
        query_embedding = response.data[0].embedding
    except Exception as e:
        return {
            "status_messages": state.get("status_messages", []) + [f"⚠️ Pre-Cognition failed: {str(e)}"],
            "retrieved_logic": None
        }

    # 2. Vector Search in Supabase (RPC call to match_logic_memories)
    # We assume 'match_logic_memories' postgres function is defined as per 002 migration.
    try:
        # Note: In a real Supabase/PostgREST setup, we use an RPC to perform vector similarity
        # because the standard client doesn't support vector operators directly in filters.
        rpc_response = await supabase.rpc(
            'match_logic_memories', 
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.78, # High precision
                'match_count': 1
            }
        ).execute()
        
        matches = rpc_response.data
        if matches:
            pattern = matches[0].get("logic_pattern", "")
            return {
                "status_messages": state.get("status_messages", []) + ["🧬 [CEREBRO] Logic Pattern retrieved from memory"],
                "retrieved_logic": pattern
            }
    except Exception:
        pass # Fallback to no retrieval

    return {
        "status_messages": state.get("status_messages", []) + ["🔍 [CEREBRO] No matching logic found — thinking from scratch"],
        "retrieved_logic": None,
        "debug_attempts": 0 # Initialize counter
    }
