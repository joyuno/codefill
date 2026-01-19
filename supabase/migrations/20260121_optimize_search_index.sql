-- =====================================================
-- Search Optimization: pg_trgm + GIN Index
-- LIKE '%keyword%' 검색 성능 최적화
-- =====================================================

-- 1. pg_trgm extension 활성화 (trigram 기반 유사 검색)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. base_problems.name에 GIN 인덱스 추가
-- 기존 B-tree 인덱스는 prefix 검색만 지원 (LIKE 'keyword%')
-- GIN + pg_trgm은 중간 검색도 지원 (LIKE '%keyword%')
DROP INDEX IF EXISTS base_problems_name_idx;
CREATE INDEX base_problems_name_trgm_idx ON base_problems USING GIN (name gin_trgm_ops);

-- 3. original_id에도 trigram 인덱스 추가 (문제 번호 검색용)
CREATE INDEX IF NOT EXISTS base_problems_original_id_trgm_idx ON base_problems USING GIN (original_id gin_trgm_ops);

-- 4. 인덱스 통계 갱신
ANALYZE base_problems;

-- =====================================================
-- 참고: pg_trgm 인덱스 작동 방식
-- =====================================================
-- - 문자열을 3글자 단위(trigram)로 분해하여 인덱싱
-- - 예: "피보나치" → "피보나", "보나치"
-- - ILIKE '%피보%' 쿼리도 인덱스 스캔 가능
-- - 유사도 검색 (% 연산자)도 지원: name % '피보나치'
-- =====================================================
