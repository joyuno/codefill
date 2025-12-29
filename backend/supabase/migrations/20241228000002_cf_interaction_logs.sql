-- ============================================================
-- CodeFill: User-Problem Interaction Logs for CF
-- ============================================================
-- 추천 시스템(Collaborative Filtering) 학습을 위한 인터랙션 로그
-- 나중에 Matrix Factorization, Neural CF 등에 활용 가능
-- ============================================================

-- Step 1: Create interaction logs table
CREATE TABLE IF NOT EXISTS public.user_problem_interactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    problem_id TEXT NOT NULL,

    -- 행동 타입: view, attempt, solve, skip, bookmark, hint_request
    action_type VARCHAR(30) NOT NULL,

    -- 풀이 관련 메트릭
    is_correct BOOLEAN,
    time_spent_seconds INTEGER,
    attempt_count INTEGER DEFAULT 1,
    hint_used_count INTEGER DEFAULT 0,

    -- 문제 스냅샷 (풀 당시 상태 보존 - CF 학습 시 feature로 활용)
    problem_difficulty TEXT,
    problem_topics TEXT[],

    -- 컨텍스트
    source VARCHAR(50),  -- 'rag_search', 'recommendation', 'browse', 'similar_code', 'intent_chat'
    session_id UUID,

    -- 사용자 상태 스냅샷
    user_level VARCHAR(20),  -- 'beginner', 'intermediate', 'advanced'

    -- 추가 메타데이터 (확장용)
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 2: Create implicit rating view (CF 학습용)
-- action_type별 가중치로 implicit rating 계산
CREATE OR REPLACE VIEW public.cf_implicit_ratings AS
SELECT
    user_id,
    problem_id,
    -- Implicit rating 계산 (0-5 스케일)
    CASE action_type
        WHEN 'solve' THEN
            CASE
                WHEN is_correct AND hint_used_count = 0 THEN 5.0
                WHEN is_correct AND hint_used_count <= 2 THEN 4.5
                WHEN is_correct THEN 4.0
                ELSE 3.0  -- 틀렸지만 풀이 완료
            END
        WHEN 'bookmark' THEN 4.0
        WHEN 'attempt' THEN 2.5
        WHEN 'view' THEN 1.0
        WHEN 'hint_request' THEN 2.0
        WHEN 'skip' THEN 0.5
        ELSE 1.0
    END AS implicit_rating,
    action_type,
    problem_difficulty,
    problem_topics,
    time_spent_seconds,
    created_at
FROM public.user_problem_interactions;

-- Step 3: Create user-problem matrix view (CF 학습용)
-- 최신 상호작용만 유지, 중복 제거
CREATE OR REPLACE VIEW public.cf_user_problem_matrix AS
SELECT DISTINCT ON (user_id, problem_id)
    user_id,
    problem_id,
    implicit_rating,
    problem_difficulty,
    problem_topics,
    created_at
FROM public.cf_implicit_ratings
ORDER BY user_id, problem_id, created_at DESC;

-- Step 4: Create indexes for CF queries
-- User-based CF: 특정 유저의 모든 상호작용 조회
CREATE INDEX IF NOT EXISTS idx_interactions_user
ON public.user_problem_interactions(user_id, created_at DESC);

-- Item-based CF: 특정 문제의 모든 상호작용 조회
CREATE INDEX IF NOT EXISTS idx_interactions_problem
ON public.user_problem_interactions(problem_id, action_type);

-- 시간 기반 필터링 (최근 N일 데이터만 사용)
CREATE INDEX IF NOT EXISTS idx_interactions_time
ON public.user_problem_interactions(created_at DESC);

-- Source별 분석 (추천 성능 측정)
CREATE INDEX IF NOT EXISTS idx_interactions_source
ON public.user_problem_interactions(source, action_type);

-- 복합 인덱스 (유저-문제 조합 빠른 조회)
CREATE INDEX IF NOT EXISTS idx_interactions_user_problem
ON public.user_problem_interactions(user_id, problem_id, created_at DESC);

-- Step 5: Create helper functions

-- 유사 유저 찾기 (User-based CF 기반)
CREATE OR REPLACE FUNCTION public.find_similar_users(
    target_user_id UUID,
    min_common_problems INT DEFAULT 3,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    similar_user_id UUID,
    common_problem_count BIGINT,
    similarity_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH target_problems AS (
        SELECT DISTINCT problem_id, implicit_rating
        FROM public.cf_user_problem_matrix
        WHERE user_id = target_user_id
    ),
    other_users AS (
        SELECT
            m.user_id,
            COUNT(*) as common_count,
            -- Cosine similarity approximation
            SUM(t.implicit_rating * m.implicit_rating) /
            (SQRT(SUM(t.implicit_rating * t.implicit_rating)) *
             SQRT(SUM(m.implicit_rating * m.implicit_rating))) as similarity
        FROM public.cf_user_problem_matrix m
        JOIN target_problems t ON m.problem_id = t.problem_id
        WHERE m.user_id != target_user_id
        GROUP BY m.user_id
        HAVING COUNT(*) >= min_common_problems
    )
    SELECT
        user_id,
        common_count,
        similarity
    FROM other_users
    ORDER BY similarity DESC, common_count DESC
    LIMIT limit_count;
END;
$$;

-- 유저에게 추천할 문제 (CF 기반)
CREATE OR REPLACE FUNCTION public.recommend_problems_cf(
    target_user_id UUID,
    limit_count INT DEFAULT 5
)
RETURNS TABLE (
    problem_id TEXT,
    predicted_rating FLOAT,
    recommender_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH similar_users AS (
        SELECT similar_user_id, similarity_score
        FROM public.find_similar_users(target_user_id, 3, 20)
    ),
    user_solved AS (
        SELECT DISTINCT problem_id
        FROM public.cf_user_problem_matrix
        WHERE user_id = target_user_id
    ),
    recommendations AS (
        SELECT
            m.problem_id,
            SUM(m.implicit_rating * s.similarity_score) / SUM(s.similarity_score) as pred_rating,
            COUNT(DISTINCT m.user_id) as recommenders
        FROM public.cf_user_problem_matrix m
        JOIN similar_users s ON m.user_id = s.similar_user_id
        WHERE m.problem_id NOT IN (SELECT problem_id FROM user_solved)
          AND m.implicit_rating >= 3.5  -- 긍정적 상호작용만
        GROUP BY m.problem_id
    )
    SELECT
        r.problem_id,
        r.pred_rating,
        r.recommenders
    FROM recommendations r
    WHERE r.recommenders >= 2  -- 최소 2명 이상이 푼 문제
    ORDER BY r.pred_rating DESC, r.recommenders DESC
    LIMIT limit_count;
END;
$$;

-- Step 6: Create analytics helper views

-- 일별 활동 통계
CREATE OR REPLACE VIEW public.daily_interaction_stats AS
SELECT
    DATE(created_at) as date,
    action_type,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT problem_id) as unique_problems,
    AVG(time_spent_seconds) as avg_time_spent
FROM public.user_problem_interactions
GROUP BY DATE(created_at), action_type;

-- 추천 소스별 전환율
CREATE OR REPLACE VIEW public.recommendation_conversion AS
SELECT
    source,
    COUNT(*) FILTER (WHERE action_type = 'view') as views,
    COUNT(*) FILTER (WHERE action_type = 'attempt') as attempts,
    COUNT(*) FILTER (WHERE action_type = 'solve' AND is_correct) as solves,
    ROUND(
        COUNT(*) FILTER (WHERE action_type = 'solve' AND is_correct)::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE action_type = 'view'), 0) * 100,
        2
    ) as conversion_rate
FROM public.user_problem_interactions
WHERE source IS NOT NULL
GROUP BY source;

-- Step 7: RLS (Row Level Security)
ALTER TABLE public.user_problem_interactions ENABLE ROW LEVEL SECURITY;

-- 유저는 자신의 로그만 조회 가능
CREATE POLICY "Users can view own interactions"
ON public.user_problem_interactions
FOR SELECT
USING (auth.uid() = user_id);

-- 유저는 자신의 로그만 삽입 가능
CREATE POLICY "Users can insert own interactions"
ON public.user_problem_interactions
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Service role은 모든 작업 가능 (분석용)
CREATE POLICY "Service role full access"
ON public.user_problem_interactions
FOR ALL
USING (auth.role() = 'service_role');

-- Step 8: Grant permissions
GRANT SELECT ON public.user_problem_interactions TO authenticated;
GRANT INSERT ON public.user_problem_interactions TO authenticated;
GRANT SELECT ON public.cf_implicit_ratings TO authenticated;
GRANT SELECT ON public.cf_user_problem_matrix TO authenticated;
GRANT SELECT ON public.daily_interaction_stats TO authenticated;
GRANT SELECT ON public.recommendation_conversion TO authenticated;
GRANT EXECUTE ON FUNCTION public.find_similar_users TO authenticated;
GRANT EXECUTE ON FUNCTION public.recommend_problems_cf TO authenticated;

-- Service role 전체 권한
GRANT ALL ON public.user_problem_interactions TO service_role;
