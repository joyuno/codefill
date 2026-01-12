-- ============================================================
-- user_memories 테이블 최적화
--
-- 변경사항:
-- 1. learning_insights JSONB 컬럼 추가 (통합 인사이트)
-- 2. 중복 컬럼 deprecate (삭제는 다음 마이그레이션에서)
-- 3. attempt_id FK 확인
-- ============================================================

-- 1. learning_insights JSONB 컬럼 추가
ALTER TABLE user_memories
ADD COLUMN IF NOT EXISTS learning_insights JSONB DEFAULT '{}';

-- 컬럼 설명
COMMENT ON COLUMN user_memories.learning_insights IS '통합 학습 인사이트 JSONB:
{
  "concepts_learned": ["이해한 개념들"],
  "concepts_struggling": ["어려워하는 개념들"],
  "student_questions": ["학생이 한 질문들"],
  "breakthrough_moments": ["아하! 순간들"],
  "teaching_notes": ["교육 노트"],
  "effective_approaches": ["효과적인 접근법"],
  "understanding_progress": [0.3, 0.5, 0.8],
  "mood_changes": ["frustrated", "curious", "confident"],
  "hint_effectiveness": {"hint1": true, "hint2": false}
}';

-- 2. attempt_id FK 확인 및 인덱스
DO $$
BEGIN
    -- attempt_id 컬럼이 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_memories' AND column_name = 'attempt_id'
    ) THEN
        ALTER TABLE user_memories ADD COLUMN attempt_id UUID;
    END IF;
END $$;

-- attempt_id 인덱스 (조인 성능)
CREATE INDEX IF NOT EXISTS user_memories_attempt_idx ON user_memories(attempt_id);

-- 3. 기존 NULL 데이터를 기본값으로 마이그레이션
UPDATE user_memories
SET learning_insights = jsonb_build_object(
    'concepts_learned', COALESCE(concepts_learned, ARRAY[]::TEXT[]),
    'concepts_struggling', COALESCE(concepts_struggling, ARRAY[]::TEXT[]),
    'student_questions', COALESCE(student_questions, ARRAY[]::TEXT[]),
    'breakthrough_moments', COALESCE(breakthrough_moments, ARRAY[]::TEXT[]),
    'teaching_notes', COALESCE(teaching_notes, ARRAY[]::TEXT[]),
    'effective_approaches', COALESCE(effective_approaches, ARRAY[]::TEXT[]),
    'understanding_progress', '[]'::jsonb,
    'mood_changes', CASE
        WHEN student_mood IS NOT NULL THEN jsonb_build_array(student_mood)
        ELSE '[]'::jsonb
    END
)
WHERE learning_insights = '{}' OR learning_insights IS NULL;

-- 4. 향후 deprecate할 컬럼들 표시 (주석으로만, 실제 삭제는 안함)
-- 다음 컬럼들은 learning_insights로 통합됨:
-- - concepts_learned
-- - concepts_struggling
-- - teaching_notes
-- - student_questions
-- - breakthrough_moments
-- - effective_approaches
-- - student_mood
-- - conversation_tone

-- 다음 컬럼들은 attempts 테이블과 중복됨 (attempt_id로 조인):
-- - problem_id
-- - problem_name
-- - problem_type
-- - problem_difficulty
-- - attempt_count

-- 5. learning_insights 검색용 GIN 인덱스
CREATE INDEX IF NOT EXISTS user_memories_insights_idx
ON user_memories USING GIN(learning_insights);

-- 6. 유용한 뷰 생성: 학습 인사이트 조회용
CREATE OR REPLACE VIEW v_user_learning_insights AS
SELECT
    um.id,
    um.user_id,
    um.session_id,
    um.created_at,
    um.summary,
    um.was_successful,
    um.hints_needed,
    um.duration_seconds,
    -- learning_insights 필드들
    um.learning_insights->>'concepts_learned' as concepts_learned_json,
    um.learning_insights->>'concepts_struggling' as concepts_struggling_json,
    um.learning_insights->>'student_questions' as student_questions_json,
    um.learning_insights->>'breakthrough_moments' as breakthrough_moments_json,
    um.learning_insights->>'understanding_progress' as understanding_progress_json,
    -- attempts 조인 (attempt_id 있는 경우)
    a.problem_name,
    a.problem_type,
    a.difficulty as problem_difficulty,
    a.topics as problem_topics
FROM user_memories um
LEFT JOIN attempts a ON um.attempt_id = a.id;

COMMENT ON VIEW v_user_learning_insights IS '학습 인사이트 통합 뷰 - learning_insights JSONB + attempts 조인';

-- 7. 통계 함수: 사용자 학습 패턴 분석
CREATE OR REPLACE FUNCTION get_user_learning_patterns(p_user_id UUID, p_days INT DEFAULT 30)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_sessions', COUNT(*),
        'success_rate', ROUND(AVG(CASE WHEN was_successful THEN 1.0 ELSE 0.0 END)::numeric, 2),
        'avg_hints_used', ROUND(AVG(COALESCE(hints_needed, 0))::numeric, 1),
        'avg_duration_seconds', ROUND(AVG(COALESCE(duration_seconds, 0))::numeric, 0),
        'common_struggles', (
            SELECT jsonb_agg(DISTINCT concept)
            FROM user_memories um2,
            LATERAL jsonb_array_elements_text(um2.learning_insights->'concepts_struggling') as concept
            WHERE um2.user_id = p_user_id
            AND um2.created_at >= NOW() - (p_days || ' days')::interval
            LIMIT 5
        ),
        'recent_breakthroughs', (
            SELECT jsonb_agg(DISTINCT moment)
            FROM user_memories um3,
            LATERAL jsonb_array_elements_text(um3.learning_insights->'breakthrough_moments') as moment
            WHERE um3.user_id = p_user_id
            AND um3.created_at >= NOW() - (p_days || ' days')::interval
            LIMIT 5
        )
    ) INTO result
    FROM user_memories
    WHERE user_id = p_user_id
    AND created_at >= NOW() - (p_days || ' days')::interval;

    RETURN COALESCE(result, '{}'::jsonb);
END;
$$;

COMMENT ON FUNCTION get_user_learning_patterns IS '사용자 학습 패턴 분석 (성공률, 힌트 사용, 어려운 개념, 돌파 순간)';

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'user_memories 최적화 완료:';
    RAISE NOTICE '  - learning_insights JSONB 컬럼 추가';
    RAISE NOTICE '  - 기존 데이터 마이그레이션';
    RAISE NOTICE '  - v_user_learning_insights 뷰 생성';
    RAISE NOTICE '  - get_user_learning_patterns() 함수 생성';
END $$;
