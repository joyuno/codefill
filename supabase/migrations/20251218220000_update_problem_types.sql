-- =====================================================
-- CodeFill Database Migration: Update Problem Types
-- Changes: blank, bug, output, refactor → blank, puzzle
-- =====================================================

-- 1. Create puzzle_blocks table for Parsons Problems
CREATE TABLE IF NOT EXISTS puzzle_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    block_id VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    indentation INTEGER DEFAULT 0,
    is_distractor BOOLEAN DEFAULT FALSE,
    correct_position INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS puzzle_blocks_problem_idx ON puzzle_blocks(problem_id);

-- 2. Delete old React/JS framework-specific problems and codes
DELETE FROM problems WHERE code_id IN (
    SELECT id FROM codes WHERE framework IN ('react', 'vue', 'angular', 'javascript')
);

DELETE FROM codes WHERE framework IN ('react', 'vue', 'angular', 'javascript');

-- 3. Insert new algorithm-focused codes using gen_random_uuid()
INSERT INTO codes (id, framework, category, tags, title, description, code, difficulty) VALUES
-- Two Sum
('10000001-0001-0001-0001-000000000001', 'python', 'Array', ARRAY['array', 'hash-map', 'two-pointer'],
'Two Sum',
'주어진 배열에서 두 수의 합이 target이 되는 인덱스를 찾으세요.',
E'def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []',
'easy'),

-- Fibonacci
('10000002-0002-0002-0002-000000000002', 'python', 'Dynamic Programming', ARRAY['dp', 'recursion', 'memoization'],
'Fibonacci Number',
'n번째 피보나치 수를 계산하세요.',
E'def fibonacci(n):\n    if n <= 1:\n        return n\n    dp = [0] * (n + 1)\n    dp[1] = 1\n    for i in range(2, n + 1):\n        dp[i] = dp[i-1] + dp[i-2]\n    return dp[n]',
'easy'),

-- Binary Search
('10000003-0003-0003-0003-000000000003', 'python', 'Search', ARRAY['binary-search', 'divide-conquer'],
'Binary Search',
'정렬된 배열에서 target의 인덱스를 찾으세요.',
E'def binary_search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1',
'easy'),

-- Merge Sort
('10000004-0004-0004-0004-000000000004', 'python', 'Sorting', ARRAY['sorting', 'divide-conquer', 'recursion'],
'Merge Sort',
'배열을 병합 정렬로 정렬하세요.',
E'def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result',
'medium'),

-- Valid Parentheses
('10000005-0005-0005-0005-000000000005', 'python', 'Stack', ARRAY['stack', 'string', 'hash-map'],
'Valid Parentheses',
'주어진 문자열의 괄호가 올바르게 짝지어졌는지 확인하세요.',
E'def is_valid(s):\n    stack = []\n    mapping = {")": "(", "}": "{", "]": "["}\n    for char in s:\n        if char in mapping:\n            if not stack or stack[-1] != mapping[char]:\n                return False\n            stack.pop()\n        else:\n            stack.append(char)\n    return len(stack) == 0',
'easy'),

-- Reverse Linked List
('10000006-0006-0006-0006-000000000006', 'python', 'Linked List', ARRAY['linked-list', 'pointer'],
'Reverse Linked List',
'연결 리스트를 뒤집으세요.',
E'def reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        next_temp = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_temp\n    return prev',
'easy');

-- 4. Insert blank type problems
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, hints, difficulty) VALUES
-- Two Sum Blank
('20000001-0001-0001-0001-000000000001', '10000001-0001-0001-0001-000000000001', 'blank',
E'def two_sum(nums, target):\n    hash_map = ___\n    for i, num in enumerate(nums):\n        complement = ___ - num\n        if complement in ___:\n            return [hash_map[complement], i]\n        hash_map[___] = i\n    return []',
'{"blanks": [{"id": "b1", "answer": "{}", "hints": ["빈 딕셔너리를 초기화합니다"]}, {"id": "b2", "answer": "target", "hints": ["target에서 현재 수를 빼면 보수를 구할 수 있습니다"]}, {"id": "b3", "answer": "hash_map", "hints": ["이미 본 숫자들이 저장된 곳을 확인합니다"]}, {"id": "b4", "answer": "num", "hints": ["현재 숫자를 키로 저장합니다"]}]}'::jsonb,
'{"level_1": "해시맵을 사용해 O(n) 시간복잡도로 풀 수 있습니다", "level_2": "각 숫자의 보수(complement)를 찾아야 합니다", "level_3": "hash_map[num] = i로 인덱스를 저장합니다"}'::jsonb,
'easy'),

-- Binary Search Blank
('20000002-0002-0002-0002-000000000002', '10000003-0003-0003-0003-000000000003', 'blank',
E'def binary_search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left ___ right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return ___\n        elif nums[mid] < target:\n            left = ___ + 1\n        else:\n            right = mid - ___\n    return -1',
'{"blanks": [{"id": "b1", "answer": "<=", "hints": ["left가 right보다 작거나 같을 때까지 반복"]}, {"id": "b2", "answer": "mid", "hints": ["target을 찾았으니 해당 인덱스를 반환"]}, {"id": "b3", "answer": "mid", "hints": ["target이 mid보다 크면 왼쪽 범위를 좁힙니다"]}, {"id": "b4", "answer": "1", "hints": ["target이 mid보다 작으면 오른쪽 범위를 좁힙니다"]}]}'::jsonb,
'{"level_1": "이진 탐색은 정렬된 배열을 절반씩 나눠 탐색합니다", "level_2": "left와 right 포인터로 탐색 범위를 조절합니다", "level_3": "mid 값과 target을 비교해 범위를 좁혀갑니다"}'::jsonb,
'easy');

-- 5. Insert puzzle type problems (Parsons Problems)
INSERT INTO problems (id, code_id, problem_type, problem_code, answer_data, hints, difficulty) VALUES
-- Fibonacci Puzzle
('30000001-0001-0001-0001-000000000001', '10000002-0002-0002-0002-000000000002', 'puzzle',
E'# 피보나치 수를 계산하는 코드 블록을 올바른 순서로 배열하세요',
'{"blocks": [{"id": "b1", "code": "def fibonacci(n):", "indentation": 0, "position": 1}, {"id": "b2", "code": "if n <= 1:", "indentation": 1, "position": 2}, {"id": "b3", "code": "return n", "indentation": 2, "position": 3}, {"id": "b4", "code": "dp = [0] * (n + 1)", "indentation": 1, "position": 4}, {"id": "b5", "code": "dp[1] = 1", "indentation": 1, "position": 5}, {"id": "b6", "code": "for i in range(2, n + 1):", "indentation": 1, "position": 6}, {"id": "b7", "code": "dp[i] = dp[i-1] + dp[i-2]", "indentation": 2, "position": 7}, {"id": "b8", "code": "return dp[n]", "indentation": 1, "position": 8}], "correct_order": ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"], "distractors": [{"id": "d1", "code": "return dp[0]", "indentation": 1}]}'::jsonb,
'{"level_1": "피보나치 수열: F(n) = F(n-1) + F(n-2)", "level_2": "base case를 먼저 처리하고 dp 배열을 초기화합니다", "level_3": "for 루프로 dp[i]를 계산하고 마지막에 dp[n]을 반환합니다"}'::jsonb,
'easy'),

-- Merge Sort Puzzle
('30000002-0002-0002-0002-000000000002', '10000004-0004-0004-0004-000000000004', 'puzzle',
E'# merge 함수의 코드 블록을 올바른 순서로 배열하세요',
'{"blocks": [{"id": "b1", "code": "def merge(left, right):", "indentation": 0, "position": 1}, {"id": "b2", "code": "result = []", "indentation": 1, "position": 2}, {"id": "b3", "code": "i = j = 0", "indentation": 1, "position": 3}, {"id": "b4", "code": "while i < len(left) and j < len(right):", "indentation": 1, "position": 4}, {"id": "b5", "code": "if left[i] <= right[j]:", "indentation": 2, "position": 5}, {"id": "b6", "code": "result.append(left[i])", "indentation": 3, "position": 6}, {"id": "b7", "code": "i += 1", "indentation": 3, "position": 7}, {"id": "b8", "code": "else:", "indentation": 2, "position": 8}, {"id": "b9", "code": "result.append(right[j])", "indentation": 3, "position": 9}, {"id": "b10", "code": "j += 1", "indentation": 3, "position": 10}, {"id": "b11", "code": "result.extend(left[i:])", "indentation": 1, "position": 11}, {"id": "b12", "code": "result.extend(right[j:])", "indentation": 1, "position": 12}, {"id": "b13", "code": "return result", "indentation": 1, "position": 13}], "correct_order": ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b11", "b12", "b13"], "distractors": [{"id": "d1", "code": "return left + right", "indentation": 1}]}'::jsonb,
'{"level_1": "두 정렬된 배열을 하나로 합칩니다", "level_2": "두 포인터를 사용해 작은 값부터 result에 추가합니다", "level_3": "while 루프 후 남은 요소들을 extend로 추가합니다"}'::jsonb,
'medium');

-- 6. Grant permissions
GRANT SELECT ON puzzle_blocks TO authenticated;
GRANT SELECT ON puzzle_blocks TO anon;
GRANT ALL ON puzzle_blocks TO service_role;

-- 7. Enable RLS
ALTER TABLE puzzle_blocks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view puzzle_blocks" ON puzzle_blocks FOR SELECT USING (true);
CREATE POLICY "Service role can manage puzzle_blocks" ON puzzle_blocks FOR ALL USING (auth.role() = 'service_role');
