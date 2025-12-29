-- ============================================================
-- CodeFill RAG: pgvector Setup
-- ============================================================
-- This migration enables pgvector and creates the necessary tables
-- for embedding-based semantic search.
-- ============================================================

-- Step 1: Enable pgvector extension (already exists on Supabase in extensions schema)
-- The extension is pre-installed, we just need to enable it
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- Make vector type available without schema prefix
ALTER EXTENSION vector SET SCHEMA extensions;

-- Step 2: Create problem_embeddings table using extensions.vector type
CREATE TABLE IF NOT EXISTS public.problem_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    problem_id TEXT NOT NULL UNIQUE,
    embedding extensions.vector(1536),  -- OpenAI text-embedding-3-small dimension
    text_content TEXT,       -- Cached text used for embedding
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Step 3: Create index for fast similarity search
-- Using ivfflat index for approximate nearest neighbor search
-- Note: Index creation may be skipped if table has less than 100 rows (ivfflat minimum)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public.problem_embeddings LIMIT 1) THEN
        CREATE INDEX IF NOT EXISTS problem_embeddings_embedding_idx
        ON public.problem_embeddings
        USING ivfflat (embedding extensions.vector_cosine_ops)
        WITH (lists = 100);
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Index creation skipped: %', SQLERRM;
END;
$$;

-- Step 4: Create index on problem_id for fast lookups
CREATE INDEX IF NOT EXISTS problem_embeddings_problem_id_idx
ON public.problem_embeddings (problem_id);

-- Step 5: Create function for similarity search
CREATE OR REPLACE FUNCTION public.search_problems_by_embedding(
    query_embedding extensions.vector(1536),
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
        1 - (pe.embedding OPERATOR(extensions.<=>) query_embedding) as similarity
    FROM public.problem_embeddings pe
    WHERE 1 - (pe.embedding OPERATOR(extensions.<=>) query_embedding) > match_threshold
    ORDER BY pe.embedding OPERATOR(extensions.<=>) query_embedding
    LIMIT match_count;
END;
$$;

-- Step 6: Create function for hybrid search (vector + keyword)
CREATE OR REPLACE FUNCTION public.search_problems_hybrid(
    query_embedding extensions.vector(1536),
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
        1 - (pe.embedding OPERATOR(extensions.<=>) query_embedding) as similarity,
        (
            SELECT COUNT(*)::int
            FROM unnest(search_keywords) kw
            WHERE pe.text_content ILIKE '%' || kw || '%'
        ) as keyword_match_count
    FROM public.problem_embeddings pe
    LEFT JOIN public.base_problems bp ON pe.problem_id = bp.id
    WHERE 1 - (pe.embedding OPERATOR(extensions.<=>) query_embedding) > match_threshold
        AND (difficulty_filter IS NULL OR bp.difficulty = difficulty_filter)
    ORDER BY
        (1 - (pe.embedding OPERATOR(extensions.<=>) query_embedding)) * 0.7 +
        COALESCE((
            SELECT COUNT(*)::float / GREATEST(array_length(search_keywords, 1), 1)
            FROM unnest(search_keywords) kw
            WHERE pe.text_content ILIKE '%' || kw || '%'
        ), 0) * 0.3
        DESC
    LIMIT match_count;
END;
$$;

-- Step 7: Create trigger for updating updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if exists and create new one
DROP TRIGGER IF EXISTS update_problem_embeddings_updated_at ON public.problem_embeddings;
CREATE TRIGGER update_problem_embeddings_updated_at
    BEFORE UPDATE ON public.problem_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================
-- Grant permissions
-- ============================================================
GRANT SELECT ON public.problem_embeddings TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.search_problems_by_embedding TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.search_problems_hybrid TO anon, authenticated;

-- For service role (admin operations)
GRANT ALL ON public.problem_embeddings TO service_role;
