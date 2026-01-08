-- =====================================================
-- CodeFill Database Cleanup: Remove Legacy Tables
-- 더 이상 사용하지 않는 이전 버전 테이블 정리
-- =====================================================

-- 1. FK 제약조건 먼저 제거 (에러 방지)
ALTER TABLE IF EXISTS attempts DROP CONSTRAINT IF EXISTS attempts_problem_id_fkey;
ALTER TABLE IF EXISTS hint_logs DROP CONSTRAINT IF EXISTS hint_logs_problem_id_fkey;
ALTER TABLE IF EXISTS puzzle_blocks DROP CONSTRAINT IF EXISTS puzzle_blocks_problem_id_fkey;

-- 2. 레거시 테이블 삭제
-- problems 테이블 (base_problems + problems_blank/puzzle/guided로 대체됨)
DROP TABLE IF EXISTS problems CASCADE;

-- codes 테이블 (base_problems에 통합됨)
DROP TABLE IF EXISTS codes CASCADE;

-- puzzle_blocks 테이블 (problems_puzzle.answer_data로 대체됨)
DROP TABLE IF EXISTS puzzle_blocks CASCADE;

-- ⚠️ 유지하는 테이블:
-- plans - 결제 시스템용 예정
-- user_memories - 세션 요약/장기 메모리용 (20260105에서 생성)

-- 3. 확인용 쿼리 (실행 후 결과 확인)
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public'
-- ORDER BY table_name;
