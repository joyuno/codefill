-- =====================================================
-- Add banned_until column for user suspension system
-- =====================================================
-- banned_until = NULL → 정상 상태
-- banned_until > NOW() → 정지 중
-- banned_until <= NOW() → 정지 만료 (자동 해제)
-- banned_until = '9999-12-31' → 영구 정지

ALTER TABLE users ADD COLUMN IF NOT EXISTS banned_until TIMESTAMPTZ DEFAULT NULL;

-- Optional: Add index for efficient banned user queries
CREATE INDEX IF NOT EXISTS idx_users_banned_until ON users(banned_until) WHERE banned_until IS NOT NULL;

COMMENT ON COLUMN users.banned_until IS '사용자 정지 만료일. NULL=정상, 미래날짜=정지중, 9999-12-31=영구정지';
