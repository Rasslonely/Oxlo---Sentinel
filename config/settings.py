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
try:
    settings = Settings()
except Exception as e:
    # This will catch missing .env or missing variables at startup
    print(f"ERROR: Configuration validation failed: {e}")
    # In production, we want to fail fast. 
    # For now, we provide the singleton for import, but it will error on use if validation fails.
    # We will handle the actual validation check in bot/main.py or similar entrypoint.
    settings = None
