# bot/main.py
"""
Oxlo-Sentinel: Main Entrypoint.
Initializes the Telegram bot, LangGraph cognitive swarm, and E2B sandbox.
Runs in Long-Polling mode as a Railway Background Worker.
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers.message_handler import router as main_router
from bot.middleware.rate_limiter import RateLimitMiddleware
from bot.middleware.session_loader import SessionLoaderMiddleware
from config.settings import settings
from mcp_server.tools.python_sandbox import _get_sandbox


async def on_startup(bot: Bot):
    """
    Called when the bot starts polling.
    Used for pre-warming the E2B sandbox microVM.
    """
    logging.info("🚀 Oxlo-Sentinel: Initializing Cognitive Core...")
    
    # Pre-warm the E2B sandbox to eliminate cold-start latency (~2s)
    # This prepares the environment before the first user message arrives.
    try:
        await _get_sandbox()
        logging.info("✅ [E2B] Secure Python Sandbox pre-warmed successfully.")
    except Exception as e:
        logging.error(f"❌ [E2B] Failed to pre-warm sandbox: {str(e)}")

    # Set bot commands for UX clarity
    commands = [
        {"command": "start", "description": "Initialize the Oxlo-Sentinel swarm"},
        {"command": "help", "description": "How to use the cognitive hivemind"},
    ]
    # In aiogram 3, we set commands via bot method (simplified for demo)
    # await bot.set_my_commands(...)


async def main():
    """
    Bootstrap the aiogram Bot and Dispatcher.
    Registers middleware and starts the long-polling event loop.
    """
    # 1. Initialize Bot & Dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # 2. Register Middleware (Sequential Execution)
    # Rate limiter first to protect the hivemind
    dp.message.middleware(RateLimitMiddleware())
    # Session loader second to enrich context
    dp.message.middleware(SessionLoaderMiddleware())

    # 3. Register Handlers
    dp.include_router(main_router)

    # 4. Starting the Polling Loop
    logging.info("📡 Oxlo-Sentinel: Listening for signals...")
    
    # Start the startup hook
    await on_startup(bot)

    try:
        # Start long-polling
        # skip_updates=True avoids backlogging old messages on restart
        await dp.start_polling(bot, skip_updates=True)
    finally:
        # Ensure we close the bot session on shutdown
        await bot.session.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Execute the event loop
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Oxlo-Sentinel: Shutdown complete.")
