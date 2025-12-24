-- =====================================================
-- CodeFill Database Migration: Reverse FK Design
-- problems_blank/puzzle/guided에서 user_generated_problems를 참조
-- =====================================================

-- =====================================================
-- 1. user_generated_problems에서 불필요한 컬럼 제거
-- =====================================================

-- 기존 뷰 삭제
DROP VIEW IF EXISTS user_generated_problems_detail CASCADE;

-- CHECK 제약조건 제거
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_type_check;

-- FK 제약조건 제거
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_blank_fkey;
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_puzzle_fkey;
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_guided_fkey;

-- 컬럼 제거
ALTER TABLE user_generated_problems
    DROP COLUMN IF EXISTS blank_problem_id,
    DROP COLUMN IF EXISTS puzzle_problem_id,
    DROP COLUMN IF EXISTS guided_problem_id;

-- =====================================================
-- 2. problems_blank/puzzle/guided에 user_generated_id 추가
-- =====================================================

-- problems_blank
ALTER TABLE problems_blank
    ADD COLUMN IF NOT EXISTS user_generated_id UUID;

ALTER TABLE problems_blank
    ADD CONSTRAINT problems_blank_user_generated_fkey
    FOREIGN KEY (user_generated_id) REFERENCES user_generated_problems(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS problems_blank_user_generated_idx
    ON problems_blank(user_generated_id) WHERE user_generated_id IS NOT NULL;

-- problems_puzzle
ALTER TABLE problems_puzzle
    ADD COLUMN IF NOT EXISTS user_generated_id UUID;

ALTER TABLE problems_puzzle
    ADD CONSTRAINT problems_puzzle_user_generated_fkey
    FOREIGN KEY (user_generated_id) REFERENCES user_generated_problems(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS problems_puzzle_user_generated_idx
    ON problems_puzzle(user_generated_id) WHERE user_generated_id IS NOT NULL;

-- problems_guided
ALTER TABLE problems_guided
    ADD COLUMN IF NOT EXISTS user_generated_id UUID;

ALTER TABLE problems_guided
    ADD CONSTRAINT problems_guided_user_generated_fkey
    FOREIGN KEY (user_generated_id) REFERENCES user_generated_problems(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS problems_guided_user_generated_idx
    ON problems_guided(user_generated_id) WHERE user_generated_id IS NOT NULL;

-- =====================================================
-- 3. 뷰 재생성
-- =====================================================

CREATE OR REPLACE VIEW user_generated_problems_detail AS
SELECT
    ugp.id,
    ugp.user_id,
    ugp.original_id,
    ugp.problem_type,
    ugp.is_public,
    ugp.created_at,
    bp.name as problem_name,
    bp.question,
    bp.difficulty,
    bp.tags,
    bp.source,
    bp.url,
    -- 각 타입별 문제 정보 (역방향 조인)
    pb.id as blank_id,
    pb.code_template as blank_template,
    pb.language as blank_language,
    pp.id as puzzle_id,
    pp.blocks as puzzle_blocks,
    pp.language as puzzle_language,
    pg.id as guided_id,
    pg.concepts as guided_concepts,
    pg.language as guided_language
FROM user_generated_problems ugp
LEFT JOIN base_problems bp ON ugp.original_id = bp.original_id
LEFT JOIN problems_blank pb ON pb.user_generated_id = ugp.id
LEFT JOIN problems_puzzle pp ON pp.user_generated_id = ugp.id
LEFT JOIN problems_guided pg ON pg.user_generated_id = ugp.id;

-- 권한 부여
GRANT SELECT ON user_generated_problems_detail TO authenticated;
GRANT SELECT ON user_generated_problems_detail TO service_role;

-- =====================================================
-- 4. 헬퍼 함수 업데이트
-- =====================================================

-- 기존 함수 삭제
DROP FUNCTION IF EXISTS record_generated_problem(UUID, VARCHAR, VARCHAR, UUID, BOOLEAN);
DROP FUNCTION IF EXISTS get_user_problems(UUID, VARCHAR);

-- 유저 생성 문제 기록 생성 함수
CREATE OR REPLACE FUNCTION create_user_generated_record(
    p_user_id UUID,
    p_original_id VARCHAR,
    p_problem_type VARCHAR,
    p_is_public BOOLEAN DEFAULT FALSE
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO user_generated_problems (
        user_id,
        original_id,
        problem_type,
        is_public
    )
    VALUES (
        p_user_id,
        p_original_id,
        p_problem_type,
        p_is_public
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 유저 문제 목록 조회 함수
CREATE OR REPLACE FUNCTION get_user_problems(
    p_user_id UUID,
    p_problem_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    original_id VARCHAR,
    problem_type VARCHAR,
    is_public BOOLEAN,
    created_at TIMESTAMPTZ,
    problem_name VARCHAR,
    difficulty VARCHAR,
    generated_problem_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ugp.id,
        ugp.original_id,
        ugp.problem_type,
        ugp.is_public,
        ugp.created_at,
        bp.name::VARCHAR as problem_name,
        bp.difficulty::VARCHAR,
        COALESCE(pb.id, pp.id, pg.id) as generated_problem_id
    FROM user_generated_problems ugp
    LEFT JOIN base_problems bp ON ugp.original_id = bp.original_id
    LEFT JOIN problems_blank pb ON pb.user_generated_id = ugp.id
    LEFT JOIN problems_puzzle pp ON pp.user_generated_id = ugp.id
    LEFT JOIN problems_guided pg ON pg.user_generated_id = ugp.id
    WHERE ugp.user_id = p_user_id
    AND (p_problem_type IS NULL OR ugp.problem_type = p_problem_type)
    ORDER BY ugp.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION create_user_generated_record TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_problems TO authenticated;

-- =====================================================
-- 5. 코멘트 추가
-- =====================================================

COMMENT ON COLUMN problems_blank.user_generated_id IS 'user_generated_problems 테이블 참조 (유저 생성 문제인 경우)';
COMMENT ON COLUMN problems_puzzle.user_generated_id IS 'user_generated_problems 테이블 참조 (유저 생성 문제인 경우)';
COMMENT ON COLUMN problems_guided.user_generated_id IS 'user_generated_problems 테이블 참조 (유저 생성 문제인 경우)';
