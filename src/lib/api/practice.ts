/**
 * Practice API Functions
 */

import { api } from './client';

export interface BlankSubmission {
  problemId: string;
  answers: Record<string, string>;
}

export interface PuzzleSubmission {
  problemId: string;
  blockOrder: Array<{ id: string; indentation: number }>;
}

export interface BlankResult {
  results: Record<string, boolean>;
  allCorrect: boolean;
  xpEarned: number;
}

export interface PuzzleResult {
  isCorrect: boolean;
  results: Record<string, boolean>;
  xpEarned: number;
}

export interface RunCodeResult {
  output?: string;
  error?: string;
}

export const practiceApi = {
  /**
   * Run code without submitting
   */
  async runCode(code: string, language: string = 'python'): Promise<RunCodeResult> {
    const response = await api.post<RunCodeResult>('/practice/run', {
      code,
      language,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Submit blank fill answers
   */
  async submitBlank(submission: BlankSubmission): Promise<BlankResult> {
    const response = await api.post<BlankResult>('/practice/submit/blank', {
      problem_id: submission.problemId,
      answers: submission.answers,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Submit puzzle (Parsons Problem) answer
   */
  async submitPuzzle(submission: PuzzleSubmission): Promise<PuzzleResult> {
    const response = await api.post<PuzzleResult>('/practice/submit/puzzle', {
      problem_id: submission.problemId,
      block_order: submission.blockOrder,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};
