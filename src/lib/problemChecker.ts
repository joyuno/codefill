/**
 * Problem Checker
 *
 * 정답 검증 함수들 - JSON 데이터 의존성 없음
 * (프로덕션에서 data/examples 없이 빌드 가능)
 */

import type { ConvertedProblem } from './dataTypes';

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

  // 띄어쓰기를 제거하고 비교 (n - 1 == n-1)
  const normalize = (s: string) => s.trim().replace(/\s+/g, '');

  const results = problem.blanks.map((blank, index) => {
    const userAnswer = normalize(userAnswers[index] || '');
    const correctAnswer = normalize(blank.answer);
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
