"""
RAG Service
Hybrid search (vector + keyword) and code generation fallback
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from ..database import get_supabase_client
from .embedding import embedding_service
from .openrouter import openrouter_service
from ..prompts import CODE_GEN_SYSTEM_PROMPT


class RAGService:
    """Service for RAG-based problem search and code generation."""

    # Similarity threshold for fallback to code generation
    SIMILARITY_THRESHOLD = 0.5  # Below this, trigger code generation

    def __init__(self):
        self.db = get_supabase_client()

    async def search_problems_hybrid(
        self,
        query: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Hybrid search combining vector similarity and keyword matching.

        Args:
            query: Search query text
            topics: Filter by topics
            difficulty: Filter by difficulty (easy/medium/hard)
            language: Filter by language (python/java/cpp)
            limit: Maximum results to return

        Returns:
            Tuple of (results, should_fallback_to_generation)
        """
        try:
            # Step 1: Generate query embedding
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 2: Perform vector search with RPC call
            # This assumes we have a Supabase function for similarity search
            response = self.db.rpc(
                "search_problems_by_embedding",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.3,
                    "match_count": limit * 2,  # Get more for filtering
                },
            ).execute()

            results = response.data or []

            # Step 3: Apply keyword filters
            filtered_results = self._apply_filters(
                results, topics, difficulty, language
            )

            # Step 4: Check if we should fallback to code generation
            should_fallback = False
            if not filtered_results:
                should_fallback = True
            elif filtered_results[0].get("similarity", 0) < self.SIMILARITY_THRESHOLD:
                should_fallback = True

            return filtered_results[:limit], should_fallback

        except Exception as e:
            print(f"Hybrid search error: {e}")
            # Fallback to keyword search
            return await self._keyword_search(topics, difficulty, language, limit), True

    async def _keyword_search(
        self,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Fallback keyword-based search.
        """
        try:
            query = self.db.table("base_problems").select("*")

            if difficulty:
                query = query.eq("difficulty", difficulty)

            if topics:
                # Use contains for array overlap
                query = query.contains("tags", topics)

            response = query.limit(limit).execute()
            return response.data or []

        except Exception as e:
            print(f"Keyword search error: {e}")
            return []

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply additional filters to search results.
        """
        filtered = results

        if difficulty:
            filtered = [r for r in filtered if r.get("difficulty") == difficulty]

        if topics:
            filtered = [
                r for r in filtered
                if any(t in r.get("tags", []) for t in topics)
            ]

        if language:
            filtered = [
                r for r in filtered
                if any(
                    s.get("language") == language
                    for s in r.get("solutions", [])
                )
            ]

        return filtered

    async def generate_problem_with_rag(
        self,
        user_request: Dict[str, Any],
        similar_problems: List[Dict[str, Any]],
        user_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate a new problem using RAG context from similar problems.

        Args:
            user_request: Collected info from chat agent
            similar_problems: Similar problems from vector search
            user_context: User onboarding data

        Returns:
            Generated problem data
        """
        user_context = user_context or {}

        # Format similar problems for context
        similar_context = []
        for p in similar_problems[:3]:  # Top 3 as context
            similar_context.append({
                "title": p.get("name", ""),
                "description": p.get("question", "")[:500],
                "tags": p.get("tags", []),
                "difficulty": p.get("difficulty", ""),
            })

        system_prompt = CODE_GEN_SYSTEM_PROMPT.format(
            user_request=json.dumps(user_request, ensure_ascii=False),
            similar_problems=json.dumps(similar_context, ensure_ascii=False),
            user_status=user_context.get("status", "unknown"),
            user_goal=user_context.get("goal", "unknown"),
            user_level=user_context.get("level", "intermediate"),
            strong_algorithms=", ".join(
                user_context.get("strong_algorithms", [])
            ) or "없음",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "사용자 요청에 맞는 교육용 코드를 생성해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="claude-sonnet",
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        return openrouter_service.parse_json_response(content)

    async def embed_and_store_problem(self, problem: Dict[str, Any]) -> bool:
        """
        Generate embedding for a problem and store it in the database.

        Args:
            problem: Problem data dictionary

        Returns:
            True if successful
        """
        try:
            # Create text for embedding
            text = embedding_service.create_problem_text_for_embedding(problem)

            # Generate embedding
            embedding = await embedding_service.generate_embedding(text)

            # Update problem with embedding
            problem_id = problem.get("id")
            if not problem_id:
                return False

            self.db.table("problem_embeddings").upsert({
                "problem_id": problem_id,
                "embedding": embedding,
                "text_content": text[:5000],  # Store truncated text
            }).execute()

            return True

        except Exception as e:
            print(f"Embed and store error for {problem.get('id')}: {e}")
            return False

    async def batch_embed_problems(
        self, problems: List[Dict[str, Any]], batch_size: int = 50
    ) -> Dict[str, int]:
        """
        Batch embed and store multiple problems.

        Args:
            problems: List of problem dictionaries
            batch_size: Number of problems per batch

        Returns:
            Dict with success and failure counts
        """
        success_count = 0
        fail_count = 0

        for i in range(0, len(problems), batch_size):
            batch = problems[i : i + batch_size]

            # Create texts for batch
            texts = [
                embedding_service.create_problem_text_for_embedding(p)
                for p in batch
            ]

            try:
                # Generate embeddings in batch
                embeddings = await embedding_service.generate_embeddings_batch(texts)

                # Store each embedding
                for j, problem in enumerate(batch):
                    try:
                        problem_id = problem.get("id")
                        if not problem_id:
                            fail_count += 1
                            continue

                        self.db.table("problem_embeddings").upsert({
                            "problem_id": problem_id,
                            "embedding": embeddings[j],
                            "text_content": texts[j][:5000],
                        }).execute()

                        success_count += 1

                    except Exception as e:
                        print(f"Store error for {problem.get('id')}: {e}")
                        fail_count += 1

            except Exception as e:
                print(f"Batch embedding error: {e}")
                fail_count += len(batch)

        return {"success": success_count, "failed": fail_count}


# Singleton instance
rag_service = RAGService()
