-- ============================================================
-- 사용자 상호작용 테이블 (협업 필터링용)
-- NoSQL-like JSONB 구조로 유연한 데이터 저장
-- ============================================================

-- 1. 사용자 상호작용 테이블
-- 채팅 메시지마다 분석된 상호작용 데이터 저장
CREATE TABLE IF NOT EXISTS user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,

    -- 상호작용 유형
    interaction_type VARCHAR(50) NOT NULL,  -- topic_select, difficulty_select, problem_select, hint_request, complete, skip

    -- 상호작용 데이터 (NoSQL-like)
    interaction_data JSONB NOT NULL DEFAULT '{}',
    -- 예: {
    --   "topic": "dp",
    --   "difficulty": "medium",
    --   "language": "python",
    --   "problem_id": "...",
    --   "response_time_ms": 1234,
    --   "was_helpful": true
    -- }

    -- 사용자 메타데이터 (협업 필터링용)
    user_metadata JSONB DEFAULT '{}',
    -- 예: {
    --   "goal": "big_tech",
    --   "level": "intermediate",
    --   "preferred_topics": ["dp", "graph"]
    -- }

    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 사용자 선호도 집계 테이블 (매터리얼라이즈드 뷰 대체)
-- 주기적으로 업데이트되는 사용자 선호도 요약
CREATE TABLE IF NOT EXISTS user_preferences_summary (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    -- 주제 선호도 (JSONB)
    topic_preferences JSONB DEFAULT '{}',
    -- 예: {"dp": 0.8, "graph": 0.6, "sorting": 0.3}

    -- 난이도 선호도
    difficulty_preferences JSONB DEFAULT '{}',
    -- 예: {"medium": 0.7, "hard": 0.2, "easy": 0.1}

    -- 언어 선호도
    language_preferences JSONB DEFAULT '{}',
    -- 예: {"python": 0.9, "java": 0.1}

    -- 문제 유형 선호도
    problem_type_preferences JSONB DEFAULT '{}',
    -- 예: {"blank": 0.5, "puzzle": 0.3, "guided": 0.2}

    -- 학습 패턴
    learning_pattern JSONB DEFAULT '{}',
    -- 예: {
    --   "avg_session_duration_min": 25,
    --   "preferred_time": "evening",
    --   "hint_usage_rate": 0.3,
    --   "completion_rate": 0.75
    -- }

    -- 메타데이터
    goal VARCHAR(50),  -- big_tech, skill_up, etc.
    level VARCHAR(50),  -- beginner, intermediate, advanced

    -- 유사 사용자 (협업 필터링용)
    similar_users JSONB DEFAULT '[]',
    -- 예: [{"user_id": "...", "similarity": 0.85}, ...]

    -- 업데이트 시간
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS user_interactions_user_idx ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS user_interactions_type_idx ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS user_interactions_created_idx ON user_interactions(created_at DESC);
CREATE INDEX IF NOT EXISTS user_interactions_data_gin ON user_interactions USING GIN (interaction_data);
CREATE INDEX IF NOT EXISTS user_preferences_goal_idx ON user_preferences_summary(goal);
CREATE INDEX IF NOT EXISTS user_preferences_level_idx ON user_preferences_summary(level);

-- RLS 정책
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences_summary ENABLE ROW LEVEL SECURITY;

-- user_interactions 정책
DO $$ BEGIN
    CREATE POLICY "Users can view own interactions"
        ON user_interactions FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can insert own interactions"
        ON user_interactions FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- user_preferences_summary 정책
DO $$ BEGIN
    CREATE POLICY "Users can view own preferences"
        ON user_preferences_summary FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- service_role 전체 권한
DO $$ BEGIN
    CREATE POLICY "Service role full access to interactions"
        ON user_interactions FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to preferences"
        ON user_preferences_summary FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 권한 부여
GRANT SELECT, INSERT ON user_interactions TO authenticated;
GRANT ALL ON user_interactions TO service_role;
GRANT SELECT ON user_preferences_summary TO authenticated;
GRANT ALL ON user_preferences_summary TO service_role;

-- ============================================================
-- 함수: 상호작용 기록
-- ============================================================
CREATE OR REPLACE FUNCTION log_user_interaction(
    p_user_id UUID,
    p_session_id UUID,
    p_interaction_type VARCHAR(50),
    p_interaction_data JSONB,
    p_user_metadata JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_interaction_id UUID;
BEGIN
    INSERT INTO user_interactions (user_id, session_id, interaction_type, interaction_data, user_metadata)
    VALUES (p_user_id, p_session_id, p_interaction_type, p_interaction_data, COALESCE(p_user_metadata, '{}'))
    RETURNING id INTO v_interaction_id;

    RETURN v_interaction_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 함수: 유사 사용자 찾기 (협업 필터링)
-- ============================================================
CREATE OR REPLACE FUNCTION find_similar_users(
    p_user_id UUID,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    similar_user_id UUID,
    similarity_score FLOAT,
    common_topics JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH user_prefs AS (
        SELECT
            topic_preferences,
            difficulty_preferences,
            goal,
            level
        FROM user_preferences_summary
        WHERE user_id = p_user_id
    ),
    other_users AS (
        SELECT
            ups.user_id,
            ups.topic_preferences,
            ups.difficulty_preferences,
            ups.goal,
            ups.level
        FROM user_preferences_summary ups
        WHERE ups.user_id != p_user_id
    )
    SELECT
        ou.user_id AS similar_user_id,
        -- 유사도 계산 (간단한 점수)
        (
            CASE WHEN ou.goal = up.goal THEN 0.3 ELSE 0 END +
            CASE WHEN ou.level = up.level THEN 0.2 ELSE 0 END +
            -- 주제 겹침 (최대 0.5)
            0.5 * (
                SELECT COUNT(*)::float / GREATEST(
                    jsonb_array_length(
                        COALESCE(
                            (SELECT jsonb_agg(key) FROM jsonb_each(ou.topic_preferences)),
                            '[]'::jsonb
                        )
                    ),
                    1
                )
                FROM jsonb_each(ou.topic_preferences) ot
                WHERE up.topic_preferences ? ot.key
            )
        )::float AS similarity_score,
        -- 공통 주제
        (
            SELECT jsonb_agg(ot.key)
            FROM jsonb_each(ou.topic_preferences) ot
            WHERE up.topic_preferences ? ot.key
        ) AS common_topics
    FROM other_users ou, user_prefs up
    ORDER BY similarity_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 함수: 협업 필터링 기반 추천
-- ============================================================
CREATE OR REPLACE FUNCTION get_collaborative_recommendations(
    p_user_id UUID,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    topic VARCHAR,
    difficulty VARCHAR,
    score FLOAT,
    reason TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH similar_users AS (
        SELECT similar_user_id, similarity_score
        FROM find_similar_users(p_user_id, 5)
    ),
    similar_user_topics AS (
        SELECT
            ui.interaction_data->>'topic' AS topic,
            ui.interaction_data->>'difficulty' AS difficulty,
            su.similarity_score,
            ui.interaction_type
        FROM user_interactions ui
        JOIN similar_users su ON ui.user_id = su.similar_user_id
        WHERE ui.interaction_type IN ('complete', 'problem_select')
        AND ui.created_at > NOW() - INTERVAL '30 days'
    )
    SELECT
        sut.topic::varchar,
        sut.difficulty::varchar,
        SUM(sut.similarity_score)::float AS score,
        '비슷한 사용자들이 푼 문제'::text AS reason
    FROM similar_user_topics sut
    WHERE sut.topic IS NOT NULL
    GROUP BY sut.topic, sut.difficulty
    ORDER BY score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION log_user_interaction(UUID, UUID, VARCHAR, JSONB, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION log_user_interaction(UUID, UUID, VARCHAR, JSONB, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION find_similar_users(UUID, INT) TO service_role;
GRANT EXECUTE ON FUNCTION get_collaborative_recommendations(UUID, INT) TO service_role;

DO $$ BEGIN RAISE NOTICE 'User interactions and collaborative filtering tables created successfully'; END $$;
