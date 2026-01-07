-- ============================================================
-- 채팅 세션 및 메시지 테이블
-- 대화 히스토리를 DB에 저장하여 새로고침 시에도 유지
-- ============================================================

-- 1. 채팅 세션 테이블
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- 세션 상태
    session_type VARCHAR(50) DEFAULT 'exploration',  -- exploration, problem_solving
    current_stage VARCHAR(50) DEFAULT 'intent',      -- intent, collection, discovery, solving

    -- 수집된 정보 (정보 수집 단계)
    collected_info JSONB DEFAULT '{}',

    -- 세션 상태 (awaiting_confirmation, suggested_value 등)
    session_state JSONB DEFAULT '{}',

    -- 현재 문제 (있을 경우)
    current_problem_id UUID,
    current_problem_data JSONB,  -- 문제 전체 데이터 (생성된 문제 포함)

    -- 풀이 진행 상태
    attempt_id UUID,
    hints_used INTEGER DEFAULT 0,
    solve_start_time TIMESTAMPTZ,

    -- 메타데이터
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 채팅 메시지 테이블
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,

    -- 메시지 내용
    role VARCHAR(20) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,

    -- 메시지 메타데이터
    message_type VARCHAR(50),   -- text, problem_display, hint, feedback 등
    metadata JSONB,             -- 추가 데이터 (chips, buttons 등)

    -- 순서
    sequence_number INTEGER NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 기존 테이블에 누락된 컬럼 추가
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS sequence_number INTEGER;

-- 인덱스
CREATE INDEX IF NOT EXISTS chat_sessions_user_idx ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS chat_sessions_updated_idx ON chat_sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS chat_messages_session_idx ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS chat_messages_sequence_idx ON chat_messages(session_id, sequence_number);

-- RLS 정책
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- chat_sessions 정책
DO $$ BEGIN
    CREATE POLICY "Users can view own sessions"
        ON chat_sessions FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can insert own sessions"
        ON chat_sessions FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can update own sessions"
        ON chat_sessions FOR UPDATE TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can delete own sessions"
        ON chat_sessions FOR DELETE TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- chat_messages 정책
DO $$ BEGIN
    CREATE POLICY "Users can view messages in own sessions"
        ON chat_messages FOR SELECT TO authenticated
        USING (EXISTS (SELECT 1 FROM chat_sessions cs WHERE cs.id = chat_messages.session_id AND cs.user_id = auth.uid()));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can insert messages in own sessions"
        ON chat_messages FOR INSERT TO authenticated
        WITH CHECK (EXISTS (SELECT 1 FROM chat_sessions cs WHERE cs.id = chat_messages.session_id AND cs.user_id = auth.uid()));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- service_role 전체 권한
DO $$ BEGIN
    CREATE POLICY "Service role full access to sessions"
        ON chat_sessions FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to messages"
        ON chat_messages FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON chat_sessions TO authenticated;
GRANT SELECT, INSERT ON chat_messages TO authenticated;
GRANT ALL ON chat_sessions TO service_role;
GRANT ALL ON chat_messages TO service_role;

-- 함수: 세션 생성 또는 가져오기
CREATE OR REPLACE FUNCTION get_or_create_chat_session(
    p_user_id UUID,
    p_session_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_session_id UUID;
    v_last_session_at TIMESTAMPTZ;
BEGIN
    -- 1. 특정 session_id가 제공되면 해당 세션 반환
    IF p_session_id IS NOT NULL THEN
        SELECT id INTO v_session_id
        FROM chat_sessions
        WHERE id = p_session_id AND user_id = p_user_id;

        IF v_session_id IS NOT NULL THEN
            -- 세션 업데이트 시간 갱신
            UPDATE chat_sessions
            SET updated_at = NOW()
            WHERE id = v_session_id;

            RETURN v_session_id;
        END IF;
    END IF;

    -- 2. 최근 활성 세션 찾기 (30분 이내)
    SELECT id, last_message_at INTO v_session_id, v_last_session_at
    FROM chat_sessions
    WHERE user_id = p_user_id
    ORDER BY last_message_at DESC
    LIMIT 1;

    -- 30분 이내 세션이 있으면 재사용
    IF v_session_id IS NOT NULL AND v_last_session_at > NOW() - INTERVAL '30 minutes' THEN
        UPDATE chat_sessions
        SET updated_at = NOW()
        WHERE id = v_session_id;

        RETURN v_session_id;
    END IF;

    -- 3. 새 세션 생성
    INSERT INTO chat_sessions (user_id)
    VALUES (p_user_id)
    RETURNING id INTO v_session_id;

    RETURN v_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 함수: 메시지 추가
CREATE OR REPLACE FUNCTION add_chat_message(
    p_session_id UUID,
    p_role VARCHAR(20),
    p_content TEXT,
    p_message_type VARCHAR(50) DEFAULT 'text',
    p_metadata JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_message_id UUID;
    v_sequence INTEGER;
BEGIN
    -- 다음 sequence_number 계산
    SELECT COALESCE(MAX(sequence_number), 0) + 1 INTO v_sequence
    FROM chat_messages
    WHERE session_id = p_session_id;

    -- 메시지 삽입
    INSERT INTO chat_messages (session_id, role, content, message_type, metadata, sequence_number)
    VALUES (p_session_id, p_role, p_content, p_message_type, p_metadata)
    RETURNING id INTO v_message_id;

    -- 세션 업데이트
    UPDATE chat_sessions
    SET
        message_count = message_count + 1,
        last_message_at = NOW(),
        updated_at = NOW()
    WHERE id = p_session_id;

    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 함수: 세션 상태 업데이트
CREATE OR REPLACE FUNCTION update_chat_session_state(
    p_session_id UUID,
    p_stage VARCHAR(50) DEFAULT NULL,
    p_collected_info JSONB DEFAULT NULL,
    p_session_state JSONB DEFAULT NULL,
    p_current_problem_data JSONB DEFAULT NULL,
    p_attempt_id UUID DEFAULT NULL,
    p_hints_used INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE chat_sessions
    SET
        current_stage = COALESCE(p_stage, current_stage),
        collected_info = COALESCE(p_collected_info, collected_info),
        session_state = COALESCE(p_session_state, session_state),
        current_problem_data = COALESCE(p_current_problem_data, current_problem_data),
        attempt_id = COALESCE(p_attempt_id, attempt_id),
        hints_used = COALESCE(p_hints_used, hints_used),
        updated_at = NOW()
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 함수: 세션의 최근 메시지 가져오기
CREATE OR REPLACE FUNCTION get_chat_history(
    p_session_id UUID,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    role VARCHAR(20),
    content TEXT,
    message_type VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.role,
        cm.content,
        cm.message_type,
        cm.metadata,
        cm.created_at
    FROM chat_messages cm
    WHERE cm.session_id = p_session_id
    ORDER BY cm.sequence_number DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION get_or_create_chat_session(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_or_create_chat_session(UUID, UUID) TO service_role;
GRANT EXECUTE ON FUNCTION add_chat_message(UUID, VARCHAR, TEXT, VARCHAR, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION add_chat_message(UUID, VARCHAR, TEXT, VARCHAR, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION update_chat_session_state(UUID, VARCHAR, JSONB, JSONB, JSONB, UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION update_chat_session_state(UUID, VARCHAR, JSONB, JSONB, JSONB, UUID, INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION get_chat_history(UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_chat_history(UUID, INTEGER) TO service_role;

DO $$ BEGIN RAISE NOTICE 'Chat sessions tables and functions created successfully'; END $$;
