"""
RAG Service
Hybrid search (vector + keyword) and code generation fallback
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from ..database import get_supabase_client
from ..config import get_settings
from .embedding import embedding_service
from .openrouter import openrouter_service
from ..prompts import CODE_GEN_SYSTEM_PROMPT

# LLM 모델 설정
settings = get_settings()


class RAGService:
    """Service for RAG-based problem search and code generation."""

    # Similarity threshold for fallback to code generation
    SIMILARITY_THRESHOLD = 0.30  # Below this, trigger code generation

    # Topic mapping (Korean -> English variations)
    TOPIC_MAPPING = {
        "DP": ["Dynamic programming", "DP", "Memoization"],
        "동적 프로그래밍": ["Dynamic programming", "DP", "Memoization"],
        "이진 탐색": ["Binary search", "Divide and conquer", "Sorting"],
        "그래프": ["Graph algorithms", "Graph traversal", "BFS", "DFS"],
        "정렬": ["Sorting", "Implementation"],
        "문자열": ["String algorithms", "String"],
        "수학": ["Mathematics", "Number theory", "Math"],
        "그리디": ["Greedy algorithms", "Greedy"],
        "완전 탐색": ["Complete search", "Brute force", "Implementation"],
        "스택": ["Data structures", "Stack"],
        "큐": ["Data structures", "Queue"],
        "해시": ["Data structures", "Hash"],
        "트리": ["Tree algorithms", "Data structures"],
        "재귀": ["Recursion", "Divide and conquer"],
    }

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
        Hybrid search: Filter by tags/difficulty FIRST, then rank by vector similarity.

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
            # Step 1: Build base query with filters
            db_query = self.db.table("base_problems").select("*")

            # Apply difficulty filter
            if difficulty:
                db_query = db_query.eq("difficulty", difficulty)

            # Apply topic filter (using expanded topics)
            if topics:
                expanded_topics = self._expand_topics(topics)
                # Use overlaps for array intersection
                db_query = db_query.overlaps("tags", expanded_topics)

            # Limit to reasonable number for embedding comparison
            db_query = db_query.limit(100)
            filtered_response = db_query.execute()
            filtered_problems = filtered_response.data or []

            if not filtered_problems:
                # No matches with filters, try without difficulty
                if difficulty:
                    return await self._search_without_difficulty(query, topics, language, limit)
                return [], True

            # Step 2: Generate query embedding
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 3: Get embeddings for filtered problems and calculate similarity
            problem_ids = [p["id"] for p in filtered_problems]
            embeddings_response = self.db.table("problem_embeddings").select("problem_id, embedding").in_("problem_id", problem_ids).execute()

            # Parse embeddings (returned as strings from pgvector)
            embeddings_map = {}
            for e in (embeddings_response.data or []):
                emb = e["embedding"]
                if isinstance(emb, str):
                    emb = json.loads(emb)
                embeddings_map[e["problem_id"]] = emb

            # Calculate similarity and rank
            import numpy as np
            query_vec = np.array(query_embedding)

            results = []
            for problem in filtered_problems:
                pid = problem["id"]
                if pid in embeddings_map:
                    prob_vec = np.array(embeddings_map[pid])
                    similarity = float(np.dot(query_vec, prob_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(prob_vec)))
                    problem["similarity"] = similarity
                    results.append(problem)

            # Sort by similarity
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            # Step 4: Apply language filter if needed
            if language:
                results = [
                    r for r in results
                    if any(s.get("language") == language for s in r.get("solutions", []))
                ]

            # Step 5: Check fallback
            # If we have filtered results (by topic/difficulty), don't fallback
            # Only fallback if no results at all
            should_fallback = len(results) == 0

            return results[:limit], should_fallback

        except Exception as e:
            print(f"Hybrid search error: {e}")
            import traceback
            traceback.print_exc()
            return await self._keyword_search(topics, difficulty, language, limit), True

    async def _search_without_difficulty(
        self,
        query: str,
        topics: List[str],
        language: str,
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """Fallback search without difficulty filter."""
        try:
            db_query = self.db.table("base_problems").select("*")

            if topics:
                expanded_topics = self._expand_topics(topics)
                db_query = db_query.overlaps("tags", expanded_topics)

            db_query = db_query.limit(50)
            response = db_query.execute()
            problems = response.data or []

            if not problems:
                return [], True

            # Rank by embedding similarity
            query_embedding = await embedding_service.generate_embedding(query)
            problem_ids = [p["id"] for p in problems]
            embeddings_response = self.db.table("problem_embeddings").select("problem_id, embedding").in_("problem_id", problem_ids).execute()

            # Parse embeddings (returned as strings from pgvector)
            embeddings_map = {}
            for e in (embeddings_response.data or []):
                emb = e["embedding"]
                if isinstance(emb, str):
                    emb = json.loads(emb)
                embeddings_map[e["problem_id"]] = emb

            import numpy as np
            query_vec = np.array(query_embedding)

            results = []
            for problem in problems:
                pid = problem["id"]
                if pid in embeddings_map:
                    prob_vec = np.array(embeddings_map[pid])
                    similarity = float(np.dot(query_vec, prob_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(prob_vec)))
                    problem["similarity"] = similarity
                    results.append(problem)

            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            return results[:limit], len(results) == 0

        except Exception as e:
            print(f"Search without difficulty error: {e}")
            return [], True

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

    def _expand_topics(self, topics: List[str]) -> List[str]:
        """Expand Korean topics to English equivalents."""
        expanded = set()
        for topic in topics:
            topic_lower = topic.lower()
            # Add original
            expanded.add(topic)
            # Check mapping
            if topic in self.TOPIC_MAPPING:
                expanded.update(self.TOPIC_MAPPING[topic])
            # Also check lowercase
            for key, values in self.TOPIC_MAPPING.items():
                if key.lower() == topic_lower:
                    expanded.update(values)
        return list(expanded)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply additional filters to search results.
        Uses flexible matching for topics.
        """
        filtered = results

        if difficulty:
            filtered = [r for r in filtered if r.get("difficulty") == difficulty]

        if topics:
            # Expand topics to include English equivalents
            expanded_topics = self._expand_topics(topics)
            expanded_lower = [t.lower() for t in expanded_topics]

            filtered = [
                r for r in filtered
                if any(
                    tag.lower() in expanded_lower or
                    any(et.lower() in tag.lower() for et in expanded_topics)
                    for tag in r.get("tags", [])
                )
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
        print(f"[CodeGen] Starting generation...")
        print(f"[CodeGen] user_request: {user_request}")
        print(f"[CodeGen] Model: {settings.llm_model_code_gen}")

        user_context = user_context or {}

        # Format similar problems for context (question + solutions 포함)
        similar_context = []
        for p in similar_problems[:3]:  # Top 3 as context
            # solutions 코드 추출 (사용자가 선택한 언어 우선)
            solutions = p.get("solutions", [])
            solution_code = None
            preferred_lang = user_request.get("language", "python")

            # 선호 언어 코드 먼저 찾기
            for sol in solutions:
                if sol.get("language") == preferred_lang:
                    solution_code = sol.get("code", "")[:2000]  # 2000자 제한
                    break

            # 없으면 첫 번째 솔루션 사용
            if not solution_code and solutions:
                solution_code = solutions[0].get("code", "")[:2000]

            similar_context.append({
                "title": p.get("name", ""),
                "question": p.get("question", ""),  # 전체 question 전달
                "tags": p.get("tags", []),
                "difficulty": p.get("difficulty", ""),
                "solution_code": solution_code,  # 솔루션 코드 추가
                "solution_language": preferred_lang if solution_code else None,
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

        try:
            # Note: Claude doesn't support response_format, so we omit it
            # The prompt already instructs to output pure JSON
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_code_gen,
                messages=messages,
                temperature=0.7,
                max_tokens=8192,
                # response_format={"type": "json_object"},  # Not supported by Claude
            )

            content = openrouter_service.get_content(response)

            # Debug: print first 500 chars of response
            print(f"[CodeGen] LLM Response preview: {content[:500]}...")

            return openrouter_service.parse_json_response(content)

        except Exception as e:
            print(f"[CodeGen] Error type: {type(e).__name__}")
            print(f"[CodeGen] Error message: {e}")
            import traceback
            traceback.print_exc()
            raise

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
