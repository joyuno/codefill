-- =====================================================
-- CodeFill Database Migration: Problem Generation Tables
-- 문제 생성 테이블 추가 (빈칸, 퍼즐, 대화형)
-- =====================================================

-- =====================================================
-- 1. 기본 문제 테이블 (원본 문제 저장)
-- =====================================================
CREATE TABLE IF NOT EXISTS base_problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    input_output JSONB,
    difficulty VARCHAR(20) DEFAULT 'medium',
    tags TEXT[],
    source VARCHAR(50),
    url TEXT,
    time_limit VARCHAR(50),
    memory_limit VARCHAR(50),
    solutions JSONB NOT NULL,  -- [{language, code}]
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS base_problems_original_id_idx ON base_problems(original_id);
CREATE INDEX IF NOT EXISTS base_problems_difficulty_idx ON base_problems(difficulty);
CREATE INDEX IF NOT EXISTS base_problems_source_idx ON base_problems(source);

-- =====================================================
-- 2. 빈칸 채우기 테이블
-- =====================================================
CREATE TABLE IF NOT EXISTS problems_blank (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id VARCHAR(50) NOT NULL,
    language VARCHAR(20) NOT NULL,
    code_template TEXT NOT NULL,  -- "_0_", "_1_" 형식
    answers TEXT[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(original_id, language)
);

CREATE INDEX IF NOT EXISTS problems_blank_original_id_idx ON problems_blank(original_id);

-- =====================================================
-- 3. 퍼즐 테이블
-- =====================================================
CREATE TABLE IF NOT EXISTS problems_puzzle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id VARCHAR(50) NOT NULL,
    language VARCHAR(20) NOT NULL,
    fixed_start TEXT,          -- 보일러플레이트 (고정 표시)
    fixed_end TEXT,            -- 닫는 부분 (고정 표시)
    blocks JSONB NOT NULL,     -- [{id, code}] id 순서 = 정답
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(original_id, language)
);

CREATE INDEX IF NOT EXISTS problems_puzzle_original_id_idx ON problems_puzzle(original_id);

-- =====================================================
-- 4. 1대1 대화형 테이블
-- =====================================================
CREATE TABLE IF NOT EXISTS problems_guided (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id VARCHAR(50) NOT NULL,
    language VARCHAR(20) NOT NULL,
    concepts TEXT[] NOT NULL,
    flow TEXT[] NOT NULL,
    checkpoints TEXT[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(original_id, language)
);

CREATE INDEX IF NOT EXISTS problems_guided_original_id_idx ON problems_guided(original_id);

-- =====================================================
-- 5. 트리거: updated_at 자동 갱신
-- =====================================================
CREATE TRIGGER update_base_problems_updated_at
    BEFORE UPDATE ON base_problems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problems_blank_updated_at
    BEFORE UPDATE ON problems_blank
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problems_puzzle_updated_at
    BEFORE UPDATE ON problems_puzzle
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problems_guided_updated_at
    BEFORE UPDATE ON problems_guided
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 6. RLS (Row Level Security)
-- =====================================================
ALTER TABLE base_problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE problems_blank ENABLE ROW LEVEL SECURITY;
ALTER TABLE problems_puzzle ENABLE ROW LEVEL SECURITY;
ALTER TABLE problems_guided ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
CREATE POLICY "Anyone can view base_problems" ON base_problems
    FOR SELECT USING (true);
CREATE POLICY "Anyone can view problems_blank" ON problems_blank
    FOR SELECT USING (true);
CREATE POLICY "Anyone can view problems_puzzle" ON problems_puzzle
    FOR SELECT USING (true);
CREATE POLICY "Anyone can view problems_guided" ON problems_guided
    FOR SELECT USING (true);

-- service_role만 쓰기 허용
CREATE POLICY "Service role can manage base_problems" ON base_problems
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage problems_blank" ON problems_blank
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage problems_puzzle" ON problems_puzzle
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage problems_guided" ON problems_guided
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 7. 샘플 데이터 삽입
-- =====================================================

-- 기본 문제
INSERT INTO base_problems (original_id, name, question, input_output, difficulty, tags, source, url, time_limit, memory_limit, solutions) VALUES
('1001', '[백준 1001] A-B', '두 정수 A와 B를 입력받은 다음, A-B를 출력하는 프로그램을 작성하시오.',
 '{"inputs": ["3 2"], "outputs": ["1"]}'::jsonb, 'easy',
 ARRAY['implementation', 'arithmetic', 'math'], 'baekjoon', 'https://www.acmicpc.net/problem/1001', '2 초', '128 MB',
 '[{"language": "python", "code": "a, b = map(int, input().split())\nprint(a - b)"}, {"language": "java", "code": "import java.util.Scanner;\npublic class Main { public static void main(String[] args) { Scanner sc = new Scanner(System.in); System.out.println(sc.nextInt() - sc.nextInt()); }}"}]'::jsonb),

('1003', '[백준 1003] 피보나치 함수', 'fibonacci(N)을 호출했을 때, 0과 1이 각각 몇 번 출력되는지 구하세요.',
 '{"inputs": ["3\\n0\\n1\\n3"], "outputs": ["1 0\\n0 1\\n1 2"]}'::jsonb, 'medium',
 ARRAY['dp'], 'baekjoon', 'https://www.acmicpc.net/problem/1003', '0.25 초', '128 MB',
 '[{"language": "python", "code": "dp = [[0,0] for _ in range(41)]\ndp[0], dp[1] = [1,0], [0,1]\nfor i in range(2,41): dp[i] = [dp[i-1][0]+dp[i-2][0], dp[i-1][1]+dp[i-2][1]]\nfor _ in range(int(input())): n=int(input()); print(dp[n][0], dp[n][1])"}]'::jsonb),

('1004', '[백준 1004] 어린 왕자', '출발점에서 도착점까지 필요한 최소 행성계 진입/이탈 횟수를 구하세요.',
 '{"inputs": ["1\\n-5 1 12 1\\n1\\n1 1 8"], "outputs": ["2"]}'::jsonb, 'medium',
 ARRAY['math', 'geometry'], 'baekjoon', 'https://www.acmicpc.net/problem/1004', '2 초', '128 MB',
 '[{"language": "python", "code": "def inside(x,y,cx,cy,r): return (x-cx)**2+(y-cy)**2<r**2\nfor _ in range(int(input())):\n  x1,y1,x2,y2=map(int,input().split());n=int(input());c=0\n  for _ in range(n): cx,cy,r=map(int,input().split()); c+=inside(x1,y1,cx,cy,r)!=inside(x2,y2,cx,cy,r)\n  print(c)"}]'::jsonb);

-- 빈칸 문제
INSERT INTO problems_blank (original_id, language, code_template, answers) VALUES
('1001', 'python', 'a, b = map(_0_, input()._1_)\nprint(_2_)', ARRAY['int', 'split()', 'a - b']),
('1001', 'java', 'import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    _0_ sc = new Scanner(System.in);\n    System.out.println(sc._1_ - sc._2_);\n  }\n}', ARRAY['Scanner', 'nextInt()', 'nextInt()']),
('1003', 'python', 'dp = [[0,0] for _ in range(41)]\ndp[0] = _0_\ndp[1] = _1_\nfor i in range(2,41): dp[i] = [_2_, dp[i-1][1]+dp[i-2][1]]', ARRAY['[1,0]', '[0,1]', 'dp[i-1][0]+dp[i-2][0]']),
('1004', 'python', 'def inside(x,y,cx,cy,r): return _0_\n# ...\nif _1_: count += 1', ARRAY['(x-cx)**2+(y-cy)**2<r**2', 'inside(x1,y1,cx,cy,r)!=inside(x2,y2,cx,cy,r)']);

-- 퍼즐 문제
INSERT INTO problems_puzzle (original_id, language, fixed_start, fixed_end, blocks) VALUES
('1001', 'python', NULL, NULL, '[{"id": 1, "code": "a, b = map(int, input().split())"}, {"id": 2, "code": "print(a - b)"}]'::jsonb),
('1001', 'java', 'import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {', '  }\n}', '[{"id": 1, "code": "Scanner sc = new Scanner(System.in);"}, {"id": 2, "code": "int a = sc.nextInt();"}, {"id": 3, "code": "int b = sc.nextInt();"}, {"id": 4, "code": "System.out.println(a - b);"}]'::jsonb),
('1003', 'python', 'dp = [[0,0] for _ in range(41)]', 'for _ in range(int(input())): print(dp[int(input())][0], dp[int(input())][1])', '[{"id": 1, "code": "dp[0] = [1, 0]"}, {"id": 2, "code": "dp[1] = [0, 1]"}, {"id": 3, "code": "for i in range(2,41): dp[i] = [dp[i-1][0]+dp[i-2][0], dp[i-1][1]+dp[i-2][1]]"}]'::jsonb);

-- 대화형 문제
INSERT INTO problems_guided (original_id, language, concepts, flow, checkpoints) VALUES
('1001', 'python', ARRAY['input().split()', 'map(int, ...)', 'print()'], ARRAY['입력 방법', '형변환', '출력'], ARRAY['공백 구분 입력', 'int 변환', '뺄셈 출력']),
('1003', 'python', ARRAY['재귀의 비효율성', 'DP', '점화식'], ARRAY['재귀 문제점 파악', 'DP 접근', '초기값 설정'], ARRAY['시간초과 이해', 'dp[0]=[1,0]', 'dp[i]=dp[i-1]+dp[i-2]']),
('1004', 'python', ARRAY['점과 원의 관계', 'XOR 조건', '카운팅'], ARRAY['원 안/밖 판별', '출발/도착 비교', '카운트'], ARRAY['거리^2 < r^2', 'in_start != in_end', 'count++']);

-- =====================================================
-- 8. 권한 부여
-- =====================================================
GRANT SELECT ON base_problems TO authenticated;
GRANT SELECT ON base_problems TO anon;
GRANT ALL ON base_problems TO service_role;

GRANT SELECT ON problems_blank TO authenticated;
GRANT SELECT ON problems_blank TO anon;
GRANT ALL ON problems_blank TO service_role;

GRANT SELECT ON problems_puzzle TO authenticated;
GRANT SELECT ON problems_puzzle TO anon;
GRANT ALL ON problems_puzzle TO service_role;

GRANT SELECT ON problems_guided TO authenticated;
GRANT SELECT ON problems_guided TO anon;
GRANT ALL ON problems_guided TO service_role;
