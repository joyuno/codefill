-- ============================================================
-- CodeFill RAG: pgvector Setup
-- ============================================================
-- This migration enables pgvector and creates the necessary tables
-- for embedding-based semantic search.
--
-- Run this in Supabase SQL Editor
-- ============================================================

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create problem_embeddings table
CREATE TABLE IF NOT EXISTS problem_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    problem_id TEXT NOT NULL UNIQUE,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
    text_content TEXT,       -- Cached text used for embedding
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Step 3: Create index for fast similarity search
-- Using ivfflat index for approximate nearest neighbor search
-- lists = sqrt(n) where n is expected row count (e.g., 100 for 10000 rows)
CREATE INDEX IF NOT EXISTS problem_embeddings_embedding_idx
ON problem_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 4: Create index on problem_id for fast lookups
CREATE INDEX IF NOT EXISTS problem_embeddings_problem_id_idx
ON problem_embeddings (problem_id);

-- Step 5: Create function for similarity search
CREATE OR REPLACE FUNCTION search_problems_by_embedding(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    problem_id TEXT,
    text_content TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pe.id,
        pe.problem_id,
        pe.text_content,
        1 - (pe.embedding <=> query_embedding) as similarity
    FROM problem_embeddings pe
    WHERE 1 - (pe.embedding <=> query_embedding) > match_threshold
    ORDER BY pe.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Step 6: Create function for hybrid search (vector + keyword)
CREATE OR REPLACE FUNCTION search_problems_hybrid(
    query_embedding vector(1536),
    search_keywords TEXT[] DEFAULT '{}',
    difficulty_filter TEXT DEFAULT NULL,
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    problem_id TEXT,
    text_content TEXT,
    similarity float,
    keyword_match_count int
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pe.id,
        pe.problem_id,
        pe.text_content,
        1 - (pe.embedding <=> query_embedding) as similarity,
        (
            SELECT COUNT(*)::int
            FROM unnest(search_keywords) kw
            WHERE pe.text_content ILIKE '%' || kw || '%'
        ) as keyword_match_count
    FROM problem_embeddings pe
    LEFT JOIN base_problems bp ON pe.problem_id = bp.id
    WHERE 1 - (pe.embedding <=> query_embedding) > match_threshold
        AND (difficulty_filter IS NULL OR bp.difficulty = difficulty_filter)
    ORDER BY
        -- Combine vector similarity and keyword matches
        (1 - (pe.embedding <=> query_embedding)) * 0.7 +
        COALESCE((
            SELECT COUNT(*)::float / GREATEST(array_length(search_keywords, 1), 1)
            FROM unnest(search_keywords) kw
            WHERE pe.text_content ILIKE '%' || kw || '%'
        ), 0) * 0.3
        DESC
    LIMIT match_count;
END;
$$;

-- Step 7: Create base_problems table if not exists (for reference)
CREATE TABLE IF NOT EXISTS base_problems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    question TEXT,
    question_html TEXT,
    difficulty TEXT,
    tags TEXT[],
    source TEXT,
    url TEXT,
    solutions JSONB,
    input_output JSONB,
    time_limit TEXT,
    memory_limit TEXT,
    original_id TEXT,
    acceptance_rate FLOAT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Step 8: Create indexes on base_problems
CREATE INDEX IF NOT EXISTS base_problems_difficulty_idx ON base_problems (difficulty);
CREATE INDEX IF NOT EXISTS base_problems_tags_idx ON base_problems USING GIN (tags);
CREATE INDEX IF NOT EXISTS base_problems_source_idx ON base_problems (source);

-- Step 9: Create trigger for updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_problem_embeddings_updated_at
    BEFORE UPDATE ON problem_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_base_problems_updated_at
    BEFORE UPDATE ON base_problems
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Grant permissions (adjust as needed)
-- ============================================================
GRANT SELECT ON problem_embeddings TO anon, authenticated;
GRANT SELECT ON base_problems TO anon, authenticated;
GRANT EXECUTE ON FUNCTION search_problems_by_embedding TO anon, authenticated;
GRANT EXECUTE ON FUNCTION search_problems_hybrid TO anon, authenticated;

-- For service role (admin operations)
GRANT ALL ON problem_embeddings TO service_role;
GRANT ALL ON base_problems TO service_role;
