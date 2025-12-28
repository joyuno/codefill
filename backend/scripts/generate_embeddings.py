"""
Generate embeddings for all base_problems and store in problem_embeddings table.
Uses OpenAI text-embedding-3-small model (1536 dimensions).
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client
from app.services.embedding import embedding_service


async def generate_embeddings_batch(batch_size: int = 50, start_offset: int = 0):
    """
    Generate embeddings for problems in batches.

    Args:
        batch_size: Number of problems per batch (OpenAI supports up to 2048)
        start_offset: Starting offset for resuming
    """
    db = get_supabase_client()

    # Get total count
    count_result = db.table('base_problems').select('id', count='exact').execute()
    total_count = count_result.count
    print(f"Total problems: {total_count}")

    # Get existing embeddings to skip
    existing = db.table('problem_embeddings').select('problem_id').execute()
    existing_ids = set(p['problem_id'] for p in existing.data)
    print(f"Existing embeddings: {len(existing_ids)}")

    success_count = 0
    error_count = 0
    offset = start_offset

    while offset < total_count:
        # Fetch batch of problems
        result = db.table('base_problems').select('*').range(offset, offset + batch_size - 1).execute()
        problems = result.data

        if not problems:
            break

        # Filter out already embedded problems
        problems_to_embed = [p for p in problems if p['id'] not in existing_ids]

        if not problems_to_embed:
            print(f"Batch {offset}-{offset+batch_size}: All already embedded, skipping")
            offset += batch_size
            continue

        print(f"\nBatch {offset}-{offset+batch_size}: Processing {len(problems_to_embed)} problems...")

        try:
            # Create texts for embedding
            texts = []
            for p in problems_to_embed:
                text = embedding_service.create_problem_text_for_embedding(p)
                # Truncate if too long (OpenAI limit is 8191 tokens)
                texts.append(text[:8000])

            # Generate embeddings in batch
            embeddings = await embedding_service.generate_embeddings_batch(texts, batch_size=50)

            # Store each embedding
            for i, problem in enumerate(problems_to_embed):
                try:
                    db.table('problem_embeddings').upsert({
                        'problem_id': problem['id'],
                        'embedding': embeddings[i],
                        'text_content': texts[i][:5000],  # Store truncated text
                    }).execute()
                    success_count += 1
                except Exception as e:
                    print(f"  Error storing {problem['id']}: {e}")
                    error_count += 1

            print(f"  Success: {len(problems_to_embed)}, Total: {success_count}")

        except Exception as e:
            print(f"  Batch error: {e}")
            error_count += len(problems_to_embed)

            # If rate limited, wait and retry
            if "rate" in str(e).lower():
                print("  Rate limited, waiting 60 seconds...")
                await asyncio.sleep(60)
                continue

        offset += batch_size

        # Small delay to avoid rate limiting
        await asyncio.sleep(1)

    print(f"\n=== Complete ===")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")

    return {"success": success_count, "errors": error_count}


async def main():
    # Parse arguments
    batch_size = 50
    start_offset = 0

    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_offset = int(sys.argv[2])

    print(f"Starting embedding generation...")
    print(f"Batch size: {batch_size}, Start offset: {start_offset}")

    await generate_embeddings_batch(batch_size, start_offset)


if __name__ == "__main__":
    asyncio.run(main())
