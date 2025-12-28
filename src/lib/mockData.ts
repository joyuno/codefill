import { User, Badge, Problem, Message, ActivityDay, RecentActivity, ProblemType, GuidedProblemData, ImplementationProblemData, BaseProblem, BlankProblem, PuzzleProblem, GuidedProblem } from './types';

// =====================================================
// 기본 문제 데이터 (example_problem.json 형식)
// =====================================================
export const baseProblems: BaseProblem[] = [
  {
    id: 'baekjoon_1001',
    original_id: '1001',
    name: '[백준 1001] A-B',
    question: '두 정수 A와 B를 입력받은 다음, A-B를 출력하는 프로그램을 작성하시오.',
    input_output: { inputs: ['3 2'], outputs: ['1'] },
    difficulty: 'easy',
    tags: ['implementation', 'arithmetic', 'math'],
    source: 'baekjoon',
    url: 'https://www.acmicpc.net/problem/1001',
    time_limit: '2 초',
    memory_limit: '128 MB',
    solutions: [
      { language: 'python', code: 'a, b = map(int, input().split())\nprint(a - b)' },
      { language: 'java', code: 'import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        System.out.println(sc.nextInt() - sc.nextInt());\n    }\n}' },
      { language: 'cpp', code: '#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a - b << endl;\n    return 0;\n}' }
    ]
  },
  {
    id: 'baekjoon_1003',
    original_id: '1003',
    name: '[백준 1003] 피보나치 함수',
    question: 'fibonacci(N)을 호출했을 때, 0과 1이 각각 몇 번 출력되는지 구하세요.',
    input_output: { inputs: ['3\n0\n1\n3'], outputs: ['1 0\n0 1\n1 2'] },
    difficulty: 'medium',
    tags: ['dp'],
    source: 'baekjoon',
    url: 'https://www.acmicpc.net/problem/1003',
    solutions: [
      { language: 'python', code: 'dp = [[0,0] for _ in range(41)]\ndp[0], dp[1] = [1,0], [0,1]\nfor i in range(2,41): dp[i] = [dp[i-1][0]+dp[i-2][0], dp[i-1][1]+dp[i-2][1]]\nfor _ in range(int(input())): n=int(input()); print(dp[n][0], dp[n][1])' }
    ]
  },
  {
    id: 'baekjoon_1004',
    original_id: '1004',
    name: '[백준 1004] 어린 왕자',
    question: '출발점에서 도착점까지 필요한 최소 행성계 진입/이탈 횟수를 구하세요.',
    input_output: { inputs: ['1\n-5 1 12 1\n1\n1 1 8'], outputs: ['2'] },
    difficulty: 'medium',
    tags: ['math', 'geometry'],
    source: 'baekjoon',
    url: 'https://www.acmicpc.net/problem/1004',
    solutions: [
      { language: 'python', code: 'def inside(x,y,cx,cy,r): return (x-cx)**2+(y-cy)**2<r**2\nfor _ in range(int(input())):\n  x1,y1,x2,y2=map(int,input().split());n=int(input());c=0\n  for _ in range(n): cx,cy,r=map(int,input().split()); c+=inside(x1,y1,cx,cy,r)!=inside(x2,y2,cx,cy,r)\n  print(c)' }
    ]
  }
];

// =====================================================
// 빈칸 문제 (problems_blank.json 형식)
// =====================================================
export const blankProblems: BlankProblem[] = [
  { original_id: '1001', language: 'python', code_template: 'a, b = map(_0_, input()._1_)\nprint(_2_)', answers: ['int', 'split()', 'a - b'] },
  { original_id: '1001', language: 'java', code_template: 'import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    _0_ sc = new Scanner(System.in);\n    System.out.println(sc._1_ - sc._2_);\n  }\n}', answers: ['Scanner', 'nextInt()', 'nextInt()'] },
  { original_id: '1003', language: 'python', code_template: 'dp = [[0,0] for _ in range(41)]\ndp[0] = _0_\ndp[1] = _1_\nfor i in range(2,41): dp[i] = [_2_, dp[i-1][1]+dp[i-2][1]]', answers: ['[1,0]', '[0,1]', 'dp[i-1][0]+dp[i-2][0]'] },
  { original_id: '1004', language: 'python', code_template: 'def inside(x,y,cx,cy,r): return _0_\n# ...\nif _1_: count += 1', answers: ['(x-cx)**2+(y-cy)**2<r**2', 'inside(x1,y1,cx,cy,r)!=inside(x2,y2,cx,cy,r)'] }
];

// =====================================================
// 퍼즐 문제 (problems_puzzle.json 형식)
// =====================================================
export const puzzleProblems: PuzzleProblem[] = [
  { original_id: '1001', language: 'python', blocks: [{ id: 1, code: 'a, b = map(int, input().split())' }, { id: 2, code: 'print(a - b)' }] },
  { original_id: '1001', language: 'java', fixed_start: 'import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {', fixed_end: '  }\n}', blocks: [{ id: 1, code: 'Scanner sc = new Scanner(System.in);' }, { id: 2, code: 'int a = sc.nextInt();' }, { id: 3, code: 'int b = sc.nextInt();' }, { id: 4, code: 'System.out.println(a - b);' }] },
  { original_id: '1003', language: 'python', fixed_start: 'dp = [[0,0] for _ in range(41)]', fixed_end: 'for _ in range(int(input())): print(dp[int(input())][0], dp[int(input())][1])', blocks: [{ id: 1, code: 'dp[0] = [1, 0]' }, { id: 2, code: 'dp[1] = [0, 1]' }, { id: 3, code: 'for i in range(2,41): dp[i] = [dp[i-1][0]+dp[i-2][0], dp[i-1][1]+dp[i-2][1]]' }] }
];

// =====================================================
// 대화형 문제 (problems_guided.json 형식)
// =====================================================
export const guidedProblemsData: GuidedProblem[] = [
  { original_id: '1001', language: 'python', concepts: ['input().split()', 'map(int, ...)', 'print()'], flow: ['입력 방법', '형변환', '출력'], checkpoints: ['공백 구분 입력', 'int 변환', '뺄셈 출력'] },
  { original_id: '1003', language: 'python', concepts: ['재귀의 비효율성', 'DP', '점화식'], flow: ['재귀 문제점 파악', 'DP 접근', '초기값 설정'], checkpoints: ['시간초과 이해', 'dp[0]=[1,0]', 'dp[i]=dp[i-1]+dp[i-2]'] },
  { original_id: '1004', language: 'python', concepts: ['점과 원의 관계', 'XOR 조건', '카운팅'], flow: ['원 안/밖 판별', '출발/도착 비교', '카운트'], checkpoints: ['거리^2 < r^2', 'in_start != in_end', 'count++'] }
];

export const mockUser: User = {
  id: '1',
  username: 'CodeNinja',
  email: 'ninja@code.dev',
  avatarShape: 'hexagon',
  avatarColor: 'hsl(142, 71%, 45%)',
  level: 23,
  currentXP: 2450,
  requiredXP: 3000,
  badges: [],
  solvedCount: 142,
  streak: 15,
  joinedAt: '2024-01-15',
  subscription: 'pro',
};

const BADGE_STORAGE_URL = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges';

export const mockBadges: Badge[] = [
  { id: '1', name: 'First Step', icon: 'first step', iconUrl: `${BADGE_STORAGE_URL}/first_step.png`, description: 'Complete your first problem', earnedAt: '2024-01-16', rarity: 'common' },
  { id: '2', name: 'Week Warrior', icon: 'week warrior', iconUrl: `${BADGE_STORAGE_URL}/week_warrior.png`, description: '7 day streak', earnedAt: '2024-02-01', rarity: 'common' },
  { id: '3', name: 'Half Century', icon: 'half century', iconUrl: `${BADGE_STORAGE_URL}/half_century.png`, description: 'Solve 50 problems', earnedAt: '2024-03-15', rarity: 'rare' },
  { id: '4', name: 'Rising Star', icon: 'rising star', iconUrl: `${BADGE_STORAGE_URL}/rising_star.png`, description: 'Reach level 10', earnedAt: '2024-04-20', rarity: 'epic' },
  { id: '5', name: 'Expert', icon: 'expert', iconUrl: `${BADGE_STORAGE_URL}/expert.png`, description: 'Reach level 50', earnedAt: '2024-05-01', rarity: 'legendary' },
];

export const mockProblems: Problem[] = [
  // Blank fill type - Two Sum
  {
    id: '1',
    original_id: 'twosum_001',
    title: 'Two Sum',
    description: '주어진 배열에서 두 수의 합이 target이 되는 인덱스를 찾으세요. 해시맵을 사용해 O(n) 시간복잡도로 해결할 수 있습니다.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['array', 'hash-map', 'two-pointer'],
    estimatedTime: 15,
    solvedCount: 1234,
    problemType: 'blank',
    codeSnippet: `def two_sum(nums, target):
    hash_map = ___
    for i, num in enumerate(nums):
        complement = ___ - num
        if complement in ___:
            return [hash_map[complement], i]
        hash_map[___] = i
    return []`,
    blanks: [
      { id: 'b1', position: 1, answer: '{}', hints: ['빈 딕셔너리를 초기화합니다', '중괄호 사용', '{}'] },
      { id: 'b2', position: 2, answer: 'target', hints: ['target에서 현재 수를 빼면 보수를 구할 수 있습니다', '찾아야 하는 값', 'target'] },
      { id: 'b3', position: 3, answer: 'hash_map', hints: ['이미 본 숫자들이 저장된 곳을 확인합니다', '딕셔너리 변수', 'hash_map'] },
      { id: 'b4', position: 4, answer: 'num', hints: ['현재 숫자를 키로 저장합니다', '키 값', 'num'] },
    ],
    relatedDocs: [
      { title: 'Python Dictionary', url: 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries' },
    ],
    keyConcepts: ['Hash Map', 'Complement', 'enumerate'],
  },
  // Blank fill type - Binary Search
  {
    id: '2',
    title: 'Binary Search',
    description: '정렬된 배열에서 target의 인덱스를 찾으세요. 이진 탐색 알고리즘을 사용합니다.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['binary-search', 'divide-conquer'],
    estimatedTime: 15,
    solvedCount: 892,
    problemType: 'blank',
    codeSnippet: `def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left ___ right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return ___
        elif nums[mid] < target:
            left = ___ + 1
        else:
            right = mid - ___
    return -1`,
    blanks: [
      { id: 'b1', position: 1, answer: '<=', hints: ['left가 right보다 작거나 같을 때까지 반복', '비교 연산자', '<='] },
      { id: 'b2', position: 2, answer: 'mid', hints: ['target을 찾았으니 해당 인덱스를 반환', '인덱스', 'mid'] },
      { id: 'b3', position: 3, answer: 'mid', hints: ['target이 mid보다 크면 왼쪽 범위를 좁힙니다', '인덱스', 'mid'] },
      { id: 'b4', position: 4, answer: '1', hints: ['오른쪽 범위를 하나 줄입니다', '숫자', '1'] },
    ],
    relatedDocs: [
      { title: 'Binary Search Algorithm', url: 'https://en.wikipedia.org/wiki/Binary_search_algorithm' },
    ],
    keyConcepts: ['Binary Search', 'Left/Right Pointers', 'Mid Calculation'],
  },
  // Puzzle type - Fibonacci
  {
    id: '3',
    title: 'Fibonacci Number',
    description: 'n번째 피보나치 수를 계산하는 코드 블록을 올바른 순서로 배열하세요.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['dp', 'recursion', 'memoization'],
    estimatedTime: 20,
    solvedCount: 567,
    problemType: 'puzzle',
    codeSnippet: '# 피보나치 수를 계산하는 코드 블록을 올바른 순서로 배열하세요',
    blanks: [],
    puzzleBlocks: [
      { id: 1, code: 'def fibonacci(n):', indentation: 0 },
      { id: 2, code: 'if n <= 1:', indentation: 1 },
      { id: 3, code: 'return n', indentation: 2 },
      { id: 4, code: 'dp = [0] * (n + 1)', indentation: 1 },
      { id: 5, code: 'dp[1] = 1', indentation: 1 },
      { id: 6, code: 'for i in range(2, n + 1):', indentation: 1 },
      { id: 7, code: 'dp[i] = dp[i-1] + dp[i-2]', indentation: 2 },
      { id: 8, code: 'return dp[n]', indentation: 1 },
    ],
    relatedDocs: [
      { title: 'Dynamic Programming', url: 'https://en.wikipedia.org/wiki/Dynamic_programming' },
    ],
    keyConcepts: ['Dynamic Programming', 'Memoization', 'Base Case'],
  },
  // Puzzle type - Merge Sort
  {
    id: '4',
    title: 'Merge Sort',
    description: 'merge 함수의 코드 블록을 올바른 순서로 배열하세요.',
    framework: 'python',
    difficulty: 'medium',
    topics: ['sorting', 'divide-conquer', 'recursion'],
    estimatedTime: 25,
    solvedCount: 423,
    problemType: 'puzzle',
    codeSnippet: '# merge 함수의 코드 블록을 올바른 순서로 배열하세요',
    blanks: [],
    puzzleBlocks: [
      { id: 1, code: 'def merge(left, right):', indentation: 0 },
      { id: 2, code: 'result = []', indentation: 1 },
      { id: 3, code: 'i = j = 0', indentation: 1 },
      { id: 4, code: 'while i < len(left) and j < len(right):', indentation: 1 },
      { id: 5, code: 'if left[i] <= right[j]:', indentation: 2 },
      { id: 6, code: 'result.append(left[i])', indentation: 3 },
      { id: 7, code: 'i += 1', indentation: 3 },
      { id: 8, code: 'else:', indentation: 2 },
      { id: 9, code: 'result.append(right[j])', indentation: 3 },
      { id: 10, code: 'j += 1', indentation: 3 },
      { id: 11, code: 'result.extend(left[i:])', indentation: 1 },
      { id: 12, code: 'result.extend(right[j:])', indentation: 1 },
      { id: 13, code: 'return result', indentation: 1 },
    ],
    relatedDocs: [
      { title: 'Merge Sort', url: 'https://en.wikipedia.org/wiki/Merge_sort' },
    ],
    keyConcepts: ['Merge Sort', 'Divide and Conquer', 'Two Pointers'],
  },
  // Blank fill type - Valid Parentheses
  {
    id: '5',
    title: 'Valid Parentheses',
    description: '주어진 문자열의 괄호가 올바르게 짝지어졌는지 확인하세요.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['stack', 'string', 'hash-map'],
    estimatedTime: 15,
    solvedCount: 654,
    problemType: 'blank',
    codeSnippet: `def is_valid(s):
    stack = ___
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in ___:
            if not stack or stack[-1] != mapping[char]:
                return ___
            stack.pop()
        else:
            stack.___(char)
    return len(stack) == ___`,
    blanks: [
      { id: 'b1', position: 1, answer: '[]', hints: ['빈 스택을 초기화합니다', '빈 리스트', '[]'] },
      { id: 'b2', position: 2, answer: 'mapping', hints: ['닫는 괄호인지 확인합니다', '딕셔너리 변수', 'mapping'] },
      { id: 'b3', position: 3, answer: 'False', hints: ['유효하지 않음을 반환', '불리언', 'False'] },
      { id: 'b4', position: 4, answer: 'append', hints: ['스택에 요소를 추가합니다', '리스트 메서드', 'append'] },
      { id: 'b5', position: 5, answer: '0', hints: ['스택이 비어있으면 유효함', '숫자', '0'] },
    ],
    relatedDocs: [
      { title: 'Stack Data Structure', url: 'https://en.wikipedia.org/wiki/Stack_(abstract_data_type)' },
    ],
    keyConcepts: ['Stack', 'Hash Map', 'String Parsing'],
  },
  // Blank fill type - Reverse Linked List
  {
    id: '6',
    title: 'Reverse Linked List',
    description: '연결 리스트를 뒤집는 알고리즘을 완성하세요.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['linked-list', 'pointer'],
    estimatedTime: 15,
    solvedCount: 432,
    problemType: 'blank',
    codeSnippet: `def reverse_list(head):
    prev = ___
    curr = head
    while curr:
        next_temp = curr.___
        curr.next = ___
        prev = curr
        curr = ___
    return ___`,
    blanks: [
      { id: 'b1', position: 1, answer: 'None', hints: ['이전 노드가 없는 초기 상태', '널 값', 'None'] },
      { id: 'b2', position: 2, answer: 'next', hints: ['다음 노드를 임시 저장', '속성 이름', 'next'] },
      { id: 'b3', position: 3, answer: 'prev', hints: ['현재 노드가 이전 노드를 가리키도록', '변수 이름', 'prev'] },
      { id: 'b4', position: 4, answer: 'next_temp', hints: ['다음 노드로 이동', '임시 변수', 'next_temp'] },
      { id: 'b5', position: 5, answer: 'prev', hints: ['새로운 헤드는 마지막 prev', '변수 이름', 'prev'] },
    ],
    relatedDocs: [
      { title: 'Linked List', url: 'https://en.wikipedia.org/wiki/Linked_list' },
    ],
    keyConcepts: ['Linked List', 'Pointer Manipulation', 'In-place Reversal'],
  },
  // Guided type - Two Sum Interactive
  {
    id: '7',
    title: 'Two Sum (1대1 대화형)',
    description: 'AI 튜터와 함께 Two Sum 문제를 단계별로 풀어봅니다.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['array', 'hash-map', 'two-pointer'],
    estimatedTime: 20,
    solvedCount: 321,
    problemType: 'guided',
    codeSnippet: '',
    blanks: [],
    relatedDocs: [
      { title: 'Python Dictionary', url: 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries' },
    ],
    keyConcepts: ['Hash Map', 'Complement', 'enumerate'],
    guidedData: {
      steps: [
        {
          stepNumber: 1,
          aiMessage: 'Two Sum 문제를 풀어볼까요?\n\n배열에서 두 수의 합이 target이 되는 인덱스를 찾아야 해요. 먼저 가장 단순한 방법은 무엇일까요?',
          responseType: 'text',
          correctCode: '이중 for문',
          hint: '모든 쌍을 비교하는 방법을 생각해보세요.',
        },
        {
          stepNumber: 2,
          aiMessage: '맞아요! 이중 for문으로 모든 쌍을 확인하면 되겠죠.\n\n그럼 시간복잡도는 어떻게 될까요?',
          responseType: 'choice',
          choices: ['O(n)', 'O(n²)', 'O(log n)', 'O(n log n)'],
          correctChoice: 1,
          hint: '두 개의 중첩된 반복문이 있으면 어떻게 될까요?',
        },
        {
          stepNumber: 3,
          aiMessage: '정확해요! O(n²)이에요.\n\n더 빠른 방법이 있을까요? 힌트: 이미 본 숫자를 기억해두면 어떨까요?',
          responseType: 'text',
          correctCode: '해시맵',
          hint: '키-값 쌍으로 데이터를 저장하는 자료구조를 생각해보세요.',
        },
        {
          stepNumber: 4,
          aiMessage: '좋아요! 해시맵을 사용하면 O(n)으로 풀 수 있어요.\n\n그럼 해시맵에 뭘 저장해야 할까요?',
          responseType: 'choice',
          choices: ['숫자만', '숫자와 인덱스', '인덱스만'],
          correctChoice: 1,
          hint: '결과로 인덱스를 반환해야 한다는 걸 기억하세요!',
        },
        {
          stepNumber: 5,
          aiMessage: '맞아요! 이제 코드로 옮겨볼까요?\n\n먼저 해시맵을 초기화하는 코드를 작성해보세요.',
          responseType: 'code',
          codeTemplate: 'hash_map = ___',
          correctCode: '{}',
          hint: '빈 딕셔너리를 만드는 방법을 생각해보세요.',
        },
        {
          stepNumber: 6,
          aiMessage: '완벽해요! 빈 딕셔너리로 시작하죠.\n\n이제 각 숫자를 순회하면서 complement(보수)를 계산해야 해요. complement = target - num 이죠.\n\ncomplement가 해시맵에 있으면 어떻게 해야 할까요?',
          responseType: 'choice',
          choices: ['계속 진행', '결과 반환', '해시맵에 추가'],
          correctChoice: 1,
          hint: '찾았으니까 정답을 반환해야겠죠?',
        },
      ],
      finalCode: `def two_sum(nums, target):
    hash_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hash_map:
            return [hash_map[complement], i]
        hash_map[num] = i
    return []`,
    },
  },
  // Implementation type - Two Sum
  {
    id: '8',
    title: 'Two Sum (구현)',
    description: '주어진 배열 nums에서 두 수의 합이 target이 되는 인덱스를 반환하세요.\n\n예시:\nInput: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\n\n제약 조건:\n- 각 입력에 정확히 하나의 답이 있다고 가정합니다.\n- 같은 요소를 두 번 사용할 수 없습니다.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['array', 'hash-map'],
    estimatedTime: 20,
    solvedCount: 987,
    problemType: 'implementation',
    codeSnippet: '',
    blanks: [],
    relatedDocs: [
      { title: 'Python Dictionary', url: 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries' },
    ],
    keyConcepts: ['Hash Map', 'Time Complexity'],
    implementationData: {
      functionSignature: 'def two_sum(nums: list[int], target: int) -> list[int]:',
      testCases: [
        { input: [[2, 7, 11, 15], 9], expected: [0, 1] },
        { input: [[3, 2, 4], 6], expected: [1, 2] },
        { input: [[3, 3], 6], expected: [0, 1] },
        { input: [[1, 2, 3, 4, 5], 9], expected: [3, 4], isHidden: true },
        { input: [[0, 4, 3, 0], 0], expected: [0, 3], isHidden: true },
      ],
    },
  },
  // Guided type - Binary Search
  {
    id: '9',
    title: 'Binary Search (1대1 대화형)',
    description: 'AI 튜터와 함께 이진 탐색 알고리즘을 단계별로 이해합니다.',
    framework: 'python',
    difficulty: 'easy',
    topics: ['binary-search', 'divide-conquer'],
    estimatedTime: 25,
    solvedCount: 234,
    problemType: 'guided',
    codeSnippet: '',
    blanks: [],
    relatedDocs: [
      { title: 'Binary Search', url: 'https://en.wikipedia.org/wiki/Binary_search_algorithm' },
    ],
    keyConcepts: ['Binary Search', 'Divide and Conquer', 'Sorted Array'],
    guidedData: {
      steps: [
        {
          stepNumber: 1,
          aiMessage: '이진 탐색을 배워볼까요?\n\n정렬된 배열에서 특정 값을 찾을 때 사용하는 알고리즘이에요.\n\n선형 탐색과 비교했을 때 이진 탐색의 장점은 뭘까요?',
          responseType: 'choice',
          choices: ['더 적은 메모리 사용', '더 빠른 탐색 속도', '정렬 불필요', '코드가 더 간단함'],
          correctChoice: 1,
          hint: '배열 크기가 클 때 어떤 차이가 날까요?',
        },
        {
          stepNumber: 2,
          aiMessage: '맞아요! 이진 탐색은 O(log n)으로 매우 빨라요.\n\n이진 탐색의 핵심 아이디어는 무엇일까요?',
          responseType: 'text',
          correctCode: '반으로 나누기',
          hint: '매번 탐색 범위를 어떻게 줄일까요?',
        },
        {
          stepNumber: 3,
          aiMessage: '정확해요! 매번 절반씩 줄여나가요.\n\n두 포인터 left와 right를 사용해요. 초기값은 어떻게 설정해야 할까요?',
          responseType: 'code',
          codeTemplate: 'left, right = ___, ___',
          correctCode: '0, len(nums) - 1',
          hint: '배열의 시작과 끝 인덱스를 생각해보세요.',
        },
        {
          stepNumber: 4,
          aiMessage: '좋아요! left = 0, right = len(nums) - 1\n\nwhile 반복문의 조건은 어떻게 되어야 할까요?',
          responseType: 'choice',
          choices: ['left < right', 'left <= right', 'left != right', 'left > right'],
          correctChoice: 1,
          hint: 'left와 right가 같을 때도 확인해야 할까요?',
        },
        {
          stepNumber: 5,
          aiMessage: 'left <= right가 맞아요! 같을 때도 확인해야 하니까요.\n\nmid 값은 어떻게 계산할까요?',
          responseType: 'code',
          codeTemplate: 'mid = ___',
          correctCode: '(left + right) // 2',
          hint: '두 값의 중간값을 구하는 방법을 생각해보세요.',
        },
      ],
      finalCode: `def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1`,
    },
  },
  // Implementation type - Maximum Subarray
  {
    id: '10',
    title: 'Maximum Subarray (구현)',
    description: '정수 배열 nums가 주어지면, 가장 큰 합을 가진 연속 부분 배열을 찾아 그 합을 반환하세요.\n\n예시:\nInput: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]\nOutput: 6\n설명: [4, -1, 2, 1]의 합이 6으로 가장 큽니다.\n\n힌트: Kadane\'s Algorithm을 사용해보세요.',
    framework: 'python',
    difficulty: 'medium',
    topics: ['dp', 'array', 'divide-conquer'],
    estimatedTime: 25,
    solvedCount: 654,
    problemType: 'implementation',
    codeSnippet: '',
    blanks: [],
    relatedDocs: [
      { title: 'Kadane\'s Algorithm', url: 'https://en.wikipedia.org/wiki/Maximum_subarray_problem' },
    ],
    keyConcepts: ['Dynamic Programming', 'Kadane\'s Algorithm'],
    implementationData: {
      functionSignature: 'def max_subarray(nums: list[int]) -> int:',
      testCases: [
        { input: [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], expected: 6 },
        { input: [[1]], expected: 1 },
        { input: [[5, 4, -1, 7, 8]], expected: 23 },
        { input: [[-1]], expected: -1, isHidden: true },
        { input: [[-2, -1]], expected: -1, isHidden: true },
      ],
    },
  },
];

export const mockMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: "안녕하세요! 코딩 테스트 및 알고리즘 연습을 도와드릴게요. 어떤 난이도로 시작하시겠어요?",
    timestamp: '2024-06-01T10:00:00Z',
    chips: [
      { label: 'Easy', value: 'easy', category: 'difficulty' },
      { label: 'Medium', value: 'medium', category: 'difficulty' },
      { label: 'Hard', value: 'hard', category: 'difficulty' },
    ],
  },
  {
    id: '2',
    role: 'user',
    content: "Easy 난이도로 시작할게요",
    timestamp: '2024-06-01T10:01:00Z',
  },
  {
    id: '3',
    role: 'assistant',
    content: "좋아요! Easy 난이도 문제를 추천해 드릴게요. 어떤 유형의 문제를 원하시나요?",
    timestamp: '2024-06-01T10:01:30Z',
    chips: [
      { label: '빈칸 채우기', value: 'blank', category: 'topic' },
      { label: '퍼즐 (코드 정렬)', value: 'puzzle', category: 'topic' },
    ],
  },
  {
    id: '4',
    role: 'user',
    content: "빈칸 채우기로 할게요",
    timestamp: '2024-06-01T10:02:00Z',
  },
  {
    id: '5',
    role: 'assistant',
    content: "Two Sum 문제를 추천합니다! 해시맵을 사용한 기본적인 알고리즘 문제예요.",
    timestamp: '2024-06-01T10:02:30Z',
  },
];

// Generate mock activity data for heatmap
export function generateMockActivityData(days: number = 365): ActivityDay[] {
  const data: ActivityDay[] = [];
  const today = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    // Random activity with some patterns
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const random = Math.random();

    let count = 0;
    let intensity: 0 | 1 | 2 | 3 | 4 = 0;

    if (random > (isWeekend ? 0.6 : 0.3)) {
      count = Math.floor(Math.random() * 10) + 1;
      intensity = count <= 2 ? 1 : count <= 4 ? 2 : count <= 7 ? 3 : 4;
    }

    data.push({
      date: date.toISOString().split('T')[0],
      count,
      intensity,
    });
  }

  return data;
}

export const mockRecentActivity: RecentActivity[] = [
  { id: '1', type: 'solved', title: 'Solved: Two Sum', description: 'Completed without hints', timestamp: '2024-06-01T09:30:00Z', xpGained: 150 },
  { id: '2', type: 'badge', title: 'New Badge: Speed Demon', description: 'Solved 10 problems in one day', timestamp: '2024-06-01T08:00:00Z' },
  { id: '3', type: 'streak', title: 'Streak Extended!', description: '15 days in a row', timestamp: '2024-05-31T23:59:00Z', xpGained: 50 },
  { id: '4', type: 'levelup', title: 'Level Up!', description: 'Reached Level 23', timestamp: '2024-05-30T15:00:00Z', xpGained: 500 },
  { id: '5', type: 'solved', title: 'Solved: Binary Search', description: 'Used 1 hint', timestamp: '2024-05-30T14:00:00Z', xpGained: 120 },
];

export const mockCodePreview = {
  title: 'Two Sum',
  description: '주어진 배열에서 두 수의 합이 target이 되는 인덱스를 찾는 문제입니다. 해시맵을 사용해 효율적으로 풀 수 있어요.',
  code: `def two_sum(nums, target):
    hash_map = _____  # Blank 1
    for i, num in enumerate(nums):
        complement = _____ - num  # Blank 2
        if complement in _____:  # Blank 3
            return [hash_map[complement], i]
        hash_map[_____] = i  # Blank 4
    return []`,
};
