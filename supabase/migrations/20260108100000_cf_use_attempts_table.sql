-- ============================================================
-- Hybrid CF System - 여러 테이블 기반 협업 필터링
-- 데이터 소스: attempts, user_skill_profiles, user_memories
-- ============================================================

-- ============================================================
-- Part 1: attempts 기반 User-Problem Matrix (Item-based CF)
-- ============================================================

DROP VIEW IF EXISTS cf_user_problem_matrix CASCADE;
DROP VIEW IF EXISTS cf_implicit_ratings CASCADE;

-- 1-1. Implicit Ratings (attempts에서 계산)
CREATE OR REPLACE VIEW public.cf_implicit_ratings AS
SELECT
    a.user_id,
    a.problem_id::TEXT AS problem_id,
    -- Implicit rating 계산 (0-5 스케일)
    CASE
        WHEN a.is_correct = true AND COALESCE(a.hints_used, 0) = 0 THEN 5.0
        WHEN a.is_correct = true AND COALESCE(a.hints_used, 0) <= 2 THEN 4.5
        WHEN a.is_correct = true THEN 4.0
        WHEN a.is_correct = false THEN 2.5  -- 시도했지만 실패
        ELSE 1.5  -- 진행 중
    END AS implicit_rating,
    CASE
        WHEN a.is_correct = true THEN 'solve'
        WHEN a.is_correct = false THEN 'failed_attempt'
        ELSE 'in_progress'
    END AS action_type,
    a.difficulty AS problem_difficulty,
    a.topics AS problem_topics,
    a.problem_type,
    a.time_spent AS time_spent_seconds,
    a.hints_used AS hint_used_count,
    a.created_at
FROM public.attempts a
WHERE a.problem_id IS NOT NULL;

-- 1-2. User-Problem Matrix (최신 상호작용만)
CREATE OR REPLACE VIEW public.cf_user_problem_matrix AS
SELECT DISTINCT ON (user_id, problem_id)
    user_id,
    problem_id,
    implicit_rating,
    action_type,
    problem_difficulty,
    problem_topics,
    problem_type,
    hint_used_count,
    time_spent_seconds,
    created_at
FROM public.cf_implicit_ratings
ORDER BY user_id, problem_id, created_at DESC;

-- ============================================================
-- Part 2: user_skill_profiles 기반 User Feature Similarity
-- ============================================================

-- 2-1. 사용자 스킬 벡터 뷰 (skill_by_topic JSONB를 펼침)
CREATE OR REPLACE VIEW public.cf_user_skill_vectors AS
SELECT
    user_id,
    skill_by_topic,
    success_rate_by_difficulty,
    strong_topics,
    weak_topics,
    learning_style,
    total_problems_solved,
    avg_solve_time_seconds,
    avg_hints_per_problem
FROM public.user_skill_profiles;

-- ============================================================
-- Part 3: user_memories 기반 Learning Context
-- ============================================================

-- 3-1. 사용자별 학습 컨텍스트 집계
CREATE OR REPLACE VIEW public.cf_user_learning_context AS
SELECT
    user_id,
    -- 학습한 개념들 (중복 제거, 최대 20개)
    (SELECT ARRAY_AGG(DISTINCT concept)
     FROM (
         SELECT UNNEST(concepts_learned) AS concept
         FROM public.user_memories m2
         WHERE m2.user_id = m.user_id
         LIMIT 100
     ) sub
     LIMIT 20
    ) AS all_concepts_learned,
    -- 어려워하는 개념들
    (SELECT ARRAY_AGG(DISTINCT concept)
     FROM (
         SELECT UNNEST(concepts_struggling) AS concept
         FROM public.user_memories m3
         WHERE m3.user_id = m.user_id
         LIMIT 100
     ) sub
     LIMIT 20
    ) AS all_concepts_struggling,
    -- 통계
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN was_successful THEN 1 ELSE 0 END) AS successful_sessions,
    AVG(hints_needed) AS avg_hints_needed,
    AVG(time_spent_seconds) AS avg_time_spent
FROM public.user_memories m
GROUP BY user_id;

-- ============================================================
-- Part 4: 통합 사용자 유사도 뷰
-- ============================================================

-- 4-1. 사용자 프로필 통합 뷰 (CF 계산용)
CREATE OR REPLACE VIEW public.cf_user_profiles AS
SELECT
    COALESCE(upm.user_id, usp.user_id, ulc.user_id) AS user_id,
    -- attempts 기반 데이터
    upm.problem_count,
    upm.avg_rating,
    -- skill_profiles 기반 데이터
    usp.skill_by_topic,
    usp.strong_topics,
    usp.weak_topics,
    usp.total_problems_solved,
    -- learning_context 기반 데이터
    ulc.all_concepts_learned,
    ulc.all_concepts_struggling,
    ulc.successful_sessions,
    ulc.avg_hints_needed
FROM (
    -- attempts 집계
    SELECT
        user_id,
        COUNT(DISTINCT problem_id) AS problem_count,
        AVG(implicit_rating) AS avg_rating
    FROM public.cf_user_problem_matrix
    GROUP BY user_id
) upm
FULL OUTER JOIN public.cf_user_skill_vectors usp ON upm.user_id = usp.user_id
FULL OUTER JOIN public.cf_user_learning_context ulc ON COALESCE(upm.user_id, usp.user_id) = ulc.user_id;

-- ============================================================
-- Part 5: 하이브리드 유사 사용자 찾기 함수들
-- ============================================================

-- 5-1. 스킬 기반 유사 사용자 찾기 (skill_by_topic JSONB 유사도)
DROP FUNCTION IF EXISTS public.find_similar_users_by_skill(UUID, INT);

CREATE OR REPLACE FUNCTION public.find_similar_users_by_skill(
    target_user_id UUID,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    similar_user_id UUID,
    skill_similarity DOUBLE PRECISION,
    common_topics INT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH target_skills AS (
        SELECT skill_by_topic
        FROM public.user_skill_profiles
        WHERE user_id = target_user_id
    ),
    other_users AS (
        SELECT
            usp.user_id AS other_user_id,
            -- JSONB 키 교집합 수
            (SELECT COUNT(*)
             FROM jsonb_object_keys(usp.skill_by_topic) k
             WHERE (SELECT skill_by_topic FROM target_skills) ? k
            ) AS common_topic_count,
            -- 평균 스킬 차이 (작을수록 유사)
            (SELECT AVG(ABS(
                COALESCE((usp.skill_by_topic->>k)::FLOAT, 0) -
                COALESCE(((SELECT skill_by_topic FROM target_skills)->>k)::FLOAT, 0)
            ))
             FROM jsonb_object_keys(usp.skill_by_topic) k
            ) AS avg_skill_diff
        FROM public.user_skill_profiles usp
        WHERE usp.user_id != target_user_id
          AND usp.skill_by_topic IS NOT NULL
          AND jsonb_typeof(usp.skill_by_topic) = 'object'
    )
    SELECT
        ou.other_user_id,
        -- 유사도 = 1 - 평균차이 (0~1 스케일)
        GREATEST(0, 1 - COALESCE(ou.avg_skill_diff, 1))::DOUBLE PRECISION AS skill_sim,
        ou.common_topic_count::INT
    FROM other_users ou
    WHERE ou.common_topic_count > 0
    ORDER BY skill_sim DESC, ou.common_topic_count DESC
    LIMIT limit_count;
END;
$$;

-- 5-2. 문제 풀이 기반 유사 사용자 찾기 (기존 Item-based CF)
DROP FUNCTION IF EXISTS public.find_similar_users(UUID, INT, INT);

CREATE OR REPLACE FUNCTION public.find_similar_users(
    target_user_id UUID,
    min_common_problems INT DEFAULT 1,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    similar_user_id UUID,
    common_problem_count BIGINT,
    similarity_score DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH target_problems AS (
        SELECT DISTINCT m.problem_id, m.implicit_rating
        FROM public.cf_user_problem_matrix m
        WHERE m.user_id = target_user_id
    ),
    other_users AS (
        SELECT
            m.user_id AS other_user_id,
            COUNT(*) AS common_count,
            -- Cosine similarity
            CASE
                WHEN SQRT(SUM(t.implicit_rating * t.implicit_rating)) *
                     SQRT(SUM(m.implicit_rating * m.implicit_rating)) = 0 THEN 0
                ELSE SUM(t.implicit_rating * m.implicit_rating) /
                     (SQRT(SUM(t.implicit_rating * t.implicit_rating)) *
                      SQRT(SUM(m.implicit_rating * m.implicit_rating)))
            END AS similarity
        FROM public.cf_user_problem_matrix m
        JOIN target_problems t ON m.problem_id = t.problem_id
        WHERE m.user_id != target_user_id
        GROUP BY m.user_id
        HAVING COUNT(*) >= min_common_problems
    )
    SELECT
        ou.other_user_id,
        ou.common_count,
        COALESCE(ou.similarity, 0)::DOUBLE PRECISION
    FROM other_users ou
    WHERE ou.similarity > 0 OR ou.common_count >= min_common_problems
    ORDER BY ou.similarity DESC NULLS LAST, ou.common_count DESC
    LIMIT limit_count;
END;
$$;

-- 5-3. 하이브리드 유사 사용자 찾기 (문제풀이 + 스킬 통합)
DROP FUNCTION IF EXISTS public.find_similar_users_hybrid(UUID, INT);

CREATE OR REPLACE FUNCTION public.find_similar_users_hybrid(
    target_user_id UUID,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    similar_user_id UUID,
    problem_similarity DOUBLE PRECISION,
    skill_similarity DOUBLE PRECISION,
    combined_score DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH problem_sim AS (
        SELECT similar_user_id, similarity_score
        FROM public.find_similar_users(target_user_id, 1, 50)
    ),
    skill_sim AS (
        SELECT similar_user_id, skill_similarity
        FROM public.find_similar_users_by_skill(target_user_id, 50)
    )
    SELECT
        COALESCE(p.similar_user_id, s.similar_user_id) AS sim_user_id,
        COALESCE(p.similarity_score, 0)::DOUBLE PRECISION AS prob_sim,
        COALESCE(s.skill_similarity, 0)::DOUBLE PRECISION AS skill_sim,
        -- 가중 평균: 문제풀이 60%, 스킬 40%
        (COALESCE(p.similarity_score, 0) * 0.6 +
         COALESCE(s.skill_similarity, 0) * 0.4)::DOUBLE PRECISION AS combined
    FROM problem_sim p
    FULL OUTER JOIN skill_sim s ON p.similar_user_id = s.similar_user_id
    WHERE COALESCE(p.similarity_score, 0) > 0 OR COALESCE(s.skill_similarity, 0) > 0
    ORDER BY combined DESC
    LIMIT limit_count;
END;
$$;

-- Step 4: recommend_problems_cf 함수 수정
DROP FUNCTION IF EXISTS public.recommend_problems_cf(UUID, INT);

CREATE OR REPLACE FUNCTION public.recommend_problems_cf(
    target_user_id UUID,
    limit_count INT DEFAULT 5
)
RETURNS TABLE (
    recommended_problem_id TEXT,
    predicted_rating DOUBLE PRECISION,
    recommender_count BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH similar_users AS (
        SELECT su.similar_user_id, su.similarity_score
        FROM public.find_similar_users(target_user_id, 2, 20) su
    ),
    user_solved AS (
        SELECT DISTINCT m.problem_id
        FROM public.cf_user_problem_matrix m
        WHERE m.user_id = target_user_id
    ),
    recommendations AS (
        SELECT
            m.problem_id AS rec_problem_id,
            CASE
                WHEN SUM(s.similarity_score) = 0 THEN 0
                ELSE SUM(m.implicit_rating * s.similarity_score) / SUM(s.similarity_score)
            END AS pred_rating,
            COUNT(DISTINCT m.user_id) AS recommenders
        FROM public.cf_user_problem_matrix m
        JOIN similar_users s ON m.user_id = s.similar_user_id
        WHERE m.problem_id NOT IN (SELECT us.problem_id FROM user_solved us)
          AND m.implicit_rating >= 3.5  -- 긍정적 상호작용만
        GROUP BY m.problem_id
    )
    SELECT
        r.rec_problem_id,
        r.pred_rating,
        r.recommenders
    FROM recommendations r
    WHERE r.recommenders >= 1  -- 최소 1명 이상이 푼 문제
    ORDER BY r.pred_rating DESC, r.recommenders DESC
    LIMIT limit_count;
END;
$$;

-- Step 5: daily_interaction_stats 뷰 수정 (attempts 기반)
DROP VIEW IF EXISTS public.daily_interaction_stats;

CREATE OR REPLACE VIEW public.daily_interaction_stats AS
SELECT
    DATE(a.created_at) AS date,
    CASE
        WHEN a.is_correct = true THEN 'solve'
        WHEN a.is_correct = false THEN 'attempt'
        ELSE 'in_progress'
    END AS action_type,
    COUNT(*) AS count,
    COUNT(DISTINCT a.user_id) AS unique_users,
    COUNT(DISTINCT a.problem_id) AS unique_problems,
    AVG(a.time_spent) AS avg_time_spent,
    AVG(a.hints_used) AS avg_hints_used,
    SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END)::FLOAT /
        NULLIF(COUNT(*), 0) * 100 AS success_rate
FROM public.attempts a
WHERE a.problem_id IS NOT NULL
GROUP BY DATE(a.created_at),
    CASE
        WHEN a.is_correct = true THEN 'solve'
        WHEN a.is_correct = false THEN 'attempt'
        ELSE 'in_progress'
    END;

-- Step 6: recommendation_conversion은 source 컬럼이 없으므로 단순화
DROP VIEW IF EXISTS public.recommendation_conversion;

CREATE OR REPLACE VIEW public.recommendation_conversion AS
SELECT
    a.difficulty AS source,  -- difficulty를 source처럼 사용
    COUNT(*) FILTER (WHERE a.is_correct IS NULL) AS in_progress,
    COUNT(*) FILTER (WHERE a.is_correct = false) AS attempts,
    COUNT(*) FILTER (WHERE a.is_correct = true) AS solves,
    ROUND(
        COUNT(*) FILTER (WHERE a.is_correct = true)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS conversion_rate
FROM public.attempts a
WHERE a.problem_id IS NOT NULL
GROUP BY a.difficulty;

-- ============================================================
-- Part 6: 권한 부여
-- ============================================================

-- Views
GRANT SELECT ON public.cf_implicit_ratings TO authenticated;
GRANT SELECT ON public.cf_user_problem_matrix TO authenticated;
GRANT SELECT ON public.cf_user_skill_vectors TO authenticated;
GRANT SELECT ON public.cf_user_learning_context TO authenticated;
GRANT SELECT ON public.cf_user_profiles TO authenticated;
GRANT SELECT ON public.daily_interaction_stats TO authenticated;
GRANT SELECT ON public.recommendation_conversion TO authenticated;

-- Functions (with specific signatures)
GRANT EXECUTE ON FUNCTION public.find_similar_users(UUID, INT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.find_similar_users_by_skill(UUID, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.find_similar_users_hybrid(UUID, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.recommend_problems_cf(UUID, INT) TO authenticated;

-- Service role 전체 권한
GRANT ALL ON public.cf_implicit_ratings TO service_role;
GRANT ALL ON public.cf_user_problem_matrix TO service_role;
GRANT ALL ON public.cf_user_skill_vectors TO service_role;
GRANT ALL ON public.cf_user_learning_context TO service_role;
GRANT ALL ON public.cf_user_profiles TO service_role;
GRANT ALL ON public.daily_interaction_stats TO service_role;
GRANT ALL ON public.recommendation_conversion TO service_role;

-- ============================================================
-- Part 7: 코멘트
-- ============================================================

COMMENT ON VIEW public.cf_implicit_ratings IS 'CF용 implicit rating - attempts 테이블 기반 (2026-01-08)';
COMMENT ON VIEW public.cf_user_problem_matrix IS 'CF용 user-problem 매트릭스 - 최신 상호작용만';
COMMENT ON VIEW public.cf_user_skill_vectors IS 'CF용 사용자 스킬 벡터 - user_skill_profiles 기반';
COMMENT ON VIEW public.cf_user_learning_context IS 'CF용 학습 컨텍스트 - user_memories 기반';
COMMENT ON VIEW public.cf_user_profiles IS 'CF용 통합 사용자 프로필 - 하이브리드 CF';
COMMENT ON FUNCTION public.find_similar_users(UUID, INT, INT) IS '문제 풀이 기반 유사 사용자 (Item-based CF)';
COMMENT ON FUNCTION public.find_similar_users_by_skill(UUID, INT) IS '스킬 프로필 기반 유사 사용자';
COMMENT ON FUNCTION public.find_similar_users_hybrid(UUID, INT) IS '하이브리드 유사 사용자 (문제풀이 60% + 스킬 40%)';
COMMENT ON FUNCTION public.recommend_problems_cf(UUID, INT) IS 'CF 기반 문제 추천';

-- ============================================================
-- Part 8: user_problem_interactions 테이블은 유지 (나중에 데이터 넣을 수도)
-- 단, 현재는 attempts 기반 CF를 사용
-- ============================================================

-- 기존 user_problem_interactions는 삭제하지 않음
-- 나중에 view/skip/bookmark 같은 추가 행동 추적 시 활용 가능
