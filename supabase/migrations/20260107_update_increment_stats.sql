-- =====================================================
-- Update increment_user_stats RPC
-- puzzle, guided, implementation 타입 및 난이도 지원 추가
-- p_difficulty는 DEFAULT NULL로 기존 호출과 호환 유지
-- =====================================================

CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER,
    p_problem_type VARCHAR(20),
    p_difficulty VARCHAR(20) DEFAULT NULL  -- 선택적, 기존 호출 호환
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
        -- 기존 문제 유형
        blank_solved = CASE WHEN p_problem_type = 'blank' THEN blank_solved + 1 ELSE blank_solved END,
        bug_solved = CASE WHEN p_problem_type = 'bug' THEN bug_solved + 1 ELSE bug_solved END,
        output_solved = CASE WHEN p_problem_type = 'output' THEN output_solved + 1 ELSE output_solved END,
        refactor_solved = CASE WHEN p_problem_type = 'refactor' THEN refactor_solved + 1 ELSE refactor_solved END,
        -- 새 문제 유형 (뱃지용)
        puzzle_solved = CASE WHEN p_problem_type = 'puzzle' THEN puzzle_solved + 1 ELSE puzzle_solved END,
        guided_solved = CASE WHEN p_problem_type = 'guided' THEN guided_solved + 1 ELSE guided_solved END,
        implementation_solved = CASE WHEN p_problem_type = 'implementation' THEN implementation_solved + 1 ELSE implementation_solved END,
        -- 난이도별 (NULL이면 스킵)
        easy_solved = CASE WHEN p_difficulty = 'easy' THEN easy_solved + 1 ELSE easy_solved END,
        medium_solved = CASE WHEN p_difficulty = 'medium' THEN medium_solved + 1 ELSE medium_solved END,
        hard_solved = CASE WHEN p_difficulty = 'hard' THEN hard_solved + 1 ELSE hard_solved END,
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

-- 검증: 함수 시그니처 확인
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE p.proname = 'increment_user_stats'
        AND n.nspname = 'public'
        AND array_length(p.proargtypes, 1) = 4
    ) THEN
        RAISE NOTICE 'increment_user_stats RPC updated successfully with 4 parameters';
    ELSE
        RAISE WARNING 'increment_user_stats function may not have been updated correctly';
    END IF;
END $$;
