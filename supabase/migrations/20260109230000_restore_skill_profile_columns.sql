-- ============================================================
-- Migration: user_skill_profiles 컬럼 복원 및 CF 뷰 업데이트
-- 2026-01-09
-- ============================================================
--
-- 목적:
-- 1. user_skill_profiles에 재계산 함수용 컬럼 복원
-- 2. cf_user_skill_vectors 뷰를 user_skill_profiles 기반으로 변경
--
-- 이유:
-- - recalculate_skill_profile_from_history 함수가 히스토리 기반 통계를 저장
-- - user_stats의 problems_solved는 정답만 카운트, skill_profiles는 분석용
-- ============================================================

-- ============================================================
-- 1. user_skill_profiles에 누락된 컬럼 추가
-- ============================================================

-- total_problems_attempted
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS total_problems_attempted INTEGER DEFAULT 0;

-- total_problems_solved
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS total_problems_solved INTEGER DEFAULT 0;

-- current_streak
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;

-- longest_streak
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;

-- common_error_patterns (LLM 분석 결과)
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS common_error_patterns TEXT[] DEFAULT '{}';

-- ============================================================
-- 2. 의존 뷰 삭제 (재생성 전)
-- ============================================================
DROP VIEW IF EXISTS public.cf_user_profiles CASCADE;
DROP VIEW IF EXISTS public.cf_user_skill_vectors CASCADE;

-- ============================================================
-- 3. cf_user_skill_vectors 뷰 재생성
-- user_skill_profiles 직접 사용 (user_stats 조인 제거)
-- ============================================================
CREATE OR REPLACE VIEW public.cf_user_skill_vectors AS
SELECT
    user_id,
    skill_by_topic,
    success_rate_by_difficulty,
    strong_topics,
    weak_topics,
    learning_style,
    total_problems_solved,
    total_problems_attempted,
    avg_solve_time_seconds,
    avg_hints_per_problem,
    current_streak,
    longest_streak,
    common_error_patterns,
    preferred_problem_type,
    preferred_language,
    stats_by_problem_type,
    recent_topics,
    recent_difficulties
FROM public.user_skill_profiles;

-- ============================================================
-- 4. cf_user_profiles 뷰 재생성
-- ============================================================
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
    usp.total_problems_attempted,
    usp.learning_style,
    usp.common_error_patterns,
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
-- 5. 권한 부여
-- ============================================================
GRANT SELECT ON public.cf_user_skill_vectors TO authenticated;
GRANT SELECT ON public.cf_user_profiles TO authenticated;
GRANT ALL ON public.cf_user_skill_vectors TO service_role;
GRANT ALL ON public.cf_user_profiles TO service_role;

-- ============================================================
-- 6. 코멘트
-- ============================================================
COMMENT ON VIEW public.cf_user_skill_vectors IS 'CF용 사용자 스킬 벡터 - user_skill_profiles 직접 참조 (2026-01-09 복원)';
COMMENT ON VIEW public.cf_user_profiles IS 'CF용 통합 사용자 프로필 - 하이브리드 CF (2026-01-09 업데이트)';

-- ============================================================
-- 완료 메시지
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE 'user_skill_profiles columns restored and CF views updated';
END $$;
