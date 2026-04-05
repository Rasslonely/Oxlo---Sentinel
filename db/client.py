# db/client.py
import asyncpg
import asyncio
from typing import Optional
from config.settings import settings


class Database:
    """
    Singleton database manager using asyncpg connection pool.
    Handles efficient connections for asynchronous bot requests.
    """
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """
        Lazily initialize and return the asyncpg connection pool.
        """
        if cls._pool is None:
            if settings is None or not settings.DATABASE_URL:
                raise ValueError("DATABASE_URL must be configured.")
            
            cls._pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                max_inactive_connection_lifetime=300.0,
                statement_cache_size=0, # Required for PgBouncer / Supabase Pooler
            )
        return cls._pool

    @classmethod
    async def disconnect(cls):
        """Close the connection pool cleanly."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    async def fetch_one(cls, query: str, *args):
        """Fetch a single record from the database."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    @classmethod
    async def fetch_all(cls, query: str, *args):
        """Fetch all records matching the query."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    @classmethod
    async def fetch_val(cls, query: str, *args):
        """Fetch a single value from the database (first column of the first row)."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @classmethod
    async def execute(cls, query: str, *args):
        """Execute a command (INSERT, UPDATE, DELETE)."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)


# Singleton instance for simple import
db = Database()

# --- Supabase Client (For High-Level RAG / Vector Ops) ---
from supabase import create_client, Client
if settings and settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
else:
    supabase = None
