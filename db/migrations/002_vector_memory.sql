-- db/migrations/002_vector_memory.sql
-- Enables pgvector for long-term Logic Retrieval (RAG)

-- 1. Enable the vector extension (Requires Supabase/Postgres 15+)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Logic Memories Table
-- Stores successful "Golden Reasoning" scripts for future recall.
CREATE TABLE IF NOT EXISTS logic_memories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query      TEXT NOT NULL,
    logic_pattern   TEXT NOT NULL,    -- The compressed logical steps/SOP
    embedding       VECTOR(1536),     -- For OpenAI/Oxlo embeddings (1536 dims)
    problem_type    TEXT,             -- e.g. 'math', 'coding', 'logic'
    success_score   FLOAT DEFAULT 1.0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. HNSW Index for fast similarity search
CREATE INDEX ON logic_memories USING hnsw (embedding vector_cosine_ops);

-- 4. Audit Log Extension
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS logic_memory_id UUID REFERENCES logic_memories(id);

-- 5. Match Logic Memories Function (RPC for RAG)
CREATE OR REPLACE FUNCTION match_logic_memories (
  query_embedding VECTOR(1536),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id UUID,
  user_query TEXT,
  logic_pattern TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lm.id,
    lm.user_query,
    lm.logic_pattern,
    1 - (lm.embedding <=> query_embedding) AS similarity
  FROM logic_memories lm
  WHERE 1 - (lm.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
