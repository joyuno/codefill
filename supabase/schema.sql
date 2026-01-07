-- =====================================================
-- CodeFill Database Schema (TRD v2)
-- Run this in Supabase SQL Editor
-- =====================================================

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- 1. USER 관련 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    avatar_url TEXT,
    provider VARCHAR(20) DEFAULT 'email',
    provider_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    problems_solved INTEGER DEFAULT 0,
    problems_attempted INTEGER DEFAULT 0,
    blank_solved INTEGER DEFAULT 0,
    bug_solved INTEGER DEFAULT 0,
    output_solved INTEGER DEFAULT 0,
    refactor_solved INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    seeds INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_language VARCHAR(20) DEFAULT 'javascript',
    preferred_difficulty VARCHAR(10) DEFAULT 'medium',
    daily_goal INTEGER DEFAULT 5,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    review_reminders BOOLEAN DEFAULT TRUE,
    theme VARCHAR(10) DEFAULT 'dark',
    editor_font_size INTEGER DEFAULT 14,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. PROBLEM 관련 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    title VARCHAR(255) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    difficulty VARCHAR(10) DEFAULT 'medium',
    source VARCHAR(50),
    source_url TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS codes_embedding_idx ON codes
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_id UUID REFERENCES codes(id) ON DELETE CASCADE,
    problem_type VARCHAR(20) NOT NULL, -- 'blank', 'bug', 'output', 'refactor'
    problem_code TEXT NOT NULL,
    answer_data JSONB NOT NULL,
    test_cases JSONB,
    hints JSONB,
    difficulty VARCHAR(10) DEFAULT 'medium',
    times_attempted INTEGER DEFAULT 0,
    times_solved INTEGER DEFAULT 0,
    avg_solve_time INTEGER,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS problems_embedding_idx ON problems
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS problems_type_idx ON problems(problem_type);
CREATE INDEX IF NOT EXISTS problems_difficulty_idx ON problems(difficulty);

-- =====================================================
-- 3. PRACTICE 관련 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    score INTEGER,
    submitted_code TEXT,
    submitted_answer VARCHAR(10),
    started_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent INTEGER,
    hints_used INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS attempts_user_idx ON attempts(user_id);
CREATE INDEX IF NOT EXISTS attempts_problem_idx ON attempts(problem_id);
CREATE INDEX IF NOT EXISTS attempts_date_idx ON attempts(created_at);

CREATE TABLE IF NOT EXISTS attempt_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,
    error_type VARCHAR(50),
    error_location INTEGER,
    error_description TEXT,
    test_results JSONB,
    review_feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hint_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES attempts(id) ON DELETE SET NULL,
    hint_level INTEGER NOT NULL,
    hint_content TEXT,
    xp_cost INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS hint_logs_user_idx ON hint_logs(user_id);

-- =====================================================
-- 4. GAMIFICATION 관련 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS daily_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    problems_solved INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0,
    blank_count INTEGER DEFAULT 0,
    bug_count INTEGER DEFAULT 0,
    output_count INTEGER DEFAULT 0,
    refactor_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, activity_date)
);

CREATE INDEX IF NOT EXISTS daily_activity_user_date_idx ON daily_activity(user_id, activity_date);

CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT,
    condition_type VARCHAR(50) NOT NULL,
    condition_value INTEGER,
    condition_data JSONB,
    rarity VARCHAR(20) DEFAULT 'common',
    xp_reward INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- =====================================================
-- 5. SUBSCRIPTION 관련 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    price_monthly INTEGER DEFAULT 0,
    price_yearly INTEGER DEFAULT 0,
    daily_problem_limit INTEGER,
    ai_tutor_access BOOLEAN DEFAULT FALSE,
    learning_path_access BOOLEAN DEFAULT FALSE,
    interview_prep_access BOOLEAN DEFAULT FALSE,
    features JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    billing_cycle VARCHAR(20),
    next_billing_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 6. 초기 데이터
-- =====================================================

INSERT INTO plans (code, name, price_monthly, price_yearly, daily_problem_limit, ai_tutor_access, learning_path_access) VALUES
('free', 'Free', 0, 0, 5, FALSE, FALSE),
('pro', 'Pro', 9900, 99000, NULL, TRUE, TRUE),
('max', 'Max', 19900, 199000, NULL, TRUE, TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('first_problem', 'First Step', '첫 문제 풀이', 'problems', 1, 'common', 50),
('streak_7', 'Week Warrior', '7일 연속 출석', 'streak', 7, 'common', 100),
('streak_30', 'Monthly Master', '30일 연속 출석', 'streak', 30, 'rare', 300),
('streak_100', 'Legendary Learner', '100일 연속 출석', 'streak', 100, 'legendary', 1000),
('problems_50', 'Half Century', '50문제 해결', 'problems', 50, 'common', 200),
('problems_100', 'Centurion', '100문제 해결', 'problems', 100, 'rare', 500),
('level_10', 'Rising Star', '레벨 10 달성', 'level', 10, 'common', 150),
('level_50', 'Expert', '레벨 50 달성', 'level', 50, 'epic', 1000)
ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- 7. Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE hint_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- User stats policies
CREATE POLICY "Users can view own stats" ON user_stats
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own stats" ON user_stats
    FOR UPDATE USING (auth.uid() = user_id);

-- User preferences policies
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Attempts policies
CREATE POLICY "Users can view own attempts" ON attempts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own attempts" ON attempts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Hint logs policies
CREATE POLICY "Users can view own hint logs" ON hint_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own hint logs" ON hint_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Daily activity policies
CREATE POLICY "Users can view own daily activity" ON daily_activity
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can upsert own daily activity" ON daily_activity
    FOR ALL USING (auth.uid() = user_id);

-- User badges policies
CREATE POLICY "Users can view own badges" ON user_badges
    FOR SELECT USING (auth.uid() = user_id);

-- Subscriptions policies
CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Public read access for reference tables
CREATE POLICY "Anyone can view codes" ON codes
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Anyone can view problems" ON problems
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Anyone can view badges" ON badges
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Anyone can view plans" ON plans
    FOR SELECT USING (true);

-- =====================================================
-- 8. Functions and Triggers
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_stats_updated_at BEFORE UPDATE ON user_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_codes_updated_at BEFORE UPDATE ON codes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problems_updated_at BEFORE UPDATE ON problems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_activity_updated_at BEFORE UPDATE ON daily_activity
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Create user_stats for new user
    INSERT INTO user_stats (user_id) VALUES (NEW.id);

    -- Create user_preferences for new user
    INSERT INTO user_preferences (user_id) VALUES (NEW.id);

    -- Assign free plan to new user
    INSERT INTO subscriptions (user_id, plan_id)
    SELECT NEW.id, id FROM plans WHERE code = 'free';

    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Trigger for new user
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Function to increment user stats after solving a problem
-- Level scaling: 2x (100, 200, 400, 800...)
CREATE OR REPLACE FUNCTION increment_user_stats(
    p_user_id UUID,
    p_xp INTEGER,
    p_problem_type VARCHAR(20)
)
RETURNS VOID AS $$
DECLARE
    v_new_xp INTEGER;
    v_new_level INTEGER;
    v_xp_for_level INTEGER;
    v_remaining_xp INTEGER;
    v_current_date DATE := CURRENT_DATE;
BEGIN
    -- Update user_stats
    UPDATE user_stats
    SET
        total_xp = total_xp + p_xp,
        problems_solved = problems_solved + 1,
        blank_solved = CASE WHEN p_problem_type = 'blank' THEN blank_solved + 1 ELSE blank_solved END,
        bug_solved = CASE WHEN p_problem_type = 'bug' THEN bug_solved + 1 ELSE bug_solved END,
        output_solved = CASE WHEN p_problem_type = 'output' THEN output_solved + 1 ELSE output_solved END,
        refactor_solved = CASE WHEN p_problem_type = 'refactor' THEN refactor_solved + 1 ELSE refactor_solved END,
        -- Update streak
        current_streak = CASE
            WHEN last_activity_date = v_current_date - 1 THEN current_streak + 1
            WHEN last_activity_date = v_current_date THEN current_streak
            ELSE 1
        END,
        longest_streak = GREATEST(
            longest_streak,
            CASE
                WHEN last_activity_date = v_current_date - 1 THEN current_streak + 1
                WHEN last_activity_date = v_current_date THEN current_streak
                ELSE 1
            END
        ),
        last_activity_date = v_current_date
    WHERE user_id = p_user_id
    RETURNING total_xp INTO v_new_xp;

    -- Calculate new level (2x scaling: 100, 200, 400, 800...)
    v_new_level := 1;
    v_remaining_xp := v_new_xp;
    v_xp_for_level := 100;  -- First level needs 100 XP

    WHILE v_remaining_xp >= v_xp_for_level LOOP
        v_remaining_xp := v_remaining_xp - v_xp_for_level;
        v_new_level := v_new_level + 1;
        v_xp_for_level := v_xp_for_level * 2;  -- 2x for next level
    END LOOP;

    -- Update level
    UPDATE user_stats
    SET level = v_new_level
    WHERE user_id = p_user_id;

    -- Update or insert daily activity
    INSERT INTO daily_activity (user_id, activity_date, problems_solved, xp_earned, blank_count, bug_count, output_count, refactor_count)
    VALUES (
        p_user_id,
        v_current_date,
        1,
        p_xp,
        CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'bug' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'output' THEN 1 ELSE 0 END,
        CASE WHEN p_problem_type = 'refactor' THEN 1 ELSE 0 END
    )
    ON CONFLICT (user_id, activity_date)
    DO UPDATE SET
        problems_solved = daily_activity.problems_solved + 1,
        xp_earned = daily_activity.xp_earned + p_xp,
        blank_count = daily_activity.blank_count + CASE WHEN p_problem_type = 'blank' THEN 1 ELSE 0 END,
        bug_count = daily_activity.bug_count + CASE WHEN p_problem_type = 'bug' THEN 1 ELSE 0 END,
        output_count = daily_activity.output_count + CASE WHEN p_problem_type = 'output' THEN 1 ELSE 0 END,
        refactor_count = daily_activity.refactor_count + CASE WHEN p_problem_type = 'refactor' THEN 1 ELSE 0 END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Function to deduct XP for hint usage
-- Returns TRUE if successful, FALSE if not enough XP
CREATE OR REPLACE FUNCTION deduct_hint_xp(
    p_user_id UUID,
    p_xp_cost INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
BEGIN
    SELECT total_xp, level INTO v_current_xp, v_current_level
    FROM user_stats
    WHERE user_id = p_user_id;

    -- Check if user has enough XP (can't go below 0 at level 1)
    IF v_current_level = 1 AND v_current_xp < p_xp_cost THEN
        RETURN FALSE;
    END IF;

    -- Deduct XP (minimum 0)
    UPDATE user_stats
    SET total_xp = GREATEST(0, total_xp - p_xp_cost)
    WHERE user_id = p_user_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Function to check if user can use hint
CREATE OR REPLACE FUNCTION can_use_hint(
    p_user_id UUID,
    p_xp_cost INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
BEGIN
    SELECT total_xp, level INTO v_current_xp, v_current_level
    FROM user_stats
    WHERE user_id = p_user_id;

    -- Level 1 with less than hint cost XP = can't use hint
    IF v_current_level = 1 AND v_current_xp < p_xp_cost THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 9. Sample Data for Development
-- =====================================================

-- Sample codes
INSERT INTO codes (id, framework, category, tags, title, description, code, difficulty) VALUES
-- React useState example
('11111111-1111-1111-1111-111111111111', 'react', 'Hooks', ARRAY['useState', 'hooks', 'state'], 'useState로 카운터 만들기', 'React useState 훅을 사용하여 간단한 카운터를 구현합니다.', E'import { useState } from ''react'';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n\n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>\n        Increment\n      </button>\n    </div>\n  );\n}', 'easy'),

-- React useEffect example
('22222222-2222-2222-2222-222222222222', 'react', 'Hooks', ARRAY['useEffect', 'hooks', 'sideEffects'], 'useEffect로 데이터 가져오기', 'React useEffect 훅을 사용하여 API에서 데이터를 가져옵니다.', E'import { useState, useEffect } from ''react'';\n\nfunction UserList() {\n  const [users, setUsers] = useState([]);\n  const [loading, setLoading] = useState(true);\n\n  useEffect(() => {\n    fetch(''/api/users'')\n      .then(res => res.json())\n      .then(data => {\n        setUsers(data);\n        setLoading(false);\n      });\n  }, []);\n\n  if (loading) return <p>Loading...</p>;\n\n  return (\n    <ul>\n      {users.map(user => (\n        <li key={user.id}>{user.name}</li>\n      ))}\n    </ul>\n  );\n}', 'medium'),

-- JavaScript array methods
('33333333-3333-3333-3333-333333333333', 'javascript', 'Arrays', ARRAY['array', 'map', 'filter', 'reduce'], 'JavaScript 배열 메서드', '자주 사용되는 JavaScript 배열 메서드들을 학습합니다.', E'const numbers = [1, 2, 3, 4, 5];\n\n// map: 각 요소를 변환\nconst doubled = numbers.map(n => n * 2);\n// [2, 4, 6, 8, 10]\n\n// filter: 조건에 맞는 요소만 선택\nconst evens = numbers.filter(n => n % 2 === 0);\n// [2, 4]\n\n// reduce: 하나의 값으로 축소\nconst sum = numbers.reduce((acc, n) => acc + n, 0);\n// 15', 'easy'),

-- Python list comprehension
('44444444-4444-4444-4444-444444444444', 'python', 'Basics', ARRAY['list', 'comprehension', 'python'], 'Python 리스트 컴프리헨션', 'Python의 리스트 컴프리헨션을 사용하여 효율적으로 리스트를 생성합니다.', E'# 기본 리스트 컴프리헨션\nnumbers = [1, 2, 3, 4, 5]\nsquares = [x ** 2 for x in numbers]\n# [1, 4, 9, 16, 25]\n\n# 조건부 리스트 컴프리헨션\nevens = [x for x in numbers if x % 2 == 0]\n# [2, 4]\n\n# 중첩 리스트 컴프리헨션\nmatrix = [[1, 2], [3, 4]]\nflattened = [x for row in matrix for x in row]\n# [1, 2, 3, 4]', 'easy')
ON CONFLICT (id) DO NOTHING;

-- Sample problems (Blank type)
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, hints, difficulty) VALUES
('aaaa1111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'blank',
E'import { ___ } from ''react'';\n\nfunction Counter() {\n  const [count, ___] = useState(0);\n\n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => ___(count + 1)}>\n        Increment\n      </button>\n    </div>\n  );\n}',
'{"blanks": [{"id": "b1", "position": 9, "answer": "useState", "hints": ["React의 상태 관리 훅입니다", "use로 시작합니다"]}, {"id": "b2", "position": 65, "answer": "setCount", "hints": ["상태를 변경하는 함수입니다", "set으로 시작합니다"]}, {"id": "b3", "position": 168, "answer": "setCount", "hints": ["클릭 시 count를 업데이트합니다"]}]}'::jsonb,
'{"level_1": "React에서 상태를 관리하는 훅을 사용합니다", "level_2": "useState는 [상태값, 상태변경함수]를 반환합니다", "level_3": "setCount 함수로 count를 업데이트합니다"}'::jsonb,
'easy'),

('aaaa2222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'blank',
E'import { useState, ___ } from ''react'';\n\nfunction UserList() {\n  const [users, setUsers] = useState([]);\n  const [loading, setLoading] = useState(true);\n\n  ___(() => {\n    fetch(''/api/users'')\n      .then(res => res.___())\n      .then(data => {\n        setUsers(data);\n        setLoading(false);\n      });\n  }, []);\n\n  if (loading) return <p>Loading...</p>;\n\n  return (\n    <ul>\n      {users.map(user => (\n        <li key={user.id}>{user.name}</li>\n      ))}\n    </ul>\n  );\n}',
'{"blanks": [{"id": "b1", "position": 19, "answer": "useEffect", "hints": ["사이드 이펙트를 처리하는 훅입니다"]}, {"id": "b2", "position": 120, "answer": "useEffect", "hints": ["컴포넌트 마운트 시 실행됩니다"]}, {"id": "b3", "position": 175, "answer": "json", "hints": ["fetch 응답을 JSON으로 파싱합니다"]}]}'::jsonb,
'{"level_1": "컴포넌트가 마운트될 때 데이터를 가져옵니다", "level_2": "useEffect 훅을 사용하고 빈 의존성 배열을 전달합니다", "level_3": "fetch().then(res => res.json())"}'::jsonb,
'medium')
ON CONFLICT (id) DO NOTHING;

-- Sample problems (Output type)
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, hints, difficulty) VALUES
('bbbb1111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'output',
E'const arr = [1, 2, 3];\nconst result = arr.map(x => x * 2).filter(x => x > 2);\nconsole.log(result.length);',
'{"options": [{"id": "a", "value": "1"}, {"id": "b", "value": "2"}, {"id": "c", "value": "3"}, {"id": "d", "value": "6"}], "correct_answer": "b", "explanation": "map은 [2, 4, 6]을 반환하고, filter는 2보다 큰 [4, 6]을 반환합니다. 따라서 length는 2입니다."}'::jsonb,
'{"level_1": "map과 filter가 순서대로 적용됩니다", "level_2": "map 결과: [2, 4, 6], filter 조건: x > 2", "level_3": "4와 6만 조건을 만족합니다"}'::jsonb,
'easy'),

('bbbb2222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 'output',
E'let a = [1, 2, 3];\nlet b = a;\nb.push(4);\nconsole.log(a.length);',
'{"options": [{"id": "a", "value": "3"}, {"id": "b", "value": "4"}, {"id": "c", "value": "undefined"}, {"id": "d", "value": "Error"}], "correct_answer": "b", "explanation": "JavaScript에서 배열은 참조 타입입니다. b = a는 같은 배열을 참조하므로, b에 push하면 a도 영향을 받습니다."}'::jsonb,
'{"level_1": "JavaScript의 참조 타입에 대해 생각해보세요", "level_2": "b = a는 배열을 복사하는 것이 아니라 같은 배열을 참조합니다", "level_3": "a와 b는 같은 배열입니다"}'::jsonb,
'medium')
ON CONFLICT (id) DO NOTHING;

-- Sample problems (Bug Fix type)
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, test_cases, hints, difficulty) VALUES
('cccc1111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'bug',
E'function sum(arr) {\n  let total = 0;\n  for (let i = 0; i <= arr.length; i++) {\n    total += arr[i];\n  }\n  return total;\n}',
'{"correct_code": "function sum(arr) {\n  let total = 0;\n  for (let i = 0; i < arr.length; i++) {\n    total += arr[i];\n  }\n  return total;\n}", "bug_info": {"type": "off-by-one", "line": 3, "description": "배열 인덱스 범위 오류"}}'::jsonb,
'[{"input": "[1, 2, 3]", "expected_output": "6"}, {"input": "[10, 20]", "expected_output": "30"}, {"input": "[]", "expected_output": "0"}]'::jsonb,
'{"level_1": "반복문의 종료 조건을 확인해보세요", "level_2": "배열의 마지막 유효한 인덱스는 length - 1입니다", "level_3": "i <= arr.length를 i < arr.length로 변경하세요"}'::jsonb,
'medium')
ON CONFLICT (id) DO NOTHING;

-- Sample problems (Refactor type)
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, test_cases, hints, difficulty) VALUES
('dddd1111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'refactor',
E'function p(d) {\n  let t = 0;\n  for (let i = 0; i < d.length; i++) {\n    if (d[i].a === true) {\n      t = t + d[i].p;\n    }\n  }\n  return t;\n}',
'{"model_answer": "function calculateActiveTotal(items) {\n  return items\n    .filter(item => item.isActive)\n    .reduce((total, item) => total + item.price, 0);\n}", "evaluation_criteria": ["meaningful variable names", "use array methods", "remove unnecessary conditions"]}'::jsonb,
'[{"input": "[{\"a\": true, \"p\": 10}, {\"a\": false, \"p\": 20}, {\"a\": true, \"p\": 30}]", "expected_output": "40"}]'::jsonb,
'{"level_1": "변수명을 의미있게 변경해보세요", "level_2": "filter와 reduce를 사용하면 더 간결해집니다", "level_3": "items.filter(item => item.isActive).reduce(...)"}'::jsonb,
'hard')
ON CONFLICT (id) DO NOTHING;
