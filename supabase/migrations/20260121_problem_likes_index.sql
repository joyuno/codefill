-- =====================================================
-- Problem Likes Table & Index Optimization
-- 좋아요 조회 성능 최적화
-- =====================================================

-- 1. problem_likes 테이블 생성 (없는 경우)
CREATE TABLE IF NOT EXISTS problem_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    base_problem_id UUID NOT NULL REFERENCES base_problems(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- 중복 좋아요 방지
    UNIQUE(user_id, base_problem_id)
);

-- 2. 복합 인덱스 추가 (user_id, base_problem_id)
-- is_liked 조회 시 사용: WHERE user_id = ? AND base_problem_id = ?
-- UNIQUE 제약조건이 이미 인덱스 역할을 하지만, 명시적으로 추가
CREATE INDEX IF NOT EXISTS idx_problem_likes_user_problem
ON problem_likes(user_id, base_problem_id);

-- 3. base_problem_id 단일 인덱스 (문제별 좋아요 수 집계용)
CREATE INDEX IF NOT EXISTS idx_problem_likes_problem
ON problem_likes(base_problem_id);

-- 4. RLS (Row Level Security) 정책
ALTER TABLE problem_likes ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 좋아요만 조회 가능
DO $$ BEGIN
    CREATE POLICY "Users can view own likes"
        ON problem_likes FOR SELECT TO authenticated
        USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 사용자는 자신의 좋아요만 추가/삭제 가능
DO $$ BEGIN
    CREATE POLICY "Users can insert own likes"
        ON problem_likes FOR INSERT TO authenticated
        WITH CHECK (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Users can delete own likes"
        ON problem_likes FOR DELETE TO authenticated
        USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- service_role 전체 권한
DO $$ BEGIN
    CREATE POLICY "Service role full access to likes"
        ON problem_likes FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 5. 권한 부여
GRANT SELECT, INSERT, DELETE ON problem_likes TO authenticated;
GRANT ALL ON problem_likes TO service_role;

-- 6. 인덱스 통계 갱신
ANALYZE problem_likes;
