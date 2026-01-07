/**
 * Raw JSON Data Types
 *
 * data/ 폴더의 JSON 파일 구조를 정의합니다.
 * LLM이 생성한 문제 데이터의 원본 형태입니다.
 */

// ===========================================
// example_problem.json (원본 문제 데이터)
// ===========================================

export interface RawSolution {
  language: string;
  code: string;
}

export interface RawInputOutput {
  inputs: string[];
  outputs: string[];
}

export interface RawProblem {
  id: string;
  name: string;
  question: string;
  input_output: RawInputOutput;
  difficulty: 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard';
  tags: string[];
  source?: string;
  url?: string;
  time_limit?: string;
  memory_limit?: string;
  original_id?: string;
  solutions: RawSolution[];
}

// ===========================================
// problems_blank.json (빈칸 채우기 문제)
// ===========================================

export interface RawBlankProblem {
  original_id: string;        // example_problem의 id 참조
  language: string;           // python, java, cpp, javascript
  code_template: string;      // _0_, _1_, _2_ 형태의 빈칸
  answers: string[];          // 정답 배열 (순서대로)
}

// ===========================================
// problems_puzzle.json (코드 블록 정렬 문제)
// ===========================================

export interface RawPuzzleBlock {
  id: number;
  code: string;
  indent?: number;  // 들여쓰기 레벨 (0: 루트, 1: 함수내부, 2: 중첩블록)
}

export interface RawPuzzleProblem {
  original_id: string;        // example_problem의 id 참조
  language: string;
  fixed_start?: string;       // 고정된 시작 코드 (선택)
  fixed_end?: string;         // 고정된 끝 코드 (선택)
  blocks: RawPuzzleBlock[];   // 정렬해야 할 블록들 (id 순서가 정답)
}

// ===========================================
// 변환된 문제 타입 (UI에서 사용)
// ===========================================

export type ConvertedProblemType = 'blank' | 'puzzle' | 'guided' | 'implementation';

export interface ConvertedBlank {
  id: string;
  position?: number;          // _0_ -> 0, _1_ -> 1
  answer: string;
  placeholder?: string;       // _0_, _1_ 등 원본 플레이스홀더
  hints?: string[];           // 힌트 배열
}

export interface ConvertedPuzzleBlock {
  id: string;
  code: string;
  correctOrder?: number;      // 정답 순서 (원본 id 기준)
  indentation?: number;       // 들여쓰기 레벨
}

export interface ConvertedPuzzleDistractor {
  id: string;
  code: string;
  indentation?: number;
  why_wrong?: string;
}

export interface ConvertedTestCase {
  input: string;
  expected: string;
  isHidden?: boolean;
}

// Guided 문제용 타입 (새 간단 형식: string arrays)
// 레거시 형식은 하위 호환성을 위해 유지
export interface GuidedConcept {
  name: string;
  explanation: string;
  analogy?: string;
}

export interface GuidedFlowStep {
  step: number;
  title: string;
  tutor_message: string;
  expected_understanding: string;
  hints_if_stuck: string[];
}

export interface GuidedCheckpoint {
  step: number;
  question: string;
  correct_indicators: string[];
  follow_up_if_wrong: string;
}

// 새 형식 (problems_guided.json과 일치)
// concepts, flow, checkpoints는 모두 string[] 형태

export interface ConvertedProblem {
  id: string;
  title: string;
  description: string;
  framework?: 'python' | 'java' | 'cpp' | 'javascript';
  difficulty: 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard';
  topics: string[];
  problemType: ConvertedProblemType;

  // 공통 필드
  solutionCode?: string;      // 정답 코드
  testCases?: ConvertedTestCase[];
  keyConcepts: string[];      // 핵심 개념 (힌트 생성용)

  // Blank 문제용
  codeSnippet?: string;       // ___ 형태로 변환된 코드 (레거시)
  codeTemplate?: string;      // _0_, _1_ 형태로 변환된 코드 (새 형식)
  blanks?: ConvertedBlank[];

  // Puzzle 문제용
  puzzleBlocks?: ConvertedPuzzleBlock[];
  blocks?: ConvertedPuzzleBlock[];      // 새 형식
  correctOrder?: string[];              // 정답 순서 (블록 ID 배열)
  distractors?: ConvertedPuzzleDistractor[];  // 오답 블록
  fixedStart?: string;
  fixedEnd?: string;

  // Guided 문제용 (새 형식: string[], 레거시 형식: 복잡한 객체 배열)
  concepts?: string[] | GuidedConcept[];
  flow?: string[] | GuidedFlowStep[];
  checkpoints?: string[] | GuidedCheckpoint[];
  finalCodeReveal?: string;

  // 메타 정보
  source?: string;
  sourceUrl?: string;
  estimatedTime?: number;
  solvedCount?: number;       // 풀이 수 (통계용)

  // 잔디 클릭 시 문제 정보 표시용
  originalId?: string;        // base_problems.original_id (e.g., "taco_100")
  baseProblemId?: string;     // base_problems.id (UUID)
}
