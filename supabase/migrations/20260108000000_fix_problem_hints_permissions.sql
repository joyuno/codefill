-- =====================================================
-- problem_hints 테이블 권한 수정
-- service_role, authenticated, anon 모두 접근 가능하도록
-- =====================================================

-- 1. 테이블 소유자 확인 및 권한 부여
GRANT ALL ON problem_hints TO postgres;
GRANT ALL ON problem_hints TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON problem_hints TO authenticated;
GRANT SELECT ON problem_hints TO anon;

-- 2. RLS 비활성화 (service role은 이미 bypass하지만 확실히 하기 위해)
-- ALTER TABLE problem_hints DISABLE ROW LEVEL SECURITY;

-- 3. 또는 RLS를 유지하면서 모든 작업 허용하는 정책 추가
DROP POLICY IF EXISTS "problem_hints_all_access" ON problem_hints;
CREATE POLICY "problem_hints_all_access" ON problem_hints
    FOR ALL USING (true) WITH CHECK (true);

-- 4. 시퀀스 권한 (있다면)
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;

COMMENT ON TABLE problem_hints IS 'LLM 힌트 캐시 테이블 - 권한 수정됨 (2026-01-08)';
