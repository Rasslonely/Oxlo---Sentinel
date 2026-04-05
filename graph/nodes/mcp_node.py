# graph/nodes/mcp_node.py
import re
import asyncio
from openai import AsyncOpenAI
from mcp_server.tools.python_sandbox import execute_python_in_sandbox
from graph.state import SentinelState
from config.settings import settings

# --- Initialization ---
oxlo_client = AsyncOpenAI(
    api_key=settings.OXLO_API_KEY,
    base_url=settings.OXLO_BASE_URL,
)

async def mcp_node(state: SentinelState) -> dict:
    """
    Node 3 — MCP Tool Caller & Internal Debugger.
    Executes Python code from hypotheses. If errors occur, it attempts to 
    self-correct the code (Multi-Attempt Loop) to improve verification accuracy.
    """
    hypotheses = state.get("agent_hypotheses", [])
    # Extract code and model ID for context
    code_to_run = [(h["model_id"], h["extracted_code"]) for h in hypotheses if h.get("extracted_code")]
    debug_count = state.get("debug_attempts", 0)
    status_messages = state.get("status_messages", [])

    if not code_to_run:
        return {
            "sandbox_logs": None,
            "sandbox_success": False,
            "status_messages": status_messages + ["🔍 No code blocks found — skipping sandbox"]
        }

    all_outputs: list[str] = []
    overall_success = True
    
    # Process each code block
    for i, (model_id, code) in enumerate(code_to_run):
        # 1. Execute initial code
        result = await execute_python_in_sandbox(code, timeout_seconds=15)
        
        # 2. Self-Debugging Loop (If failed and has retries)
        if not result.get("success") and debug_count < 2:
            try:
                # Ask a fast model to fix the code
                coro = oxlo_client.chat.completions.create(
                    model="llama-3.2-3b",
                    messages=[
                        {"role": "system", "content": "You are a Python Debugger. Fix this code to solve the user's error. RESPOND ONLY WITH A REPLACEMENT ```python CODE BLOCK."},
                        {"role": "user", "content": f"MODEL_ID: {model_id}\nCODE:\n{code}\n\nERROR:\n{result.get('stderr')}"}
                    ],
                    temperature=0.0
                )
                fix_res = await asyncio.wait_for(coro, timeout=10.0)
                fixed_content = fix_res.choices[0].message.content or ""
                fixed_code_match = re.search(r"```(?:python)?\s*\n(.*?)```", fixed_content, re.DOTALL)
                
                if fixed_code_match:
                    fixed_code = fixed_code_match.group(1).strip()
                    # Re-run fixed code
                    result = await execute_python_in_sandbox(fixed_code, timeout_seconds=15)
                    debug_count += 1
            except Exception:
                pass # Fallback to original failure if debugger fails

        # 3. Collect Results
        status_icon = "✅" if result.get("success") else "❌"
        all_outputs.append(
            f"### Sandbox Run {i+1} [{status_icon} {result.get('execution_time_ms')}ms] — Model: {model_id}\n"
            f"STDOUT:\n{result.get('stdout', '')}\n"
            f"STDERR:\n{result.get('stderr', '')}"
        )
        if not result.get("success"):
            overall_success = False

    combined_logs = "\n\n".join(all_outputs)
    
    return {
        "sandbox_logs": combined_logs,
        "sandbox_success": overall_success,
        "debug_attempts": debug_count,
        "status_messages": status_messages + [f"🛠️ MCP Sandbox executed {len(code_to_run)} script(s) (Self-Fixes: {debug_count})"]
    }
