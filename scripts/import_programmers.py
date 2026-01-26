#!/usr/bin/env python3
"""
프로그래머스 문제 DB 임포트 스크립트

1. 이미지 파일 Supabase Storage에 업로드
2. base_problems 테이블에 459개 문제 삽입
3. programmers_embeddings 테이블 생성 및 임베딩 저장
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import uuid
import hashlib

# Supabase client
from supabase import create_client, Client

# OpenAI for embeddings
from openai import OpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# Configuration
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "programmers"
JSON_FILE = DATA_DIR / "problems_validated_solutions.json"
IMAGES_DIR = DATA_DIR / "images"

# Storage bucket name
STORAGE_BUCKET = "problem-images"

# ELO rating by difficulty
ELO_BY_DIFFICULTY = {
    "easy": 800,
    "medium": 1000,
    "medium_hard": 1200,
    "hard": 1400,
    "very_hard": 1600,
}

# Difficulty mapping (normalize medium_hard and very_hard)
DIFFICULTY_MAP = {
    "easy": "easy",
    "medium": "medium",
    "medium_hard": "hard",  # medium_hard -> hard for DB
    "hard": "hard",
    "very_hard": "hard",  # very_hard -> hard for DB (ELO will differentiate)
}


def init_clients():
    """Initialize Supabase and OpenAI clients"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    return supabase, openai_client


def load_problems():
    """Load problems from JSON file"""
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_storage_bucket(supabase: Client):
    """Ensure storage bucket exists"""
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]

        if STORAGE_BUCKET not in bucket_names:
            print(f"Creating storage bucket: {STORAGE_BUCKET}")
            supabase.storage.create_bucket(
                STORAGE_BUCKET,
                options={"public": True}
            )
        else:
            print(f"Storage bucket exists: {STORAGE_BUCKET}")
    except Exception as e:
        print(f"Warning: Could not check/create bucket: {e}")


def upload_images(supabase: Client, problems: list) -> dict:
    """
    Upload all images to Supabase Storage
    Returns: mapping of local_path -> storage_url
    """
    print("\n=== Uploading Images to Supabase Storage ===")

    image_url_map = {}
    total_images = 0
    uploaded = 0
    skipped = 0
    errors = 0

    # Count total images
    for p in problems:
        if p.get("images"):
            total_images += len(p["images"])

    print(f"Total images to process: {total_images}")

    for p in problems:
        if not p.get("images"):
            continue

        problem_id = p.get("original_id") or p["id"].replace("programmers_", "")

        for img in p["images"]:
            local_path = img.get("local_path")
            if not local_path:
                continue

            # Full path to image file
            full_path = IMAGES_DIR / local_path.replace("images/", "")

            if not full_path.exists():
                print(f"  Warning: Image not found: {full_path}")
                errors += 1
                continue

            # Storage path: programmers/{problem_id}/{filename}
            filename = full_path.name
            storage_path = f"programmers/{problem_id}/{filename}"

            try:
                # Check if already uploaded
                try:
                    existing = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
                    if existing:
                        image_url_map[local_path] = existing
                        skipped += 1
                        continue
                except:
                    pass

                # Read and upload file
                with open(full_path, "rb") as f:
                    file_data = f.read()

                # Determine content type
                ext = filename.lower().split(".")[-1]
                content_type = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "gif": "image/gif",
                    "webp": "image/webp",
                }.get(ext, "image/jpeg")

                # Upload
                result = supabase.storage.from_(STORAGE_BUCKET).upload(
                    storage_path,
                    file_data,
                    file_options={"content-type": content_type, "upsert": "true"}
                )

                # Get public URL
                public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
                image_url_map[local_path] = public_url
                uploaded += 1

                if uploaded % 50 == 0:
                    print(f"  Uploaded: {uploaded}/{total_images}")

            except Exception as e:
                print(f"  Error uploading {local_path}: {e}")
                errors += 1

    print(f"\nImage upload complete:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Errors: {errors}")

    return image_url_map


def process_question_html(question_html: str, images: list, image_url_map: dict) -> str:
    """
    Process question_html:
    - Replace image URLs with Supabase Storage URLs
    - Clean up HTML for better rendering
    """
    if not question_html:
        return ""

    result = question_html

    # Replace image URLs
    if images:
        for img in images:
            original_url = img.get("original_url", "")
            local_path = img.get("local_path", "")

            if local_path in image_url_map:
                new_url = image_url_map[local_path]
                # Replace both original URL and any relative path references
                if original_url:
                    result = result.replace(original_url, new_url)
                # Also try to replace by filename pattern
                filename = local_path.split("/")[-1]
                result = re.sub(
                    rf'src="[^"]*{re.escape(filename)}"',
                    f'src="{new_url}"',
                    result
                )

    return result


def convert_to_markdown_with_latex(question: str, question_html: str, images: list, image_url_map: dict) -> str:
    """
    Convert question to markdown with proper LaTeX support
    - Use question_html if available for better structure
    - Replace images with Supabase URLs
    - Handle LaTeX math expressions
    """
    # If we have HTML, convert it
    if question_html:
        # Process HTML to replace image URLs
        processed_html = process_question_html(question_html, images, image_url_map)

        # Convert HTML to markdown-ish format
        # Remove wrapper divs
        result = re.sub(r'<div[^>]*class="[^"]*guide-section[^"]*"[^>]*>', '', processed_html)
        result = re.sub(r'<h6[^>]*class="guide-section-title"[^>]*>([^<]+)</h6>', r'## \1\n', result)

        # Convert HTML tables to markdown
        result = re.sub(r'<table[^>]*>', '\n', result)
        result = re.sub(r'</table>', '\n', result)
        result = re.sub(r'<thead[^>]*>', '', result)
        result = re.sub(r'</thead>', '', result)
        result = re.sub(r'<tbody[^>]*>', '', result)
        result = re.sub(r'</tbody>', '', result)
        result = re.sub(r'<tr[^>]*>', '| ', result)
        result = re.sub(r'</tr>', ' |\n', result)
        result = re.sub(r'<th[^>]*>([^<]*)</th>', r'\1 | ', result)
        result = re.sub(r'<td[^>]*>([^<]*)</td>', r'\1 | ', result)

        # Convert lists
        result = re.sub(r'<ul[^>]*>', '\n', result)
        result = re.sub(r'</ul>', '\n', result)
        result = re.sub(r'<ol[^>]*>', '\n', result)
        result = re.sub(r'</ol>', '\n', result)
        result = re.sub(r'<li[^>]*>', '- ', result)
        result = re.sub(r'</li>', '\n', result)

        # Convert paragraphs and line breaks
        result = re.sub(r'<p[^>]*>', '\n', result)
        result = re.sub(r'</p>', '\n', result)
        result = re.sub(r'<br\s*/?>', '\n', result)

        # Convert code blocks
        result = re.sub(r'<pre[^>]*><code[^>]*>', '\n```\n', result)
        result = re.sub(r'</code></pre>', '\n```\n', result)
        result = re.sub(r'<code[^>]*>', '`', result)
        result = re.sub(r'</code>', '`', result)

        # Convert emphasis
        result = re.sub(r'<strong[^>]*>', '**', result)
        result = re.sub(r'</strong>', '**', result)
        result = re.sub(r'<em[^>]*>', '*', result)
        result = re.sub(r'</em>', '*', result)
        result = re.sub(r'<b[^>]*>', '**', result)
        result = re.sub(r'</b>', '**', result)

        # Keep images with updated URLs
        result = re.sub(r'<img[^>]*src="([^"]+)"[^>]*/>', r'![](\1)', result)
        result = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', r'![](\1)', result)

        # Remove remaining HTML tags
        result = re.sub(r'<[^>]+>', '', result)

        # Clean up whitespace
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = result.strip()

        return result

    # Fallback: use plain question text
    return question or ""


def insert_problems(supabase: Client, problems: list, image_url_map: dict):
    """Insert problems into base_problems table"""
    print("\n=== Inserting Problems into base_problems ===")

    inserted = 0
    updated = 0
    errors = 0

    for i, p in enumerate(problems):
        try:
            original_id = p.get("original_id") or p["id"].replace("programmers_", "")

            # Get difficulty and ELO
            raw_difficulty = p.get("difficulty", "medium")
            difficulty = DIFFICULTY_MAP.get(raw_difficulty, "medium")
            elo_rating = ELO_BY_DIFFICULTY.get(raw_difficulty, 1000)

            # Process question with images
            question = convert_to_markdown_with_latex(
                p.get("question", ""),
                p.get("question_html", ""),
                p.get("images", []),
                image_url_map
            )

            # Process question_html with image URLs replaced
            question_html = process_question_html(
                p.get("question_html", ""),
                p.get("images", []),
                image_url_map
            )

            # Build images array with Supabase URLs
            images_data = []
            if p.get("images"):
                for img in p["images"]:
                    local_path = img.get("local_path", "")
                    if local_path in image_url_map:
                        images_data.append({
                            "url": image_url_map[local_path],
                            "original_url": img.get("original_url", ""),
                        })

            # Parse input_output
            input_output = p.get("input_output")
            if isinstance(input_output, str):
                try:
                    input_output = json.loads(input_output)
                except:
                    input_output = {"inputs": [], "outputs": []}

            # Build record
            record = {
                "original_id": f"programmers_{original_id}",
                "name": p.get("name", f"프로그래머스 {original_id}"),
                "question": question,
                "question_html": question_html if question_html else None,
                "input_output": input_output,
                "difficulty": difficulty,
                "tags": p.get("tags") or [],
                "source": "programmers",
                "url": p.get("url"),
                "time_limit": p.get("time_limit"),
                "memory_limit": p.get("memory_limit"),
                "solutions": p.get("solutions", []),
                "images": images_data,
                "starter_code": p.get("starter_code"),
                "explanation": p.get("explanation"),
                "elo_rating": elo_rating,
                "like_count": 0,
                "solve_count": 0,
                "elo_update_count": 0,
            }

            # Upsert (insert or update)
            result = supabase.table("base_problems").upsert(
                record,
                on_conflict="original_id"
            ).execute()

            if result.data:
                inserted += 1

            if (i + 1) % 50 == 0:
                print(f"  Processed: {i + 1}/{len(problems)}")

        except Exception as e:
            print(f"  Error inserting problem {p.get('id')}: {e}")
            errors += 1

    print(f"\nProblem insertion complete:")
    print(f"  Inserted/Updated: {inserted}")
    print(f"  Errors: {errors}")


def create_programmers_embeddings_table(supabase: Client):
    """Create programmers_embeddings table if not exists"""
    print("\n=== Creating programmers_embeddings table ===")

    # Check if table exists
    check_sql = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'programmers_embeddings'
    );
    """

    result = supabase.rpc("exec_sql", {"query": check_sql}).execute()

    # Create table via migration
    create_sql = """
    -- Create programmers_embeddings table for RAG (code_gen agent)
    -- Separate from problem_embeddings to exclude from problem search

    CREATE TABLE IF NOT EXISTS programmers_embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        base_problem_id UUID NOT NULL REFERENCES base_problems(id) ON DELETE CASCADE,
        problem_id TEXT NOT NULL,
        embedding vector(1536),
        text_content TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(problem_id)
    );

    -- Create index for similarity search
    CREATE INDEX IF NOT EXISTS idx_programmers_embeddings_embedding
    ON programmers_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

    -- RLS policies
    ALTER TABLE programmers_embeddings ENABLE ROW LEVEL SECURITY;

    CREATE POLICY IF NOT EXISTS "Allow public read access on programmers_embeddings"
    ON programmers_embeddings FOR SELECT
    USING (true);

    CREATE POLICY IF NOT EXISTS "Allow service role full access on programmers_embeddings"
    ON programmers_embeddings FOR ALL
    USING (auth.role() = 'service_role');
    """

    print("Table creation should be done via migration. Skipping direct SQL execution.")
    print("Please run the migration manually if table doesn't exist.")


def generate_embeddings(openai_client: OpenAI, supabase: Client, problems: list):
    """Generate embeddings for programmers problems and store in programmers_embeddings"""
    if not openai_client:
        print("\n=== Skipping embeddings (no OpenAI API key) ===")
        return

    print("\n=== Generating Embeddings for programmers problems ===")

    generated = 0
    skipped = 0
    errors = 0

    for i, p in enumerate(problems):
        try:
            original_id = p.get("original_id") or p["id"].replace("programmers_", "")
            problem_id = f"programmers_{original_id}"

            # Check if embedding already exists
            existing = supabase.table("programmers_embeddings")\
                .select("id")\
                .eq("problem_id", problem_id)\
                .execute()

            if existing.data:
                skipped += 1
                continue

            # Get base_problem_id
            bp = supabase.table("base_problems")\
                .select("id")\
                .eq("original_id", problem_id)\
                .single()\
                .execute()

            if not bp.data:
                print(f"  Warning: base_problem not found for {problem_id}")
                errors += 1
                continue

            base_problem_id = bp.data["id"]

            # Prepare text content for embedding
            text_content = f"""
            Title: {p.get('name', '')}
            Difficulty: {p.get('difficulty', 'medium')}
            Tags: {', '.join(p.get('tags') or [])}

            Question:
            {p.get('question', '')}
            """

            # Generate embedding
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text_content[:8000]  # Limit input length
            )

            embedding = response.data[0].embedding

            # Insert into programmers_embeddings
            supabase.table("programmers_embeddings").insert({
                "base_problem_id": base_problem_id,
                "problem_id": problem_id,
                "embedding": embedding,
                "text_content": text_content[:5000],
            }).execute()

            generated += 1

            if (i + 1) % 20 == 0:
                print(f"  Generated: {generated}/{len(problems)} (skipped: {skipped})")

        except Exception as e:
            print(f"  Error generating embedding for {p.get('id')}: {e}")
            errors += 1

    print(f"\nEmbedding generation complete:")
    print(f"  Generated: {generated}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Errors: {errors}")


def remove_programmers_from_problem_embeddings(supabase: Client):
    """Remove programmers problems from problem_embeddings table"""
    print("\n=== Removing programmers from problem_embeddings ===")

    try:
        result = supabase.table("problem_embeddings")\
            .delete()\
            .like("problem_id", "programmers_%")\
            .execute()

        deleted = len(result.data) if result.data else 0
        print(f"  Deleted {deleted} programmers entries from problem_embeddings")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    print("=" * 60)
    print("프로그래머스 문제 DB 임포트")
    print("=" * 60)

    # Initialize clients
    supabase, openai_client = init_clients()

    # Load problems
    problems = load_problems()
    print(f"\nLoaded {len(problems)} problems from JSON")

    # Ensure storage bucket exists
    ensure_storage_bucket(supabase)

    # Step 1: Upload images
    image_url_map = upload_images(supabase, problems)

    # Step 2: Insert problems
    insert_problems(supabase, problems, image_url_map)

    # Step 3: Create programmers_embeddings table (via migration)
    # create_programmers_embeddings_table(supabase)

    # Step 4: Generate embeddings
    # generate_embeddings(openai_client, supabase, problems)

    # Step 5: Remove programmers from problem_embeddings
    # remove_programmers_from_problem_embeddings(supabase)

    print("\n" + "=" * 60)
    print("Import complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
