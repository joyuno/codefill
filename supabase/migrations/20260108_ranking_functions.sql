-- =====================================================
-- Ranking System RPC Functions
-- 글로벌, 주간, 월간 랭킹 및 내 순위 조회
-- =====================================================

-- =====================================================
-- 1. 글로벌 랭킹 조회
-- type: 'xp' | 'problems' | 'streak'
-- =====================================================
CREATE OR REPLACE FUNCTION get_global_ranking(
    p_type TEXT DEFAULT 'xp',
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    rank BIGINT,
    user_id UUID,
    username TEXT,
    profile_image TEXT,
    value INT,
    level INT
) AS $$
BEGIN
    IF p_type = 'xp' THEN
        RETURN QUERY
        SELECT
            ROW_NUMBER() OVER (ORDER BY us.total_xp DESC, us.created_at ASC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            us.total_xp as value,
            us.level
        FROM user_stats us
        JOIN users u ON u.id = us.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY us.total_xp DESC, us.created_at ASC
        LIMIT p_limit OFFSET p_offset;

    ELSIF p_type = 'problems' THEN
        RETURN QUERY
        SELECT
            ROW_NUMBER() OVER (ORDER BY us.problems_solved DESC, us.created_at ASC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            us.problems_solved as value,
            us.level
        FROM user_stats us
        JOIN users u ON u.id = us.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY us.problems_solved DESC, us.created_at ASC
        LIMIT p_limit OFFSET p_offset;

    ELSIF p_type = 'streak' THEN
        RETURN QUERY
        SELECT
            ROW_NUMBER() OVER (ORDER BY us.longest_streak DESC, us.created_at ASC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            us.longest_streak as value,
            us.level
        FROM user_stats us
        JOIN users u ON u.id = us.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY us.longest_streak DESC, us.created_at ASC
        LIMIT p_limit OFFSET p_offset;
    ELSE
        -- 기본값: XP 랭킹
        RETURN QUERY
        SELECT
            ROW_NUMBER() OVER (ORDER BY us.total_xp DESC, us.created_at ASC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            us.total_xp as value,
            us.level
        FROM user_stats us
        JOIN users u ON u.id = us.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY us.total_xp DESC, us.created_at ASC
        LIMIT p_limit OFFSET p_offset;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 2. 주간 랭킹 조회 (월요일 ~ 일요일 기준)
-- type: 'xp' | 'problems'
-- =====================================================
CREATE OR REPLACE FUNCTION get_weekly_ranking(
    p_type TEXT DEFAULT 'xp',
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    rank BIGINT,
    user_id UUID,
    username TEXT,
    profile_image TEXT,
    value BIGINT,
    level INT
) AS $$
DECLARE
    week_start DATE;
    week_end DATE;
BEGIN
    -- 이번 주 월요일 ~ 일요일 계산
    week_start := date_trunc('week', CURRENT_DATE)::DATE;
    week_end := week_start + INTERVAL '6 days';

    IF p_type = 'xp' THEN
        RETURN QUERY
        WITH weekly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.xp_earned), 0)::BIGINT as weekly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN week_start AND week_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.xp_earned), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY wd.weekly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            wd.weekly_value as value,
            us.level
        FROM weekly_data wd
        JOIN users u ON u.id = wd.user_id
        JOIN user_stats us ON us.user_id = wd.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY wd.weekly_value DESC
        LIMIT p_limit OFFSET p_offset;

    ELSIF p_type = 'problems' THEN
        RETURN QUERY
        WITH weekly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.problems_solved), 0)::BIGINT as weekly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN week_start AND week_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.problems_solved), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY wd.weekly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            wd.weekly_value as value,
            us.level
        FROM weekly_data wd
        JOIN users u ON u.id = wd.user_id
        JOIN user_stats us ON us.user_id = wd.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY wd.weekly_value DESC
        LIMIT p_limit OFFSET p_offset;
    ELSE
        -- 기본값: XP 랭킹
        RETURN QUERY
        WITH weekly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.xp_earned), 0)::BIGINT as weekly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN week_start AND week_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.xp_earned), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY wd.weekly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            wd.weekly_value as value,
            us.level
        FROM weekly_data wd
        JOIN users u ON u.id = wd.user_id
        JOIN user_stats us ON us.user_id = wd.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY wd.weekly_value DESC
        LIMIT p_limit OFFSET p_offset;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 3. 월간 랭킹 조회 (1일 ~ 말일 기준)
-- type: 'xp' | 'problems'
-- =====================================================
CREATE OR REPLACE FUNCTION get_monthly_ranking(
    p_type TEXT DEFAULT 'xp',
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    rank BIGINT,
    user_id UUID,
    username TEXT,
    profile_image TEXT,
    value BIGINT,
    level INT
) AS $$
DECLARE
    month_start DATE;
    month_end DATE;
BEGIN
    -- 이번 달 1일 ~ 말일 계산
    month_start := date_trunc('month', CURRENT_DATE)::DATE;
    month_end := (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;

    IF p_type = 'xp' THEN
        RETURN QUERY
        WITH monthly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.xp_earned), 0)::BIGINT as monthly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN month_start AND month_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.xp_earned), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY md.monthly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            md.monthly_value as value,
            us.level
        FROM monthly_data md
        JOIN users u ON u.id = md.user_id
        JOIN user_stats us ON us.user_id = md.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY md.monthly_value DESC
        LIMIT p_limit OFFSET p_offset;

    ELSIF p_type = 'problems' THEN
        RETURN QUERY
        WITH monthly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.problems_solved), 0)::BIGINT as monthly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN month_start AND month_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.problems_solved), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY md.monthly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            md.monthly_value as value,
            us.level
        FROM monthly_data md
        JOIN users u ON u.id = md.user_id
        JOIN user_stats us ON us.user_id = md.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY md.monthly_value DESC
        LIMIT p_limit OFFSET p_offset;
    ELSE
        -- 기본값: XP 랭킹
        RETURN QUERY
        WITH monthly_data AS (
            SELECT
                da.user_id,
                COALESCE(SUM(da.xp_earned), 0)::BIGINT as monthly_value
            FROM daily_activity da
            WHERE da.activity_date BETWEEN month_start AND month_end
            GROUP BY da.user_id
            HAVING COALESCE(SUM(da.xp_earned), 0) > 0
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY md.monthly_value DESC)::BIGINT as rank,
            u.id as user_id,
            u.name::TEXT as username,
            u.avatar_url::TEXT as profile_image,
            md.monthly_value as value,
            us.level
        FROM monthly_data md
        JOIN users u ON u.id = md.user_id
        JOIN user_stats us ON us.user_id = md.user_id
        WHERE u.deleted_at IS NULL
        ORDER BY md.monthly_value DESC
        LIMIT p_limit OFFSET p_offset;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 4. 내 순위 조회 (모든 랭킹에서 내 위치)
-- =====================================================
CREATE OR REPLACE FUNCTION get_my_ranking(p_user_id UUID)
RETURNS TABLE (
    global_xp_rank BIGINT,
    global_solve_rank BIGINT,
    global_streak_rank BIGINT,
    weekly_xp_rank BIGINT,
    weekly_solve_rank BIGINT,
    monthly_xp_rank BIGINT,
    monthly_solve_rank BIGINT,
    total_users BIGINT
) AS $$
DECLARE
    week_start DATE;
    week_end DATE;
    month_start DATE;
    month_end DATE;
    v_global_xp_rank BIGINT;
    v_global_solve_rank BIGINT;
    v_global_streak_rank BIGINT;
    v_weekly_xp_rank BIGINT;
    v_weekly_solve_rank BIGINT;
    v_monthly_xp_rank BIGINT;
    v_monthly_solve_rank BIGINT;
    v_total_users BIGINT;
    v_my_total_xp INT;
    v_my_problems_solved INT;
    v_my_longest_streak INT;
    v_my_weekly_xp BIGINT;
    v_my_weekly_problems BIGINT;
    v_my_monthly_xp BIGINT;
    v_my_monthly_problems BIGINT;
BEGIN
    -- 날짜 범위 설정
    week_start := date_trunc('week', CURRENT_DATE)::DATE;
    week_end := week_start + INTERVAL '6 days';
    month_start := date_trunc('month', CURRENT_DATE)::DATE;
    month_end := (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;

    -- 전체 사용자 수
    SELECT COUNT(*) INTO v_total_users FROM user_stats;

    -- 내 글로벌 통계 가져오기
    SELECT us.total_xp, us.problems_solved, us.longest_streak
    INTO v_my_total_xp, v_my_problems_solved, v_my_longest_streak
    FROM user_stats us
    WHERE us.user_id = p_user_id;

    -- 글로벌 XP 순위
    SELECT COUNT(*) + 1 INTO v_global_xp_rank
    FROM user_stats us
    JOIN users u ON u.id = us.user_id
    WHERE u.deleted_at IS NULL AND us.total_xp > COALESCE(v_my_total_xp, 0);

    -- 글로벌 문제 풀이 순위
    SELECT COUNT(*) + 1 INTO v_global_solve_rank
    FROM user_stats us
    JOIN users u ON u.id = us.user_id
    WHERE u.deleted_at IS NULL AND us.problems_solved > COALESCE(v_my_problems_solved, 0);

    -- 글로벌 스트릭 순위
    SELECT COUNT(*) + 1 INTO v_global_streak_rank
    FROM user_stats us
    JOIN users u ON u.id = us.user_id
    WHERE u.deleted_at IS NULL AND us.longest_streak > COALESCE(v_my_longest_streak, 0);

    -- 내 주간 통계
    SELECT COALESCE(SUM(xp_earned), 0), COALESCE(SUM(problems_solved), 0)
    INTO v_my_weekly_xp, v_my_weekly_problems
    FROM daily_activity
    WHERE user_id = p_user_id
    AND activity_date BETWEEN week_start AND week_end;

    -- 주간 XP 순위
    SELECT COUNT(*) + 1 INTO v_weekly_xp_rank
    FROM (
        SELECT da.user_id, SUM(da.xp_earned) as total
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN week_start AND week_end
        GROUP BY da.user_id
        HAVING SUM(da.xp_earned) > v_my_weekly_xp
    ) sub;

    -- 주간 문제 풀이 순위
    SELECT COUNT(*) + 1 INTO v_weekly_solve_rank
    FROM (
        SELECT da.user_id, SUM(da.problems_solved) as total
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN week_start AND week_end
        GROUP BY da.user_id
        HAVING SUM(da.problems_solved) > v_my_weekly_problems
    ) sub;

    -- 내 월간 통계
    SELECT COALESCE(SUM(xp_earned), 0), COALESCE(SUM(problems_solved), 0)
    INTO v_my_monthly_xp, v_my_monthly_problems
    FROM daily_activity
    WHERE user_id = p_user_id
    AND activity_date BETWEEN month_start AND month_end;

    -- 월간 XP 순위
    SELECT COUNT(*) + 1 INTO v_monthly_xp_rank
    FROM (
        SELECT da.user_id, SUM(da.xp_earned) as total
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN month_start AND month_end
        GROUP BY da.user_id
        HAVING SUM(da.xp_earned) > v_my_monthly_xp
    ) sub;

    -- 월간 문제 풀이 순위
    SELECT COUNT(*) + 1 INTO v_monthly_solve_rank
    FROM (
        SELECT da.user_id, SUM(da.problems_solved) as total
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN month_start AND month_end
        GROUP BY da.user_id
        HAVING SUM(da.problems_solved) > v_my_monthly_problems
    ) sub;

    RETURN QUERY SELECT
        v_global_xp_rank,
        v_global_solve_rank,
        v_global_streak_rank,
        v_weekly_xp_rank,
        v_weekly_solve_rank,
        v_monthly_xp_rank,
        v_monthly_solve_rank,
        v_total_users;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 5. 전체 사용자 수 조회 (각 랭킹별)
-- =====================================================
CREATE OR REPLACE FUNCTION get_ranking_total_count(
    p_period TEXT DEFAULT 'global',
    p_type TEXT DEFAULT 'xp'
)
RETURNS BIGINT AS $$
DECLARE
    week_start DATE;
    week_end DATE;
    month_start DATE;
    month_end DATE;
    v_count BIGINT;
BEGIN
    week_start := date_trunc('week', CURRENT_DATE)::DATE;
    week_end := week_start + INTERVAL '6 days';
    month_start := date_trunc('month', CURRENT_DATE)::DATE;
    month_end := (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;

    IF p_period = 'global' THEN
        SELECT COUNT(*) INTO v_count
        FROM user_stats us
        JOIN users u ON u.id = us.user_id
        WHERE u.deleted_at IS NULL;
    ELSIF p_period = 'weekly' THEN
        SELECT COUNT(DISTINCT da.user_id) INTO v_count
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN week_start AND week_end
        AND (
            (p_type = 'xp' AND da.xp_earned > 0) OR
            (p_type = 'problems' AND da.problems_solved > 0)
        );
    ELSIF p_period = 'monthly' THEN
        SELECT COUNT(DISTINCT da.user_id) INTO v_count
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN month_start AND month_end
        AND (
            (p_type = 'xp' AND da.xp_earned > 0) OR
            (p_type = 'problems' AND da.problems_solved > 0)
        );
    ELSE
        v_count := 0;
    END IF;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 검증: 함수 생성 확인
-- =====================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_global_ranking') THEN
        RAISE NOTICE 'get_global_ranking function created successfully';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_weekly_ranking') THEN
        RAISE NOTICE 'get_weekly_ranking function created successfully';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_monthly_ranking') THEN
        RAISE NOTICE 'get_monthly_ranking function created successfully';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_my_ranking') THEN
        RAISE NOTICE 'get_my_ranking function created successfully';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_ranking_total_count') THEN
        RAISE NOTICE 'get_ranking_total_count function created successfully';
    END IF;
END $$;
