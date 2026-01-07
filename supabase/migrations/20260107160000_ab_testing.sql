-- ============================================================
-- A/B 테스팅 테이블
-- 추천 알고리즘 실험 및 메트릭 수집
-- ============================================================

-- 1. A/B 테스트 할당 테이블
-- 사용자가 어떤 실험의 어떤 그룹에 할당되었는지 추적
CREATE TABLE IF NOT EXISTS ab_test_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    experiment_name VARCHAR(100) NOT NULL,
    variant_name VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),

    -- 사용자는 실험당 하나의 그룹에만 할당
    CONSTRAINT unique_user_experiment UNIQUE (user_id, experiment_name)
);

-- 2. A/B 테스트 이벤트 테이블
-- 실험 관련 이벤트 (노출, 클릭, 전환) 추적
CREATE TABLE IF NOT EXISTS ab_test_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    experiment_name VARCHAR(100) NOT NULL,
    variant_name VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- impression, click, conversion, custom
    event_data JSONB DEFAULT '{}',
    -- 예: {
    --   "topic": "dp",
    --   "difficulty": "medium",
    --   "time_spent": 120,
    --   "was_successful": true
    -- }
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. A/B 테스트 실험 정의 테이블 (선택적)
-- 실험 메타데이터 (현재는 하드코딩으로 관리 가능)
CREATE TABLE IF NOT EXISTS ab_test_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, running, paused, completed
    variants JSONB NOT NULL DEFAULT '[]',
    -- 예: [
    --   {"name": "control", "weight": 0.5, "config": {"algorithm": "basic"}},
    --   {"name": "treatment", "weight": 0.5, "config": {"algorithm": "cosine"}}
    -- ]
    target_sample_size INT DEFAULT 1000,
    current_sample_size INT DEFAULT 0,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS ab_assignments_user_idx ON ab_test_assignments(user_id);
CREATE INDEX IF NOT EXISTS ab_assignments_experiment_idx ON ab_test_assignments(experiment_name);
CREATE INDEX IF NOT EXISTS ab_assignments_variant_idx ON ab_test_assignments(variant_name);

CREATE INDEX IF NOT EXISTS ab_events_user_idx ON ab_test_events(user_id);
CREATE INDEX IF NOT EXISTS ab_events_experiment_idx ON ab_test_events(experiment_name);
CREATE INDEX IF NOT EXISTS ab_events_variant_idx ON ab_test_events(variant_name);
CREATE INDEX IF NOT EXISTS ab_events_type_idx ON ab_test_events(event_type);
CREATE INDEX IF NOT EXISTS ab_events_created_idx ON ab_test_events(created_at DESC);

-- RLS 정책
ALTER TABLE ab_test_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_test_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_test_experiments ENABLE ROW LEVEL SECURITY;

-- ab_test_assignments 정책
DO $$ BEGIN
    CREATE POLICY "Users can view own assignments"
        ON ab_test_assignments FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to assignments"
        ON ab_test_assignments FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ab_test_events 정책
DO $$ BEGIN
    CREATE POLICY "Users can view own events"
        ON ab_test_events FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to events"
        ON ab_test_events FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ab_test_experiments 정책
DO $$ BEGIN
    CREATE POLICY "Public can view experiments"
        ON ab_test_experiments FOR SELECT TO authenticated USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to experiments"
        ON ab_test_experiments FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 권한 부여
GRANT SELECT ON ab_test_assignments TO authenticated;
GRANT ALL ON ab_test_assignments TO service_role;

GRANT SELECT ON ab_test_events TO authenticated;
GRANT ALL ON ab_test_events TO service_role;

GRANT SELECT ON ab_test_experiments TO authenticated;
GRANT ALL ON ab_test_experiments TO service_role;

-- ============================================================
-- 함수: A/B 테스트 메트릭 집계
-- ============================================================
CREATE OR REPLACE FUNCTION get_ab_test_metrics(
    p_experiment_name VARCHAR(100)
)
RETURNS TABLE (
    variant_name VARCHAR,
    impressions BIGINT,
    clicks BIGINT,
    conversions BIGINT,
    ctr FLOAT,
    conversion_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.variant_name::varchar,
        COUNT(*) FILTER (WHERE e.event_type = 'impression') AS impressions,
        COUNT(*) FILTER (WHERE e.event_type = 'click') AS clicks,
        COUNT(*) FILTER (WHERE e.event_type = 'conversion') AS conversions,
        CASE
            WHEN COUNT(*) FILTER (WHERE e.event_type = 'impression') > 0 THEN
                COUNT(*) FILTER (WHERE e.event_type = 'click')::float /
                COUNT(*) FILTER (WHERE e.event_type = 'impression')::float
            ELSE 0
        END AS ctr,
        CASE
            WHEN COUNT(*) FILTER (WHERE e.event_type = 'click') > 0 THEN
                COUNT(*) FILTER (WHERE e.event_type = 'conversion')::float /
                COUNT(*) FILTER (WHERE e.event_type = 'click')::float
            ELSE 0
        END AS conversion_rate
    FROM ab_test_events e
    WHERE e.experiment_name = p_experiment_name
    GROUP BY e.variant_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 함수: 실험별 일일 메트릭
-- ============================================================
CREATE OR REPLACE FUNCTION get_ab_test_daily_metrics(
    p_experiment_name VARCHAR(100),
    p_days INT DEFAULT 7
)
RETURNS TABLE (
    date DATE,
    variant_name VARCHAR,
    impressions BIGINT,
    clicks BIGINT,
    conversions BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.created_at::date AS date,
        e.variant_name::varchar,
        COUNT(*) FILTER (WHERE e.event_type = 'impression') AS impressions,
        COUNT(*) FILTER (WHERE e.event_type = 'click') AS clicks,
        COUNT(*) FILTER (WHERE e.event_type = 'conversion') AS conversions
    FROM ab_test_events e
    WHERE e.experiment_name = p_experiment_name
    AND e.created_at >= NOW() - (p_days || ' days')::interval
    GROUP BY e.created_at::date, e.variant_name
    ORDER BY date DESC, variant_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION get_ab_test_metrics(VARCHAR) TO service_role;
GRANT EXECUTE ON FUNCTION get_ab_test_daily_metrics(VARCHAR, INT) TO service_role;

-- ============================================================
-- 초기 실험 데이터 삽입
-- ============================================================
INSERT INTO ab_test_experiments (name, description, status, variants, target_sample_size)
VALUES
    (
        'rec_algo_v2',
        '추천 알고리즘 v2 테스트 (코사인 유사도 vs 기존)',
        'running',
        '[
            {"name": "control", "weight": 0.5, "config": {"algorithm": "basic"}},
            {"name": "treatment", "weight": 0.5, "config": {"algorithm": "cosine_similarity"}}
        ]'::jsonb,
        1000
    ),
    (
        'cold_start_onboarding',
        '신규 사용자 온보딩 테스트',
        'running',
        '[
            {"name": "control", "weight": 0.5, "config": {"show_onboarding": false}},
            {"name": "treatment", "weight": 0.5, "config": {"show_onboarding": true}}
        ]'::jsonb,
        500
    ),
    (
        'suggestion_ui',
        '추천 선택지 UI 테스트',
        'draft',
        '[
            {"name": "chips", "weight": 0.33, "config": {"ui_type": "chips"}},
            {"name": "buttons", "weight": 0.34, "config": {"ui_type": "buttons"}},
            {"name": "cards", "weight": 0.33, "config": {"ui_type": "cards"}}
        ]'::jsonb,
        1500
    )
ON CONFLICT (name) DO NOTHING;

DO $$ BEGIN RAISE NOTICE 'A/B testing tables created successfully'; END $$;
