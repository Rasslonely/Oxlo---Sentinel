import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from graph.graph_builder import sentinel_graph
from config.settings import settings

app = FastAPI(title="Oxlo-Sentinel API")

# Enable CORS for the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

async def stream_graph_updates(user_query: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Invokes the LangGraph and yields SSE events for each status update.
    """
    initial_state = {
        "messages": [],
        "user_query": user_query,
        "session_id": session_id,
        "status_messages": [],
        "agent_hypotheses": [],
        "audit_cycles": 0,
        "consensus_reached": False
    }

    def serialize_v2(obj):
        """Recursive helper to make LangGraph/LangChain objects JSON serializable."""
        if isinstance(obj, list):
            return [serialize_v2(i) for i in obj]
        if isinstance(obj, dict):
            return {k: serialize_v2(v) for k, v in obj.items()}
        # Handle LangChain messages (AIMessage, HumanMessage, etc.)
        if hasattr(obj, "content") and hasattr(obj, "type"):
            return {"content": str(obj.content), "type": obj.type}
        return str(obj) if hasattr(obj, "__dict__") else obj

    try:
        final_sent = False
        # We use astream_events to capture granular node transitions
        async for event in sentinel_graph.astream_events(
            initial_state, 
            version="v2",
            config={"configurable": {"thread_id": session_id}}
        ):
            kind = event["event"]
            
            # Filter for specific events we want to surface to the UI
            # Trigger 'final' as soon as the synthesizer is done to avoid hanging on side-effects
            if kind == "on_chain_end" and (event["name"] == "synthesizer" or event["name"] == "LangChain"):
                if not final_sent:
                    yield json.dumps({
                        "type": "final",
                        "data": serialize_v2(event["data"]["output"])
                    })
                    final_sent = True
            
            # Custom status updates from nodes
            elif kind == "on_chat_model_stream":
                # If we wanted to stream tokens, we would do it here
                pass
                
            elif kind == "on_chain_stream":
                # This usually contains the state chunks from nodes
                data = event["data"].get("chunk", {})
                if "status_messages" in data:
                    yield json.dumps({
                        "type": "status",
                        "content": data["status_messages"][-1]
                    })
                    
    except Exception as e:
        yield json.dumps({
            "type": "error",
            "content": f"Graph Execution Error: {str(e)}"
        })

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, req: Request):
    """
    Streaming chat endpoint using SSE.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    return EventSourceResponse(
        stream_graph_updates(request.message, session_id)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
