# bot/handlers/message_handler.py
import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from graph.graph_builder import sentinel_graph
from bot.utils.edit_queue import EditQueue


# --- Initialization ---
router = Router()


# --- Command Handlers ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Welcome message and initialization guide."""
    welcome_text = (
        "🚀 **Oxlo-Sentinel: The Cognitive AI Swarm**\n\n"
        "Welcome to the hivemind. I use a parallel swarm of models "
        "(DeepSeek-V3.2, Mistral, Llama-3.2) and a secure E2B Python sandbox "
        "to verify math/logic/coding queries.\n\n"
        "💡 **How to use:**\n"
        "- Send any reasoning question.\n"
        "- Watch the 'Live Terminal' as the swarm debates.\n"
        "- Get a verified answer with model attribution.\n"
        "\n"
        "Try: `Calculate prime factors of 123456789`"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


# --- Main Hivemind Handler ---
@router.message(F.text)
async def handle_query(message: types.Message, user_uuid: str, session_id: str):
    """
    Main entry point for all cognitive queries.
    Bridges aiogram to the LangGraph astream_events engine.
    """
    # 1. Initial Status Message
    status_msg = await message.answer("⏳ **Initializing Oxlo-Sentinel Swarm...**", parse_mode="Markdown")
    
    # 2. Setup Live Terminal (Edit Queue)
    queue = EditQueue(message.bot, message.chat.id, status_msg.message_id)
    
    # 3. Preparation State
    initial_state = {
        "user_query": message.text,
        "telegram_chat_id": message.chat.id,
        "telegram_message_id": status_msg.message_id,
        "session_id": session_id,
        "status_messages": ["[⏳ Initializing Swarm]"],
        "messages": [("user", message.text)]
    }

    # 4. Invoke LangGraph with Event Streaming
    try:
        # We use astream_events to capture node-level status changes in real-time
        async for event in sentinel_graph.astream_events(initial_state, version="v1"):
            kind = event["event"]
            
            # --- Status Updates ---
            # Every time a node modifies the 'status_messages' list, we push it to the Telegram EditQueue
            if kind == "on_chain_end" and event["name"] == "LangGraph":
                # Final state received
                final_state = event["data"]["output"]
                status_list = final_state.get("status_messages", [])
                
                # Format current status stack for the "Live Terminal"
                display_text = "🧠 **Oxlo-Sentinel Hivemind Activity:**\n"
                display_text += "\n".join(f"- {s}" for s in status_list)
                
                await queue.push(display_text)
                await queue.show_typing() # Show typing while waiting for the next node activity

            # --- Final Answer Composition ---
            # Node 5 (Synthesizer) will produce the final AIMessage
            if kind == "on_chat_model_end":
                # Could capture intermediate streaming tokens here for even more "live" feel
                pass

        # 5. Final Flush + Cleanup
        # (The synthesizer will have added the final Markdown AIMessage to the list)
        # We manually fetch the final output from the graph's terminal state
        final_output = await sentinel_graph.ainvoke(initial_state)
        
        final_answer = ""
        if final_output["messages"]:
            final_answer = final_output["messages"][-1].content

        # One final push to ensures the latest status is visible before the answer
        await queue.flush()
        
        # Send the finalized answer as a new message (or replace the status if you prefer)
        await message.answer(final_answer, parse_mode="Markdown")

    except Exception as e:
        # Global Error Handling for the Swarm
        error_text = f"❌ **Swarm Execution Error**\n\n{str(e)}"
        await queue.push(error_text)
        await queue.flush()
