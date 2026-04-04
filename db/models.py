# db/models.py
"""
Data models for database interactions.
Using standard Python constants/enums for table and column names to ensure
consistency across the LangGraph nodes and Database client.
"""

# Table names
TABLE_USERS = "users"
TABLE_SESSIONS = "sessions"
TABLE_CHAT_HISTORY = "chat_history"
TABLE_AUDIT_LOGS = "audit_logs"
TABLE_RATE_LIMITS = "rate_limits"

# Role enums for chat_history
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"

# Route enums for audit_logs
ROUTE_CHAT = "chat"
ROUTE_COMPLEX = "complex"
