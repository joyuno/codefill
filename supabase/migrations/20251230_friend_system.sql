-- =====================================================
-- CodeFill Database Migration: Friend System
-- 날짜: 2025-12-30
-- 목적: 친구 시스템 (친구 요청, 수락/거부, 1:1 메시지)
-- =====================================================

-- =====================================================
-- 1. friendships (친구 관계)
-- =====================================================
CREATE TABLE IF NOT EXISTS friendships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    addressee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted')),
    blocked_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 자기 자신에게 요청 방지
    CONSTRAINT friendships_no_self CHECK (requester_id != addressee_id)
);

-- 중복 관계 방지를 위한 unique index (A→B와 B→A 모두 방지)
CREATE UNIQUE INDEX IF NOT EXISTS idx_friendships_unique_pair
ON friendships (LEAST(requester_id, addressee_id), GREATEST(requester_id, addressee_id));

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_friendships_requester ON friendships(requester_id);
CREATE INDEX IF NOT EXISTS idx_friendships_addressee ON friendships(addressee_id);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_friendships_accepted ON friendships(status) WHERE status = 'accepted' AND blocked_at IS NULL;

-- =====================================================
-- 2. direct_messages (1:1 메시지)
-- =====================================================
CREATE TABLE IF NOT EXISTS direct_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_by_sender BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_by_receiver BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 자기 자신에게 메시지 방지
    CONSTRAINT dm_no_self CHECK (sender_id != receiver_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_dm_sender ON direct_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_dm_receiver ON direct_messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_dm_conversation ON direct_messages(
    LEAST(sender_id, receiver_id),
    GREATEST(sender_id, receiver_id),
    created_at DESC
);
CREATE INDEX IF NOT EXISTS idx_dm_unread ON direct_messages(receiver_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_dm_created ON direct_messages(created_at DESC);

-- =====================================================
-- 3. 트리거: updated_at 자동 갱신
-- =====================================================
CREATE TRIGGER update_friendships_updated_at
    BEFORE UPDATE ON friendships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 4. RLS (Row Level Security)
-- =====================================================
ALTER TABLE friendships ENABLE ROW LEVEL SECURITY;
ALTER TABLE direct_messages ENABLE ROW LEVEL SECURITY;

-- friendships 정책
CREATE POLICY "Users can view their own friendships" ON friendships
    FOR SELECT USING (auth.uid() = requester_id OR auth.uid() = addressee_id);

CREATE POLICY "Users can create friend requests" ON friendships
    FOR INSERT WITH CHECK (auth.uid() = requester_id);

CREATE POLICY "Users can update their own friendships" ON friendships
    FOR UPDATE USING (auth.uid() = requester_id OR auth.uid() = addressee_id);

CREATE POLICY "Users can delete their own friendships" ON friendships
    FOR DELETE USING (auth.uid() = requester_id OR auth.uid() = addressee_id);

CREATE POLICY "Service role can manage friendships" ON friendships
    FOR ALL USING (auth.role() = 'service_role');

-- direct_messages 정책
CREATE POLICY "Users can view their own messages" ON direct_messages
    FOR SELECT USING (
        (auth.uid() = sender_id AND NOT deleted_by_sender) OR
        (auth.uid() = receiver_id AND NOT deleted_by_receiver)
    );

CREATE POLICY "Users can send messages" ON direct_messages
    FOR INSERT WITH CHECK (auth.uid() = sender_id);

CREATE POLICY "Users can update their own messages" ON direct_messages
    FOR UPDATE USING (auth.uid() = sender_id OR auth.uid() = receiver_id);

CREATE POLICY "Service role can manage messages" ON direct_messages
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 5. 뷰: 친구 관계 상세 (사용자 정보 포함)
-- =====================================================
CREATE OR REPLACE VIEW friendship_details AS
SELECT
    f.id,
    f.requester_id,
    f.addressee_id,
    f.status,
    f.blocked_at,
    f.created_at,
    f.updated_at,
    req.name as requester_name,
    req.avatar_url as requester_avatar,
    addr.name as addressee_name,
    addr.avatar_url as addressee_avatar
FROM friendships f
LEFT JOIN users req ON f.requester_id = req.id
LEFT JOIN users addr ON f.addressee_id = addr.id;

-- 뷰 권한
GRANT SELECT ON friendship_details TO authenticated;
GRANT SELECT ON friendship_details TO service_role;

-- =====================================================
-- 6. 뷰: 메시지 상세 (발신자 정보 포함)
-- =====================================================
CREATE OR REPLACE VIEW message_details AS
SELECT
    m.id,
    m.sender_id,
    m.receiver_id,
    m.content,
    m.is_read,
    m.deleted_by_sender,
    m.deleted_by_receiver,
    m.created_at,
    s.name as sender_name,
    s.avatar_url as sender_avatar
FROM direct_messages m
LEFT JOIN users s ON m.sender_id = s.id;

-- 뷰 권한
GRANT SELECT ON message_details TO authenticated;
GRANT SELECT ON message_details TO service_role;

-- =====================================================
-- 7. 테이블 권한
-- =====================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON friendships TO authenticated;
GRANT ALL ON friendships TO service_role;

GRANT SELECT, INSERT, UPDATE ON direct_messages TO authenticated;
GRANT ALL ON direct_messages TO service_role;

-- =====================================================
-- 8. 코멘트 (문서화)
-- =====================================================
COMMENT ON TABLE friendships IS '사용자 간 친구 관계 (요청, 수락, 차단)';
COMMENT ON TABLE direct_messages IS '1:1 다이렉트 메시지';

COMMENT ON COLUMN friendships.status IS '관계 상태: pending(요청중), accepted(친구)';
COMMENT ON COLUMN friendships.blocked_at IS '차단 시간 (NULL이면 차단 안함)';
COMMENT ON COLUMN direct_messages.is_read IS '수신자가 읽었는지 여부';
COMMENT ON COLUMN direct_messages.deleted_by_sender IS '발신자가 삭제했는지 (soft delete)';
COMMENT ON COLUMN direct_messages.deleted_by_receiver IS '수신자가 삭제했는지 (soft delete)';
