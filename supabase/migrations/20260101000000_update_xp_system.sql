-- Update XP system: 2x level scaling and hint deduction
-- 레벨업 XP 2배 증가, 힌트 사용 시 XP 차감

-- Drop existing function
DROP FUNCTION IF EXISTS increment_user_stats(UUID, INTEGER, VARCHAR);

-- Recreate with new level calculation (2x scaling)
CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER,
    p_problem_type VARCHAR(20)
)
RETURNS VOID AS $$
DECLARE
    v_new_xp INTEGER;
    v_new_level INTEGER;
    v_xp_for_level INTEGER;
    v_remaining_xp INTEGER;
    v_current_date DATE := CURRENT_DATE;
BEGIN
    -- Update user_stats
    UPDATE user_stats
    SET
        total_xp = total_xp + p_xp,
        problems_solved = problems_solved + 1,
        blank_solved = CASE WHEN p_problem_type = 'blank' THEN blank_solved + 1 ELSE blank_solved END,
        bug_solved = CASE WHEN p_problem_type = 'bug' THEN bug_solved + 1 ELSE bug_solved END,
        output_solved = CASE WHEN p_problem_type = 'output' THEN output_solved + 1 ELSE output_solved END,
        refactor_solved = CASE WHEN p_problem_type = 'refactor' THEN refactor_solved + 1 ELSE refactor_solved END,
        -- Update streak
        current_streak = CASE
            WHEN last_activity_date = v_current_date - 1 THEN current_streak + 1
            WHEN last_activity_date = v_current_date THEN current_streak
            ELSE 1
        END,
        longest_streak = GREATEST(
            longest_streak,
            CASE
                WHEN last_activity_date = v_current_date - 1 THEN current_streak + 1
                WHEN last_activity_date = v_current_date THEN current_streak
                ELSE 1
            END
        ),
        last_activity_date = v_current_date
    WHERE user_id = p_user_id
    RETURNING total_xp INTO v_new_xp;

    -- Calculate new level (2x scaling: 100, 200, 400, 800...)
    -- Level 1: 0-99 XP, Level 2: 100-299 XP (need 200 more), Level 3: 300-699 XP (need 400 more)
    v_new_level := 1;
    v_remaining_xp := v_new_xp;
    v_xp_for_level := 100;  -- First level needs 100 XP

    WHILE v_remaining_xp >= v_xp_for_level LOOP
        v_remaining_xp := v_remaining_xp - v_xp_for_level;
        v_new_level := v_new_level + 1;
        v_xp_for_level := v_xp_for_level * 2;  -- 2x for next level
    END LOOP;

    -- Update level
    UPDATE user_stats
    SET level = v_new_level
    WHERE user_id = p_user_id;

    -- Update or insert daily activity
    INSERT INTO daily_activity (user_id, activity_date, problems_solved, xp_earned, blank_count, bug_count, output_count, refactor_count)
    VALUES (
        p_user_id,
        v_current_date,
        1,
        p_xp,
        CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'bug' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'output' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'refactor' THEN 1 ELSE 0 END
    )
    ON CONFLICT (user_id, activity_date)
    DO UPDATE SET
        problems_solved = daily_activity.problems_solved + 1,
        xp_earned = daily_activity.xp_earned + p_xp,
        blank_count = daily_activity.blank_count + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        bug_count = daily_activity.bug_count + CASE WHEN p_problem_type = 'bug' THEN 1 ELSE 0 END,
        output_count = daily_activity.output_count + CASE WHEN p_problem_type = 'output' THEN 1 ELSE 0 END,
        refactor_count = daily_activity.refactor_count + CASE WHEN p_problem_type = 'refactor' THEN 1 ELSE 0 END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Function to deduct XP for hint usage
-- Returns TRUE if successful, FALSE if not enough XP
CREATE OR REPLACE FUNCTION deduct_hint_xp(
    p_user_id UUID,
    p_xp_cost INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
BEGIN
    -- Get current XP and level
    SELECT total_xp, level INTO v_current_xp, v_current_level
    FROM user_stats
    WHERE user_id = p_user_id;

    -- Check if user has enough XP (can't go below 0 at level 1)
    IF v_current_level = 1 AND v_current_xp < p_xp_cost THEN
        RETURN FALSE;
    END IF;

    -- Deduct XP (minimum 0)
    UPDATE user_stats
    SET total_xp = GREATEST(0, total_xp - p_xp_cost)
    WHERE user_id = p_user_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Function to check if user can use hint
CREATE OR REPLACE FUNCTION can_use_hint(
    p_user_id UUID,
    p_xp_cost INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
BEGIN
    SELECT total_xp, level INTO v_current_xp, v_current_level
    FROM user_stats
    WHERE user_id = p_user_id;

    -- Level 1 with less than hint cost XP = can't use hint
    IF v_current_level = 1 AND v_current_xp < p_xp_cost THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
