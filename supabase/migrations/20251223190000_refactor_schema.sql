-- =====================================================
-- CodeFill Database Migration: Schema Refactoring
-- 기존 레거시 테이블 정리 및 base_problems 중심으로 재구성
-- =====================================================

-- =====================================================
-- 1. 기존 레거시 테이블 삭제 준비 (FK 제거)
-- =====================================================

-- attempts 테이블의 problem_id FK 제거 (problems 테이블 삭제 전)
ALTER TABLE attempts DROP CONSTRAINT IF EXISTS attempts_problem_id_fkey;

-- hint_logs 테이블의 problem_id FK 제거
ALTER TABLE hint_logs DROP CONSTRAINT IF EXISTS hint_logs_problem_id_fkey;

-- problems 테이블의 code_id FK 제거 (codes 테이블 삭제 전)
ALTER TABLE problems DROP CONSTRAINT IF EXISTS problems_code_id_fkey;

-- =====================================================
-- 2. 레거시 테이블 삭제
-- =====================================================

-- codes 테이블 삭제
DROP TABLE IF EXISTS codes CASCADE;

-- problems 테이블 삭제 (이전 버전)
DROP TABLE IF EXISTS problems CASCADE;

-- puzzle_blocks 테이블 삭제
DROP TABLE IF EXISTS puzzle_blocks CASCADE;

-- =====================================================
-- 3. user_generated_problems 컬럼명 변경
-- original_problem_id → original_id
-- =====================================================

ALTER TABLE user_generated_problems
    RENAME COLUMN original_problem_id TO original_id;

-- =====================================================
-- 4. base_problems 테이블 컬럼 추가/수정
-- JSON 형식에 맞게 컬럼 구조 변경
-- =====================================================

-- images 컬럼 추가 (이미지 정보 배열)
ALTER TABLE base_problems
    ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]';

-- starter_code 컬럼 추가 (시작 코드)
ALTER TABLE base_problems
    ADD COLUMN IF NOT EXISTS starter_code TEXT;

-- explanation 컬럼 추가 (문제 해설)
ALTER TABLE base_problems
    ADD COLUMN IF NOT EXISTS explanation TEXT;

-- input_output을 TEXT로도 저장 가능하게 (기존 JSONB 유지, 호환성)
-- 이미 JSONB로 되어있으므로 유지

-- difficulty 값 확장 (medium_hard 등 추가)
ALTER TABLE base_problems
    DROP CONSTRAINT IF EXISTS base_problems_difficulty_check;

-- =====================================================
-- 5. attempts, hint_logs 테이블 재구성
-- base_problems 및 생성 문제 테이블과 연결
-- =====================================================

-- attempts 테이블에 새 컬럼 추가
ALTER TABLE attempts
    ADD COLUMN IF NOT EXISTS base_problem_id UUID,
    ADD COLUMN IF NOT EXISTS problem_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS generated_problem_id UUID;

-- hint_logs 테이블에 새 컬럼 추가
ALTER TABLE hint_logs
    ADD COLUMN IF NOT EXISTS base_problem_id UUID,
    ADD COLUMN IF NOT EXISTS problem_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS generated_problem_id UUID;

-- 기존 problem_id 컬럼은 유지 (호환성, nullable)
-- 새 시스템에서는 base_problem_id + problem_type + generated_problem_id 사용

-- =====================================================
-- 6. FK 제약조건 추가 (base_problems 연결)
-- =====================================================

-- base_problems.id에 대한 FK (optional)
ALTER TABLE attempts
    ADD CONSTRAINT attempts_base_problem_id_fkey
    FOREIGN KEY (base_problem_id) REFERENCES base_problems(id) ON DELETE SET NULL;

ALTER TABLE hint_logs
    ADD CONSTRAINT hint_logs_base_problem_id_fkey
    FOREIGN KEY (base_problem_id) REFERENCES base_problems(id) ON DELETE SET NULL;

-- user_generated_problems와 base_problems 연결 (original_id 기준)
-- 이미 VARCHAR로 연결되어 있으므로 FK는 추가하지 않음 (성능상)
-- 대신 인덱스로 조회 최적화
CREATE INDEX IF NOT EXISTS user_generated_problems_original_id_idx
    ON user_generated_problems(original_id);

-- =====================================================
-- 7. 뷰 업데이트
-- =====================================================

-- 기존 뷰 삭제 후 재생성
DROP VIEW IF EXISTS user_generated_problems_detail CASCADE;

CREATE OR REPLACE VIEW user_generated_problems_detail AS
SELECT
    ugp.id,
    ugp.user_id,
    ugp.problem_type,
    ugp.generated_problem_id,
    ugp.is_public,
    ugp.created_at,
    ugp.original_id,
    bp.name as problem_name,
    bp.question,
    bp.difficulty,
    bp.tags,
    bp.source,
    bp.url,
    bp.images
FROM user_generated_problems ugp
LEFT JOIN base_problems bp ON ugp.original_id = bp.original_id;

-- 문제 전체 뷰 (base_problems + 생성된 문제 수)
CREATE OR REPLACE VIEW problems_overview AS
SELECT
    bp.id,
    bp.original_id,
    bp.name,
    bp.difficulty,
    bp.source,
    bp.tags,
    bp.created_at,
    (SELECT COUNT(*) FROM problems_blank pb WHERE pb.original_id = bp.original_id) as blank_count,
    (SELECT COUNT(*) FROM problems_puzzle pp WHERE pp.original_id = bp.original_id) as puzzle_count,
    (SELECT COUNT(*) FROM problems_guided pg WHERE pg.original_id = bp.original_id) as guided_count
FROM base_problems bp;

-- =====================================================
-- 8. 인덱스 추가
-- =====================================================

CREATE INDEX IF NOT EXISTS base_problems_tags_idx ON base_problems USING GIN(tags);
CREATE INDEX IF NOT EXISTS base_problems_name_idx ON base_problems(name);

-- attempts 테이블 인덱스
CREATE INDEX IF NOT EXISTS attempts_base_problem_idx ON attempts(base_problem_id);
CREATE INDEX IF NOT EXISTS attempts_problem_type_idx ON attempts(problem_type);

-- hint_logs 테이블 인덱스
CREATE INDEX IF NOT EXISTS hint_logs_base_problem_idx ON hint_logs(base_problem_id);

-- =====================================================
-- 9. RLS 정책 업데이트
-- =====================================================

-- problems_overview 뷰 권한
GRANT SELECT ON problems_overview TO authenticated;
GRANT SELECT ON problems_overview TO anon;
GRANT SELECT ON problems_overview TO service_role;

-- user_generated_problems_detail 뷰 권한
GRANT SELECT ON user_generated_problems_detail TO authenticated;
GRANT SELECT ON user_generated_problems_detail TO service_role;

-- =====================================================
-- 10. 헬퍼 함수 업데이트
-- =====================================================

-- 문제 검색 함수
CREATE OR REPLACE FUNCTION search_problems(
    p_query TEXT DEFAULT NULL,
    p_source VARCHAR DEFAULT NULL,
    p_difficulty VARCHAR DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL,
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    original_id VARCHAR,
    name VARCHAR,
    question TEXT,
    difficulty VARCHAR,
    tags TEXT[],
    source VARCHAR,
    url TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bp.id,
        bp.original_id,
        bp.name,
        bp.question,
        bp.difficulty,
        bp.tags,
        bp.source,
        bp.url,
        bp.created_at
    FROM base_problems bp
    WHERE
        (p_query IS NULL OR bp.name ILIKE '%' || p_query || '%' OR bp.question ILIKE '%' || p_query || '%')
        AND (p_source IS NULL OR bp.source = p_source)
        AND (p_difficulty IS NULL OR bp.difficulty = p_difficulty)
        AND (p_tags IS NULL OR bp.tags && p_tags)
    ORDER BY bp.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 문제 시도 기록 함수 (새 스키마용)
CREATE OR REPLACE FUNCTION record_attempt(
    p_user_id UUID,
    p_base_problem_id UUID,
    p_problem_type VARCHAR,
    p_generated_problem_id UUID,
    p_is_correct BOOLEAN,
    p_submitted_code TEXT DEFAULT NULL,
    p_time_spent INTEGER DEFAULT NULL,
    p_hints_used INTEGER DEFAULT 0
)
RETURNS UUID AS $$
DECLARE
    v_attempt_id UUID;
    v_xp INTEGER;
BEGIN
    -- XP 계산
    IF p_is_correct THEN
        v_xp := CASE p_problem_type
            WHEN 'blank' THEN 10
            WHEN 'puzzle' THEN 15
            WHEN 'guided' THEN 20
            ELSE 10
        END;
    ELSE
        v_xp := 0;
    END IF;

    -- 시도 기록
    INSERT INTO attempts (
        user_id,
        base_problem_id,
        problem_type,
        generated_problem_id,
        is_correct,
        submitted_code,
        time_spent,
        hints_used,
        xp_earned
    )
    VALUES (
        p_user_id,
        p_base_problem_id,
        p_problem_type,
        p_generated_problem_id,
        p_is_correct,
        p_submitted_code,
        p_time_spent,
        p_hints_used,
        v_xp
    )
    RETURNING id INTO v_attempt_id;

    -- 정답인 경우 user_stats 업데이트
    IF p_is_correct THEN
        PERFORM increment_user_stats(p_user_id, v_xp, p_problem_type);
    END IF;

    RETURN v_attempt_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION search_problems TO authenticated;
GRANT EXECUTE ON FUNCTION search_problems TO anon;
GRANT EXECUTE ON FUNCTION record_attempt TO authenticated;

-- =====================================================
-- 11. 코멘트 추가 (문서화)
-- =====================================================

COMMENT ON TABLE base_problems IS '원본 코딩 테스트 문제 (백준, 프로그래머스 등)';
COMMENT ON TABLE problems_blank IS '빈칸 채우기 문제 (base_problems 기반 생성)';
COMMENT ON TABLE problems_puzzle IS '퍼즐 문제 (base_problems 기반 생성)';
COMMENT ON TABLE problems_guided IS '1대1 대화형 문제 (base_problems 기반 생성)';
COMMENT ON TABLE user_generated_problems IS '유저가 생성한 문제 매핑 테이블';

COMMENT ON COLUMN base_problems.original_id IS '원본 문제 ID (baekjoon_1000, taco_123 등)';
COMMENT ON COLUMN base_problems.images IS '문제에 포함된 이미지 정보 [{original_url, local_path}]';
COMMENT ON COLUMN base_problems.solutions IS '언어별 솔루션 코드 [{language, code}]';
COMMENT ON COLUMN base_problems.input_output IS '입출력 예시 {inputs: [], outputs: []}';
COMMENT ON COLUMN base_problems.starter_code IS '시작 코드 템플릿';
COMMENT ON COLUMN base_problems.explanation IS '문제 해설';
