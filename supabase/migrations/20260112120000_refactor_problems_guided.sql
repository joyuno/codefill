-- =====================================================
-- problems_guided 테이블 전면 리팩토링
-- 날짜: 2026-01-12
-- 목적: 1대1 대화형 문제의 새로운 학습 흐름 지원
-- =====================================================
--
-- 새로운 흐름:
--   1. 사용자가 1대1 대화형 선택
--   2. LLM이 개념 정의, 변수 정의, 접근법 가이드 생성
--   3. 초반 2줄 맛보기 코드 제공 (일반 구현과 차별화)
--   4. 사용자와 대화 (강력한 힌트)
--   5. 피드백 에이전트 실행 전까지 대화 내용 저장
--   6. 정답 시도 시 코드를 check_points에 저장
--
-- =====================================================

-- =====================================================
-- 1. 기존 테이블 및 관련 객체 삭제
-- =====================================================
-- 트리거 삭제
DROP TRIGGER IF EXISTS update_problems_guided_updated_at ON problems_guided;

-- RLS 정책 삭제
DROP POLICY IF EXISTS "Anyone can view problems_guided" ON problems_guided;
DROP POLICY IF EXISTS "Service role can manage problems_guided" ON problems_guided;
DROP POLICY IF EXISTS "Users can view own problems_guided" ON problems_guided;
DROP POLICY IF EXISTS "Users can manage own problems_guided" ON problems_guided;

-- 인덱스 삭제
DROP INDEX IF EXISTS idx_problems_guided_base_problem_id;
DROP INDEX IF EXISTS problems_guided_original_id_idx;

-- 테이블 삭제
DROP TABLE IF EXISTS problems_guided CASCADE;

-- =====================================================
-- 2. 새 problems_guided 테이블 생성
-- =====================================================
CREATE TABLE problems_guided (
    -- 기본 키
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 외래 키 (NOT NULL)
    base_problem_id UUID NOT NULL REFERENCES base_problems(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 언어
    language VARCHAR(20) NOT NULL DEFAULT 'python',

    -- ============================================================
    -- 초기 가이드 (LLM 생성) - 문제 시작 시 한 번 생성
    -- ============================================================

    -- 개념 설명: 핵심 알고리즘/자료구조 설명
    -- 예: "이 문제는 DP(동적 프로그래밍)를 사용합니다. DP는 큰 문제를 작은 부분 문제로 나누어..."
    concept_explanation TEXT NOT NULL,

    -- 변수 가이드: 필요한 변수들의 역할, 타입, 초기값
    -- JSON 형태: {"variables": [{"name": "dp", "role": "메모이제이션 배열", "type": "list", "initial": "[0] * (n+1)"}]}
    variables_guide JSONB NOT NULL,

    -- 접근법 가이드: 어떻게 시작할지 간단한 설명
    -- 예: "먼저 입력을 받고, DP 배열을 초기화한 후, 점화식을 적용합니다."
    approach_guide TEXT NOT NULL,

    -- 맛보기 코드: 함수 정의 제외 앞 2줄 정도
    -- 예: "n = int(input())\ndp = [0] * (n + 1)"
    starter_code TEXT NOT NULL,

    -- ============================================================
    -- 대화 기록 (세션 동안 누적)
    -- ============================================================

    -- 피드백 에이전트 실행 전까지의 모든 대화 내용
    -- JSON 형태: [{"role": "user", "content": "...", "timestamp": "..."}, {"role": "assistant", "content": "...", "timestamp": "..."}]
    conversation_history JSONB NOT NULL DEFAULT '[]',

    -- ============================================================
    -- 진행 상태 및 체크포인트
    -- ============================================================

    -- 정답 시도 시 작성한 코드들 (시도 기록)
    -- JSON 형태: [{"code": "...", "timestamp": "...", "is_correct": false}, ...]
    check_points JSONB NOT NULL DEFAULT '[]',

    -- 진행 상태: in_progress, completed, abandoned
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',

    -- ============================================================
    -- 통계 정보
    -- ============================================================

    -- 시도 횟수
    attempts_count INTEGER NOT NULL DEFAULT 0,

    -- 제공된 힌트 수
    hints_given INTEGER NOT NULL DEFAULT 0,

    -- 완료까지 걸린 시간 (초)
    completion_time_seconds INTEGER,

    -- ============================================================
    -- 타임스탬프
    -- ============================================================
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- ============================================================
    -- 제약 조건
    -- ============================================================
    -- 같은 사용자가 같은 문제를 같은 언어로 중복 생성 방지
    UNIQUE(base_problem_id, creator_id, language)
);

-- =====================================================
-- 3. 인덱스 생성
-- =====================================================
CREATE INDEX idx_problems_guided_base_problem_id ON problems_guided(base_problem_id);
CREATE INDEX idx_problems_guided_creator_id ON problems_guided(creator_id);
CREATE INDEX idx_problems_guided_status ON problems_guided(status);
CREATE INDEX idx_problems_guided_created_at ON problems_guided(created_at DESC);

-- =====================================================
-- 4. 트리거: updated_at 자동 갱신
-- =====================================================
CREATE TRIGGER update_problems_guided_updated_at
    BEFORE UPDATE ON problems_guided
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 5. RLS (Row Level Security)
-- =====================================================
ALTER TABLE problems_guided ENABLE ROW LEVEL SECURITY;

-- 본인 문제만 조회 가능
CREATE POLICY "Users can view own problems_guided" ON problems_guided
    FOR SELECT USING (auth.uid() = creator_id);

-- 본인 문제만 관리 가능
CREATE POLICY "Users can manage own problems_guided" ON problems_guided
    FOR ALL USING (auth.uid() = creator_id);

-- service_role은 모든 권한
CREATE POLICY "Service role can manage all problems_guided" ON problems_guided
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 6. 권한 부여
-- =====================================================
GRANT SELECT, INSERT, UPDATE ON problems_guided TO authenticated;
GRANT ALL ON problems_guided TO service_role;

-- =====================================================
-- 7. 대화 내용 추가 함수
-- =====================================================
CREATE OR REPLACE FUNCTION append_guided_conversation(
    p_guided_id UUID,
    p_role TEXT,
    p_content TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE problems_guided
    SET
        conversation_history = conversation_history || jsonb_build_array(
            jsonb_build_object(
                'role', p_role,
                'content', p_content,
                'timestamp', NOW()
            )
        ),
        updated_at = NOW()
    WHERE id = p_guided_id;
END;
$$;

-- =====================================================
-- 8. 체크포인트(코드 시도) 추가 함수
-- =====================================================
CREATE OR REPLACE FUNCTION append_guided_checkpoint(
    p_guided_id UUID,
    p_code TEXT,
    p_is_correct BOOLEAN DEFAULT FALSE
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE problems_guided
    SET
        check_points = check_points || jsonb_build_array(
            jsonb_build_object(
                'code', p_code,
                'timestamp', NOW(),
                'is_correct', p_is_correct
            )
        ),
        attempts_count = attempts_count + 1,
        status = CASE WHEN p_is_correct THEN 'completed' ELSE status END,
        updated_at = NOW()
    WHERE id = p_guided_id;
END;
$$;

-- =====================================================
-- 9. 힌트 카운트 증가 함수
-- =====================================================
CREATE OR REPLACE FUNCTION increment_guided_hints(
    p_guided_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE problems_guided
    SET
        hints_given = hints_given + 1,
        updated_at = NOW()
    WHERE id = p_guided_id;
END;
$$;

-- =====================================================
-- 10. 권한 부여 (함수)
-- =====================================================
GRANT EXECUTE ON FUNCTION append_guided_conversation TO authenticated;
GRANT EXECUTE ON FUNCTION append_guided_checkpoint TO authenticated;
GRANT EXECUTE ON FUNCTION increment_guided_hints TO authenticated;

-- =====================================================
-- 완료
-- =====================================================
COMMENT ON TABLE problems_guided IS '1대1 대화형 문제 - 개념 정의, 변수 가이드, 대화 기록, 코드 시도 저장';
COMMENT ON COLUMN problems_guided.concept_explanation IS '핵심 알고리즘/자료구조에 대한 설명';
COMMENT ON COLUMN problems_guided.variables_guide IS '필요한 변수들의 역할, 타입, 초기값 (JSON)';
COMMENT ON COLUMN problems_guided.approach_guide IS '문제 접근법에 대한 가이드';
COMMENT ON COLUMN problems_guided.starter_code IS '초반 맛보기 코드 (함수 정의 제외 앞 2줄)';
COMMENT ON COLUMN problems_guided.conversation_history IS '피드백 에이전트 전까지의 대화 내용';
COMMENT ON COLUMN problems_guided.check_points IS '정답 시도 시 작성한 코드들';
