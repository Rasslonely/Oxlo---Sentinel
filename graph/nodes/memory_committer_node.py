# graph/nodes/memory_committer_node.py
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

async def memory_committer_node(state: SentinelState) -> dict:
    """
    Final Node — Cognitive Commitment.
    If the Auditor found consensus, store the final reasoning as a Logic Pattern.
    """
    consensus = state.get("consensus_reached", False)
    if not consensus:
        return {} # Don't learn from failures or unverified answers

    user_query = state.get("user_query", "")
    
    # Use the Synthesizer logic (the last message) or the Auditor's reasoning
    # But better to use the specific best hypothesis for the code logic
    best_answer = state.get("messages", [])[-1].content if state.get("messages") else ""
    
    # 1. Summarize into a Logic Pattern (God-Tier Compression)
    # Background tasks must NEVER hang the user. We wrap everything in an 8-second limit.
    async def _commit_logic():
        # We use a fast model to compress the reasoning for future retrieval
        summary_res = await oxlo_client.chat.completions.create(
            model="llama-3.2-3b",
            messages=[
                {"role": "system", "content": "Extract the generic LOGIC PATTERN from this solution. Avoid specific numbers. Focus on formulas, constraints, and steps. Respond with exactly the pattern."},
                {"role": "user", "content": best_answer},
            ],
            temperature=0.0,
            max_tokens=200
        )
        logic_pattern = summary_res.choices[0].message.content or ""
        
        # 2. Generate Embedding
        emb_res = await oxlo_client.embeddings.create(
            input=[user_query],
            model=EMBEDDING_MODEL
        )
        embedding = emb_res.data[0].embedding
        return logic_pattern, embedding

    try:
        logic_pattern, embedding = await asyncio.wait_for(_commit_logic(), timeout=8.0)
        
        # 3. Commit to Supabase
        await supabase.table("logic_memories").insert({
            "user_query": user_query,
            "logic_pattern": logic_pattern,
            "embedding": embedding,
            "problem_type": "math_logic" # Logic could be more dynamic
        }).execute()
        
        return {
            "status_messages": state.get("status_messages", []) + ["💾 [MEMORY] Applied Logic stored in Long-Term Memory"]
        }
    except Exception:
        return {} # Silent fail — memory commitment is a side effect
