-- =====================================================
-- Performance Optimization: Ranking Function
-- 11개 순차 쿼리 → 2개 테이블 스캔으로 최적화
-- =====================================================

-- =====================================================
-- 1. Covering Index for daily_activity aggregation
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_daily_activity_period_agg
ON daily_activity(activity_date, user_id)
INCLUDE (xp_earned, problems_solved);

-- =====================================================
-- 2. Optimized get_my_ranking function
-- - Single scan of user_stats for global rankings
-- - Single scan of daily_activity for period rankings
-- - Returns user stats together to avoid duplicate queries
-- =====================================================
CREATE OR REPLACE FUNCTION get_my_ranking_optimized(p_user_id UUID)
RETURNS TABLE (
    global_xp_rank BIGINT,
    global_solve_rank BIGINT,
    global_streak_rank BIGINT,
    weekly_xp_rank BIGINT,
    weekly_solve_rank BIGINT,
    monthly_xp_rank BIGINT,
    monthly_solve_rank BIGINT,
    total_users BIGINT,
    -- User stats included to avoid duplicate query
    my_total_xp INT,
    my_problems_solved INT,
    my_longest_streak INT,
    my_level INT
) AS $$
DECLARE
    week_start DATE;
    week_end DATE;
    month_start DATE;
    month_end DATE;
    -- User's values
    v_my_total_xp INT;
    v_my_problems_solved INT;
    v_my_longest_streak INT;
    v_my_level INT;
    v_my_weekly_xp BIGINT;
    v_my_weekly_problems BIGINT;
    v_my_monthly_xp BIGINT;
    v_my_monthly_problems BIGINT;
    -- Ranks
    v_global_xp_rank BIGINT;
    v_global_solve_rank BIGINT;
    v_global_streak_rank BIGINT;
    v_weekly_xp_rank BIGINT;
    v_weekly_solve_rank BIGINT;
    v_monthly_xp_rank BIGINT;
    v_monthly_solve_rank BIGINT;
    v_total_users BIGINT;
BEGIN
    -- Calculate date ranges
    week_start := date_trunc('week', CURRENT_DATE)::DATE;
    week_end := week_start + INTERVAL '6 days';
    month_start := date_trunc('month', CURRENT_DATE)::DATE;
    month_end := (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;

    -- Get user's global stats
    SELECT us.total_xp, us.problems_solved, us.longest_streak, us.level
    INTO v_my_total_xp, v_my_problems_solved, v_my_longest_streak, v_my_level
    FROM user_stats us
    WHERE us.user_id = p_user_id;

    -- Handle case where user has no stats
    v_my_total_xp := COALESCE(v_my_total_xp, 0);
    v_my_problems_solved := COALESCE(v_my_problems_solved, 0);
    v_my_longest_streak := COALESCE(v_my_longest_streak, 0);
    v_my_level := COALESCE(v_my_level, 1);

    -- OPTIMIZED: Single scan for all global rankings using COUNT(*) FILTER
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE us.total_xp > v_my_total_xp) + 1,
        COUNT(*) FILTER (WHERE us.problems_solved > v_my_problems_solved) + 1,
        COUNT(*) FILTER (WHERE us.longest_streak > v_my_longest_streak) + 1
    INTO
        v_total_users,
        v_global_xp_rank,
        v_global_solve_rank,
        v_global_streak_rank
    FROM user_stats us
    JOIN users u ON u.id = us.user_id
    WHERE u.deleted_at IS NULL;

    -- Get user's period stats and calculate ranks in single query
    WITH user_period_stats AS (
        SELECT
            COALESCE(SUM(xp_earned) FILTER (WHERE activity_date BETWEEN week_start AND week_end), 0) as weekly_xp,
            COALESCE(SUM(problems_solved) FILTER (WHERE activity_date BETWEEN week_start AND week_end), 0) as weekly_problems,
            COALESCE(SUM(xp_earned) FILTER (WHERE activity_date BETWEEN month_start AND month_end), 0) as monthly_xp,
            COALESCE(SUM(problems_solved) FILTER (WHERE activity_date BETWEEN month_start AND month_end), 0) as monthly_problems
        FROM daily_activity
        WHERE user_id = p_user_id
    ),
    all_users_period_stats AS (
        SELECT
            da.user_id,
            SUM(da.xp_earned) FILTER (WHERE da.activity_date BETWEEN week_start AND week_end) as weekly_xp,
            SUM(da.problems_solved) FILTER (WHERE da.activity_date BETWEEN week_start AND week_end) as weekly_problems,
            SUM(da.xp_earned) FILTER (WHERE da.activity_date BETWEEN month_start AND month_end) as monthly_xp,
            SUM(da.problems_solved) FILTER (WHERE da.activity_date BETWEEN month_start AND month_end) as monthly_problems
        FROM daily_activity da
        JOIN users u ON u.id = da.user_id
        WHERE u.deleted_at IS NULL
        AND da.activity_date BETWEEN week_start AND month_end
        GROUP BY da.user_id
    )
    SELECT
        ups.weekly_xp,
        ups.weekly_problems,
        ups.monthly_xp,
        ups.monthly_problems,
        COUNT(*) FILTER (WHERE aups.weekly_xp > ups.weekly_xp) + 1,
        COUNT(*) FILTER (WHERE aups.weekly_problems > ups.weekly_problems) + 1,
        COUNT(*) FILTER (WHERE aups.monthly_xp > ups.monthly_xp) + 1,
        COUNT(*) FILTER (WHERE aups.monthly_problems > ups.monthly_problems) + 1
    INTO
        v_my_weekly_xp,
        v_my_weekly_problems,
        v_my_monthly_xp,
        v_my_monthly_problems,
        v_weekly_xp_rank,
        v_weekly_solve_rank,
        v_monthly_xp_rank,
        v_monthly_solve_rank
    FROM user_period_stats ups
    CROSS JOIN all_users_period_stats aups
    GROUP BY ups.weekly_xp, ups.weekly_problems, ups.monthly_xp, ups.monthly_problems;

    -- Handle NULL results when no activity data exists
    v_weekly_xp_rank := COALESCE(v_weekly_xp_rank, 1);
    v_weekly_solve_rank := COALESCE(v_weekly_solve_rank, 1);
    v_monthly_xp_rank := COALESCE(v_monthly_xp_rank, 1);
    v_monthly_solve_rank := COALESCE(v_monthly_solve_rank, 1);

    RETURN QUERY SELECT
        v_global_xp_rank,
        v_global_solve_rank,
        v_global_streak_rank,
        v_weekly_xp_rank,
        v_weekly_solve_rank,
        v_monthly_xp_rank,
        v_monthly_solve_rank,
        v_total_users,
        v_my_total_xp,
        v_my_problems_solved,
        v_my_longest_streak,
        v_my_level;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 3. Grant permissions
-- =====================================================
GRANT EXECUTE ON FUNCTION get_my_ranking_optimized(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_my_ranking_optimized(UUID) TO service_role;

-- =====================================================
-- Verification
-- =====================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_my_ranking_optimized') THEN
        RAISE NOTICE 'get_my_ranking_optimized function created successfully';
    END IF;
END $$;
