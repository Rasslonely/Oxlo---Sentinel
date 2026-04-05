# mcp_server/server.py
"""
Oxlo-Sentinel MCP Server.
Exposes a secure Python execution tool via MCP stdio transport.
The LangGraph agent connects to this server as an MCP Client.
"""
import asyncio
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp_server.tools.python_sandbox import execute_python_in_sandbox


# Initialize FastMCP Server
mcp = FastMCP(
    name="oxlo-sentinel-tools",
    description="Secure code execution tools for the Oxlo-Sentinel agent swarm. Verified by E2B.",
)


@mcp.tool()
async def execute_python(
    code: str,
    timeout_seconds: int = 15,
) -> dict:
    """
    Execute a Python script in an isolated E2B microVM sandbox.

    Use this tool when a hypothesis contains a Python code block that
    needs to be verified against ground truth (math/logic).

    Args:
        code: The complete Python script to execute. Must be self-contained.
        timeout_seconds: Max execution time (1–30). Default 15.

    Returns:
        A dict with the execution results:
            - stdout (str): All printed output.
            - stderr (str): Any error messages/tracebacks.
            - success (bool): True if exit code was 0.
            - execution_time_ms (int): Duration of the run.
    """
    # 1. Input Validation
    timeout_seconds = max(1, min(30, timeout_seconds))  # Clamp to safe range
    
    # 2. Secure Execution
    return await execute_python_in_sandbox(code, timeout_seconds)


if __name__ == "__main__":
    # Start the server on stdio transport
    mcp.run()
