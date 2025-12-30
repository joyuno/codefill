-- =====================================================
-- CodeFill Database Migration: Problem Solutions System
-- 날짜: 2025-12-29
-- 목적: 문제 게시글 시스템 (사용자 풀이, 댓글, 투표)
-- =====================================================

-- =====================================================
-- 1. problem_solutions (사용자 풀이)
-- =====================================================
CREATE TABLE IF NOT EXISTS problem_solutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_problem_id UUID NOT NULL REFERENCES base_problems(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    title VARCHAR(200),
    description TEXT,
    is_correct BOOLEAN DEFAULT TRUE,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_solutions_problem ON problem_solutions(base_problem_id);
CREATE INDEX IF NOT EXISTS idx_solutions_user ON problem_solutions(user_id);
CREATE INDEX IF NOT EXISTS idx_solutions_language ON problem_solutions(language);
CREATE INDEX IF NOT EXISTS idx_solutions_created ON problem_solutions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_solutions_upvotes ON problem_solutions(upvotes DESC);

-- =====================================================
-- 2. solution_comments (댓글/대댓글)
-- =====================================================
CREATE TABLE IF NOT EXISTS solution_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES problem_solutions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES solution_comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_comments_solution ON solution_comments(solution_id);
CREATE INDEX IF NOT EXISTS idx_comments_user ON solution_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_parent ON solution_comments(parent_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON solution_comments(created_at);

-- =====================================================
-- 3. solution_votes (풀이 투표)
-- =====================================================
CREATE TABLE IF NOT EXISTS solution_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES problem_solutions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(4) NOT NULL CHECK (vote_type IN ('up', 'down')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(solution_id, user_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_solution_votes_solution ON solution_votes(solution_id);
CREATE INDEX IF NOT EXISTS idx_solution_votes_user ON solution_votes(user_id);

-- =====================================================
-- 4. comment_votes (댓글 투표)
-- =====================================================
CREATE TABLE IF NOT EXISTS comment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL REFERENCES solution_comments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(4) NOT NULL CHECK (vote_type IN ('up', 'down')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(comment_id, user_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_comment_votes_comment ON comment_votes(comment_id);
CREATE INDEX IF NOT EXISTS idx_comment_votes_user ON comment_votes(user_id);

-- =====================================================
-- 5. 트리거: updated_at 자동 갱신
-- =====================================================
CREATE TRIGGER update_problem_solutions_updated_at
    BEFORE UPDATE ON problem_solutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solution_comments_updated_at
    BEFORE UPDATE ON solution_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 6. 투표 시 upvotes/downvotes 자동 갱신 함수
-- =====================================================

-- 풀이 투표 트리거 함수
CREATE OR REPLACE FUNCTION update_solution_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE problem_solutions SET upvotes = upvotes + 1 WHERE id = NEW.solution_id;
        ELSE
            UPDATE problem_solutions SET downvotes = downvotes + 1 WHERE id = NEW.solution_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.vote_type = 'up' THEN
            UPDATE problem_solutions SET upvotes = upvotes - 1 WHERE id = OLD.solution_id;
        ELSE
            UPDATE problem_solutions SET downvotes = downvotes - 1 WHERE id = OLD.solution_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' AND OLD.vote_type != NEW.vote_type THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE problem_solutions SET upvotes = upvotes + 1, downvotes = downvotes - 1 WHERE id = NEW.solution_id;
        ELSE
            UPDATE problem_solutions SET upvotes = upvotes - 1, downvotes = downvotes + 1 WHERE id = NEW.solution_id;
        END IF;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_solution_vote_change
    AFTER INSERT OR UPDATE OR DELETE ON solution_votes
    FOR EACH ROW EXECUTE FUNCTION update_solution_vote_counts();

-- 댓글 투표 트리거 함수
CREATE OR REPLACE FUNCTION update_comment_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE solution_comments SET upvotes = upvotes + 1 WHERE id = NEW.comment_id;
        ELSE
            UPDATE solution_comments SET downvotes = downvotes + 1 WHERE id = NEW.comment_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.vote_type = 'up' THEN
            UPDATE solution_comments SET upvotes = upvotes - 1 WHERE id = OLD.comment_id;
        ELSE
            UPDATE solution_comments SET downvotes = downvotes - 1 WHERE id = OLD.comment_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' AND OLD.vote_type != NEW.vote_type THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE solution_comments SET upvotes = upvotes + 1, downvotes = downvotes - 1 WHERE id = NEW.comment_id;
        ELSE
            UPDATE solution_comments SET upvotes = upvotes - 1, downvotes = downvotes + 1 WHERE id = NEW.comment_id;
        END IF;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_comment_vote_change
    AFTER INSERT OR UPDATE OR DELETE ON comment_votes
    FOR EACH ROW EXECUTE FUNCTION update_comment_vote_counts();

-- =====================================================
-- 7. RLS (Row Level Security)
-- =====================================================
ALTER TABLE problem_solutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE solution_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE solution_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comment_votes ENABLE ROW LEVEL SECURITY;

-- problem_solutions 정책
CREATE POLICY "Anyone can view solutions" ON problem_solutions
    FOR SELECT USING (true);

CREATE POLICY "Users can create own solutions" ON problem_solutions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own solutions" ON problem_solutions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own solutions" ON problem_solutions
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage solutions" ON problem_solutions
    FOR ALL USING (auth.role() = 'service_role');

-- solution_comments 정책
CREATE POLICY "Anyone can view comments" ON solution_comments
    FOR SELECT USING (true);

CREATE POLICY "Users can create comments" ON solution_comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own comments" ON solution_comments
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own comments" ON solution_comments
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage comments" ON solution_comments
    FOR ALL USING (auth.role() = 'service_role');

-- solution_votes 정책
CREATE POLICY "Anyone can view solution votes" ON solution_votes
    FOR SELECT USING (true);

CREATE POLICY "Users can manage own solution votes" ON solution_votes
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage solution_votes" ON solution_votes
    FOR ALL USING (auth.role() = 'service_role');

-- comment_votes 정책
CREATE POLICY "Anyone can view comment votes" ON comment_votes
    FOR SELECT USING (true);

CREATE POLICY "Users can manage own comment votes" ON comment_votes
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage comment_votes" ON comment_votes
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 8. 뷰: 풀이 상세 (작성자 정보 포함)
-- =====================================================
CREATE OR REPLACE VIEW solution_details AS
SELECT
    ps.id,
    ps.base_problem_id,
    ps.user_id,
    ps.language,
    ps.code,
    ps.title,
    ps.description,
    ps.is_correct,
    ps.upvotes,
    ps.downvotes,
    ps.view_count,
    ps.created_at,
    ps.updated_at,
    u.name as author_name,
    u.avatar_url as author_avatar,
    bp.original_id as problem_original_id,
    bp.name as problem_name,
    (SELECT COUNT(*) FROM solution_comments sc WHERE sc.solution_id = ps.id AND sc.is_deleted = FALSE) as comment_count
FROM problem_solutions ps
LEFT JOIN users u ON ps.user_id = u.id
LEFT JOIN base_problems bp ON ps.base_problem_id = bp.id;

-- 뷰 권한
GRANT SELECT ON solution_details TO authenticated;
GRANT SELECT ON solution_details TO anon;
GRANT SELECT ON solution_details TO service_role;

-- =====================================================
-- 9. 뷰: 댓글 상세 (작성자 정보 포함)
-- =====================================================
CREATE OR REPLACE VIEW comment_details AS
SELECT
    sc.id,
    sc.solution_id,
    sc.user_id,
    sc.parent_id,
    sc.content,
    sc.upvotes,
    sc.downvotes,
    sc.is_deleted,
    sc.created_at,
    sc.updated_at,
    u.name as author_name,
    u.avatar_url as author_avatar,
    (SELECT COUNT(*) FROM solution_comments child WHERE child.parent_id = sc.id AND child.is_deleted = FALSE) as reply_count
FROM solution_comments sc
LEFT JOIN users u ON sc.user_id = u.id;

-- 뷰 권한
GRANT SELECT ON comment_details TO authenticated;
GRANT SELECT ON comment_details TO anon;
GRANT SELECT ON comment_details TO service_role;

-- =====================================================
-- 10. 테이블 권한
-- =====================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON problem_solutions TO authenticated;
GRANT SELECT ON problem_solutions TO anon;
GRANT ALL ON problem_solutions TO service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON solution_comments TO authenticated;
GRANT SELECT ON solution_comments TO anon;
GRANT ALL ON solution_comments TO service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON solution_votes TO authenticated;
GRANT SELECT ON solution_votes TO anon;
GRANT ALL ON solution_votes TO service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON comment_votes TO authenticated;
GRANT SELECT ON comment_votes TO anon;
GRANT ALL ON comment_votes TO service_role;

-- =====================================================
-- 11. 코멘트 (문서화)
-- =====================================================
COMMENT ON TABLE problem_solutions IS '사용자가 제출한 문제 풀이 코드';
COMMENT ON TABLE solution_comments IS '풀이에 대한 댓글 (대댓글 지원)';
COMMENT ON TABLE solution_votes IS '풀이 좋아요/싫어요 투표';
COMMENT ON TABLE comment_votes IS '댓글 좋아요/싫어요 투표';

COMMENT ON COLUMN problem_solutions.is_correct IS '코드 실행 결과 정답 여부';
COMMENT ON COLUMN solution_comments.parent_id IS '대댓글인 경우 부모 댓글 ID';
COMMENT ON COLUMN solution_comments.is_deleted IS '소프트 삭제 (대댓글 유지용)';
