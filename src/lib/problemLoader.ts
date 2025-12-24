/**
 * Problem Loader
 *
 * data/ 폴더의 JSON 파일을 로드하고 UI에서 사용할 수 있는 형태로 변환합니다.
 */

import type {
  RawProblem,
  RawBlankProblem,
  RawPuzzleProblem,
  ConvertedProblem,
  ConvertedBlank,
  ConvertedPuzzleBlock,
  ConvertedTestCase,
  ConvertedProblemType,
} from './dataTypes';

// JSON 데이터 import (빌드 시점에 포함)
import exampleProblems from '../../data/example/example_problem.json';
import blankProblems from '../../data/example/problems_blank.json';
import puzzleProblems from '../../data/example/problems_puzzle.json';

// 타입 캐스팅
const rawProblems = exampleProblems as RawProblem[];
const rawBlankProblems = blankProblems as RawBlankProblem[];
const rawPuzzleProblems = puzzleProblems as RawPuzzleProblem[];

// ===========================================
// 언어 매핑
// ===========================================

type FrameworkType = 'python' | 'java' | 'cpp' | 'javascript';

function normalizeLanguage(lang: string): FrameworkType {
  const normalized = lang.toLowerCase();
  if (normalized === 'python' || normalized === 'python3') return 'python';
  if (normalized === 'java') return 'java';
  if (normalized === 'cpp' || normalized === 'c++') return 'cpp';
  if (normalized === 'javascript' || normalized === 'js') return 'javascript';
  return 'python'; // 기본값
}

// ===========================================
// 빈칸 문제 변환
// ===========================================

function convertBlankProblem(
  raw: RawBlankProblem,
  baseProblem: RawProblem
): ConvertedProblem {
  // _0_, _1_, _2_ 패턴을 찾아서 빈칸 정보 생성
  const blankPattern = /_(\d+)_/g;
  const blanks: ConvertedBlank[] = [];
  let match;

  while ((match = blankPattern.exec(raw.code_template)) !== null) {
    const index = parseInt(match[1], 10);
    blanks.push({
      id: `blank-${index}`,
      position: index,
      answer: raw.answers[index] || '',
      placeholder: match[0], // _0_, _1_, etc.
    });
  }

  // 정렬 (position 순서대로)
  blanks.sort((a, b) => a.position - b.position);

  // _0_, _1_ 를 ___ 로 변환 (UI 표시용)
  const codeSnippet = raw.code_template.replace(/_\d+_/g, '___');

  // 정답 코드 찾기
  const solution = baseProblem.solutions.find(
    (s) => normalizeLanguage(s.language) === normalizeLanguage(raw.language)
  );

  // 테스트 케이스 변환
  const testCases = convertTestCases(baseProblem.input_output);

  return {
    id: `${raw.original_id}-${raw.language}-blank`,
    title: baseProblem.name,
    description: baseProblem.question,
    framework: normalizeLanguage(raw.language),
    difficulty: baseProblem.difficulty,
    topics: baseProblem.tags,
    problemType: 'blank',
    solutionCode: solution?.code || '',
    testCases,
    keyConcepts: generateKeyConcepts(baseProblem.tags, 'blank'),
    codeSnippet,
    blanks,
    source: baseProblem.source,
    sourceUrl: baseProblem.url,
    estimatedTime: estimateTime(baseProblem.difficulty),
  };
}

// ===========================================
// 퍼즐 문제 변환
// ===========================================

function convertPuzzleProblem(
  raw: RawPuzzleProblem,
  baseProblem: RawProblem
): ConvertedProblem {
  // 블록 변환 (id는 정답 순서를 나타냄)
  const puzzleBlocks: ConvertedPuzzleBlock[] = raw.blocks.map((block) => ({
    id: `block-${block.id}`,
    code: block.code,
    correctOrder: block.id, // 원본 id가 정답 순서
  }));

  // 정답 코드 찾기
  const solution = baseProblem.solutions.find(
    (s) => normalizeLanguage(s.language) === normalizeLanguage(raw.language)
  );

  // 테스트 케이스 변환
  const testCases = convertTestCases(baseProblem.input_output);

  return {
    id: `${raw.original_id}-${raw.language}-puzzle`,
    title: baseProblem.name,
    description: baseProblem.question,
    framework: normalizeLanguage(raw.language),
    difficulty: baseProblem.difficulty,
    topics: baseProblem.tags,
    problemType: 'puzzle',
    solutionCode: solution?.code || '',
    testCases,
    keyConcepts: generateKeyConcepts(baseProblem.tags, 'puzzle'),
    puzzleBlocks,
    fixedStart: raw.fixed_start,
    fixedEnd: raw.fixed_end,
    source: baseProblem.source,
    sourceUrl: baseProblem.url,
    estimatedTime: estimateTime(baseProblem.difficulty),
  };
}

// ===========================================
// Implementation 문제 변환 (원본 문제 그대로)
// ===========================================

function convertImplementationProblem(
  baseProblem: RawProblem,
  language: FrameworkType
): ConvertedProblem {
  const solution = baseProblem.solutions.find(
    (s) => normalizeLanguage(s.language) === language
  );

  const testCases = convertTestCases(baseProblem.input_output);

  return {
    id: `${baseProblem.id}-${language}-implementation`,
    title: baseProblem.name,
    description: baseProblem.question,
    framework: language,
    difficulty: baseProblem.difficulty,
    topics: baseProblem.tags,
    problemType: 'implementation',
    solutionCode: solution?.code || '',
    testCases,
    keyConcepts: generateKeyConcepts(baseProblem.tags, 'implementation'),
    source: baseProblem.source,
    sourceUrl: baseProblem.url,
    estimatedTime: estimateTime(baseProblem.difficulty),
  };
}

// ===========================================
// 유틸리티 함수
// ===========================================

function convertTestCases(inputOutput: {
  inputs: string[];
  outputs: string[];
}): ConvertedTestCase[] {
  const { inputs, outputs } = inputOutput;
  const length = Math.min(inputs.length, outputs.length);

  return Array.from({ length }, (_, i) => ({
    input: inputs[i],
    expected: outputs[i],
    isHidden: false,
  }));
}

function estimateTime(difficulty: 'easy' | 'medium' | 'hard'): number {
  switch (difficulty) {
    case 'easy':
      return 10;
    case 'medium':
      return 20;
    case 'hard':
      return 30;
  }
}

/**
 * 태그에서 핵심 개념을 생성합니다.
 */
function generateKeyConcepts(tags: string[], problemType: ConvertedProblemType): string[] {
  const conceptMap: Record<string, string> = {
    'implementation': '구현 로직',
    'arithmetic': '산술 연산',
    'math': '수학적 계산',
    'dp': '동적 프로그래밍 (DP)',
    'geometry': '기하학',
    'case_work': '케이스 분석',
    'string': '문자열 처리',
    'array': '배열 조작',
    'loop': '반복문',
    'condition': '조건문',
  };

  const concepts = tags.map(tag => conceptMap[tag] || tag);

  // 문제 타입별 추가 개념
  if (problemType === 'blank') {
    concepts.push('빈칸 채우기를 통한 코드 이해');
  } else if (problemType === 'puzzle') {
    concepts.push('코드 순서 파악');
  }

  return concepts.slice(0, 5); // 최대 5개
}

// ===========================================
// 메인 로더 함수
// ===========================================

/**
 * 모든 문제를 로드하고 변환합니다.
 */
export function loadAllProblems(): ConvertedProblem[] {
  const problems: ConvertedProblem[] = [];

  // 원본 문제 맵 생성 (빠른 조회용)
  const problemMap = new Map<string, RawProblem>();
  for (const problem of rawProblems) {
    problemMap.set(problem.id, problem);
  }

  // Blank 문제 변환
  for (const blank of rawBlankProblems) {
    const baseProblem = problemMap.get(blank.original_id);
    if (baseProblem) {
      problems.push(convertBlankProblem(blank, baseProblem));
    }
  }

  // Puzzle 문제 변환
  for (const puzzle of rawPuzzleProblems) {
    const baseProblem = problemMap.get(puzzle.original_id);
    if (baseProblem) {
      problems.push(convertPuzzleProblem(puzzle, baseProblem));
    }
  }

  // Implementation 문제 변환 (각 원본 문제의 첫 번째 언어 사용)
  for (const problem of rawProblems) {
    if (problem.solutions.length > 0) {
      const firstLang = normalizeLanguage(problem.solutions[0].language);
      problems.push(convertImplementationProblem(problem, firstLang));
    }
  }

  return problems;
}

/**
 * 특정 타입의 문제만 로드합니다.
 */
export function loadProblemsByType(
  type: ConvertedProblemType
): ConvertedProblem[] {
  return loadAllProblems().filter((p) => p.problemType === type);
}

/**
 * 특정 언어의 문제만 로드합니다.
 */
export function loadProblemsByLanguage(
  language: FrameworkType
): ConvertedProblem[] {
  return loadAllProblems().filter((p) => p.framework === language);
}

/**
 * 특정 난이도의 문제만 로드합니다.
 */
export function loadProblemsByDifficulty(
  difficulty: 'easy' | 'medium' | 'hard'
): ConvertedProblem[] {
  return loadAllProblems().filter((p) => p.difficulty === difficulty);
}

/**
 * ID로 문제를 찾습니다.
 */
export function findProblemById(id: string): ConvertedProblem | undefined {
  return loadAllProblems().find((p) => p.id === id);
}

/**
 * 원본 문제 ID로 관련된 모든 문제를 찾습니다.
 * (같은 원본에서 파생된 blank, puzzle, implementation 문제들)
 */
export function findRelatedProblems(originalId: string): ConvertedProblem[] {
  return loadAllProblems().filter((p) => p.id.startsWith(originalId));
}

// ===========================================
// 정답 검증 함수
// ===========================================

/**
 * Blank 문제 정답 검증
 * @param problem 문제
 * @param userAnswers 사용자가 입력한 정답 배열
 */
export function checkBlankAnswers(
  problem: ConvertedProblem,
  userAnswers: string[]
): { correct: boolean; results: boolean[] } {
  if (!problem.blanks) {
    return { correct: false, results: [] };
  }

  const results = problem.blanks.map((blank, index) => {
    const userAnswer = userAnswers[index]?.trim() || '';
    const correctAnswer = blank.answer.trim();
    return userAnswer === correctAnswer;
  });

  return {
    correct: results.every((r) => r),
    results,
  };
}

/**
 * Puzzle 문제 정답 검증
 * @param problem 문제
 * @param userOrder 사용자가 정렬한 블록 ID 순서
 */
export function checkPuzzleOrder(
  problem: ConvertedProblem,
  userOrder: string[]
): { correct: boolean; results: boolean[] } {
  if (!problem.puzzleBlocks) {
    return { correct: false, results: [] };
  }

  // 정답 순서 생성
  const correctOrder = [...problem.puzzleBlocks]
    .sort((a, b) => a.correctOrder - b.correctOrder)
    .map((b) => b.id);

  const results = userOrder.map((id, index) => id === correctOrder[index]);

  return {
    correct: results.every((r) => r),
    results,
  };
}

/**
 * 사용자 코드와 정답 코드 비교 (단순 비교)
 */
export function checkCodeMatch(
  problem: ConvertedProblem,
  userCode: string
): boolean {
  // 공백/줄바꿈 정규화 후 비교
  const normalize = (code: string) =>
    code.replace(/\s+/g, ' ').trim().toLowerCase();

  return normalize(userCode) === normalize(problem.solutionCode);
}

// ===========================================
// 캐시된 문제 목록 (성능 최적화)
// ===========================================

let cachedProblems: ConvertedProblem[] | null = null;

export function getProblems(): ConvertedProblem[] {
  if (!cachedProblems) {
    cachedProblems = loadAllProblems();
  }
  return cachedProblems;
}

export function clearProblemCache(): void {
  cachedProblems = null;
}
