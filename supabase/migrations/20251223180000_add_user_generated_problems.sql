-- =====================================================
-- CodeFill Database Migration: User Generated Problems
-- 유저가 생성한 문제를 매핑하는 중간 테이블 추가
-- =====================================================

-- =====================================================
-- 1. user_generated_problems 테이블 생성 (핵심 매핑 테이블)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_generated_problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 유저 정보 (Supabase Auth와 연결)
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- 원본 문제 참조 (base_problems.original_id)
    original_problem_id VARCHAR(50) NOT NULL,

    -- 생성된 문제 타입
    problem_type VARCHAR(20) NOT NULL CHECK (problem_type IN ('blank', 'puzzle', 'guided')),

    -- 각 타입별 테이블의 id
    generated_problem_id UUID NOT NULL,

    -- 공유 설정
    is_public BOOLEAN DEFAULT FALSE,

    -- 메타데이터 (추가 정보 저장용)
    metadata JSONB DEFAULT '{}',

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 같은 유저가 같은 문제를 중복 생성 방지 (옵션)
    UNIQUE(user_id, original_problem_id, problem_type, generated_problem_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS user_generated_problems_user_id_idx
    ON user_generated_problems(user_id);
CREATE INDEX IF NOT EXISTS user_generated_problems_original_id_idx
    ON user_generated_problems(original_problem_id);
CREATE INDEX IF NOT EXISTS user_generated_problems_type_idx
    ON user_generated_problems(problem_type);
CREATE INDEX IF NOT EXISTS user_generated_problems_public_idx
    ON user_generated_problems(is_public) WHERE is_public = TRUE;

-- =====================================================
-- 2. 기존 테이블에 creator_id 컬럼 추가 (선택적)
-- 빈칸/퍼즐/대화형 테이블에 생성자 정보 추가
-- =====================================================

-- problems_blank에 creator_id 추가
ALTER TABLE problems_blank
    ADD COLUMN IF NOT EXISTS creator_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- problems_puzzle에 creator_id 추가
ALTER TABLE problems_puzzle
    ADD COLUMN IF NOT EXISTS creator_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- problems_guided에 creator_id 추가
ALTER TABLE problems_guided
    ADD COLUMN IF NOT EXISTS creator_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- creator_id 인덱스 추가
CREATE INDEX IF NOT EXISTS problems_blank_creator_idx ON problems_blank(creator_id);
CREATE INDEX IF NOT EXISTS problems_puzzle_creator_idx ON problems_puzzle(creator_id);
CREATE INDEX IF NOT EXISTS problems_guided_creator_idx ON problems_guided(creator_id);

-- =====================================================
-- 3. RLS (Row Level Security) 정책
-- =====================================================

ALTER TABLE user_generated_problems ENABLE ROW LEVEL SECURITY;

-- 본인이 생성한 문제 조회
CREATE POLICY "Users can view own generated problems"
    ON user_generated_problems FOR SELECT
    USING (auth.uid() = user_id);

-- 공개된 문제는 누구나 조회 가능
CREATE POLICY "Anyone can view public generated problems"
    ON user_generated_problems FOR SELECT
    USING (is_public = TRUE);

-- 본인만 생성 가능
CREATE POLICY "Users can create own generated problems"
    ON user_generated_problems FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 본인만 수정 가능
CREATE POLICY "Users can update own generated problems"
    ON user_generated_problems FOR UPDATE
    USING (auth.uid() = user_id);

-- 본인만 삭제 가능
CREATE POLICY "Users can delete own generated problems"
    ON user_generated_problems FOR DELETE
    USING (auth.uid() = user_id);

-- Service role은 모든 작업 가능
CREATE POLICY "Service role can manage user_generated_problems"
    ON user_generated_problems FOR ALL
    USING (auth.role() = 'service_role');

-- =====================================================
-- 4. 기존 테이블 RLS 정책 업데이트
-- creator_id가 있는 경우 본인 것만 수정/삭제 가능
-- =====================================================

-- problems_blank: 본인이 생성한 것만 수정 가능
DROP POLICY IF EXISTS "Users can update own blank problems" ON problems_blank;
CREATE POLICY "Users can update own blank problems"
    ON problems_blank FOR UPDATE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

DROP POLICY IF EXISTS "Users can delete own blank problems" ON problems_blank;
CREATE POLICY "Users can delete own blank problems"
    ON problems_blank FOR DELETE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

-- problems_puzzle: 본인이 생성한 것만 수정 가능
DROP POLICY IF EXISTS "Users can update own puzzle problems" ON problems_puzzle;
CREATE POLICY "Users can update own puzzle problems"
    ON problems_puzzle FOR UPDATE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

DROP POLICY IF EXISTS "Users can delete own puzzle problems" ON problems_puzzle;
CREATE POLICY "Users can delete own puzzle problems"
    ON problems_puzzle FOR DELETE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

-- problems_guided: 본인이 생성한 것만 수정 가능
DROP POLICY IF EXISTS "Users can update own guided problems" ON problems_guided;
CREATE POLICY "Users can update own guided problems"
    ON problems_guided FOR UPDATE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

DROP POLICY IF EXISTS "Users can delete own guided problems" ON problems_guided;
CREATE POLICY "Users can delete own guided problems"
    ON problems_guided FOR DELETE
    USING (creator_id IS NOT NULL AND auth.uid() = creator_id);

-- =====================================================
-- 5. Trigger: updated_at 자동 갱신
-- =====================================================

CREATE TRIGGER update_user_generated_problems_updated_at
    BEFORE UPDATE ON user_generated_problems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 6. 유용한 뷰 생성
-- =====================================================

-- 유저별 생성 문제 통계 뷰
CREATE OR REPLACE VIEW user_problem_stats AS
SELECT
    user_id,
    COUNT(*) as total_generated,
    COUNT(*) FILTER (WHERE problem_type = 'blank') as blank_count,
    COUNT(*) FILTER (WHERE problem_type = 'puzzle') as puzzle_count,
    COUNT(*) FILTER (WHERE problem_type = 'guided') as guided_count,
    COUNT(*) FILTER (WHERE is_public = TRUE) as public_count
FROM user_generated_problems
GROUP BY user_id;

-- 유저의 생성 문제 상세 뷰 (원본 문제 정보 포함)
CREATE OR REPLACE VIEW user_generated_problems_detail AS
SELECT
    ugp.id,
    ugp.user_id,
    ugp.problem_type,
    ugp.generated_problem_id,
    ugp.is_public,
    ugp.created_at,
    bp.original_id,
    bp.name as problem_name,
    bp.difficulty,
    bp.tags,
    bp.source
FROM user_generated_problems ugp
JOIN base_problems bp ON ugp.original_problem_id = bp.original_id;

-- =====================================================
-- 7. 권한 부여
-- =====================================================

GRANT SELECT ON user_generated_problems TO authenticated;
GRANT INSERT ON user_generated_problems TO authenticated;
GRANT UPDATE ON user_generated_problems TO authenticated;
GRANT DELETE ON user_generated_problems TO authenticated;
GRANT ALL ON user_generated_problems TO service_role;

GRANT SELECT ON user_problem_stats TO authenticated;
GRANT SELECT ON user_problem_stats TO service_role;

GRANT SELECT ON user_generated_problems_detail TO authenticated;
GRANT SELECT ON user_generated_problems_detail TO service_role;

-- =====================================================
-- 8. 헬퍼 함수들
-- =====================================================

-- 유저의 특정 타입 문제 목록 조회 함수
CREATE OR REPLACE FUNCTION get_user_problems(
    p_user_id UUID,
    p_problem_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    original_problem_id VARCHAR,
    problem_type VARCHAR,
    generated_problem_id UUID,
    is_public BOOLEAN,
    created_at TIMESTAMPTZ,
    problem_name VARCHAR,
    difficulty VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ugp.id,
        ugp.original_problem_id,
        ugp.problem_type,
        ugp.generated_problem_id,
        ugp.is_public,
        ugp.created_at,
        bp.name::VARCHAR as problem_name,
        bp.difficulty::VARCHAR
    FROM user_generated_problems ugp
    JOIN base_problems bp ON ugp.original_problem_id = bp.original_id
    WHERE ugp.user_id = p_user_id
    AND (p_problem_type IS NULL OR ugp.problem_type = p_problem_type)
    ORDER BY ugp.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 문제 생성 기록 함수
CREATE OR REPLACE FUNCTION record_generated_problem(
    p_user_id UUID,
    p_original_problem_id VARCHAR,
    p_problem_type VARCHAR,
    p_generated_problem_id UUID,
    p_is_public BOOLEAN DEFAULT FALSE
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO user_generated_problems (
        user_id,
        original_problem_id,
        problem_type,
        generated_problem_id,
        is_public
    )
    VALUES (
        p_user_id,
        p_original_problem_id,
        p_problem_type,
        p_generated_problem_id,
        p_is_public
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION get_user_problems TO authenticated;
GRANT EXECUTE ON FUNCTION record_generated_problem TO authenticated;
