-- =====================================================
-- CodeFill Database Migration: Solution Views
-- 날짜: 2026-01-06
-- 목적: solution_details, comment_details 뷰 생성
-- 참조: 20251229_problem_solutions_system.sql (테이블은 이미 존재)
-- =====================================================

-- =====================================================
-- 1. 뷰: 풀이 상세 (작성자 정보 포함)
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
-- 2. 뷰: 댓글 상세 (작성자 정보 포함)
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
-- 3. 코멘트 (문서화)
-- =====================================================
COMMENT ON VIEW solution_details IS '풀이 상세 정보 (작성자 정보, 문제 정보, 댓글 수 포함)';
COMMENT ON VIEW comment_details IS '댓글 상세 정보 (작성자 정보, 대댓글 수 포함)';
