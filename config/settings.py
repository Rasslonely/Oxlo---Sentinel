# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    All application secrets loaded from environment variables using Pydantic.
    Validation happens at startup to ensure all required vars exist.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str

    # --- Oxlo AI Platform ---
    OXLO_API_KEY: str
    OXLO_BASE_URL: str = "https://api.oxlo.ai/v1"

    # --- E2B Code Interpreter ---
    E2B_API_KEY: str

    # --- Supabase / PostgreSQL ---
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    DATABASE_URL: str            # Full asyncpg-compatible connection string

    # --- Runtime Tuning ---
    MAX_AUDIT_CYCLES: int = 3
    RATE_LIMIT_PER_MINUTE: int = 5
    SANDBOX_TTL_SECONDS: int = 600
    LOG_LEVEL: str = "INFO"


# Singleton instance for the entire app
# Validation happens immediately upon import. 
# If any required ENV var is missing, the app will crash with a detailed Pydantic error.
settings = Settings()
