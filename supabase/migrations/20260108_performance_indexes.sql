-- =====================================================
-- Performance Indexes for Query Optimization
-- 2026-01-08
-- =====================================================

-- 1. users.name 인덱스 (공개 프로필 조회 최적화)
-- username으로 사용자 검색시 Full Table Scan 방지
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);

-- 2. user_stats 랭킹 정렬 인덱스
-- 글로벌 랭킹 조회시 정렬 성능 개선
CREATE INDEX IF NOT EXISTS idx_user_stats_total_xp ON user_stats(total_xp DESC);
CREATE INDEX IF NOT EXISTS idx_user_stats_problems_solved ON user_stats(problems_solved DESC);
CREATE INDEX IF NOT EXISTS idx_user_stats_longest_streak ON user_stats(longest_streak DESC);

-- 3. daily_activity 날짜 범위 검색 인덱스
-- 주간/월간 랭킹 조회시 날짜 범위 검색 최적화
CREATE INDEX IF NOT EXISTS idx_daily_activity_date ON daily_activity(activity_date);
CREATE INDEX IF NOT EXISTS idx_daily_activity_user_date ON daily_activity(user_id, activity_date);

-- 4. user_badges 조회 최적화
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);

-- 5. attempts 조회 최적화 (문제별, 사용자별)
CREATE INDEX IF NOT EXISTS idx_attempts_user_problem ON attempts(user_id, problem_id);
CREATE INDEX IF NOT EXISTS idx_attempts_problem_id ON attempts(problem_id);
