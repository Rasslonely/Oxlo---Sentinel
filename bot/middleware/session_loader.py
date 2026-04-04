# bot/middleware/session_loader.py
from datetime import datetime
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from db.client import db
from db.models import TABLE_USERS, TABLE_SESSIONS


class SessionLoaderMiddleware(BaseMiddleware):
    """
    Auto-loads or creates User and Session records in the database.
    Injects `session_id` and `user_id` into the middleware data dictionary.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_info = event.from_user
        now = datetime.utcnow()

        # 1. Upsert User
        # (Using PostgreSQL ON CONFLICT for UPSERT)
        upsert_query = f"""
            INSERT INTO {TABLE_USERS} (telegram_id, username, display_name, last_active_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE SET
                username = EXCLUDED.username,
                display_name = EXCLUDED.display_name,
                last_active_at = EXCLUDED.last_active_at,
                request_count = {TABLE_USERS}.request_count + 1
            RETURNING id
        """
        user_uuid = await db.fetch_val(
            upsert_query,
            user_info.id,
            user_info.username,
            user_info.full_name,
            now
        )

        # 2. Start/Load Session
        # For simplicity, we create a new session for every message in this hackathon version
        # (Could be session-based using UUID persistence in state)
        session_id = str(uuid.uuid4())
        
        insert_session_query = f"""
            INSERT INTO {TABLE_SESSIONS} (id, user_id, started_at)
            VALUES ($1, $2, $3)
        """
        await db.execute(insert_session_query, session_id, user_uuid, now)

        # 3. Inject into context data
        data["user_uuid"] = user_uuid
        data["session_id"] = session_id

        return await handler(event, data)
