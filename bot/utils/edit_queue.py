# bot/utils/edit_queue.py
"""
Debounced Telegram message editor.
Buffering status updates and flushing to Telegram at most once per 1.2 seconds.
Prevents reaching Telegram's rate limit for message edits.
"""
import asyncio
import time
from typing import Optional
from aiogram import Bot


class EditQueue:
    """
    Manages a debounced edit cycle for a single Telegram message.

    This ensures that frequent status updates from the LangGraph swarm
    don't overwhelm the Telegram Bot API or get throttled.
    """

    DEBOUNCE_INTERVAL = 1.2  # Telegram's per-message edit limit is ~1/sec

    def __init__(self, bot: Bot, chat_id: int, message_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self._pending_text: Optional[str] = None
        self._last_edit_time: float = 0.0
        self._lock = asyncio.Lock()

    async def push(self, text: str) -> None:
        """
        Queue a new status message. 
        If the debounce interval has passed, it flushes immediately.
        Otherwise, it buffers the latest text for the next flush.
        """
        async with self._lock:
            self._pending_text = text
            now = time.time()
            
            if now - self._last_edit_time >= self.DEBOUNCE_INTERVAL:
                await self._do_edit(text)

    async def flush(self) -> None:
        """
        Force-send the latest pending text immediately.
        Call this at the end of the graph execution to show the final state.
        """
        async with self._lock:
            if self._pending_text:
                await self._do_edit(self._pending_text)
                self._pending_text = None

    async def _do_edit(self, text: str) -> None:
        """The internal low-level edit call."""
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            self._last_edit_time = time.time()
        except Exception:
            # Silent fail on edit errors (e.g., message not modified or deleted)
            # This is standard for debounced status counters
            pass

    async def show_typing(self) -> None:
        """
        Send the 'typing' chat action to give a natural feel.
        """
        try:
            await self.bot.send_chat_action(
                chat_id=self.chat_id,
                action="typing"
            )
        except Exception:
            pass
