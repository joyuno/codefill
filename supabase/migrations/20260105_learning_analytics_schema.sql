-- ============================================================
-- CodeFill Learning Analytics Schema
-- ============================================================
-- 학습 분석 및 개인화를 위한 테이블 스키마
--
-- 포함 내용:
-- 1. attempts 테이블 확장 (문제 유형, 풀이 경로)
-- 2. attempt_details 재설계 (유형별 상세 기록)
-- 3. user_skill_profiles (실력 프로파일)
-- 4. user_memories (세션 요약, 장기 메모리)
-- ============================================================

-- ============================================================
-- 1. attempts 테이블 확장
-- ============================================================

-- 새 컬럼 추가
ALTER TABLE attempts
ADD COLUMN IF NOT EXISTS problem_type VARCHAR(20),      -- blank, puzzle, guided
ADD COLUMN IF NOT EXISTS difficulty VARCHAR(20),        -- easy, medium, hard 등
ADD COLUMN IF NOT EXISTS topics TEXT[],                 -- 문제 주제들
ADD COLUMN IF NOT EXISTS problem_name TEXT,             -- 문제 이름 (비정규화)
ADD COLUMN IF NOT EXISTS total_hints_requested INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS solve_path JSONB,              -- 풀이 경로 기록
ADD COLUMN IF NOT EXISTS session_id TEXT;               -- 세션 식별자

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS attempts_problem_type_idx ON attempts(problem_type);
CREATE INDEX IF NOT EXISTS attempts_difficulty_idx ON attempts(difficulty);
CREATE INDEX IF NOT EXISTS attempts_topics_idx ON attempts USING GIN(topics);
CREATE INDEX IF NOT EXISTS attempts_session_idx ON attempts(session_id);

COMMENT ON COLUMN attempts.problem_type IS '문제 유형: blank(빈칸), puzzle(퍼즐), guided(1대1 대화형)';
COMMENT ON COLUMN attempts.solve_path IS '풀이 경로 JSON: [{"step": 1, "action": "hint", "timestamp": "..."}]';


-- ============================================================
-- 2. attempt_details 재설계
-- ============================================================

-- 기존 테이블 백업 (데이터가 있을 경우)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'attempt_details') THEN
        IF EXISTS (SELECT 1 FROM attempt_details LIMIT 1) THEN
            CREATE TABLE IF NOT EXISTS attempt_details_backup AS SELECT * FROM attempt_details;
        END IF;
    END IF;
END $$;

-- 기존 테이블 삭제 후 재생성
DROP TABLE IF EXISTS attempt_details CASCADE;

CREATE TABLE attempt_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,

    -- 공통 필드
    step_number INTEGER,                    -- 순서
    action_type VARCHAR(50) NOT NULL,       -- 액션 유형
    action_timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- ============================================================
    -- 빈칸 문제 전용
    -- ============================================================
    blank_index INTEGER,                    -- 빈칸 번호 (0-based)
    blank_user_answer TEXT,                 -- 사용자 입력 답
    blank_correct_answer TEXT,              -- 정답
    blank_is_correct BOOLEAN,               -- 정답 여부
    blank_hint_level INTEGER,               -- 힌트 레벨 (0: 미요청, 1: 마스킹, 2: 공개)
    blank_hint_content TEXT,                -- 제공된 힌트 내용

    -- ============================================================
    -- 퍼즐 문제 전용
    -- ============================================================
    puzzle_user_order JSONB,                -- 사용자 블록 순서: [3, 1, 2, 4]
    puzzle_correct_order JSONB,             -- 정답 순서: [1, 2, 3, 4]
    puzzle_wrong_positions JSONB,           -- 틀린 위치들: [{"pos": 0, "expected": 1, "actual": 3}]
    puzzle_hint_content TEXT,               -- 퍼즐 힌트 (첫 틀린 위치 + 이유)
    puzzle_validation_method VARCHAR(20),   -- 검증 방법: exact, functional, judge0

    -- ============================================================
    -- 1대1 대화형 전용
    -- ============================================================
    guided_step INTEGER,                    -- 현재 학습 단계
    guided_user_message TEXT,               -- 사용자 메시지
    guided_tutor_response TEXT,             -- 튜터 응답
    guided_understanding_score FLOAT,       -- 이해도 점수 (0.0~1.0)
    guided_concepts_covered TEXT[],         -- 다룬 개념들
    guided_teaching_action VARCHAR(50),     -- explain, ask_question, give_example, next_step

    -- ============================================================
    -- 힌트 기록 (공통)
    -- ============================================================
    hint_was_requested BOOLEAN DEFAULT FALSE,
    hint_was_helpful BOOLEAN,               -- 사용자 피드백 (optional)

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX attempt_details_attempt_idx ON attempt_details(attempt_id);
CREATE INDEX attempt_details_action_idx ON attempt_details(action_type);
CREATE INDEX attempt_details_blank_idx ON attempt_details(blank_index) WHERE blank_index IS NOT NULL;
CREATE INDEX attempt_details_guided_step_idx ON attempt_details(guided_step) WHERE guided_step IS NOT NULL;

-- 액션 타입 ENUM 체크
COMMENT ON COLUMN attempt_details.action_type IS '
액션 유형:
- blank_submit: 빈칸 답 제출
- blank_hint_request: 빈칸 힌트 요청
- blank_hint_reveal: 힌트 마스킹 해제
- puzzle_submit: 퍼즐 순서 제출
- puzzle_hint_request: 퍼즐 힌트 요청
- guided_message: 대화형 메시지 교환
- guided_step_complete: 학습 단계 완료
- give_up: 포기
- skip: 건너뛰기
';


-- ============================================================
-- 3. user_skill_profiles (사용자 실력 프로파일)
-- ============================================================

CREATE TABLE IF NOT EXISTS user_skill_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,

    -- ============================================================
    -- 주제별 실력 (0.0 ~ 1.0)
    -- ============================================================
    skill_by_topic JSONB DEFAULT '{}'::JSONB,
    -- 예: {"DP": 0.7, "그래프": 0.4, "정렬": 0.9, "구현": 0.6}

    -- ============================================================
    -- 난이도별 성공률
    -- ============================================================
    success_rate_by_difficulty JSONB DEFAULT '{}'::JSONB,
    -- 예: {"easy": {"success": 15, "total": 16}, "medium": {"success": 8, "total": 12}}

    -- ============================================================
    -- 문제 유형별 선호도/성공률
    -- ============================================================
    stats_by_problem_type JSONB DEFAULT '{}'::JSONB,
    -- 예: {"blank": {"success": 20, "total": 25, "avg_time": 120}, "puzzle": {...}}

    -- ============================================================
    -- 학습 패턴
    -- ============================================================
    recent_topics TEXT[],                   -- 최근 학습 주제 (최대 10개)
    recent_difficulties TEXT[],             -- 최근 푼 난이도
    preferred_problem_type VARCHAR(20),     -- 선호 문제 유형
    preferred_language VARCHAR(20),         -- 선호 언어
    avg_solve_time_seconds INTEGER,         -- 평균 풀이 시간
    avg_hints_per_problem FLOAT,            -- 문제당 평균 힌트 사용

    -- ============================================================
    -- 약점/강점 분석
    -- ============================================================
    weak_topics TEXT[],                     -- 약한 주제 (실력 < 0.4)
    strong_topics TEXT[],                   -- 강한 주제 (실력 > 0.7)
    common_error_patterns JSONB,            -- 자주 하는 실수 패턴
    -- 예: {"off_by_one": 5, "null_check": 3, "edge_case": 2}

    -- ============================================================
    -- 학습 스타일 (튜터링용)
    -- ============================================================
    learning_style JSONB DEFAULT '{}'::JSONB,
    -- 예: {
    --   "prefers_examples": true,
    --   "prefers_analogies": true,
    --   "hint_sensitivity": "low",  -- low: 힌트 잘 안 씀, high: 자주 씀
    --   "pace": "slow"              -- slow, medium, fast
    -- }

    -- ============================================================
    -- 통계
    -- ============================================================
    total_problems_solved INTEGER DEFAULT 0,
    total_problems_attempted INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,       -- 연속 정답 수
    longest_streak INTEGER DEFAULT 0,
    total_xp_earned INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS user_skill_profiles_user_idx ON user_skill_profiles(user_id);
CREATE INDEX IF NOT EXISTS user_skill_profiles_weak_topics_idx ON user_skill_profiles USING GIN(weak_topics);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_user_skill_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_user_skill_profiles_updated_at ON user_skill_profiles;
CREATE TRIGGER trigger_user_skill_profiles_updated_at
    BEFORE UPDATE ON user_skill_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_skill_profiles_updated_at();


-- ============================================================
-- 4. user_memories (세션 요약, 장기 메모리)
-- ============================================================

-- pgvector 확장 확인 (이미 있으면 무시)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS user_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- ============================================================
    -- 세션 정보
    -- ============================================================
    session_id TEXT NOT NULL,
    session_type VARCHAR(50),               -- problem_solving, exploration, free_chat

    -- ============================================================
    -- 요약 내용
    -- ============================================================
    summary TEXT NOT NULL,                  -- 세션 요약 (2-3문장)
    key_topics TEXT[],                      -- 주요 주제
    key_concepts TEXT[],                    -- 다룬 개념들

    -- ============================================================
    -- 학습 인사이트
    -- ============================================================
    concepts_learned TEXT[],                -- 이해한 개념들
    concepts_struggling TEXT[],             -- 어려워한 개념들
    teaching_notes TEXT[],                  -- 다음 세션을 위한 교육 노트
    -- 예: ["비유로 설명하면 이해 잘함", "시간복잡도 추가 설명 필요"]

    student_questions TEXT[],               -- 학생이 한 질문들
    breakthrough_moments TEXT[],            -- "아하!" 순간들

    -- ============================================================
    -- 문제 풀이 기록 (있을 경우)
    -- ============================================================
    problem_id TEXT,
    problem_name TEXT,
    problem_type VARCHAR(20),
    problem_difficulty VARCHAR(20),
    was_successful BOOLEAN,
    hints_needed INTEGER,
    time_spent_seconds INTEGER,
    attempt_count INTEGER,

    -- ============================================================
    -- 대화 스타일/톤 기록
    -- ============================================================
    conversation_tone VARCHAR(50),          -- encouraging, challenging, neutral
    student_mood VARCHAR(50),               -- frustrated, confident, curious
    effective_approaches TEXT[],            -- 효과적이었던 교육 방법

    -- ============================================================
    -- 임베딩 (의미 검색용)
    -- ============================================================
    summary_embedding vector(1536),

    -- ============================================================
    -- 메타데이터
    -- ============================================================
    message_count INTEGER,                  -- 세션 내 메시지 수
    duration_seconds INTEGER,               -- 세션 지속 시간

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS user_memories_user_idx ON user_memories(user_id);
CREATE INDEX IF NOT EXISTS user_memories_session_idx ON user_memories(session_id);
CREATE INDEX IF NOT EXISTS user_memories_topics_idx ON user_memories USING GIN(key_topics);
CREATE INDEX IF NOT EXISTS user_memories_created_idx ON user_memories(created_at DESC);

-- 벡터 유사도 검색용 인덱스
-- Note: Supabase의 pgvector 버전에 따라 operator class가 다를 수 있음
-- 현재 버전에서는 기본 vector_l2_ops 사용
-- 추후 pgvector 업그레이드 후 cosine 거리 인덱스로 변경 가능
-- CREATE INDEX IF NOT EXISTS user_memories_embedding_idx
-- ON user_memories
-- USING hnsw (summary_embedding vector_cosine_ops);


-- ============================================================
-- 5. 검색 함수들
-- ============================================================

-- 사용자의 최근 메모리 검색
CREATE OR REPLACE FUNCTION get_recent_user_memories(
    p_user_id UUID,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    session_id TEXT,
    summary TEXT,
    key_topics TEXT[],
    concepts_learned TEXT[],
    concepts_struggling TEXT[],
    teaching_notes TEXT[],
    problem_name TEXT,
    was_successful BOOLEAN,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        um.id,
        um.session_id,
        um.summary,
        um.key_topics,
        um.concepts_learned,
        um.concepts_struggling,
        um.teaching_notes,
        um.problem_name,
        um.was_successful,
        um.created_at
    FROM user_memories um
    WHERE um.user_id = p_user_id
    ORDER BY um.created_at DESC
    LIMIT p_limit;
END;
$$;


-- 의미 기반 관련 메모리 검색
-- Note: Supabase 환경에서 vector 타입이 함수 시그니처에서 인식되지 않음
-- 추후 pgvector 확장 업그레이드 후 활성화 필요
/*
CREATE OR REPLACE FUNCTION search_user_memories_by_similarity(
    p_query_embedding vector(1536),
    p_user_id UUID,
    p_match_threshold FLOAT DEFAULT 0.3,
    p_match_count INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    summary TEXT,
    key_topics TEXT[],
    concepts_learned TEXT[],
    concepts_struggling TEXT[],
    teaching_notes TEXT[],
    problem_name TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        um.id,
        um.summary,
        um.key_topics,
        um.concepts_learned,
        um.concepts_struggling,
        um.teaching_notes,
        um.problem_name,
        1 - (um.summary_embedding <=> p_query_embedding) as similarity
    FROM user_memories um
    WHERE um.user_id = p_user_id
        AND um.summary_embedding IS NOT NULL
        AND 1 - (um.summary_embedding <=> p_query_embedding) > p_match_threshold
    ORDER BY um.summary_embedding <=> p_query_embedding
    LIMIT p_match_count;
END;
$$;
*/


-- 주제 기반 메모리 검색
CREATE OR REPLACE FUNCTION search_user_memories_by_topic(
    p_user_id UUID,
    p_topics TEXT[],
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    summary TEXT,
    key_topics TEXT[],
    concepts_struggling TEXT[],
    teaching_notes TEXT[],
    problem_name TEXT,
    topic_match_count INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        um.id,
        um.summary,
        um.key_topics,
        um.concepts_struggling,
        um.teaching_notes,
        um.problem_name,
        (SELECT COUNT(*)::INTEGER FROM unnest(um.key_topics) t WHERE t = ANY(p_topics)) as topic_match_count
    FROM user_memories um
    WHERE um.user_id = p_user_id
        AND um.key_topics && p_topics  -- 배열 겹침 체크
    ORDER BY topic_match_count DESC, um.created_at DESC
    LIMIT p_limit;
END;
$$;


-- ============================================================
-- 6. 사용자 통계 업데이트 함수
-- ============================================================

CREATE OR REPLACE FUNCTION update_user_skill_after_attempt(
    p_user_id UUID,
    p_topics TEXT[],
    p_difficulty VARCHAR(20),
    p_problem_type VARCHAR(20),
    p_is_correct BOOLEAN,
    p_hints_used INTEGER,
    p_time_spent INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_skill_by_topic JSONB;
    v_success_rate JSONB;
    v_stats_by_type JSONB;
    v_topic TEXT;
    v_current_skill FLOAT;
    v_new_skill FLOAT;
    v_current_rate JSONB;
BEGIN
    -- 기존 프로파일 조회 또는 생성
    INSERT INTO user_skill_profiles (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id) DO NOTHING;

    SELECT skill_by_topic, success_rate_by_difficulty, stats_by_problem_type
    INTO v_skill_by_topic, v_success_rate, v_stats_by_type
    FROM user_skill_profiles
    WHERE user_id = p_user_id;

    -- 주제별 실력 업데이트 (ELO-like)
    FOREACH v_topic IN ARRAY p_topics
    LOOP
        v_current_skill := COALESCE((v_skill_by_topic->>v_topic)::FLOAT, 0.5);

        IF p_is_correct THEN
            -- 정답: 실력 상승 (상한에 가까울수록 천천히)
            v_new_skill := v_current_skill + 0.05 * (1 - v_current_skill);
        ELSE
            -- 오답: 실력 하락 (하한에 가까울수록 천천히)
            v_new_skill := v_current_skill - 0.03 * v_current_skill;
        END IF;

        -- 범위 제한 (0.1 ~ 0.95)
        v_new_skill := GREATEST(0.1, LEAST(0.95, v_new_skill));
        v_skill_by_topic := jsonb_set(v_skill_by_topic, ARRAY[v_topic], to_jsonb(ROUND(v_new_skill::NUMERIC, 3)));
    END LOOP;

    -- 난이도별 성공률 업데이트
    v_current_rate := COALESCE(v_success_rate->p_difficulty, '{"success": 0, "total": 0}'::JSONB);
    v_current_rate := jsonb_set(v_current_rate, '{total}', to_jsonb((v_current_rate->>'total')::INTEGER + 1));
    IF p_is_correct THEN
        v_current_rate := jsonb_set(v_current_rate, '{success}', to_jsonb((v_current_rate->>'success')::INTEGER + 1));
    END IF;
    v_success_rate := jsonb_set(v_success_rate, ARRAY[p_difficulty], v_current_rate);

    -- 문제 유형별 통계 업데이트
    v_current_rate := COALESCE(v_stats_by_type->p_problem_type, '{"success": 0, "total": 0, "total_time": 0}'::JSONB);
    v_current_rate := jsonb_set(v_current_rate, '{total}', to_jsonb((v_current_rate->>'total')::INTEGER + 1));
    v_current_rate := jsonb_set(v_current_rate, '{total_time}', to_jsonb((v_current_rate->>'total_time')::INTEGER + COALESCE(p_time_spent, 0)));
    IF p_is_correct THEN
        v_current_rate := jsonb_set(v_current_rate, '{success}', to_jsonb((v_current_rate->>'success')::INTEGER + 1));
    END IF;
    v_stats_by_type := jsonb_set(v_stats_by_type, ARRAY[p_problem_type], v_current_rate);

    -- 프로파일 업데이트
    UPDATE user_skill_profiles
    SET
        skill_by_topic = v_skill_by_topic,
        success_rate_by_difficulty = v_success_rate,
        stats_by_problem_type = v_stats_by_type,
        total_problems_attempted = total_problems_attempted + 1,
        total_problems_solved = total_problems_solved + (CASE WHEN p_is_correct THEN 1 ELSE 0 END),
        recent_topics = (
            SELECT ARRAY(
                SELECT DISTINCT unnest
                FROM unnest(ARRAY_CAT(p_topics, COALESCE(recent_topics, '{}'::TEXT[])))
                LIMIT 10
            )
        ),
        weak_topics = (
            SELECT ARRAY(
                SELECT key
                FROM jsonb_each_text(v_skill_by_topic)
                WHERE value::FLOAT < 0.4
            )
        ),
        strong_topics = (
            SELECT ARRAY(
                SELECT key
                FROM jsonb_each_text(v_skill_by_topic)
                WHERE value::FLOAT > 0.7
            )
        ),
        current_streak = CASE WHEN p_is_correct THEN current_streak + 1 ELSE 0 END,
        longest_streak = GREATEST(longest_streak, CASE WHEN p_is_correct THEN current_streak + 1 ELSE current_streak END)
    WHERE user_id = p_user_id;
END;
$$;


-- ============================================================
-- 7. RLS 정책
-- ============================================================

-- user_skill_profiles
ALTER TABLE user_skill_profiles ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    CREATE POLICY "Users can view own skill profile"
        ON user_skill_profiles FOR SELECT
        USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE POLICY "Users can update own skill profile"
        ON user_skill_profiles FOR UPDATE
        USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE POLICY "Service role full access to skill profiles"
        ON user_skill_profiles FOR ALL
        TO service_role
        USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- user_memories
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    CREATE POLICY "Users can view own memories"
        ON user_memories FOR SELECT
        USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE POLICY "Service role full access to memories"
        ON user_memories FOR ALL
        TO service_role
        USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- attempt_details
ALTER TABLE attempt_details ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    CREATE POLICY "Users can view own attempt details"
        ON attempt_details FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM attempts a
                WHERE a.id = attempt_details.attempt_id
                AND a.user_id = auth.uid()
            )
        );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE POLICY "Service role full access to attempt details"
        ON attempt_details FOR ALL
        TO service_role
        USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ============================================================
-- 8. 권한 설정
-- ============================================================

-- 함수 실행 권한
GRANT EXECUTE ON FUNCTION get_recent_user_memories TO authenticated;
-- GRANT EXECUTE ON FUNCTION search_user_memories_by_similarity TO authenticated;  -- 비활성화 (벡터 함수 미지원)
GRANT EXECUTE ON FUNCTION search_user_memories_by_topic TO authenticated;
GRANT EXECUTE ON FUNCTION update_user_skill_after_attempt TO service_role;

-- 테이블 권한
GRANT SELECT ON user_skill_profiles TO authenticated;
GRANT SELECT ON user_memories TO authenticated;
GRANT SELECT ON attempt_details TO authenticated;

GRANT ALL ON user_skill_profiles TO service_role;
GRANT ALL ON user_memories TO service_role;
GRANT ALL ON attempt_details TO service_role;


-- ============================================================
-- 완료 메시지
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Learning Analytics Schema migration completed!';
    RAISE NOTICE '   - attempts table extended';
    RAISE NOTICE '   - attempt_details table recreated';
    RAISE NOTICE '   - user_skill_profiles table created';
    RAISE NOTICE '   - user_memories table created';
    RAISE NOTICE '   - Search functions created';
    RAISE NOTICE '   - RLS policies applied';
END $$;
