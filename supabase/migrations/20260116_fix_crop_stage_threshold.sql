-- =====================================================
-- Fix crop stage threshold: 4 -> 6
-- 7단계 성장 시스템 적용 (0~6)
-- 2026-01-16
-- =====================================================

-- Update get_public_profile_all function with correct stage threshold
CREATE OR REPLACE FUNCTION get_public_profile_all(
    p_username TEXT,
    p_days INTEGER DEFAULT 365
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID;
    v_user RECORD;
    v_stats RECORD;
    v_farm RECORD;
    v_level INTEGER;
    v_current_xp INTEGER;
    v_required_xp INTEGER;
    v_total_xp INTEGER;
    v_start_date DATE;
    v_result JSONB;
    v_badges JSONB;
    v_activity JSONB;
    v_farm_slots JSONB;
    v_character JSONB;
BEGIN
    -- 1. Find user by username
    SELECT id, name, avatar_url, created_at
    INTO v_user
    FROM users
    WHERE name = p_username AND deleted_at IS NULL
    LIMIT 1;

    IF v_user.id IS NULL THEN
        RAISE EXCEPTION 'User not found: %', p_username;
    END IF;

    v_user_id := v_user.id;

    -- 2. Get user stats
    SELECT total_xp, problems_solved, current_streak, longest_streak
    INTO v_stats
    FROM user_stats
    WHERE user_id = v_user_id;

    -- Calculate level and XP
    v_total_xp := COALESCE(v_stats.total_xp, 0);
    v_level := calculate_level_from_xp(v_total_xp);
    v_current_xp := calculate_current_xp(v_total_xp);
    v_required_xp := calculate_required_xp(v_level);

    -- 3. Get badges with badge info (aggregated)
    SELECT COALESCE(jsonb_agg(
        jsonb_build_object(
            'id', ub.id::TEXT,
            'name', b.name,
            'icon', '🏅',
            'icon_url', b.icon_url,
            'description', b.description,
            'rarity', b.rarity
        ) ORDER BY ub.earned_at DESC
    ), '[]'::JSONB)
    INTO v_badges
    FROM user_badges ub
    JOIN badges b ON ub.badge_id = b.id
    WHERE ub.user_id = v_user_id;

    -- 4. Get farm data
    SELECT farm_level, gold, character_data, farm_slots, character_created
    INTO v_farm
    FROM user_farm
    WHERE user_id = v_user_id;

    -- Build farm character
    IF v_farm.character_created AND v_farm.character_data IS NOT NULL AND v_farm.character_data != '{}'::JSONB THEN
        v_character := jsonb_build_object(
            'name', COALESCE(v_farm.character_data->>'name', 'Farmer'), 
            'hair', COALESCE(v_farm.character_data->>'hair', 'short'),
            'hairColor', COALESCE(v_farm.character_data->>'hair_color', '#8B4513'),
            'face', COALESCE(v_farm.character_data->>'face', 'happy'),
            'outfit', COALESCE(v_farm.character_data->>'outfit', 'basic'),
            'outfitColor', COALESCE(v_farm.character_data->>'outfit_color', '#4A90D9'),
            'farmName', COALESCE(v_farm.character_data->>'farm_name', 'My Farm')
        );

        -- Build farm slots (stage >= 6 for harvest ready)
        SELECT COALESCE(jsonb_agg(
            jsonb_build_object(
                'slotIndex', (slot->>'slot')::INTEGER,
                'cropType', slot->>'crop_code',
                'stage', COALESCE((slot->>'stage')::INTEGER, 0),
                'isReady', COALESCE((slot->>'stage')::INTEGER, 0) >= 6
            )
        ), '[]'::JSONB)
        INTO v_farm_slots
        FROM jsonb_array_elements(COALESCE(v_farm.farm_slots, '[]'::JSONB)) AS slot;
    ELSE
        v_character := NULL;
        v_farm_slots := '[]'::JSONB;
    END IF;

    -- 5. Get activity data (last p_days days)
    v_start_date := CURRENT_DATE - p_days;

    SELECT COALESCE(jsonb_agg(
        jsonb_build_object(
            'date', activity_date::TEXT,
            'problems_solved', problems_solved,
            'xp_earned', xp_earned,
            'time_spent', time_spent,
            'blank_count', blank_count,
            'bug_count', bug_count,
            'output_count', output_count,
            'refactor_count', refactor_count
        ) ORDER BY activity_date
    ), '[]'::JSONB)
    INTO v_activity
    FROM daily_activity
    WHERE user_id = v_user_id AND activity_date >= v_start_date;

    -- 6. Build final result
    v_result := jsonb_build_object(
        'profile', jsonb_build_object(
            'id', v_user_id::TEXT,
            'username', v_user.name,
            'avatarUrl', v_user.avatar_url,
            'avatarColor', 'hsl(142, 71%, 45%)',
            'level', v_level,
            'currentXP', v_current_xp,
            'requiredXP', v_required_xp,
            'totalXP', v_total_xp,
            'solvedCount', COALESCE(v_stats.problems_solved, 0),
            'streak', COALESCE(v_stats.current_streak, 0),
            'joinedAt', v_user.created_at
        ),
        'badges', v_badges,
        'farm', jsonb_build_object(
            'hasCharacter', v_character IS NOT NULL,
            'character', v_character,
            'farmLevel', COALESCE(v_farm.farm_level, 1),
            'gold', COALESCE(v_farm.gold, 0),
            'slots', v_farm_slots
        ),
        'activity', jsonb_build_object(
            'days', v_activity,
            'totalDays', jsonb_array_length(v_activity)
        )
    );

    RETURN v_result;
END;
$$;
