# mcp_server/tools/python_sandbox.py
import time
import asyncio
from typing import Optional, Dict, Any
from e2b_code_interpreter import AsyncSandbox
from config.settings import settings


# --- State Management ---
# Module-level warm sandbox instance 
_warm_sandbox: Optional[AsyncSandbox] = None
_sandbox_created_at: float = 0.0
_last_loop: Optional[asyncio.AbstractEventLoop] = None
_sandbox_lock = asyncio.Lock() # Protect against parallel initialization

# Configuration
SANDBOX_TTL_SECONDS = 280  # 4.6 minutes (E2B default death-timer is 5 mins)


# --- Logic ---
async def _get_sandbox() -> AsyncSandbox:
    """
    Return a warm E2B sandbox, creating or recycling as needed.
    Ensures < 500ms execution latency by avoiding cold starts.
    """
    global _warm_sandbox, _sandbox_created_at, _last_loop

    async with _sandbox_lock: # Atomically check and create
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            _warm_sandbox = None
            current_loop = None

        # 1. Detect loop changes
        if _warm_sandbox is not None and current_loop != _last_loop:
            _warm_sandbox = None

        # 2. Check age and existence
        age = time.time() - _sandbox_created_at
        
        if _warm_sandbox is None or age > SANDBOX_TTL_SECONDS:
            if _warm_sandbox is not None:
                try:
                    # Timeout-protected kill
                    await asyncio.wait_for(_warm_sandbox.kill(), timeout=5.0)
                except Exception:
                    pass
                _warm_sandbox = None
            
            # 3. Create a fresh sandbox with a strict watchdog timeout
            # If E2B is slow or the network is blocked, we must THROW, not hang.
            try:
                _warm_sandbox = await asyncio.wait_for(
                    AsyncSandbox.create(
                        api_key=settings.E2B_API_KEY, 
                        timeout=SANDBOX_TTL_SECONDS
                    ),
                    timeout=15.0
                )
                _sandbox_created_at = time.time()
                _last_loop = current_loop
            except Exception as e:
                _warm_sandbox = None
                raise TimeoutError(f"E2B Sandbox Connection Timeout: {str(e)}")

        return _warm_sandbox


async def execute_python_in_sandbox(code: str, timeout_seconds: int = 15) -> Dict[str, Any]:
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
        # In E2B's AsyncSandbox.run_code:
        # - logs.stdout/stderr contain the standard output/error (list of strings)
        # - results contains the return value of the last expression (list of objects)
        stdout = "\n".join(execution.logs.stdout)
        stderr = "\n".join(execution.logs.stderr)
        
        # If there's an error, append the traceback
        if execution.error:
            stderr += f"\n{execution.error.name}: {execution.error.value}\n{execution.error.traceback}"
        
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
