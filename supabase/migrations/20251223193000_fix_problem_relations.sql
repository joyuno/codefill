-- =====================================================
-- CodeFill Database Migration: Fix Problem Relations
-- 1. problems_blank/puzzle/guided ↔ base_problems FK 제거
-- 2. user_generated_problems ↔ 각 문제 테이블 직접 연결
-- =====================================================

-- =====================================================
-- 0. 의존성 있는 뷰 먼저 삭제
-- =====================================================

DROP VIEW IF EXISTS user_generated_problems_detail CASCADE;
DROP VIEW IF EXISTS user_problem_stats CASCADE;

-- =====================================================
-- 1. problems_blank/puzzle/guided의 original_id FK 제거
-- =====================================================

ALTER TABLE problems_blank
    DROP CONSTRAINT IF EXISTS problems_blank_original_id_fkey;

ALTER TABLE problems_puzzle
    DROP CONSTRAINT IF EXISTS problems_puzzle_original_id_fkey;

ALTER TABLE problems_guided
    DROP CONSTRAINT IF EXISTS problems_guided_original_id_fkey;

-- =====================================================
-- 2. user_generated_problems 테이블 수정
-- 기존 generated_problem_id 대신 각 테이블별 FK 컬럼 추가
-- =====================================================

-- 기존 컬럼 제거 (generated_problem_id는 더 이상 사용 안함)
ALTER TABLE user_generated_problems
    DROP COLUMN IF EXISTS generated_problem_id;

-- 각 문제 타입별 FK 컬럼 추가
ALTER TABLE user_generated_problems
    ADD COLUMN IF NOT EXISTS blank_problem_id UUID,
    ADD COLUMN IF NOT EXISTS puzzle_problem_id UUID,
    ADD COLUMN IF NOT EXISTS guided_problem_id UUID;

-- FK 제약조건 추가
ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_blank_fkey
    FOREIGN KEY (blank_problem_id) REFERENCES problems_blank(id) ON DELETE CASCADE;

ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_puzzle_fkey
    FOREIGN KEY (puzzle_problem_id) REFERENCES problems_puzzle(id) ON DELETE CASCADE;

ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_guided_fkey
    FOREIGN KEY (guided_problem_id) REFERENCES problems_guided(id) ON DELETE CASCADE;

-- =====================================================
-- 3. CHECK 제약조건: problem_type과 해당 FK가 일치하도록
-- =====================================================

ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_type_check
    CHECK (
        (problem_type = 'blank' AND blank_problem_id IS NOT NULL AND puzzle_problem_id IS NULL AND guided_problem_id IS NULL) OR
        (problem_type = 'puzzle' AND puzzle_problem_id IS NOT NULL AND blank_problem_id IS NULL AND guided_problem_id IS NULL) OR
        (problem_type = 'guided' AND guided_problem_id IS NOT NULL AND blank_problem_id IS NULL AND puzzle_problem_id IS NULL)
    );

-- =====================================================
-- 4. 인덱스 추가
-- =====================================================

CREATE INDEX IF NOT EXISTS user_generated_problems_blank_idx
    ON user_generated_problems(blank_problem_id) WHERE blank_problem_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS user_generated_problems_puzzle_idx
    ON user_generated_problems(puzzle_problem_id) WHERE puzzle_problem_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS user_generated_problems_guided_idx
    ON user_generated_problems(guided_problem_id) WHERE guided_problem_id IS NOT NULL;

-- =====================================================
-- 5. 뷰 업데이트
-- =====================================================

DROP VIEW IF EXISTS user_generated_problems_detail CASCADE;

CREATE OR REPLACE VIEW user_generated_problems_detail AS
SELECT
    ugp.id,
    ugp.user_id,
    ugp.original_id,
    ugp.problem_type,
    ugp.blank_problem_id,
    ugp.puzzle_problem_id,
    ugp.guided_problem_id,
    ugp.is_public,
    ugp.created_at,
    bp.name as problem_name,
    bp.question,
    bp.difficulty,
    bp.tags,
    bp.source,
    bp.url,
    -- 각 타입별 상세 정보
    pb.code_template as blank_template,
    pb.language as blank_language,
    pp.blocks as puzzle_blocks,
    pp.language as puzzle_language,
    pg.concepts as guided_concepts,
    pg.language as guided_language
FROM user_generated_problems ugp
LEFT JOIN base_problems bp ON ugp.original_id = bp.original_id
LEFT JOIN problems_blank pb ON ugp.blank_problem_id = pb.id
LEFT JOIN problems_puzzle pp ON ugp.puzzle_problem_id = pp.id
LEFT JOIN problems_guided pg ON ugp.guided_problem_id = pg.id;

-- 권한 부여
GRANT SELECT ON user_generated_problems_detail TO authenticated;
GRANT SELECT ON user_generated_problems_detail TO service_role;

-- =====================================================
-- 6. 헬퍼 함수 업데이트
-- =====================================================

-- 기존 함수 삭제 (파라미터 시그니처 변경으로 인해 필요)
DROP FUNCTION IF EXISTS record_generated_problem(UUID, VARCHAR, VARCHAR, UUID, BOOLEAN);
DROP FUNCTION IF EXISTS get_user_problems(UUID, VARCHAR);

-- 문제 생성 기록 함수 업데이트
CREATE OR REPLACE FUNCTION record_generated_problem(
    p_user_id UUID,
    p_original_id VARCHAR,
    p_problem_type VARCHAR,
    p_problem_id UUID,
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
        blank_problem_id,
        puzzle_problem_id,
        guided_problem_id,
        is_public
    )
    VALUES (
        p_user_id,
        p_original_id,
        p_problem_type,
        CASE WHEN p_problem_type = 'blank' THEN p_problem_id ELSE NULL END,
        CASE WHEN p_problem_type = 'puzzle' THEN p_problem_id ELSE NULL END,
        CASE WHEN p_problem_type = 'guided' THEN p_problem_id ELSE NULL END,
        p_is_public
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 유저 문제 목록 함수 업데이트
CREATE OR REPLACE FUNCTION get_user_problems(
    p_user_id UUID,
    p_problem_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    original_id VARCHAR,
    problem_type VARCHAR,
    problem_id UUID,
    is_public BOOLEAN,
    created_at TIMESTAMPTZ,
    problem_name VARCHAR,
    difficulty VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ugp.id,
        ugp.original_id,
        ugp.problem_type,
        COALESCE(ugp.blank_problem_id, ugp.puzzle_problem_id, ugp.guided_problem_id) as problem_id,
        ugp.is_public,
        ugp.created_at,
        bp.name::VARCHAR as problem_name,
        bp.difficulty::VARCHAR
    FROM user_generated_problems ugp
    LEFT JOIN base_problems bp ON ugp.original_id = bp.original_id
    WHERE ugp.user_id = p_user_id
    AND (p_problem_type IS NULL OR ugp.problem_type = p_problem_type)
    ORDER BY ugp.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 7. 코멘트 추가
-- =====================================================

COMMENT ON COLUMN user_generated_problems.blank_problem_id IS 'problems_blank 테이블의 id (problem_type=blank일 때)';
COMMENT ON COLUMN user_generated_problems.puzzle_problem_id IS 'problems_puzzle 테이블의 id (problem_type=puzzle일 때)';
COMMENT ON COLUMN user_generated_problems.guided_problem_id IS 'problems_guided 테이블의 id (problem_type=guided일 때)';
