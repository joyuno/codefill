-- Fix user_badges RLS policy
-- fix_rls.sql에서 DROP만 하고 재생성 안 한 정책 복구

-- Service role 정책 복구 (init_schema.sql 원본과 동일)
DROP POLICY IF EXISTS "Service role can manage user_badges" ON user_badges;
CREATE POLICY "Service role can manage user_badges" ON user_badges
    FOR ALL USING (auth.role() = 'service_role');

-- GRANT 추가 (다른 테이블들과 동일한 패턴)
GRANT ALL ON user_badges TO service_role;
