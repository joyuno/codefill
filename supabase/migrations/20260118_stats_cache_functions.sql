-- ============================================================
-- Stats Cache Helper Functions
-- 인메모리 캐시에서 배치로 업데이트할 때 사용하는 atomic increment 함수
-- ============================================================

-- ============================================================
-- 1. user_stats atomic increment
-- ============================================================
CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp_delta INT DEFAULT 0,
    p_problems_solved_delta INT DEFAULT 0,
    p_hints_used_delta INT DEFAULT 0,
    p_seeds_delta INT DEFAULT 0,
    p_time_spent_delta INT DEFAULT 0
)
RETURNS VOID AS $$
DECLARE
    v_new_xp INTEGER;
    v_new_level INTEGER;
    v_xp_for_level INTEGER;
    v_remaining_xp INTEGER;
BEGIN
    UPDATE user_stats SET
        total_xp = COALESCE(total_xp, 0) + p_xp_delta,
        problems_solved = COALESCE(problems_solved, 0) + p_problems_solved_delta,
        hints_used = COALESCE(hints_used, 0) + p_hints_used_delta,
        seeds = COALESCE(seeds, 0) + p_seeds_delta,
        updated_at = NOW()
    WHERE user_id = p_user_id
    RETURNING total_xp INTO v_new_xp;

    -- 레코드 없으면 생성
    IF NOT FOUND THEN
        v_new_xp := GREATEST(0, p_xp_delta);
        INSERT INTO user_stats (
            user_id, total_xp, problems_solved, hints_used, seeds, level
        ) VALUES (
            p_user_id,
            v_new_xp,
            GREATEST(0, p_problems_solved_delta),
            GREATEST(0, p_hints_used_delta),
            GREATEST(0, p_seeds_delta),
            1
        );
    END IF;

    -- XP가 변경되었으면 레벨 재계산
    IF p_xp_delta != 0 AND v_new_xp IS NOT NULL THEN
        -- 레벨 계산 (선형 증가: 100, 250, 400, 550, 700...)
        -- 공식: level * 100 + (level - 1) * 50
        v_new_level := 1;
        v_remaining_xp := v_new_xp;

        WHILE TRUE LOOP
            v_xp_for_level := v_new_level * 100 + (v_new_level - 1) * 50;

            IF v_remaining_xp >= v_xp_for_level THEN
                v_remaining_xp := v_remaining_xp - v_xp_for_level;
                v_new_level := v_new_level + 1;
            ELSE
                EXIT;
            END IF;
        END LOOP;

        -- 레벨 업데이트
        UPDATE user_stats
        SET level = v_new_level
        WHERE user_id = p_user_id;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 2. daily_activity upsert with increment
-- ============================================================
CREATE OR REPLACE FUNCTION upsert_daily_activity(
    p_user_id UUID,
    p_date DATE,
    p_problems_solved_delta INT DEFAULT 0,
    p_xp_earned_delta INT DEFAULT 0,
    p_time_spent_delta INT DEFAULT 0,
    p_hints_used_delta INT DEFAULT 0
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_activity (
        user_id, activity_date, problems_solved, xp_earned, time_spent, hints_used
    ) VALUES (
        p_user_id, p_date,
        GREATEST(0, p_problems_solved_delta),
        GREATEST(0, p_xp_earned_delta),
        GREATEST(0, p_time_spent_delta),
        GREATEST(0, p_hints_used_delta)
    )
    ON CONFLICT (user_id, activity_date) DO UPDATE SET
        problems_solved = COALESCE(daily_activity.problems_solved, 0) + EXCLUDED.problems_solved,
        xp_earned = COALESCE(daily_activity.xp_earned, 0) + EXCLUDED.xp_earned,
        time_spent = COALESCE(daily_activity.time_spent, 0) + EXCLUDED.time_spent,
        hints_used = COALESCE(daily_activity.hints_used, 0) + EXCLUDED.hints_used;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 3. 배치 인터랙션 삽입 함수 (선택적)
-- ============================================================
CREATE OR REPLACE FUNCTION insert_interactions_batch(
    p_interactions JSONB
)
RETURNS INT AS $$
DECLARE
    v_count INT := 0;
    v_interaction JSONB;
BEGIN
    FOR v_interaction IN SELECT * FROM jsonb_array_elements(p_interactions)
    LOOP
        INSERT INTO user_interactions (
            user_id,
            session_id,
            interaction_type,
            interaction_data,
            user_metadata,
            created_at
        ) VALUES (
            (v_interaction->>'user_id')::UUID,
            (v_interaction->>'session_id')::UUID,
            v_interaction->>'interaction_type',
            COALESCE(v_interaction->'interaction_data', '{}'::JSONB),
            COALESCE(v_interaction->'user_metadata', '{}'::JSONB),
            COALESCE((v_interaction->>'created_at')::TIMESTAMPTZ, NOW())
        );
        v_count := v_count + 1;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 권한 부여
-- ============================================================
GRANT EXECUTE ON FUNCTION increment_user_stats(UUID, INT, INT, INT, INT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION upsert_daily_activity(UUID, DATE, INT, INT, INT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION insert_interactions_batch(JSONB) TO service_role;

DO $$ BEGIN RAISE NOTICE 'Stats cache helper functions created successfully'; END $$;
