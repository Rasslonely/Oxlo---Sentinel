# mcp_server/tools/python_sandbox.py
import time
import asyncio
from e2b_code_interpreter import AsyncSandbox
from config.settings import settings


# --- State Management ---
# Module-level warm sandbox instance
_warm_sandbox: Optional[AsyncSandbox] = None
_sandbox_created_at: float = 0.0

# Configuration
SANDBOX_TTL_SECONDS = 600  # 10 minutes session life


# --- Logic ---
async def _get_sandbox() -> AsyncSandbox:
    """
    Return a warm E2B sandbox, creating or recycling as needed.
    Ensures < 500ms execution latency by avoiding cold starts.
    """
    global _warm_sandbox, _sandbox_created_at

    age = time.time() - _sandbox_created_at
    
    # Recycle if missing or expired
    if _warm_sandbox is None or age > SANDBOX_TTL_SECONDS:
        if _warm_sandbox is not None:
            await _warm_sandbox.kill()
        
        # Create a new network-isolated microVM
        # NOTE: E2B sandboxes are isolated by design
        _warm_sandbox = await AsyncSandbox.create(
            api_key=settings.E2B_API_KEY,
            timeout=30,
        )
        _sandbox_created_at = time.time()

    return _warm_sandbox


async def execute_python_in_sandbox(code: str, timeout_seconds: int = 15) -> dict:
    """
    Execute arbitrary Python code in the secure E2B sandbox.
    Captures stdout, stderr, and execution status.
    """
    start_time = time.time()
    
    try:
        sandbox = await _get_sandbox()
        
        # Execute the code block safely
        execution = await sandbox.run_code(code, timeout=timeout_seconds)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Format the results
        stdout = "\n".join(str(r) for r in execution.results) if execution.results else ""
        stderr = execution.error.traceback if execution.error else ""
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "success": execution.error is None,
            "execution_time_ms": elapsed_ms,
        }
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "stdout": "",
            "stderr": f"Sandbox Execution Error: {type(e).__name__}: {str(e)}",
            "success": False,
            "execution_time_ms": elapsed_ms,
        }
