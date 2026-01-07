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
        exclude_ids: List[str] = None,
        user_context: Dict[str, Any] = None,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Hybrid search: Filter by tags/difficulty FIRST, then rank by vector similarity.

        Args:
            query: Search query text
            topics: Filter by topics
            difficulty: Filter by difficulty (easy/medium/hard)
            language: Filter by language (python/java/cpp)
            limit: Maximum results to return
            exclude_ids: Problem IDs to exclude (e.g., already solved)
            user_context: Personalization context (weak_topics, skill_levels, etc.)

        Returns:
            Tuple of (results, should_fallback_to_generation)
        """
        try:
            # Step 0: Enhance query with user context (personalization)
            enhanced_topics = topics or []
            if user_context:
                weak_topics = user_context.get("weak_topics", [])
                # Add weak topics to search if not already specified
                if weak_topics and not topics:
                    enhanced_topics = weak_topics[:2]
                # Adjust difficulty based on skill level if not specified
                if not difficulty and user_context.get("preferred_difficulty"):
                    difficulty = user_context["preferred_difficulty"]

            # Step 1: Build base query with filters
            db_query = self.db.table("base_problems").select("*")

            # Apply difficulty filter
            if difficulty:
                db_query = db_query.eq("difficulty", difficulty)

            # Apply topic filter (using expanded topics)
            if enhanced_topics:
                expanded_topics = self._expand_topics(enhanced_topics)
                # Use overlaps for array intersection
                db_query = db_query.overlaps("tags", expanded_topics)
            elif topics:
                expanded_topics = self._expand_topics(topics)
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

            # Step 5: Exclude already solved problems (personalization)
            if exclude_ids:
                exclude_set = set(exclude_ids)
                results = [r for r in results if r.get("id") not in exclude_set]

            # Step 6: Check fallback
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

    async def search_concepts(
        self,
        query: str,
        topics: List[str] = None,
        limit: int = 3,
        user_id: str = None,
    ) -> List[Dict[str, Any]]:
        """
        개념/문서 검색 (Agentic RAG Guided Tutor용)

        학생 질문에 관련된 개념 설명을 검색합니다.
        base_problems 테이블의 description을 활용합니다.

        Args:
            query: 검색 쿼리 (학생 질문)
            topics: 관련 주제
            limit: 최대 결과 수
            user_id: 사용자 ID (개인화용)

        Returns:
            관련 문서 목록 [{content, metadata, similarity}]
        """
        # 개인화 컨텍스트 조회 (옵션)
        user_context = None
        if user_id:
            try:
                from .personalization import get_personalization_service
                ps = get_personalization_service()
                user_context = await ps.get_rag_context(user_id)
            except Exception as e:
                print(f"[RAG:SearchConcepts] Personalization error: {e}")

        # 개인화 컨텍스트 기반 토픽 확장
        if user_context:
            # 약점 토픽을 우선적으로 검색
            if user_context.get("weak_topics"):
                topics = list(set((topics or []) + user_context["weak_topics"]))
            # 최근 학습 토픽도 추가
            if user_context.get("recent_topics"):
                topics = list(set((topics or []) + user_context["recent_topics"][:2]))
        try:
            # Step 1: Query embedding 생성
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 2: topics가 있으면 필터링
            if topics:
                expanded_topics = self._expand_topics(topics)
                # 필터링된 문제에서 검색
                db_query = self.db.table("base_problems").select(
                    "id, name, title, description, tags, difficulty"
                ).overlaps("tags", expanded_topics).limit(50)
            else:
                db_query = self.db.table("base_problems").select(
                    "id, name, title, description, tags, difficulty"
                ).limit(50)

            response = db_query.execute()
            problems = response.data or []

            if not problems:
                return []

            # Step 3: Embedding 유사도 계산
            problem_ids = [p["id"] for p in problems]
            embeddings_response = self.db.table("problem_embeddings").select(
                "problem_id, embedding"
            ).in_("problem_id", problem_ids).execute()

            embeddings_map = {}
            for e in (embeddings_response.data or []):
                try:
                    emb = e.get("embedding")
                    if isinstance(emb, str):
                        emb = json.loads(emb.replace("[", "[").replace("]", "]"))
                    embeddings_map[e["problem_id"]] = emb
                except Exception:
                    continue

            # Step 4: 유사도 계산 및 정렬
            results = []
            for p in problems:
                emb = embeddings_map.get(p["id"])
                if emb:
                    similarity = self._cosine_similarity(query_embedding, emb)
                else:
                    similarity = 0.3  # 기본값

                results.append({
                    "content": f"[{p.get('title', p.get('name', ''))}] {p.get('description', '')[:300]}",
                    "metadata": {
                        "id": p.get("id"),
                        "title": p.get("title") or p.get("name"),
                        "tags": p.get("tags", []),
                        "difficulty": p.get("difficulty"),
                    },
                    "similarity": similarity,
                })

            # 유사도 순 정렬
            results.sort(key=lambda x: x["similarity"], reverse=True)

            return results[:limit]

        except Exception as e:
            print(f"[RAG:SearchConcepts] Error: {e}")
            return []


    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    async def search_problems_personalized(
        self,
        query: str,
        user_id: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        개인화된 문제 검색

        사용자 학습 프로필을 기반으로 검색 결과를 개인화합니다.

        Args:
            query: 검색 쿼리
            user_id: 사용자 ID
            topics: 주제 필터
            difficulty: 난이도 필터
            language: 언어 필터
            limit: 결과 개수

        Returns:
            Tuple of (results, should_fallback)
        """
        # 1. 개인화 컨텍스트 조회
        user_context = None
        solved_problem_ids = []
        try:
            from .personalization import get_personalization_service
            ps = get_personalization_service()
            user_context = await ps.get_rag_context(user_id)

            # 이미 푼 문제 ID 목록 조회
            solved_ids_set = await ps._get_solved_problem_ids(user_id)
            solved_problem_ids = list(solved_ids_set)
        except Exception as e:
            print(f"[RAG:PersonalizedSearch] Personalization error: {e}")

        # 2. 난이도 조정 (지정되지 않았으면 선호 난이도 사용)
        if not difficulty and user_context:
            difficulty = user_context.get("preferred_difficulty")

        # 3. 토픽 확장 (약점 토픽 우선)
        if user_context:
            weak_topics = user_context.get("weak_topics", [])
            if weak_topics and not topics:
                # 약점 토픽 중 하나를 랜덤 선택
                import random
                topics = [random.choice(weak_topics)]

        # 4. 기본 하이브리드 검색 실행 (이미 푼 문제 제외)
        results, should_fallback = await self.search_problems_hybrid(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=limit * 2,  # 더 많이 가져와서 필터링
            exclude_ids=solved_problem_ids,  # 🔥 핵심: 이미 푼 문제 제외
            user_context=user_context,
        )

        if not results:
            return results, should_fallback

        # 5. 개인화 스코어링
        if user_context:
            for result in results:
                personalization_boost = 0.0
                result_tags = result.get("tags", [])
                result_difficulty = result.get("difficulty", "")

                # 약점 토픽 매칭 시 부스트
                weak_topics = user_context.get("weak_topics", [])
                if weak_topics and any(t in result_tags for t in weak_topics):
                    personalization_boost += 0.15

                # 선호 난이도 또는 한 단계 높은 난이도 매칭 시 부스트
                pref_diff = user_context.get("preferred_difficulty", "")
                if result_difficulty == pref_diff:
                    personalization_boost += 0.1
                elif self._is_next_difficulty(pref_diff, result_difficulty):
                    personalization_boost += 0.05

                # 최근 학습 토픽과 관련 시 부스트
                recent_topics = user_context.get("recent_topics", [])
                if recent_topics and any(t in result_tags for t in recent_topics):
                    personalization_boost += 0.05

                # 원본 유사도에 개인화 부스트 추가
                original_sim = result.get("similarity", 0.5)
                result["similarity"] = min(1.0, original_sim + personalization_boost)
                result["personalization_boost"] = personalization_boost

            # 재정렬
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        return results[:limit], should_fallback

    def _is_next_difficulty(self, current: str, target: str) -> bool:
        """target이 current의 다음 난이도인지 확인"""
        order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        try:
            curr_idx = order.index(current)
            tgt_idx = order.index(target)
            return tgt_idx == curr_idx + 1
        except ValueError:
            return False


# Singleton instance
rag_service = RAGService()
