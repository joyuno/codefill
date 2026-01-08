-- ============================================================
-- Fix find_similar_users_hybrid function - column ambiguity
-- ============================================================

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
        SELECT
            ps.similar_user_id AS ps_user_id,
            ps.similarity_score AS ps_score
        FROM public.find_similar_users(target_user_id, 1, 50) ps
    ),
    skill_sim AS (
        SELECT
            ss.similar_user_id AS ss_user_id,
            ss.skill_similarity AS ss_score
        FROM public.find_similar_users_by_skill(target_user_id, 50) ss
    )
    SELECT
        COALESCE(p.ps_user_id, s.ss_user_id) AS similar_user_id,
        COALESCE(p.ps_score, 0)::DOUBLE PRECISION AS problem_similarity,
        COALESCE(s.ss_score, 0)::DOUBLE PRECISION AS skill_similarity,
        -- 가중 평균: 문제풀이 60%, 스킬 40%
        (COALESCE(p.ps_score, 0) * 0.6 +
         COALESCE(s.ss_score, 0) * 0.4)::DOUBLE PRECISION AS combined_score
    FROM problem_sim p
    FULL OUTER JOIN skill_sim s ON p.ps_user_id = s.ss_user_id
    WHERE COALESCE(p.ps_score, 0) > 0 OR COALESCE(s.ss_score, 0) > 0
    ORDER BY combined_score DESC
    LIMIT limit_count;
END;
$$;

GRANT EXECUTE ON FUNCTION public.find_similar_users_hybrid(UUID, INT) TO authenticated;
COMMENT ON FUNCTION public.find_similar_users_hybrid(UUID, INT) IS '하이브리드 유사 사용자 (문제풀이 60% + 스킬 40%)';
