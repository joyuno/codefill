-- =====================================================
-- CodeFill 테스트 데이터 시드 스크립트
-- 약점 분석 페이지 테스트용
-- =====================================================

DO $$
DECLARE
    target_user_id UUID := 'ccb94830-e83e-44b2-be14-67d02475eaf8';

    topics TEXT[] := ARRAY[
        'DP', 'Graph', 'Greedy', 'BinarySearch', 'Implementation',
        'Math', 'String', 'DataStructure', 'Tree', 'BFS/DFS'
    ];
    difficulties TEXT[] := ARRAY['easy', 'medium', 'hard'];
    problem_types TEXT[] := ARRAY['blank', 'puzzle', 'guided'];

    i INTEGER;
    rand_topic TEXT;
    rand_difficulty TEXT;
    rand_type TEXT;
    rand_correct BOOLEAN;
    rand_hints INTEGER;
    rand_time INTEGER;
    rand_xp INTEGER;
    attempt_id UUID;
    base_problem_id UUID;

BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = target_user_id) THEN
        RAISE EXCEPTION 'User not found: %', target_user_id;
    END IF;

    RAISE NOTICE '시드 데이터 생성 시작: user_id = %', target_user_id;

    -- 50개의 시도 기록 생성
    FOR i IN 1..50 LOOP
        rand_topic := topics[1 + floor(random() * array_length(topics, 1))::int];
        rand_difficulty := difficulties[1 + floor(random() * 3)::int];
        rand_type := problem_types[1 + floor(random() * 3)::int];

        -- 주제별 정답률 (약점/강점 시뮬레이션)
        IF rand_topic IN ('DP', 'Graph', 'Tree') THEN
            rand_correct := random() < 0.30;
        ELSIF rand_topic IN ('Greedy', 'Implementation', 'String') THEN
            rand_correct := random() < 0.85;
        ELSE
            rand_correct := random() < 0.60;
        END IF;

        rand_hints := floor(random() * 4)::int;
        rand_time := 60 + floor(random() * 600)::int;
        rand_xp := CASE WHEN rand_correct THEN 10 + floor(random() * 50)::int ELSE 0 END;

        SELECT id INTO base_problem_id
        FROM base_problems
        ORDER BY random()
        LIMIT 1;

        INSERT INTO attempts (
            id, user_id, base_problem_id, is_correct, problem_type,
            difficulty, topics, problem_name, hints_used, time_spent,
            xp_earned, created_at, submitted_at
        ) VALUES (
            gen_random_uuid(), target_user_id, base_problem_id, rand_correct,
            rand_type, rand_difficulty, ARRAY[rand_topic], '테스트 문제 ' || i,
            rand_hints, rand_time, rand_xp,
            NOW() - (interval '1 day' * floor(random() * 30)::int),
            NOW() - (interval '1 day' * floor(random() * 30)::int)
        )
        RETURNING id INTO attempt_id;

        IF rand_type = 'blank' THEN
            INSERT INTO attempt_details (
                attempt_id, action_type, blank_index, blank_is_correct,
                blank_hint_level, hint_was_requested
            ) VALUES (
                attempt_id, 'blank_submit', 0, rand_correct, rand_hints, rand_hints > 0
            );
        END IF;
    END LOOP;

    RAISE NOTICE '50개의 attempts 생성 완료';

    -- user_skill_profiles 업데이트
    INSERT INTO user_skill_profiles (
        user_id, skill_by_topic, weak_topics, strong_topics,
        success_rate_by_difficulty, stats_by_problem_type,
        total_problems_solved, total_problems_attempted
    ) VALUES (
        target_user_id,
        jsonb_build_object(
            'DP', 0.28, 'Graph', 0.32, 'Tree', 0.35,
            'Greedy', 0.82, 'Implementation', 0.88, 'String', 0.79,
            'BinarySearch', 0.55, 'Math', 0.62, 'DataStructure', 0.58, 'BFS/DFS', 0.45
        ),
        ARRAY['DP', 'Graph', 'Tree', 'BFS/DFS'],
        ARRAY['Implementation', 'Greedy', 'String'],
        jsonb_build_object(
            'easy', jsonb_build_object('success', 18, 'total', 20),
            'medium', jsonb_build_object('success', 12, 'total', 20),
            'hard', jsonb_build_object('success', 4, 'total', 10)
        ),
        jsonb_build_object(
            'blank', jsonb_build_object('success', 15, 'total', 20, 'total_time', 3600),
            'puzzle', jsonb_build_object('success', 12, 'total', 18, 'total_time', 2800),
            'guided', jsonb_build_object('success', 7, 'total', 12, 'total_time', 4200)
        ),
        34, 50
    )
    ON CONFLICT (user_id) DO UPDATE SET
        skill_by_topic = EXCLUDED.skill_by_topic,
        weak_topics = EXCLUDED.weak_topics,
        strong_topics = EXCLUDED.strong_topics,
        success_rate_by_difficulty = EXCLUDED.success_rate_by_difficulty,
        stats_by_problem_type = EXCLUDED.stats_by_problem_type,
        total_problems_solved = EXCLUDED.total_problems_solved,
        total_problems_attempted = EXCLUDED.total_problems_attempted,
        updated_at = NOW();

    RAISE NOTICE 'user_skill_profiles 업데이트 완료';

    -- user_stats 업데이트
    UPDATE user_stats SET
        problems_solved = 34, problems_attempted = 50, total_xp = 1250,
        level = 8, current_streak = 5, longest_streak = 12,
        last_activity_date = CURRENT_DATE, updated_at = NOW()
    WHERE user_id = target_user_id;

    IF NOT FOUND THEN
        INSERT INTO user_stats (
            user_id, problems_solved, problems_attempted, total_xp,
            level, current_streak, longest_streak, last_activity_date
        ) VALUES (target_user_id, 34, 50, 1250, 8, 5, 12, CURRENT_DATE);
    END IF;

    RAISE NOTICE 'user_stats 업데이트 완료';

    -- user_memories 추가
    INSERT INTO user_memories (
        user_id, session_id, session_type, summary, key_topics,
        concepts_learned, concepts_struggling, teaching_notes,
        problem_name, was_successful, hints_needed, student_mood, created_at
    ) VALUES
    (
        target_user_id, 'session_' || gen_random_uuid()::text, 'problem_solving',
        'DP 문제에서 점화식 도출에 어려움을 겪었으나, 작은 예시부터 시작하는 방법으로 해결함',
        ARRAY['DP', '점화식'], ARRAY['메모이제이션 개념'],
        ARRAY['점화식 도출', '상태 정의'],
        ARRAY['작은 예시로 시작하면 이해가 빠름'],
        'DP 기초 문제', FALSE, 3, 'frustrated', NOW() - interval '2 days'
    ),
    (
        target_user_id, 'session_' || gen_random_uuid()::text, 'problem_solving',
        '그래프 탐색에서 BFS와 DFS 선택 기준을 학습함',
        ARRAY['Graph', 'BFS', 'DFS'], ARRAY['BFS는 최단거리', 'DFS는 경로탐색'],
        ARRAY['그래프 구현', '방문 배열 관리'],
        ARRAY['시각적으로 그래프를 그려보면 도움됨'],
        '그래프 탐색', TRUE, 2, 'curious', NOW() - interval '5 days'
    ),
    (
        target_user_id, 'session_' || gen_random_uuid()::text, 'problem_solving',
        'Greedy 알고리즘으로 최적해를 빠르게 도출함',
        ARRAY['Greedy', '정렬'], ARRAY['탐욕적 선택 속성', '최적 부분 구조'],
        ARRAY[]::TEXT[], ARRAY['자신감 있게 풀이함'],
        'Greedy 문제', TRUE, 0, 'confident', NOW() - interval '1 day'
    );

    RAISE NOTICE 'user_memories 추가 완료';

    -- daily_activity 추가
    INSERT INTO daily_activity (user_id, activity_date, problems_solved, xp_earned, time_spent)
    VALUES
        (target_user_id, CURRENT_DATE, 3, 85, 1800),
        (target_user_id, CURRENT_DATE - 1, 4, 120, 2400),
        (target_user_id, CURRENT_DATE - 2, 2, 45, 1200),
        (target_user_id, CURRENT_DATE - 3, 5, 150, 3000),
        (target_user_id, CURRENT_DATE - 4, 3, 90, 1500)
    ON CONFLICT (user_id, activity_date) DO UPDATE SET
        problems_solved = EXCLUDED.problems_solved,
        xp_earned = EXCLUDED.xp_earned,
        time_spent = EXCLUDED.time_spent;

    RAISE NOTICE '========================================';
    RAISE NOTICE '모든 테스트 데이터 생성 완료!';
    RAISE NOTICE '/analysis 페이지에서 분석 시작 버튼 클릭';
    RAISE NOTICE '========================================';

END $$;
