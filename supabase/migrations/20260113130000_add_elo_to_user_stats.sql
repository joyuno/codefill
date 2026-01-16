-- =====================================================
-- user_stats 테이블에 ELO 컬럼 추가
-- 날짜: 2026-01-13
-- 목적: 사용자 프로필에 ELO 레이팅 표시
-- =====================================================
--
-- user_stats: 프로필 표시용 전체 ELO만 저장
-- user_analysis_reports: 토픽별 상세 ELO (약점분석용)
--
-- =====================================================

-- 1. ELO 컬럼 추가
ALTER TABLE user_stats
ADD COLUMN IF NOT EXISTS elo_overall INTEGER DEFAULT 1000;

-- 2. 인덱스 추가 (랭킹 조회용)
CREATE INDEX IF NOT EXISTS idx_user_stats_elo_overall
ON user_stats(elo_overall DESC);

-- 3. 컬럼 설명
COMMENT ON COLUMN user_stats.elo_overall IS '전체 ELO 레이팅 (600~1600, 기본 1000). 프로필 표시용';

-- 4. 기존 user_analysis_reports에서 ELO 동기화
UPDATE user_stats us
SET elo_overall = uar.elo_overall
FROM user_analysis_reports uar
WHERE us.user_id = uar.user_id
  AND uar.elo_overall IS NOT NULL
  AND uar.elo_overall != 1000;

-- 5. ELO 기반 랭킹 뷰 (user_stats 기준)
CREATE OR REPLACE VIEW user_elo_leaderboard AS
SELECT
    us.user_id,
    u.name AS user_name,
    u.avatar_url,
    us.elo_overall,
    us.level,
    us.total_xp,
    us.problems_solved,
    RANK() OVER (ORDER BY us.elo_overall DESC) AS elo_rank,
    us.updated_at
FROM user_stats us
JOIN users u ON us.user_id = u.id
WHERE us.elo_overall IS NOT NULL
ORDER BY us.elo_overall DESC;

GRANT SELECT ON user_elo_leaderboard TO authenticated;
GRANT SELECT ON user_elo_leaderboard TO service_role;

-- =====================================================
-- 완료
-- =====================================================
