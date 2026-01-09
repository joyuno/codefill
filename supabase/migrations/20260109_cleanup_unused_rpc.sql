-- =====================================================
-- Cleanup unused RPC functions
-- 2026-01-09
-- 백엔드에서 직접 쿼리 사용으로 인해 불필요해진 함수들 제거
-- =====================================================

-- Drop unused public profile RPC function
DROP FUNCTION IF EXISTS get_public_profile_all(TEXT, INTEGER);

-- Drop unused helper functions (backend uses Python implementation)
DROP FUNCTION IF EXISTS calculate_level_from_xp(INTEGER);
DROP FUNCTION IF EXISTS calculate_current_xp(INTEGER);
DROP FUNCTION IF EXISTS calculate_required_xp(INTEGER);
