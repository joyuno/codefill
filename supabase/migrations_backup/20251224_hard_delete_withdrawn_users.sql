-- =====================================================
-- 탈퇴 사용자 30일 후 영구 삭제 (Hard Delete)
-- 날짜: 2025-12-24
-- 목적: 개인정보보호법 준수 - 탈퇴 후 30일 경과 시 데이터 완전 삭제
-- =====================================================
--
-- 플로우:
--   1. 사용자 탈퇴 → deleted_at 타임스탬프 설정 (soft delete)
--   2. 30일 이내 → 로그인 시 계정 복구 가능
--   3. 30일 경과 → 이 함수가 실행되어 완전 삭제
--
-- 실행 방법:
--   - Supabase pg_cron (Pro 플랜): 자동 스케줄링
--   - Edge Function + 외부 스케줄러: 매일 함수 호출
--   - 수동 실행: SELECT hard_delete_withdrawn_users();
-- =====================================================

-- 1. 탈퇴 사용자 영구 삭제 함수
CREATE OR REPLACE FUNCTION hard_delete_withdrawn_users()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 관련 테이블 먼저 삭제 (CASCADE가 설정되지 않은 경우)
    -- user_stats
    DELETE FROM user_stats
    WHERE user_id IN (
        SELECT id FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    );

    -- user_preferences
    DELETE FROM user_preferences
    WHERE user_id IN (
        SELECT id FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    );

    -- attempts (문제 풀이 기록)
    DELETE FROM attempts
    WHERE user_id IN (
        SELECT id FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    );

    -- users 테이블에서 삭제
    WITH deleted AS (
        DELETE FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$;

-- 2. 함수 실행 권한 설정
GRANT EXECUTE ON FUNCTION hard_delete_withdrawn_users() TO service_role;

-- 3. pg_cron 스케줄 설정 (Supabase Pro 플랜 이상에서만 사용 가능)
-- 매일 새벽 3시(KST, UTC+9 → UTC 18:00)에 실행
--
-- pg_cron이 활성화되어 있다면 아래 주석을 해제하세요:
--
-- SELECT cron.schedule(
--     'hard-delete-withdrawn-users',   -- job name
--     '0 18 * * *',                     -- cron expression (매일 UTC 18:00 = KST 03:00)
--     $$SELECT hard_delete_withdrawn_users()$$
-- );

-- =====================================================
-- 대안: Supabase Edge Function으로 구현
-- =====================================================
--
-- 1. Edge Function 생성: supabase/functions/cleanup-users/index.ts
-- 2. 외부 스케줄러(cron-job.org, GitHub Actions 등)로 매일 호출
--
-- Edge Function 예시:
-- ```typescript
-- import { createClient } from '@supabase/supabase-js'
--
-- Deno.serve(async () => {
--   const supabase = createClient(
--     Deno.env.get('SUPABASE_URL')!,
--     Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
--   )
--
--   const { data, error } = await supabase.rpc('hard_delete_withdrawn_users')
--
--   return new Response(JSON.stringify({ deleted_count: data, error }))
-- })
-- ```
-- =====================================================

COMMENT ON FUNCTION hard_delete_withdrawn_users() IS '탈퇴 후 30일 경과한 사용자 데이터를 영구 삭제합니다.';
