-- =====================================================
-- 테스트 데이터 삽입 (약점 분석 테스트용)
-- UUID: 0c3d30cb-c560-4046-bbd2-b910e4575181
-- 시나리오: DP/Graph 약함, Array/String 강함
-- =====================================================

-- 0. 기존 테스트 데이터 삭제
DELETE FROM hint_logs WHERE user_id = '0c3d30cb-c560-4046-bbd2-b910e4575181';
DELETE FROM attempt_details WHERE attempt_id IN (
    SELECT id FROM attempts WHERE user_id = '0c3d30cb-c560-4046-bbd2-b910e4575181'
);
DELETE FROM attempts WHERE user_id = '0c3d30cb-c560-4046-bbd2-b910e4575181';
DELETE FROM user_memories WHERE user_id = '0c3d30cb-c560-4046-bbd2-b910e4575181';
DELETE FROM user_analysis_reports WHERE user_id = '0c3d30cb-c560-4046-bbd2-b910e4575181';

-- =====================================================
-- 1. user_stats 업데이트
-- =====================================================
INSERT INTO user_stats (user_id, level, total_xp, problems_solved, problems_attempted,
                        current_streak, longest_streak, last_activity_date,
                        blank_solved, puzzle_solved, guided_solved,
                        easy_solved, medium_solved, hard_solved)
VALUES ('0c3d30cb-c560-4046-bbd2-b910e4575181', 5, 1500, 47, 63, 3, 7, CURRENT_DATE,
        30, 10, 7, 20, 20, 7)
ON CONFLICT (user_id) DO UPDATE SET
    level = 5, total_xp = 1500, problems_solved = 47, problems_attempted = 63,
    current_streak = 3, longest_streak = 7, last_activity_date = CURRENT_DATE,
    blank_solved = 30, puzzle_solved = 10, guided_solved = 7,
    easy_solved = 20, medium_solved = 20, hard_solved = 7;

-- =====================================================
-- 2. attempts 삽입 (ID 명시)
-- =====================================================

-- Array (강함: 12개 중 11개 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000001-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 순회 기초', true, 0, 120, NOW() - INTERVAL '30 days'),
('a0000001-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 합계 구하기', true, 0, 90, NOW() - INTERVAL '29 days'),
('a0000001-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 최대값 찾기', true, 0, 100, NOW() - INTERVAL '28 days'),
('a0000001-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Two Pointers'], 'medium', 'blank', 'Array 투 포인터', true, 0, 180, NOW() - INTERVAL '27 days'),
('a0000001-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Sorting'], 'medium', 'blank', 'Array 정렬하기', true, 0, 150, NOW() - INTERVAL '26 days'),
('a0000001-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 뒤집기', false, 1, 200, NOW() - INTERVAL '25 days'),
('a0000001-0000-0000-0000-000000000007', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'medium', 'blank', 'Array 중복 제거', true, 0, 140, NOW() - INTERVAL '24 days'),
('a0000001-0000-0000-0000-000000000008', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Sliding Window'], 'medium', 'blank', 'Array 슬라이딩 윈도우', true, 0, 200, NOW() - INTERVAL '23 days'),
('a0000001-0000-0000-0000-000000000009', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 회전', true, 0, 130, NOW() - INTERVAL '22 days'),
('a0000001-0000-0000-0000-000000000010', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'medium', 'blank', 'Array 구간 합', true, 0, 160, NOW() - INTERVAL '21 days'),
('a0000001-0000-0000-0000-000000000011', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'easy', 'blank', 'Array 필터링', true, 0, 110, NOW() - INTERVAL '20 days'),
('a0000001-0000-0000-0000-000000000012', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Array', 'Implementation'], 'medium', 'blank', 'Array 병합', true, 0, 170, NOW() - INTERVAL '19 days');

-- String (강함: 10개 중 9개 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000002-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 뒤집기', true, 0, 80, NOW() - INTERVAL '29 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 길이 세기', true, 0, 60, NOW() - INTERVAL '28 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 대소문자 변환', true, 0, 90, NOW() - INTERVAL '27 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'medium', 'blank', 'String 팰린드롬', false, 1, 250, NOW() - INTERVAL '26 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 공백 제거', true, 0, 70, NOW() - INTERVAL '25 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'medium', 'blank', 'String 압축', true, 0, 200, NOW() - INTERVAL '24 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000007', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 단어 세기', true, 0, 100, NOW() - INTERVAL '23 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000008', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'medium', 'blank', 'String 아나그램', true, 0, 180, NOW() - INTERVAL '22 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000009', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'easy', 'blank', 'String 치환', true, 0, 90, NOW() - INTERVAL '21 days' + INTERVAL '2 hours'),
('a0000002-0000-0000-0000-000000000010', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['String', 'Implementation'], 'medium', 'blank', 'String 부분 문자열', true, 0, 150, NOW() - INTERVAL '20 days' + INTERVAL '2 hours');

-- DP (약함: 15개 중 3개만 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000003-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 피보나치', false, 2, 400, NOW() - INTERVAL '28 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 계단 오르기', false, 3, 500, NOW() - INTERVAL '27 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'guided', 'DP 동전 교환', true, 2, 600, NOW() - INTERVAL '26 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 최대 부분합', false, 3, 450, NOW() - INTERVAL '25 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP LIS', false, 3, 550, NOW() - INTERVAL '24 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'hard', 'blank', 'DP 배낭 문제', false, 3, 700, NOW() - INTERVAL '23 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000007', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'guided', 'DP 격자 경로', false, 3, 480, NOW() - INTERVAL '22 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000008', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 타일링', true, 1, 350, NOW() - INTERVAL '21 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000009', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'hard', 'blank', 'DP LCS', false, 3, 650, NOW() - INTERVAL '20 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000010', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 구간 합', false, 2, 400, NOW() - INTERVAL '19 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000011', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'hard', 'guided', 'DP 편집 거리', false, 3, 800, NOW() - INTERVAL '18 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000012', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 점프 게임', false, 3, 420, NOW() - INTERVAL '17 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000013', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'hard', 'blank', 'DP 행렬 곱셈', true, 2, 550, NOW() - INTERVAL '16 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000014', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'medium', 'blank', 'DP 동전 개수', false, 3, 380, NOW() - INTERVAL '15 days' + INTERVAL '4 hours'),
('a0000003-0000-0000-0000-000000000015', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['DP', 'Dynamic Programming'], 'hard', 'blank', 'DP 부분집합 합', false, 3, 720, NOW() - INTERVAL '14 days' + INTERVAL '4 hours');

-- Graph (약함: 12개 중 2개만 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000004-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'BFS'], 'medium', 'blank', 'Graph BFS 기초', false, 3, 500, NOW() - INTERVAL '27 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'DFS'], 'medium', 'blank', 'Graph DFS 기초', false, 3, 480, NOW() - INTERVAL '26 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'BFS'], 'medium', 'guided', 'Graph 미로 탐색', false, 3, 600, NOW() - INTERVAL '25 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'DFS'], 'medium', 'blank', 'Graph 섬 개수', false, 3, 550, NOW() - INTERVAL '24 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'BFS'], 'medium', 'blank', 'Graph 최단 거리', true, 2, 400, NOW() - INTERVAL '23 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'DFS'], 'hard', 'blank', 'Graph 연결 요소', false, 3, 650, NOW() - INTERVAL '22 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000007', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'Dijkstra'], 'hard', 'guided', 'Graph 다익스트라', false, 3, 800, NOW() - INTERVAL '21 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000008', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'BFS'], 'medium', 'blank', 'Graph 레벨 순회', false, 3, 520, NOW() - INTERVAL '20 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000009', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'DFS'], 'medium', 'blank', 'Graph 사이클 탐지', false, 3, 580, NOW() - INTERVAL '19 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000010', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'Dijkstra'], 'hard', 'blank', 'Graph 최단 경로', true, 2, 450, NOW() - INTERVAL '18 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000011', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'BFS'], 'hard', 'blank', 'Graph 이분 그래프', false, 3, 700, NOW() - INTERVAL '17 days' + INTERVAL '6 hours'),
('a0000004-0000-0000-0000-000000000012', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Graph', 'DFS'], 'hard', 'blank', 'Graph 위상 정렬', false, 3, 750, NOW() - INTERVAL '16 days' + INTERVAL '6 hours');

-- Binary Search (중간: 8개 중 5개 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000005-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search 기본', true, 0, 200, NOW() - INTERVAL '26 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search 범위', false, 1, 300, NOW() - INTERVAL '25 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search Lower Bound', true, 0, 250, NOW() - INTERVAL '24 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search Upper Bound', true, 0, 260, NOW() - INTERVAL '23 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'hard', 'blank', 'Binary Search 회전 배열', false, 2, 400, NOW() - INTERVAL '22 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search 파라메트릭', true, 1, 350, NOW() - INTERVAL '21 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000007', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'hard', 'blank', 'Binary Search 2D', false, 2, 450, NOW() - INTERVAL '20 days' + INTERVAL '8 hours'),
('a0000005-0000-0000-0000-000000000008', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Binary Search'], 'medium', 'blank', 'Binary Search 삽입 위치', true, 0, 220, NOW() - INTERVAL '19 days' + INTERVAL '8 hours');

-- Stack (중상: 6개 중 5개 정답)
INSERT INTO attempts (id, user_id, topics, difficulty, problem_type, problem_name, is_correct, hints_used, time_spent, created_at) VALUES
('a0000006-0000-0000-0000-000000000001', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'easy', 'blank', 'Stack 기본 연산', true, 0, 100, NOW() - INTERVAL '25 days' + INTERVAL '10 hours'),
('a0000006-0000-0000-0000-000000000002', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'easy', 'blank', 'Stack 괄호 검사', true, 0, 120, NOW() - INTERVAL '24 days' + INTERVAL '10 hours'),
('a0000006-0000-0000-0000-000000000003', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'medium', 'blank', 'Stack 후위 표기', false, 1, 250, NOW() - INTERVAL '23 days' + INTERVAL '10 hours'),
('a0000006-0000-0000-0000-000000000004', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'easy', 'blank', 'Stack 역순 출력', true, 0, 80, NOW() - INTERVAL '22 days' + INTERVAL '10 hours'),
('a0000006-0000-0000-0000-000000000005', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'medium', 'blank', 'Stack 히스토그램', true, 0, 200, NOW() - INTERVAL '21 days' + INTERVAL '10 hours'),
('a0000006-0000-0000-0000-000000000006', '0c3d30cb-c560-4046-bbd2-b910e4575181', ARRAY['Stack', 'Data Structures'], 'medium', 'blank', 'Stack 단조 스택', true, 0, 180, NOW() - INTERVAL '20 days' + INTERVAL '10 hours');

-- =====================================================
-- 3. attempt_details 삽입 (힌트 사용 기록)
-- =====================================================

-- Array 뒤집기 (hints_used: 1, 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000001-0000-0000-0000-000000000006', 'hint', true, true, 1, false);

-- String 팰린드롬 (hints_used: 1, 도움 안됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000002-0000-0000-0000-000000000004', 'hint', true, false, 1, false);

-- DP 피보나치 (hints_used: 2, 1개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000001', 'hint', true, true, 1, false),
('a0000003-0000-0000-0000-000000000001', 'hint', true, false, 2, false);

-- DP 계단 오르기 (hints_used: 3, 1개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000002', 'hint', true, false, 1, false),
('a0000003-0000-0000-0000-000000000002', 'hint', true, true, 2, false),
('a0000003-0000-0000-0000-000000000002', 'hint', true, false, 3, false);

-- DP 동전 교환 (hints_used: 2, 2개 도움됨 - 성공 케이스)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000003', 'hint', true, true, 1, false),
('a0000003-0000-0000-0000-000000000003', 'hint', true, true, 2, true);

-- DP 최대 부분합 (hints_used: 3, 0개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000004', 'hint', true, false, 1, false),
('a0000003-0000-0000-0000-000000000004', 'hint', true, false, 2, false),
('a0000003-0000-0000-0000-000000000004', 'hint', true, false, 3, false);

-- DP LIS (hints_used: 3, 1개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000005', 'hint', true, false, 1, false),
('a0000003-0000-0000-0000-000000000005', 'hint', true, true, 2, false),
('a0000003-0000-0000-0000-000000000005', 'hint', true, false, 3, false);

-- DP 배낭 문제 (hints_used: 3, 0개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000006', 'hint', true, false, 1, false),
('a0000003-0000-0000-0000-000000000006', 'hint', true, false, 2, false),
('a0000003-0000-0000-0000-000000000006', 'hint', true, false, 3, false);

-- DP 타일링 (hints_used: 1, 1개 도움됨 - 성공 케이스)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000003-0000-0000-0000-000000000008', 'hint', true, true, 1, true);

-- Graph BFS 기초 (hints_used: 3, 0개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000004-0000-0000-0000-000000000001', 'hint', true, false, 1, false),
('a0000004-0000-0000-0000-000000000001', 'hint', true, false, 2, false),
('a0000004-0000-0000-0000-000000000001', 'hint', true, false, 3, false);

-- Graph DFS 기초 (hints_used: 3, 1개 도움됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000004-0000-0000-0000-000000000002', 'hint', true, false, 1, false),
('a0000004-0000-0000-0000-000000000002', 'hint', true, true, 2, false),
('a0000004-0000-0000-0000-000000000002', 'hint', true, false, 3, false);

-- Graph 최단 거리 (hints_used: 2, 2개 도움됨 - 성공 케이스)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000004-0000-0000-0000-000000000005', 'hint', true, true, 1, false),
('a0000004-0000-0000-0000-000000000005', 'hint', true, true, 2, true);

-- Graph 최단 경로 (hints_used: 2, 1개 도움됨 - 성공 케이스)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000004-0000-0000-0000-000000000010', 'hint', true, true, 1, false),
('a0000004-0000-0000-0000-000000000010', 'hint', true, false, 2, true);

-- Binary Search 범위 (hints_used: 1, 도움 안됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000005-0000-0000-0000-000000000002', 'hint', true, false, 1, false);

-- Binary Search 파라메트릭 (hints_used: 1, 도움됨 - 성공 케이스)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000005-0000-0000-0000-000000000006', 'hint', true, true, 1, true);

-- Stack 후위 표기 (hints_used: 1, 도움 안됨)
INSERT INTO attempt_details (attempt_id, action_type, hint_was_requested, hint_was_helpful, blank_hint_level, blank_is_correct) VALUES
('a0000006-0000-0000-0000-000000000003', 'hint', true, false, 1, false);

-- =====================================================
-- 4. user_memories 삽입
-- =====================================================
INSERT INTO user_memories (user_id, session_id, summary, key_topics, concepts_learned, concepts_struggling,
                           teaching_notes, breakthrough_moments, student_mood, problem_name,
                           problem_type, problem_difficulty, was_successful, hints_needed,
                           time_spent_seconds, created_at, learning_insights) VALUES

-- DP 실패 세션들
('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_dp_1',
 'DP 배낭 문제 시도. 점화식을 세우는 것에 어려움을 겪었고, 상태 정의를 명확히 하지 못함. 힌트 3개 사용에도 풀이 실패.',
 ARRAY['DP', '배낭 문제'],
 ARRAY[]::TEXT[],
 ARRAY['점화식 도출', '상태 정의', '2차원 DP 테이블'],
 ARRAY['작은 케이스부터 시작하도록 유도 필요', 'dp[i][j]의 의미를 문장으로 먼저 정의하게 해야 함'],
 ARRAY[]::TEXT[],
 'frustrated', 'DP 배낭 문제', 'blank', 'hard', false, 3, 700,
 NOW() - INTERVAL '10 days',
 '{"prefers_examples": true, "prefers_analogies": false, "hint_sensitivity": "high", "pace": "slow", "common_errors": ["점화식 도출", "상태 정의"]}'::jsonb),

('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_dp_2',
 'DP 계단 오르기 문제 시도. 점화식은 이해했으나 초기값 설정에서 실수. 힌트 도움으로 해결.',
 ARRAY['DP', '점화식'],
 ARRAY['1차원 DP 기초'],
 ARRAY['초기값 설정', '경계 조건'],
 ARRAY['n=0, n=1 케이스를 먼저 확인하게 유도'],
 ARRAY['dp[i] = dp[i-1] + dp[i-2] 패턴 이해'],
 'confused', 'DP 계단 오르기', 'blank', 'medium', true, 2, 500,
 NOW() - INTERVAL '9 days',
 '{"prefers_examples": true, "common_errors": ["초기값 설정"]}'::jsonb),

('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_dp_3',
 'DP LCS 문제 완전 실패. 2차원 테이블 개념 자체를 이해하지 못함. 추가 학습 필요.',
 ARRAY['DP', 'LCS', '2차원 DP'],
 ARRAY[]::TEXT[],
 ARRAY['2차원 DP', 'LCS 점화식', '부분 문제 분해'],
 ARRAY['2차원 DP는 1차원 완전 숙달 후 진행해야 함', '시각적 테이블로 설명 필요'],
 ARRAY[]::TEXT[],
 'frustrated', 'DP LCS', 'blank', 'hard', false, 3, 650,
 NOW() - INTERVAL '8 days',
 '{"prefers_examples": true, "hint_sensitivity": "high", "common_errors": ["2차원 DP", "점화식 도출"]}'::jsonb),

-- Graph 실패 세션들
('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_graph_1',
 'BFS 미로 탐색 문제. visited 배열 업데이트 위치를 잘못 설정하여 무한 루프 발생. 큐에 넣을 때 vs pop할 때 차이를 이해하지 못함.',
 ARRAY['Graph', 'BFS', '미로 탐색'],
 ARRAY[]::TEXT[],
 ARRAY['방문 체크 타이밍', 'BFS 큐 사용법', '그래프 표현'],
 ARRAY['BFS는 큐 삽입 시점에 visited 체크해야 함을 강조', '그래프를 시각화하면서 설명 필요'],
 ARRAY[]::TEXT[],
 'frustrated', 'BFS 미로 탐색', 'guided', 'medium', false, 3, 600,
 NOW() - INTERVAL '7 days',
 '{"prefers_examples": true, "common_errors": ["방문 체크 타이밍", "무한 루프"]}'::jsonb),

('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_graph_2',
 'DFS 섬 개수 세기 문제. 재귀 호출에서 종료 조건을 잘못 설정하여 스택 오버플로우 발생.',
 ARRAY['Graph', 'DFS', '재귀'],
 ARRAY[]::TEXT[],
 ARRAY['재귀 종료 조건', '방문 체크', 'DFS 구현'],
 ARRAY['base case를 먼저 작성하도록 유도', '재귀 호출 전 visited 체크 강조'],
 ARRAY[]::TEXT[],
 'frustrated', 'DFS 섬 개수', 'blank', 'medium', false, 3, 550,
 NOW() - INTERVAL '6 days',
 '{"common_errors": ["재귀 종료 조건", "방문 체크"]}'::jsonb),

('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_graph_3',
 'Graph 다익스트라 알고리즘 시도. 우선순위 큐 개념은 알지만 구현에서 막힘. 음수 가중치 처리도 혼동.',
 ARRAY['Graph', 'Dijkstra', '최단 경로'],
 ARRAY[]::TEXT[],
 ARRAY['우선순위 큐 구현', '다익스트라 로직', '음수 가중치'],
 ARRAY['heapq 사용법 복습 필요', '다익스트라 vs 벨만포드 차이 설명'],
 ARRAY[]::TEXT[],
 'confused', 'Graph 다익스트라', 'guided', 'hard', false, 3, 800,
 NOW() - INTERVAL '5 days',
 '{"hint_sensitivity": "high", "common_errors": ["우선순위 큐", "다익스트라 구현"]}'::jsonb),

-- Array 성공 세션
('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_array_1',
 '배열 투 포인터 문제 완벽 해결. 양끝에서 시작하는 투 포인터 기법을 잘 적용함.',
 ARRAY['Array', 'Two Pointers'],
 ARRAY['투 포인터 기법', 'in-place 연산'],
 ARRAY[]::TEXT[],
 ARRAY[]::TEXT[],
 ARRAY['투 포인터로 O(n) 해결 가능함을 깨달음'],
 'confident', 'Array 투 포인터', 'blank', 'medium', true, 0, 180,
 NOW() - INTERVAL '4 days',
 '{"pace": "fast"}'::jsonb),

-- String 성공 세션
('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_string_1',
 '문자열 아나그램 문제 성공. Counter 활용하여 효율적으로 해결.',
 ARRAY['String', 'Hash'],
 ARRAY['문자열 카운팅', '해시맵 활용'],
 ARRAY[]::TEXT[],
 ARRAY[]::TEXT[],
 ARRAY['Counter로 O(n) 해결'],
 'confident', 'String 아나그램', 'blank', 'medium', true, 0, 180,
 NOW() - INTERVAL '3 days',
 '{"pace": "fast"}'::jsonb),

-- Binary Search 부분 성공
('0c3d30cb-c560-4046-bbd2-b910e4575181', 'session_bs_1',
 '이분 탐색 파라메트릭 문제. 결정 함수 설계에서 약간 헤맸으나 힌트 후 해결.',
 ARRAY['Binary Search', 'Parametric Search'],
 ARRAY['파라메트릭 서치 개념'],
 ARRAY['결정 함수 설계', 'left와 right 갱신'],
 ARRAY['결정 함수를 먼저 정의하고 이분 탐색 적용하도록 유도'],
 ARRAY[]::TEXT[],
 'curious', 'Binary Search 파라메트릭', 'blank', 'medium', true, 1, 350,
 NOW() - INTERVAL '2 days',
 '{"common_errors": ["경계값 처리"]}'::jsonb);

-- =====================================================
-- 5. hint_logs 삽입
-- =====================================================

-- DP 힌트 (많이 사용)
INSERT INTO hint_logs (user_id, hint_level, xp_cost, created_at) VALUES
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '28 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '28 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '28 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '27 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '27 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '27 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '26 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '26 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '25 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '25 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '25 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '24 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '24 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '24 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '23 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '23 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '23 days' + INTERVAL '10 minutes');

-- Graph 힌트 (많이 사용)
INSERT INTO hint_logs (user_id, hint_level, xp_cost, created_at) VALUES
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '22 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '22 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '22 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '21 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '21 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '21 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '20 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '20 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '20 days' + INTERVAL '10 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '19 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '19 days' + INTERVAL '5 minutes'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 3, 15, NOW() - INTERVAL '19 days' + INTERVAL '10 minutes');

-- Binary Search 힌트 (약간)
INSERT INTO hint_logs (user_id, hint_level, xp_cost, created_at) VALUES
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '15 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 2, 10, NOW() - INTERVAL '14 days'),
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '13 days');

-- Array/String 힌트 (거의 없음)
INSERT INTO hint_logs (user_id, hint_level, xp_cost, created_at) VALUES
('0c3d30cb-c560-4046-bbd2-b910e4575181', 1, 5, NOW() - INTERVAL '12 days');

-- =====================================================
-- 결과 확인
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE 'Test data inserted successfully!';
    RAISE NOTICE 'User: 0c3d30cb-c560-4046-bbd2-b910e4575181';
    RAISE NOTICE 'Expected: DP/Graph weak, Array/String strong';
    RAISE NOTICE 'Hint stats: 33 total, ~13 helpful';
END $$;
