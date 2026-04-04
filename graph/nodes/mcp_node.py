# graph/nodes/mcp_node.py
"""
Node 3 — MCP Tool Caller.
Checks each hypothesis for Python code; executes via MCP client bridge.
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from graph.state import SentinelState


async def mcp_node(state: SentinelState) -> dict:
    """
    For each hypothesis that contains a Python code block,
    invoke the MCP execute_python tool and collect results.
    """
    hypotheses = state.get("agent_hypotheses", [])
    
    # 1. Filter code to run
    code_to_run = [
        (h["model_id"], h["extracted_code"]) 
        for h in hypotheses if h["extracted_code"]
    ]

    # No code found — skip node
    if not code_to_run:
        status = "🔍 No code blocks found — skipping sandbox"
        return {
            "sandbox_logs": None,
            "sandbox_success": False,
            "status_messages": state.get("status_messages", []) + [status]
        }

    # 2. Spawning MCP Server
    # Using stdio transport for inter-node tool invocation
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server.server"],
    )

    all_outputs: list[str] = []
    overall_success = True

    try:
        # Connect to the local MCP server via stdio
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Process all code blocks
                for i, (model_id, code) in enumerate(code_to_run):
                    # Call the tool defined in mcp_server/server.py
                    result = await session.call_tool(
                        "execute_python",
                        arguments={"code": code, "timeout_seconds": 15},
                    )
                    
                    # 3. Parse Tool Response
                    # FastMCP returns content as a list of TextContent objects
                    raw = result.content[0].text if result.content else "{}"
                    parsed = json.loads(raw)

                    status_icon = "✅" if parsed.get("success") else "❌"
                    execution_time = parsed.get("execution_time_ms", 0)
                    
                    # Log the results for the Auditor
                    all_outputs.append(
                        f"### Sandbox Run {i+1} [{status_icon} {execution_time}ms] — Model: {model_id}\n"
                        f"STDOUT:\n{parsed.get('stdout', '')}\n"
                        f"STDERR:\n{parsed.get('stderr', '')}"
                    )
                    
                    # Overall success tracking
                    if not parsed.get("success"):
                        overall_success = False

        combined_logs = "\n\n".join(all_outputs)
        status = f"🛠️ MCP Python Sandbox executed {len(code_to_run)} script(s)"

        return {
            "sandbox_logs": combined_logs,
            "sandbox_success": overall_success,
            "status_messages": state.get("status_messages", []) + [status]
        }
        
    except Exception as e:
        # Critical error — log the failure to the state
        status = f"❌ MCP Server Error: {str(e)}"
        return {
            "sandbox_logs": f"CRITICAL TOOLING FAILURE: {str(e)}",
            "sandbox_success": False,
            "status_messages": state.get("status_messages", []) + [status]
        }
