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

export interface RecordSubmission {
  problemId: string;
  problemType: 'blank' | 'puzzle' | 'guided';
  isCorrect: boolean;
  xpEarned?: number;
}

export interface RecordResult {
  success: boolean;
  xpEarned: number;
  message: string;
}

export interface HintCheckResult {
  canUse: boolean;
  currentXp: number;
  hintCost: number;
  message: string;
}

export interface HintUseResult {
  success: boolean;
  xpDeducted: number;
  remainingXp: number;
  message: string;
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

  /**
   * Record problem solve for XP and grass (simple record without validation)
   */
  async recordSolve(submission: RecordSubmission & { difficulty?: string }): Promise<RecordResult> {
    const response = await api.post<RecordResult>('/practice/submit/record', {
      problem_id: submission.problemId,
      problem_type: submission.problemType,
      difficulty: submission.difficulty,
      is_correct: submission.isCorrect,
      xp_earned: submission.xpEarned,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Check if user can use a hint (has enough XP)
   */
  async checkHint(): Promise<HintCheckResult> {
    const response = await api.get<{
      can_use: boolean;
      current_xp: number;
      hint_cost: number;
      message: string;
    }>('/practice/hint/check');
    if (response.error) throw new Error(response.error.message);
    return {
      canUse: response.data!.can_use,
      currentXp: response.data!.current_xp,
      hintCost: response.data!.hint_cost,
      message: response.data!.message,
    };
  },

  /**
   * Use a hint (deducts XP)
   */
  async useHint(): Promise<HintUseResult> {
    const response = await api.post<{
      success: boolean;
      xp_deducted: number;
      remaining_xp: number;
      message: string;
    }>('/practice/hint/use');
    if (response.error) throw new Error(response.error.message);
    return {
      success: response.data!.success,
      xpDeducted: response.data!.xp_deducted,
      remainingXp: response.data!.remaining_xp,
      message: response.data!.message,
    };
  },
};
