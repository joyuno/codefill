-- =====================================================
-- user_skill_snapshots 테이블에 ELO 컬럼 추가
-- 날짜: 2026-01-13
-- 목적: 스냅샷에 ELO 레이팅 데이터 저장
-- =====================================================

-- 1. ELO 컬럼 추가
ALTER TABLE user_skill_snapshots
ADD COLUMN IF NOT EXISTS elo_by_topic JSONB DEFAULT '{}';

ALTER TABLE user_skill_snapshots
ADD COLUMN IF NOT EXISTS elo_overall INTEGER DEFAULT 1000;

-- 2. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_user_skill_snapshots_elo_overall
ON user_skill_snapshots(elo_overall);

-- 3. 컬럼 설명
COMMENT ON COLUMN user_skill_snapshots.elo_by_topic IS '토픽별 ELO 레이팅 (600~1600)';
COMMENT ON COLUMN user_skill_snapshots.elo_overall IS '전체 ELO 레이팅';

-- 4. 기존 skill_by_topic 데이터를 ELO로 변환
UPDATE user_skill_snapshots
SET elo_by_topic = (
    SELECT COALESCE(
        jsonb_object_agg(
            key,
            ROUND(600 + (value::float * 800))::integer
        ),
        '{}'::jsonb
    )
    FROM jsonb_each_text(skill_by_topic)
)
WHERE skill_by_topic IS NOT NULL
  AND skill_by_topic != '{}'::jsonb
  AND (elo_by_topic IS NULL OR elo_by_topic = '{}'::jsonb);

-- 5. elo_overall 계산
UPDATE user_skill_snapshots
SET elo_overall = (
    SELECT COALESCE(ROUND(AVG(value::integer)), 1000)
    FROM jsonb_each_text(elo_by_topic)
)
WHERE elo_by_topic IS NOT NULL
  AND elo_by_topic != '{}'::jsonb;

-- 6. ELO 성장 추적 뷰
CREATE OR REPLACE VIEW user_elo_growth AS
SELECT
    uss.user_id,
    u.name AS user_name,
    uss.snapshot_at,
    uss.elo_overall,
    uss.problems_solved,
    uss.problems_attempted,
    ROUND(uss.problems_solved::numeric / NULLIF(uss.problems_attempted, 0) * 100, 1) AS success_rate,
    uss.created_at,
    uss.elo_overall - LAG(uss.elo_overall) OVER (
        PARTITION BY uss.user_id ORDER BY uss.snapshot_at
    ) AS elo_change
FROM user_skill_snapshots uss
JOIN users u ON uss.user_id = u.id
ORDER BY uss.user_id, uss.snapshot_at;

GRANT SELECT ON user_elo_growth TO authenticated;
GRANT SELECT ON user_elo_growth TO service_role;

-- =====================================================
-- 완료
-- =====================================================
