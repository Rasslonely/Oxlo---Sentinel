# graph/concurrency.py
import asyncio
from config.settings import settings

# Global semaphore to manage Oxlo concurrency across all nodes.
# This prevents 429 errors on accounts with low concurrency limits.
oxlo_semaphore = asyncio.Semaphore(settings.RATE_LIMIT_PER_MINUTE) # We reuse this for basic throttling
# But specifically for concurrency:
oxlo_concurrency_semaphore = asyncio.Semaphore(getattr(settings, "OXLO_MAX_CONCURRENCY", 1))
