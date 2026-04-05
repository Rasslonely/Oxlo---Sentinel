# bot/middleware/rate_limiter.py
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from db.client import db
from db.models import TABLE_RATE_LIMITS


class RateLimitMiddleware(BaseMiddleware):
    """
    Enforces a strict 5 requests per minute limit per user.
    Uses Supabase (PostgreSQL) for persistence to allow multi-instance persistence.
    """

    RATE_LIMIT_COUNT = 5
    WINDOW_SECONDS = 60

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        from datetime import timezone
        now = datetime.now(timezone.utc)

        # 1. Fetch current rate limit state
        # (Using raw SQL for atomic update or fetch)
        query = f"""
            SELECT window_start, request_count 
            FROM {TABLE_RATE_LIMITS} 
            WHERE telegram_id = $1
        """
        record = await db.fetch_one(query, user_id)

        if record:
            window_start = record['window_start']
            count = record['request_count']
            
            # Check if window has expired
            if now - window_start > timedelta(seconds=self.WINDOW_SECONDS):
                # Reset window
                await db.execute(
                    f"UPDATE {TABLE_RATE_LIMITS} SET window_start = $1, request_count = 1 WHERE telegram_id = $2",
                    now, user_id
                )
            else:
                # Still in window, check count
                if count >= self.RATE_LIMIT_COUNT:
                    await event.answer("⚠️ **Rate Limit Exceeded**\n\nPlease wait a moment before sending another request (Limit: 5/min).")
                    return
                # Increment count
                await db.execute(
                    f"UPDATE {TABLE_RATE_LIMITS} SET request_count = request_count + 1 WHERE telegram_id = $1",
                    user_id
                )
        else:
            # First time user, create record
            await db.execute(
                f"INSERT INTO {TABLE_RATE_LIMITS} (telegram_id, window_start, request_count) VALUES ($1, $2, 1)",
                user_id, now
            )

        return await handler(event, data)
