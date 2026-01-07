-- =====================================================
-- 문제별 힌트 캐시 테이블
-- LLM 생성 힌트를 저장하여 중복 호출 방지
-- 모든 문제 유형 지원: blank, puzzle, guided
-- =====================================================

-- 1. problem_hints 테이블 생성
CREATE TABLE IF NOT EXISTS problem_hints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 문제 식별
    problem_id TEXT NOT NULL,           -- problems_blank/puzzle/guided의 ID
    problem_type TEXT NOT NULL DEFAULT 'blank',  -- 'blank' | 'puzzle' | 'guided'

    -- 힌트 위치 (유형별 의미)
    -- blank: 빈칸 인덱스 (0, 1, 2, ...)
    -- puzzle: 블록 인덱스 (0, 1, 2, ...)
    -- guided: 단계 인덱스 (0, 1, 2, ...)
    hint_index INT NOT NULL DEFAULT 0,

    -- 힌트 내용 (역할 설명, 정답 제공 안함)
    hint_content TEXT NOT NULL,

    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 유니크 제약: 같은 문제, 같은 유형, 같은 인덱스는 하나만
    UNIQUE (problem_id, problem_type, hint_index)
);

-- 2. 인덱스 생성 (조회 성능)
CREATE INDEX IF NOT EXISTS idx_problem_hints_lookup
ON problem_hints (problem_id, problem_type, hint_index);

CREATE INDEX IF NOT EXISTS idx_problem_hints_problem_id
ON problem_hints (problem_id);

-- 3. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_problem_hints_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_problem_hints_updated_at ON problem_hints;
CREATE TRIGGER trigger_problem_hints_updated_at
    BEFORE UPDATE ON problem_hints
    FOR EACH ROW
    EXECUTE FUNCTION update_problem_hints_updated_at();

-- 4. RLS 정책 (읽기만 허용, 쓰기는 서버에서)
ALTER TABLE problem_hints ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽을 수 있음 (캐시된 힌트 조회)
CREATE POLICY "problem_hints_select_policy" ON problem_hints
    FOR SELECT USING (true);

-- 서버(service role)만 쓰기 가능
CREATE POLICY "problem_hints_insert_policy" ON problem_hints
    FOR INSERT WITH CHECK (true);

CREATE POLICY "problem_hints_update_policy" ON problem_hints
    FOR UPDATE USING (true);

-- 5. 코멘트
COMMENT ON TABLE problem_hints IS '문제별 LLM 생성 힌트 캐시 테이블 (모든 유형 지원)';
COMMENT ON COLUMN problem_hints.problem_id IS '문제 ID (problems_blank/puzzle/guided)';
COMMENT ON COLUMN problem_hints.problem_type IS '문제 유형: blank, puzzle, guided';
COMMENT ON COLUMN problem_hints.hint_index IS '힌트 위치: 빈칸/블록/단계 인덱스';
COMMENT ON COLUMN problem_hints.hint_content IS 'LLM 생성 역할 설명 (정답 제공 안함)';
