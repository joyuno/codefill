-- =====================================================
-- Fix level calculation formula
-- DB 레벨업 공식을 프론트엔드와 일치시킴
-- 기존: 2x 스케일링 (100, 200, 400, 800...)
-- 변경: 선형 증가 (100, 250, 400, 550, 700...)
-- 공식: level * 100 + (level - 1) * 50
-- =====================================================

CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER,
    p_problem_type VARCHAR(20),
    p_difficulty VARCHAR(20) DEFAULT NULL
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

    -- Calculate new level (선형 증가: 100, 250, 400, 550, 700...)
    -- 공식: level * 100 + (level - 1) * 50
    -- Level 1: 0-99 XP
    -- Level 2: 100-349 XP (need 100)
    -- Level 3: 350-749 XP (need 250)
    -- Level 4: 750-1299 XP (need 400)
    -- Level 5: 1300-1999 XP (need 550)
    v_new_level := 1;
    v_remaining_xp := v_new_xp;

    WHILE TRUE LOOP
        -- 현재 레벨에서 다음 레벨로 가기 위해 필요한 XP
        -- level * 100 + (level - 1) * 50
        v_xp_for_level := v_new_level * 100 + (v_new_level - 1) * 50;

        IF v_remaining_xp >= v_xp_for_level THEN
            v_remaining_xp := v_remaining_xp - v_xp_for_level;
            v_new_level := v_new_level + 1;
        ELSE
            EXIT;
        END IF;
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


-- =====================================================
-- 기존 사용자들의 레벨 재계산
-- =====================================================
CREATE OR REPLACE FUNCTION recalculate_all_user_levels()
RETURNS INTEGER AS $$
DECLARE
    v_user RECORD;
    v_new_level INTEGER;
    v_xp_for_level INTEGER;
    v_remaining_xp INTEGER;
    v_updated_count INTEGER := 0;
BEGIN
    FOR v_user IN SELECT user_id, total_xp, level FROM user_stats LOOP
        -- 새 공식으로 레벨 계산
        v_new_level := 1;
        v_remaining_xp := v_user.total_xp;

        WHILE TRUE LOOP
            v_xp_for_level := v_new_level * 100 + (v_new_level - 1) * 50;

            IF v_remaining_xp >= v_xp_for_level THEN
                v_remaining_xp := v_remaining_xp - v_xp_for_level;
                v_new_level := v_new_level + 1;
            ELSE
                EXIT;
            END IF;
        END LOOP;

        -- 레벨이 변경되었으면 업데이트
        IF v_user.level != v_new_level THEN
            UPDATE user_stats
            SET level = v_new_level
            WHERE user_id = v_user.user_id;

            v_updated_count := v_updated_count + 1;
        END IF;
    END LOOP;

    RETURN v_updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 모든 사용자 레벨 재계산 실행
SELECT recalculate_all_user_levels();

-- 재계산 함수 삭제 (일회성)
DROP FUNCTION IF EXISTS recalculate_all_user_levels();

-- 검증 로그
DO $$
BEGIN
    RAISE NOTICE 'Level calculation formula updated: level * 100 + (level - 1) * 50';
    RAISE NOTICE 'Level thresholds: L2=100, L3=350, L4=750, L5=1300, L6=2000';
END $$;
