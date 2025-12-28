#!/usr/bin/env python3
"""
Apply pgvector migration to Supabase database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Supabase PostgreSQL connection
# Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL not set, construct from Supabase credentials
if not DATABASE_URL:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    # Extract project ref from URL: https://[project-ref].supabase.co
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

    # For direct connection, we need the database password
    # This is typically the same as the service role key or set separately
    DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))

    # Supabase connection string format
    DATABASE_URL = f"postgresql://postgres.{project_ref}:{DB_PASSWORD}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

MIGRATION_SQL = """
-- ============================================================
-- CodeFill RAG: pgvector Setup
-- ============================================================

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create problem_embeddings table
CREATE TABLE IF NOT EXISTS problem_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    problem_id TEXT NOT NULL UNIQUE,
    embedding vector(1536),
    text_content TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Step 3: Create index for fast similarity search
CREATE INDEX IF NOT EXISTS problem_embeddings_embedding_idx
ON problem_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 4: Create index on problem_id
CREATE INDEX IF NOT EXISTS problem_embeddings_problem_id_idx
ON problem_embeddings (problem_id);

-- Step 5: Create similarity search function
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

-- Step 6: Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_problem_embeddings_updated_at ON problem_embeddings;
CREATE TRIGGER update_problem_embeddings_updated_at
    BEFORE UPDATE ON problem_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT ON problem_embeddings TO anon, authenticated;
GRANT EXECUTE ON FUNCTION search_problems_by_embedding TO anon, authenticated;
GRANT ALL ON problem_embeddings TO service_role;
"""

def apply_migration():
    print("Connecting to Supabase PostgreSQL...")
    print(f"Using project: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Executing migration SQL...")

        # Split and execute statements
        statements = [s.strip() for s in MIGRATION_SQL.split(';') if s.strip() and not s.strip().startswith('--')]

        for i, stmt in enumerate(statements):
            if stmt:
                try:
                    cursor.execute(stmt)
                    print(f"  [{i+1}/{len(statements)}] OK")
                except Exception as e:
                    print(f"  [{i+1}/{len(statements)}] Error: {e}")

        print("\nMigration completed!")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM problem_embeddings")
        count = cursor.fetchone()[0]
        print(f"problem_embeddings table exists with {count} rows")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Connection error: {e}")
        print("\nPlease run the SQL manually in Supabase Dashboard > SQL Editor")
        return False

    return True

if __name__ == "__main__":
    apply_migration()
