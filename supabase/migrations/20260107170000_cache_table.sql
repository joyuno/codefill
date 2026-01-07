-- ============================================================
-- PostgreSQL 캐시 테이블
-- Redis 대신 PostgreSQL을 캐시로 사용
-- ============================================================

-- 1. 범용 캐시 테이블
CREATE TABLE IF NOT EXISTS cache (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 만료 시간 인덱스 (정리용)
CREATE INDEX IF NOT EXISTS cache_expires_idx ON cache(expires_at);

-- 키 패턴 검색용 인덱스
CREATE INDEX IF NOT EXISTS cache_key_pattern_idx ON cache(key varchar_pattern_ops);

-- ============================================================
-- 캐시 함수들
-- ============================================================

-- 캐시 조회 (만료된 항목은 NULL 반환)
CREATE OR REPLACE FUNCTION cache_get(p_key VARCHAR(255))
RETURNS JSONB AS $$
DECLARE
    v_value JSONB;
BEGIN
    SELECT value INTO v_value
    FROM cache
    WHERE key = p_key AND expires_at > NOW();

    RETURN v_value;
END;
$$ LANGUAGE plpgsql;

-- 캐시 설정 (UPSERT)
CREATE OR REPLACE FUNCTION cache_set(
    p_key VARCHAR(255),
    p_value JSONB,
    p_ttl_seconds INT DEFAULT 300
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO cache (key, value, expires_at, updated_at)
    VALUES (p_key, p_value, NOW() + (p_ttl_seconds || ' seconds')::interval, NOW())
    ON CONFLICT (key) DO UPDATE SET
        value = EXCLUDED.value,
        expires_at = EXCLUDED.expires_at,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- 캐시 삭제
CREATE OR REPLACE FUNCTION cache_delete(p_key VARCHAR(255))
RETURNS VOID AS $$
BEGIN
    DELETE FROM cache WHERE key = p_key;
END;
$$ LANGUAGE plpgsql;

-- 패턴 매칭 삭제 (예: 'cf:rec:user123:%')
CREATE OR REPLACE FUNCTION cache_delete_pattern(p_pattern VARCHAR(255))
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    DELETE FROM cache WHERE key LIKE p_pattern;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 만료된 캐시 정리
CREATE OR REPLACE FUNCTION cache_cleanup()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    DELETE FROM cache WHERE expires_at < NOW();
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 자동 정리 (pg_cron 사용 시)
-- Supabase에서는 Dashboard > Database > Extensions에서 pg_cron 활성화 후 사용
-- ============================================================
-- SELECT cron.schedule('cache-cleanup', '*/10 * * * *', 'SELECT cache_cleanup()');

-- ============================================================
-- RLS 정책
-- ============================================================
ALTER TABLE cache ENABLE ROW LEVEL SECURITY;

-- service_role만 접근 가능 (백엔드 전용)
DO $$ BEGIN
    CREATE POLICY "Service role full access to cache"
        ON cache FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 권한 부여
GRANT ALL ON cache TO service_role;
GRANT EXECUTE ON FUNCTION cache_get(VARCHAR) TO service_role;
GRANT EXECUTE ON FUNCTION cache_set(VARCHAR, JSONB, INT) TO service_role;
GRANT EXECUTE ON FUNCTION cache_delete(VARCHAR) TO service_role;
GRANT EXECUTE ON FUNCTION cache_delete_pattern(VARCHAR) TO service_role;
GRANT EXECUTE ON FUNCTION cache_cleanup() TO service_role;

DO $$ BEGIN RAISE NOTICE 'PostgreSQL cache table created successfully'; END $$;
