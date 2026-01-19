-- =====================================================
-- ELO 샘플 데이터 삽입 (테스트용)
-- 날짜: 2026-01-18
-- 목적: ELO 그래프 표시 테스트
-- =====================================================

-- 현재 사용자의 elo_history, elo_overall 업데이트
-- 실제 user_id로 교체 필요

-- 1. 먼저 현재 사용자 확인
-- SELECT id, email FROM users LIMIT 5;

-- 2. 샘플 ELO 히스토리 데이터
-- 최근 문제 풀이 기록 시뮬레이션 (DB update_user_elo() 함수 형식)
-- 형식: { date, topic, before, after, change, problem_elo, expected }
UPDATE user_analysis_reports
SET
    elo_history = '[
        {"date": "2026-01-18", "topic": "DP", "before": 980, "after": 1005, "change": 25, "problem_elo": 1050, "expected": 0.42},
        {"date": "2026-01-17", "topic": "Graph", "before": 1000, "after": 980, "change": -20, "problem_elo": 1100, "expected": 0.36},
        {"date": "2026-01-17", "topic": "BFS", "before": 950, "after": 935, "change": -15, "problem_elo": 1100, "expected": 0.30},
        {"date": "2026-01-16", "topic": "String", "before": 1050, "after": 1060, "change": 10, "problem_elo": 900, "expected": 0.71},
        {"date": "2026-01-15", "topic": "Array", "before": 1100, "after": 1108, "change": 8, "problem_elo": 850, "expected": 0.78},
        {"date": "2026-01-14", "topic": "DP", "before": 1000, "after": 980, "change": -20, "problem_elo": 1150, "expected": 0.30},
        {"date": "2026-01-13", "topic": "Graph", "before": 980, "after": 1000, "change": 20, "problem_elo": 950, "expected": 0.54},
        {"date": "2026-01-12", "topic": "Sorting", "before": 1020, "after": 1028, "change": 8, "problem_elo": 800, "expected": 0.76},
        {"date": "2026-01-11", "topic": "String", "before": 1030, "after": 1050, "change": 20, "problem_elo": 950, "expected": 0.61},
        {"date": "2026-01-11", "topic": "Array", "before": 1080, "after": 1100, "change": 20, "problem_elo": 950, "expected": 0.66},
        {"date": "2026-01-10", "topic": "DP", "before": 1020, "after": 1000, "change": -20, "problem_elo": 1200, "expected": 0.25},
        {"date": "2026-01-09", "topic": "BFS", "before": 920, "after": 950, "change": 30, "problem_elo": 900, "expected": 0.53}
    ]'::jsonb,
    elo_overall = 1020,
    elo_by_topic = '{
        "DP": 1005,
        "Graph": 980,
        "BFS": 935,
        "String": 1060,
        "Array": 1108,
        "Sorting": 1028
    }'::jsonb
WHERE user_id = 'ccb94830-e83e-44b2-be14-67d02475eaf8';

-- 3. 결과 확인
SELECT
    user_id,
    elo_overall,
    jsonb_array_length(elo_history) as history_count,
    elo_history
FROM user_analysis_reports
WHERE elo_history IS NOT NULL AND elo_history != '[]'::jsonb
LIMIT 1;
