# bot/handlers/message_handler.py
import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from graph.graph_builder import sentinel_graph
from bot.utils.edit_queue import EditQueue


# --- Initialization ---
router = Router()


# --- State Storage (In-memory for hackathon speed) ---
USER_MODES = {}


# --- Command Handlers ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Welcome message and initialization guide."""
    welcome_text = (
        "🚀 **Oxlo-Sentinel: The Cognitive AI Hivemind**\n\n"
        "Welcome to the hivemind. I use a dual-mode engine for speed and precision:\n\n"
        "⚡ **Flash Mode**: Instant (<1s) answers for simple chat.\n"
        "🧠 **Thinking Mode**: Parallel Swarm debate + E2B Sandbox.\n\n"
        "💡 **Commands:**\n"
        "- `/think`: Force the Deep Swarm for your next question.\n"
        "- `/fast`: Force a Flash response for speed.\n"
        "- `/audit <claim>`: Start a full swarm audit immediately.\n"
        "- `/calc <math>`: Mathematical proof via secure sandbox.\n"
        "- `/help`: Deep-dive into our architecture."
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Architectural explanation."""
    help_text = (
        "🏗️ **System Architecture**\n\n"
        "1. **Cerebro**: Pre-cognitive logic retrieval from memory.\n"
        "2. **Omniscient Shield**: Global concurrency protection (Rate-Limit safe).\n"
        "3. **Skeptic Pattern**: Multiple models debate your claim.\n"
        "4. **MCP Sandbox**: Verified Python execution for mathematical truth.\n\n"
        "**Usage:**\n"
        "Simply send a message, or use `/audit` for critical logical verification."
    )
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("think"))
async def cmd_think(message: types.Message):
    USER_MODES[message.chat.id] = "think"
    await message.answer("🧠 **Mode: Deep Thinking enabled.**\nYour next question will invoke the full model swarm.")


@router.message(Command("fast"))
async def cmd_fast(message: types.Message):
    USER_MODES[message.chat.id] = "fast"
    await message.answer("⚡ **Mode: Flash Response enabled.**\nI will prioritize speed and instant answers.")


@router.message(Command("calc"))
@router.message(Command("audit"))
async def cmd_complex_shortcuts(message: types.Message):
    """Directly trigger swarm from a command."""
    # If using /audit or /calc with text, process it immediately
    arg_text = message.text.split(maxsplit=1)[1] if " " in message.text else None
    
    if not arg_text:
        USER_MODES[message.chat.id] = "think"
        label = "Logical Audit" if "/audit" in message.text else "Math Verification"
        return await message.answer(f"🧠 **Mode: {label} enabled.**\nSend your query and I will fire the swarm.")
    
    # Otherwise, hijack and fire handle_query immediately
    USER_MODES[message.chat.id] = "think"
    message.text = arg_text
    return await handle_query(message, "cmd_user", "cmd_session")


# --- Main Hivemind Handler ---
@router.message(F.text)
async def handle_query(message: types.Message, user_uuid: str, session_id: str):
    """
    Main entry point for all cognitive queries.
    """
    current_mode = USER_MODES.get(message.chat.id, None)
    
    # Reset mode after one use to keep the bot autonomous by default
    if current_mode:
        USER_MODES.pop(message.chat.id)

    # 1. Initial Status Message
    status_msg = await message.answer("⏳ **Initializing Oxlo-Sentinel...**", parse_mode="Markdown")
    
    # 2. Setup Live Terminal (Edit Queue)
    queue = EditQueue(message.bot, message.chat.id, status_msg.message_id)
    
    # 3. Preparation State
    initial_state = {
        "user_query": message.text,
        "user_mode": current_mode,
        "telegram_chat_id": message.chat.id,
        "telegram_message_id": status_msg.message_id,
        "session_id": session_id,
        "status_messages": ["[⏳ Initializing Swarm]"],
        "messages": [("user", message.text)]
    }

    # 4. Invoke LangGraph with Event Streaming (v2.4 Global Watchdog)
    final_output = None
    try:
        # Flexible 300s cap for the entire swarm operation to allow multi-cycle debates during API congestion
        async with asyncio.timeout(300.0):
            async for event in sentinel_graph.astream_events(initial_state, version="v1"):
                kind = event["event"]
                if kind == "on_chain_end":
                    data = event.get("data", {})
                    output = data.get("output", {})
                    if isinstance(output, dict) and "status_messages" in output:
                        final_output = output # Capture latest state
                        status_list = output.get("status_messages", [])
                        display_text = "🧠 **Oxlo-Sentinel Hivemind Activity:**\n"
                        display_text += "\n".join(f"- {s}" for s in status_list)
                        await queue.push(display_text)

        # 5. Extract and Deliver Final Answer
        if final_output and "messages" in final_output and final_output["messages"]:
            final_answer = final_output["messages"][-1].content
            await queue.flush()
            
            # Robust Edit with Markdown Fallback
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=final_answer,
                    parse_mode="Markdown"
                )
            except Exception:
                # Fallback to plain text if Markdown parsing fails
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=final_answer,
                    parse_mode=None
                )
        else:
            raise ValueError("Swarm execution completed but no message was generated.")

    except asyncio.TimeoutError:
        error_text = "❌ **Swarm Execution Timeout**\n\nThe Hivemind took too long (60s+) to reach a consensus. Please try again or use `/fast` for an instant response."
        await queue.push(error_text)
        await queue.flush()
    except Exception as e:
        error_text = f"❌ **Swarm Execution Error**\n\n{str(e)}"
        await queue.push(error_text)
        await queue.flush()
