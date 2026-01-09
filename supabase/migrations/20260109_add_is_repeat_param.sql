-- =====================================================
-- Add p_is_repeat parameter to increment_user_stats
-- 2026-01-09
-- 반복 풀이 시 problems_solved 증가 방지
-- =====================================================

CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER DEFAULT 0,
    p_problem_type VARCHAR DEFAULT 'blank',
    p_difficulty VARCHAR DEFAULT 'medium',
    p_is_repeat BOOLEAN DEFAULT FALSE
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
        p_user_id, p_xp, 1,
        CASE WHEN p_is_repeat THEN 0 ELSE 1 END,  -- 반복이면 0
        1,
        CASE WHEN p_problem_type = 'blank' AND NOT p_is_repeat THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'puzzle' AND NOT p_is_repeat THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'guided' AND NOT p_is_repeat THEN 1 ELSE 0 END,
        1, 1, CURRENT_DATE
    )
    ON CONFLICT (user_id) DO UPDATE SET
        total_xp = user_stats.total_xp + p_xp,
        problems_solved = user_stats.problems_solved + CASE WHEN p_is_repeat THEN 0 ELSE 1 END,
        problems_attempted = user_stats.problems_attempted + 1,
        blank_solved = user_stats.blank_solved + CASE WHEN p_problem_type = 'blank' AND NOT p_is_repeat THEN 1 ELSE 0 END,
        puzzle_solved = user_stats.puzzle_solved + CASE WHEN p_problem_type = 'puzzle' AND NOT p_is_repeat THEN 1 ELSE 0 END,
        guided_solved = user_stats.guided_solved + CASE WHEN p_problem_type = 'guided' AND NOT p_is_repeat THEN 1 ELSE 0 END,
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
    -- 잔디는 반복 풀이도 기록 (활동 자체는 했으니까)
    INSERT INTO daily_activity (
        user_id, activity_date, problems_solved, xp_earned,
        blank_count, puzzle_count, guided_count
    )
    VALUES (
        p_user_id, CURRENT_DATE,
        CASE WHEN p_is_repeat THEN 0 ELSE 1 END,
        p_xp,
        CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END
    )
    ON CONFLICT (user_id, activity_date) DO UPDATE SET
        problems_solved = daily_activity.problems_solved + CASE WHEN p_is_repeat THEN 0 ELSE 1 END,
        xp_earned = daily_activity.xp_earned + p_xp,
        blank_count = daily_activity.blank_count + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        puzzle_count = daily_activity.puzzle_count + CASE WHEN p_problem_type = 'puzzle' THEN 1 ELSE 0 END,
        guided_count = daily_activity.guided_count + CASE WHEN p_problem_type = 'guided' THEN 1 ELSE 0 END;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
