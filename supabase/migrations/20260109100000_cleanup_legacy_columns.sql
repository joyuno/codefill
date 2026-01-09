-- ============================================================
-- 레거시 컬럼 정리 마이그레이션
-- 2026-01-09
-- ============================================================
--
-- 목적:
-- 1. 레거시 문제 유형(bug, output, refactor) 관련 컬럼 삭제
-- 2. user_skill_profiles에서 user_stats와 중복되는 컬럼 삭제
-- 3. increment_user_stats 함수 업데이트
--
-- 삭제되는 컬럼:
-- - user_stats: bug_solved, output_solved, refactor_solved
-- - daily_activity: bug_count, output_count, refactor_count
-- - user_skill_profiles: total_problems_solved, total_problems_attempted,
--                        current_streak, longest_streak, total_xp_earned
-- ============================================================

-- ============================================================
-- 1. user_stats 테이블에서 레거시 컬럼 삭제
-- ============================================================
ALTER TABLE user_stats
    DROP COLUMN IF EXISTS bug_solved,
    DROP COLUMN IF EXISTS output_solved,
    DROP COLUMN IF EXISTS refactor_solved;

-- ============================================================
-- 2. daily_activity 테이블에서 레거시 컬럼 삭제
-- ============================================================
ALTER TABLE daily_activity
    DROP COLUMN IF EXISTS bug_count,
    DROP COLUMN IF EXISTS output_count,
    DROP COLUMN IF EXISTS refactor_count;

-- ============================================================
-- 3. user_skill_profiles에서 user_stats와 중복 컬럼 삭제
-- ============================================================
ALTER TABLE user_skill_profiles
    DROP COLUMN IF EXISTS total_problems_solved,
    DROP COLUMN IF EXISTS total_problems_attempted,
    DROP COLUMN IF EXISTS current_streak,
    DROP COLUMN IF EXISTS longest_streak,
    DROP COLUMN IF EXISTS total_xp_earned;

-- ============================================================
-- 4. increment_user_stats 함수 업데이트 (레거시 로직 제거)
-- ============================================================
CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER DEFAULT 0,
    p_problem_type VARCHAR DEFAULT 'blank',
    p_difficulty VARCHAR DEFAULT 'medium'
)
RETURNS VOID AS $$
DECLARE
    v_new_xp INTEGER;
    v_new_level INTEGER;
    v_total_solved INTEGER;
BEGIN
    -- user_stats 업데이트 (UPSERT)
    INSERT INTO user_stats (user_id, total_xp, level, problems_solved, problems_attempted, blank_solved, current_streak, longest_streak, last_activity_date)
    VALUES (p_user_id, p_xp, 1, 1, 1,
            CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
            1, 1, CURRENT_DATE)
    ON CONFLICT (user_id) DO UPDATE SET
        total_xp = user_stats.total_xp + p_xp,
        problems_solved = user_stats.problems_solved + 1,
        problems_attempted = user_stats.problems_attempted + 1,
        blank_solved = user_stats.blank_solved + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        current_streak = CASE
            WHEN user_stats.last_activity_date = CURRENT_DATE THEN user_stats.current_streak
            WHEN user_stats.last_activity_date = CURRENT_DATE - INTERVAL '1 day' THEN user_stats.current_streak + 1
            ELSE 1
        END,
        longest_streak = GREATEST(user_stats.longest_streak,
            CASE
                WHEN user_stats.last_activity_date = CURRENT_DATE THEN user_stats.current_streak
                WHEN user_stats.last_activity_date = CURRENT_DATE - INTERVAL '1 day' THEN user_stats.current_streak + 1
                ELSE 1
            END),
        last_activity_date = CURRENT_DATE,
        updated_at = NOW()
    RETURNING total_xp, problems_solved INTO v_new_xp, v_total_solved;

    -- 레벨 계산 (XP 기반)
    v_new_level := GREATEST(1, FLOOR(SQRT(v_new_xp / 100.0))::INTEGER + 1);

    -- 레벨 업데이트
    UPDATE user_stats
    SET level = v_new_level
    WHERE user_id = p_user_id AND level != v_new_level;

    -- daily_activity 업데이트 (UPSERT) - 레거시 컬럼 제거됨
    INSERT INTO daily_activity (user_id, activity_date, problems_solved, xp_earned, blank_count)
    VALUES (p_user_id, CURRENT_DATE, 1, p_xp,
            CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END)
    ON CONFLICT (user_id, activity_date) DO UPDATE SET
        problems_solved = daily_activity.problems_solved + 1,
        xp_earned = daily_activity.xp_earned + p_xp,
        blank_count = daily_activity.blank_count + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 5. daily_activity에 puzzle_count, guided_count 추가 (현재 문제 유형)
-- ============================================================
ALTER TABLE daily_activity
    ADD COLUMN IF NOT EXISTS puzzle_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS guided_count INTEGER DEFAULT 0;

-- ============================================================
-- 6. user_stats에 puzzle_solved, guided_solved 추가 (현재 문제 유형)
-- ============================================================
ALTER TABLE user_stats
    ADD COLUMN IF NOT EXISTS puzzle_solved INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS guided_solved INTEGER DEFAULT 0;

-- ============================================================
-- 7. increment_user_stats 최종 업데이트 (puzzle, guided 지원)
-- ============================================================
CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER DEFAULT 0,
    p_problem_type VARCHAR DEFAULT 'blank',
    p_difficulty VARCHAR DEFAULT 'medium'
)
RETURNS VOID AS $$
DECLARE
    v_new_xp INTEGER;
    v_new_level INTEGER;
    v_total_solved INTEGER;
BEGIN
    -- user_stats 업데이트 (UPSERT)
    INSERT INTO user_stats (
        user_id, total_xp, level, problems_solved, problems_attempted,
        blank_solved, puzzle_solved, guided_solved,
        current_streak, longest_streak, last_activity_date
    )
    VALUES (
        p_user_id, p_xp, 1, 1, 1,
        CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END,
        1, 1, CURRENT_DATE
    )
    ON CONFLICT (user_id) DO UPDATE SET
        total_xp = user_stats.total_xp + p_xp,
        problems_solved = user_stats.problems_solved + 1,
        problems_attempted = user_stats.problems_attempted + 1,
        blank_solved = user_stats.blank_solved + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        puzzle_solved = user_stats.puzzle_solved + CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        guided_solved = user_stats.guided_solved + CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END,
        current_streak = CASE
            WHEN user_stats.last_activity_date = CURRENT_DATE THEN user_stats.current_streak
            WHEN user_stats.last_activity_date = CURRENT_DATE - INTERVAL '1 day' THEN user_stats.current_streak + 1
            ELSE 1
        END,
        longest_streak = GREATEST(user_stats.longest_streak,
            CASE
                WHEN user_stats.last_activity_date = CURRENT_DATE THEN user_stats.current_streak
                WHEN user_stats.last_activity_date = CURRENT_DATE - INTERVAL '1 day' THEN user_stats.current_streak + 1
                ELSE 1
            END),
        last_activity_date = CURRENT_DATE,
        updated_at = NOW()
    RETURNING total_xp, problems_solved INTO v_new_xp, v_total_solved;

    -- 레벨 계산 (XP 기반)
    v_new_level := GREATEST(1, FLOOR(SQRT(v_new_xp / 100.0))::INTEGER + 1);

    -- 레벨 업데이트
    UPDATE user_stats
    SET level = v_new_level
    WHERE user_id = p_user_id AND level != v_new_level;

    -- daily_activity 업데이트 (UPSERT)
    INSERT INTO daily_activity (
        user_id, activity_date, problems_solved, xp_earned,
        blank_count, puzzle_count, guided_count
    )
    VALUES (
        p_user_id, CURRENT_DATE, 1, p_xp,
        CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END
    )
    ON CONFLICT (user_id, activity_date) DO UPDATE SET
        problems_solved = daily_activity.problems_solved + 1,
        xp_earned = daily_activity.xp_earned + p_xp,
        blank_count = daily_activity.blank_count + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        puzzle_count = daily_activity.puzzle_count + CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        guided_count = daily_activity.guided_count + CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 마이그레이션 완료 메시지
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE 'Legacy columns cleanup completed successfully';
    RAISE NOTICE 'Removed: user_stats (bug_solved, output_solved, refactor_solved)';
    RAISE NOTICE 'Removed: daily_activity (bug_count, output_count, refactor_count)';
    RAISE NOTICE 'Removed: user_skill_profiles (total_*, *_streak)';
    RAISE NOTICE 'Added: user_stats (puzzle_solved, guided_solved)';
    RAISE NOTICE 'Added: daily_activity (puzzle_count, guided_count)';
END $$;
