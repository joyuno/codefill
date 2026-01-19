-- ============================================================
-- Edge Case Logs Table
-- 런타임 엣지케이스 수집 및 분석용
-- ============================================================

-- 1. 메인 테이블
CREATE TABLE IF NOT EXISTS edge_case_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- ============================================================
    -- 사용자/세션 정보
    -- ============================================================
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id TEXT,

    -- ============================================================
    -- LangGraph 상태
    -- ============================================================
    graph_name TEXT NOT NULL,           -- 'orchestrator', 'discovery', 'collection', 'solving'
    current_node TEXT,                  -- 'handle_selection', 'fallback_clarify' 등
    previous_node TEXT,

    -- ============================================================
    -- 엣지케이스 분류
    -- ============================================================
    edge_case_code TEXT NOT NULL,       -- 'EC-D03', 'EC-S02' 등
    edge_case_type TEXT NOT NULL,       -- 'index_out_of_range', 'no_code_submitted' 등
    severity TEXT DEFAULT 'low',        -- 'low', 'medium', 'high', 'critical'

    -- ============================================================
    -- 컨텍스트 (상세 디버깅용)
    -- ============================================================
    user_message TEXT,                  -- 사용자 입력 원문
    intent_detected TEXT,               -- 감지된 의도
    intent_confidence FLOAT,            -- 의도 신뢰도
    state_snapshot JSONB,               -- 당시 상태 스냅샷 (search_results, collected_info 등)

    -- ============================================================
    -- 처리 결과
    -- ============================================================
    fallback_triggered BOOLEAN DEFAULT FALSE,
    response_message TEXT,              -- 실제 응답 메시지
    was_recovered BOOLEAN DEFAULT FALSE, -- 자동 복구 여부

    -- ============================================================
    -- 분석/관리용
    -- ============================================================
    tags TEXT[] DEFAULT '{}',           -- 분석용 태그
    notes TEXT,                         -- 개발자 메모 (나중에 추가)
    resolved BOOLEAN DEFAULT FALSE,     -- 해결 여부 (업데이트 후 체크)
    resolved_at TIMESTAMPTZ,
    resolved_in_version TEXT,           -- 해결된 버전

    -- ============================================================
    -- GA4 연동
    -- ============================================================
    ga4_event_sent BOOLEAN DEFAULT FALSE,
    ga4_event_id TEXT
);

-- 2. 인덱스
CREATE INDEX IF NOT EXISTS edge_case_logs_user_idx ON edge_case_logs(user_id);
CREATE INDEX IF NOT EXISTS edge_case_logs_session_idx ON edge_case_logs(session_id);
CREATE INDEX IF NOT EXISTS edge_case_logs_code_idx ON edge_case_logs(edge_case_code);
CREATE INDEX IF NOT EXISTS edge_case_logs_type_idx ON edge_case_logs(edge_case_type);
CREATE INDEX IF NOT EXISTS edge_case_logs_graph_idx ON edge_case_logs(graph_name);
CREATE INDEX IF NOT EXISTS edge_case_logs_severity_idx ON edge_case_logs(severity);
CREATE INDEX IF NOT EXISTS edge_case_logs_created_idx ON edge_case_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS edge_case_logs_resolved_idx ON edge_case_logs(resolved) WHERE resolved = FALSE;
CREATE INDEX IF NOT EXISTS edge_case_logs_tags_idx ON edge_case_logs USING GIN(tags);

-- 3. 집계 뷰 (분석 대시보드용)
CREATE OR REPLACE VIEW edge_case_summary AS
SELECT
    edge_case_code,
    edge_case_type,
    graph_name,
    severity,
    COUNT(*) as occurrence_count,
    COUNT(DISTINCT user_id) as affected_users,
    COUNT(DISTINCT session_id) as affected_sessions,
    SUM(CASE WHEN fallback_triggered THEN 1 ELSE 0 END) as fallback_count,
    SUM(CASE WHEN was_recovered THEN 1 ELSE 0 END) as recovered_count,
    SUM(CASE WHEN resolved THEN 1 ELSE 0 END) as resolved_count,
    MIN(created_at) as first_occurrence,
    MAX(created_at) as last_occurrence,
    DATE_TRUNC('day', created_at) as occurrence_date
FROM edge_case_logs
GROUP BY edge_case_code, edge_case_type, graph_name, severity, DATE_TRUNC('day', created_at)
ORDER BY occurrence_count DESC;

-- 4. 일별 트렌드 뷰
CREATE OR REPLACE VIEW edge_case_daily_trend AS
SELECT
    DATE_TRUNC('day', created_at) as date,
    edge_case_code,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users
FROM edge_case_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), edge_case_code
ORDER BY date DESC, count DESC;

-- 5. RLS 정책
ALTER TABLE edge_case_logs ENABLE ROW LEVEL SECURITY;

-- Service role 전체 접근
DO $$ BEGIN
    CREATE POLICY "Service role full access to edge_case_logs"
        ON edge_case_logs FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 사용자는 자신의 로그만 조회 가능
DO $$ BEGIN
    CREATE POLICY "Users can view own edge case logs"
        ON edge_case_logs FOR SELECT TO authenticated
        USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 6. 로깅 함수
CREATE OR REPLACE FUNCTION log_edge_case(
    p_user_id UUID,
    p_session_id TEXT,
    p_graph_name TEXT,
    p_current_node TEXT,
    p_previous_node TEXT,
    p_edge_case_code TEXT,
    p_edge_case_type TEXT,
    p_severity TEXT DEFAULT 'low',
    p_user_message TEXT DEFAULT NULL,
    p_intent_detected TEXT DEFAULT NULL,
    p_intent_confidence FLOAT DEFAULT NULL,
    p_state_snapshot JSONB DEFAULT NULL,
    p_fallback_triggered BOOLEAN DEFAULT FALSE,
    p_response_message TEXT DEFAULT NULL,
    p_was_recovered BOOLEAN DEFAULT FALSE,
    p_tags TEXT[] DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO edge_case_logs (
        user_id, session_id, graph_name, current_node, previous_node,
        edge_case_code, edge_case_type, severity,
        user_message, intent_detected, intent_confidence, state_snapshot,
        fallback_triggered, response_message, was_recovered, tags
    ) VALUES (
        p_user_id, p_session_id, p_graph_name, p_current_node, p_previous_node,
        p_edge_case_code, p_edge_case_type, p_severity,
        p_user_message, p_intent_detected, p_intent_confidence, p_state_snapshot,
        p_fallback_triggered, p_response_message, p_was_recovered, p_tags
    )
    RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. 분석 함수: 가장 빈번한 엣지케이스
CREATE OR REPLACE FUNCTION get_top_edge_cases(
    p_days INTEGER DEFAULT 7,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    edge_case_code TEXT,
    edge_case_type TEXT,
    graph_name TEXT,
    occurrence_count BIGINT,
    affected_users BIGINT,
    recovery_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ecl.edge_case_code,
        ecl.edge_case_type,
        ecl.graph_name,
        COUNT(*) as occurrence_count,
        COUNT(DISTINCT ecl.user_id) as affected_users,
        (SUM(CASE WHEN ecl.was_recovered THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*)::FLOAT, 0)) as recovery_rate
    FROM edge_case_logs ecl
    WHERE ecl.created_at > NOW() - (p_days || ' days')::INTERVAL
      AND ecl.resolved = FALSE
    GROUP BY ecl.edge_case_code, ecl.edge_case_type, ecl.graph_name
    ORDER BY occurrence_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. 권한 부여
GRANT SELECT ON edge_case_logs TO authenticated;
GRANT ALL ON edge_case_logs TO service_role;
GRANT SELECT ON edge_case_summary TO service_role;
GRANT SELECT ON edge_case_daily_trend TO service_role;
GRANT EXECUTE ON FUNCTION log_edge_case TO service_role;
GRANT EXECUTE ON FUNCTION get_top_edge_cases TO service_role;

-- 완료 메시지
DO $$ BEGIN
    RAISE NOTICE '✅ Edge Case Logs migration completed!';
    RAISE NOTICE '   - edge_case_logs table created';
    RAISE NOTICE '   - edge_case_summary view created';
    RAISE NOTICE '   - edge_case_daily_trend view created';
    RAISE NOTICE '   - log_edge_case function created';
    RAISE NOTICE '   - get_top_edge_cases function created';
END $$;
