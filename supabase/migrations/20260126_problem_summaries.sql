-- =====================================================
-- problem_summaries 테이블
-- 문제의 요약 정보를 저장하는 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS problem_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_problem_id UUID NOT NULL REFERENCES base_problems(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'ko',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(base_problem_id, language)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS problem_summaries_base_problem_id_idx ON problem_summaries(base_problem_id);
CREATE INDEX IF NOT EXISTS problem_summaries_language_idx ON problem_summaries(language);

-- RLS 활성화
ALTER TABLE problem_summaries ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능
CREATE POLICY "problem_summaries_select_policy" ON problem_summaries
    FOR SELECT USING (true);

-- 인증된 사용자만 삽입/업데이트 가능 (서비스 역할)
CREATE POLICY "problem_summaries_insert_policy" ON problem_summaries
    FOR INSERT WITH CHECK (true);

CREATE POLICY "problem_summaries_update_policy" ON problem_summaries
    FOR UPDATE USING (true);

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_problem_summaries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER problem_summaries_updated_at_trigger
    BEFORE UPDATE ON problem_summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_problem_summaries_updated_at();

-- 문제 요약 조회 또는 생성 함수
CREATE OR REPLACE FUNCTION get_problem_summary(
    p_base_problem_id UUID,
    p_language VARCHAR DEFAULT 'ko'
)
RETURNS TABLE (
    id UUID,
    base_problem_id UUID,
    summary_text TEXT,
    language VARCHAR,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ps.id,
        ps.base_problem_id,
        ps.summary_text,
        ps.language,
        ps.created_at
    FROM problem_summaries ps
    WHERE ps.base_problem_id = p_base_problem_id
      AND ps.language = p_language;
END;
$$ LANGUAGE plpgsql;

-- 문제 요약 저장/업데이트 함수 (upsert)
CREATE OR REPLACE FUNCTION upsert_problem_summary(
    p_base_problem_id UUID,
    p_summary_text TEXT,
    p_language VARCHAR DEFAULT 'ko'
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO problem_summaries (base_problem_id, summary_text, language)
    VALUES (p_base_problem_id, p_summary_text, p_language)
    ON CONFLICT (base_problem_id, language)
    DO UPDATE SET
        summary_text = EXCLUDED.summary_text,
        updated_at = NOW()
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE problem_summaries IS '문제 요약 정보 저장 테이블';
COMMENT ON COLUMN problem_summaries.base_problem_id IS '원본 문제 참조';
COMMENT ON COLUMN problem_summaries.summary_text IS '문제 요약 텍스트';
COMMENT ON COLUMN problem_summaries.language IS '요약 언어 (ko, en, ja 등)';
