-- db/migrations/001_initial_schema.sql
-- Full production schema for Oxlo-Sentinel session tracking and audit logging.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── USERS ──────────────────────────────────────────────────────────────────
-- Track unique Telegram users and their activity.
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        TEXT,
    display_name    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_count   INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT telegram_id_positive CHECK (telegram_id > 0)
);

CREATE INDEX idx_users_telegram_id ON users (telegram_id);

-- ─── SESSIONS ───────────────────────────────────────────────────────────────
-- Track discrete conversation sessions per user.
CREATE TABLE IF NOT EXISTS sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    total_requests  INTEGER NOT NULL DEFAULT 0,
    oxlo_api_calls  INTEGER NOT NULL DEFAULT 0,   -- Track API usage for hackathon metrics

    CONSTRAINT positive_requests CHECK (total_requests >= 0),
    CONSTRAINT positive_api_calls CHECK (oxlo_api_calls >= 0)
);

-- ─── CHAT HISTORY ───────────────────────────────────────────────────────────
-- Store the full message log for context and retrieval.
CREATE TABLE IF NOT EXISTS chat_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    token_count     INTEGER,

    CONSTRAINT content_not_empty CHECK (length(trim(content)) > 0)
);

CREATE INDEX idx_chat_session_id ON chat_history (session_id, created_at);

-- ─── AUDIT LOGS ─────────────────────────────────────────────────────────────
-- Capture detailed swarm execution data for every request.
CREATE TABLE IF NOT EXISTS audit_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_query          TEXT NOT NULL,
    route               TEXT NOT NULL CHECK (route IN ('chat', 'complex')),
    audit_cycles        INTEGER NOT NULL DEFAULT 0,
    consensus_reached   BOOLEAN NOT NULL DEFAULT FALSE,
    sandbox_executed    BOOLEAN NOT NULL DEFAULT FALSE,
    sandbox_success     BOOLEAN,
    final_answer        TEXT,
    oxlo_calls_made     INTEGER NOT NULL DEFAULT 0,
    total_latency_ms    INTEGER,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT cycles_non_negative CHECK (audit_cycles >= 0),
    CONSTRAINT oxlo_calls_non_negative CHECK (oxlo_calls_made >= 0)
);

CREATE INDEX idx_audit_session ON audit_logs (session_id, created_at DESC);

-- ─── RATE LIMITING STATE ─────────────────────────────────────────────────────
-- Persistent store for rate-limiting windows.
CREATE TABLE IF NOT EXISTS rate_limits (
    telegram_id     BIGINT PRIMARY KEY,
    window_start    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_count   INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT count_positive CHECK (request_count > 0)
);
