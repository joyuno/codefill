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

export interface NewBadge {
  code: string;
  name: string;
  iconUrl?: string | null;
  rarity: string;
}

export interface BlankResult {
  results: Record<string, boolean>;
  allCorrect: boolean;
  xpEarned: number;
  newBadges?: NewBadge[];
}

export interface PuzzleResult {
  isCorrect: boolean;
  results: Record<string, boolean>;
  xpEarned: number;
  newBadges?: NewBadge[];
}

export interface RunCodeResult {
  output?: string;
  error?: string;
}

export interface RecordSubmission {
  problemId: string;
  baseProblemId?: string;  // base_problems 테이블 UUID (잔디 클릭 시 문제 정보 표시용)
  problemType: 'blank' | 'puzzle' | 'guided';
  isCorrect: boolean;
  xpEarned?: number;
  problemName?: string;  // 문제 이름 (잔디 클릭 시 표시용)
  hintsUsed?: number;    // 힌트 사용 횟수 (기록용)
  topics?: string[];     // 문제 주제/태그 (예: ["DP", "그래프"])
  attemptId?: string;    // 기존 pending attempt ID (attempt_details 기록용)
  // ✅ attempts 테이블 완전 저장용 추가 필드
  timeSpent?: number;    // 풀이 소요 시간 (초)
  submittedCode?: string; // 제출한 코드 (guided/코드 제출용)
  sessionId?: string;    // 세션 ID (세션 추적용)
}

export interface RecordResult {
  success: boolean;
  xpEarned: number;
  message: string;
  newBadges?: NewBadge[];
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

// ============================================================
// 힌트 요청/응답 타입 (Blank, Puzzle, Guided 공통 구조)
// ============================================================

export interface BlankHintRequest {
  problemId: string;
  blankIndex: number;
  codeTemplate?: string;
  attemptId?: string;  // attempt 추적용
}

export interface BlankHintResult {
  blankIndex: number;
  hintContent: string;
  fromCache: boolean;
}

export interface PuzzleHintRequest {
  problemId: string;
  blockIndex: number;
  blocks?: Array<{ id: string; code: string }>;
  attemptId?: string;  // attempt 추적용
}

export interface PuzzleHintResult {
  blockIndex: number;
  hintContent: string;
  fromCache: boolean;
}

export interface GuidedHintRequest {
  problemId: string;
  stepIndex: number;
  steps?: Array<unknown>;
  attemptId?: string;  // attempt 추적용
}

export interface GuidedHintResult {
  stepIndex: number;
  hintContent: string;
  fromCache: boolean;
}

// ============================================================
// Start Practice (Attempt Tracking)
// ============================================================

export interface StartPracticeRequest {
  problemId: string;
  problemType: 'blank' | 'puzzle' | 'guided';
  difficulty?: string;
  problemName?: string;
  topics?: string[];
}

export interface StartPracticeResult {
  attemptId: string;
  startedAt: string;
  message: string;
  sessionId?: string;  // 세션 추적용 ID
}

// ============================================================
// Session Tracking
// ============================================================

export interface SessionHeartbeatRequest {
  sessionId: string;
  hintsUsed?: number;
  attemptCount?: number;
}

export interface SessionHeartbeatResult {
  success: boolean;
  sessionStatus: 'active' | 'expired' | 'abandoned';
  timeSpent?: number;
  error?: string;
}

export interface SessionEndRequest {
  sessionId: string;
  endType: 'complete' | 'skip' | 'abandon';
  reason?: string;
  isCorrect?: boolean;
  score?: number;
}

export interface SessionEndResult {
  success: boolean;
  sessionId: string;
  status: 'completed' | 'skipped' | 'abandoned';
  timeSpent: number;
  hintsUsed: number;
  attemptCount: number;
  error?: string;
}

export const practiceApi = {
  /**
   * Start practice session - creates pending attempt
   */
  async startPractice(request: StartPracticeRequest): Promise<StartPracticeResult> {
    const response = await api.post<{
      attempt_id: string;
      started_at: string;
      message: string;
      session_id?: string;
    }>('/practice/start', {
      problem_id: request.problemId,
      problem_type: request.problemType,
      difficulty: request.difficulty,
      problem_name: request.problemName,
      topics: request.topics,
    });
    if (response.error) throw new Error(response.error.message);
    return {
      attemptId: response.data!.attempt_id,
      startedAt: response.data!.started_at,
      message: response.data!.message,
      sessionId: response.data!.session_id,
    };
  },

  /**
   * Send session heartbeat to keep session alive
   */
  async sessionHeartbeat(request: SessionHeartbeatRequest): Promise<SessionHeartbeatResult> {
    const response = await api.post<{
      success: boolean;
      session_status: 'active' | 'expired' | 'abandoned';
      time_spent?: number;
      error?: string;
    }>('/practice/session/heartbeat', {
      session_id: request.sessionId,
      hints_used: request.hintsUsed,
      attempt_count: request.attemptCount,
    });
    if (response.error) throw new Error(response.error.message);
    return {
      success: response.data!.success,
      sessionStatus: response.data!.session_status,
      timeSpent: response.data!.time_spent,
      error: response.data!.error,
    };
  },

  /**
   * End session (complete, skip, or abandon)
   */
  async sessionEnd(request: SessionEndRequest): Promise<SessionEndResult> {
    const response = await api.post<{
      success: boolean;
      session_id: string;
      status: 'completed' | 'skipped' | 'abandoned';
      time_spent: number;
      hints_used: number;
      attempt_count: number;
      error?: string;
    }>('/practice/session/end', {
      session_id: request.sessionId,
      end_type: request.endType,
      reason: request.reason,
      is_correct: request.isCorrect,
      score: request.score,
    });
    if (response.error) throw new Error(response.error.message);
    return {
      success: response.data!.success,
      sessionId: response.data!.session_id,
      status: response.data!.status,
      timeSpent: response.data!.time_spent,
      hintsUsed: response.data!.hints_used,
      attemptCount: response.data!.attempt_count,
      error: response.data!.error,
    };
  },

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
    const response = await api.post<{
      results: Record<string, boolean>;
      all_correct: boolean;
      xp_earned: number;
      new_badges?: Array<{ code: string; name: string; icon_url?: string; rarity: string }>;
    }>('/practice/submit/blank', {
      problem_id: submission.problemId,
      answers: submission.answers,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      results: data.results,
      allCorrect: data.all_correct,
      xpEarned: data.xp_earned,
      newBadges: data.new_badges?.map(b => ({
        code: b.code,
        name: b.name,
        iconUrl: b.icon_url,
        rarity: b.rarity,
      })),
    };
  },

  /**
   * Submit puzzle (Parsons Problem) answer
   */
  async submitPuzzle(submission: PuzzleSubmission): Promise<PuzzleResult> {
    const response = await api.post<{
      is_correct: boolean;
      results: Record<string, boolean>;
      xp_earned: number;
      new_badges?: Array<{ code: string; name: string; icon_url?: string; rarity: string }>;
    }>('/practice/submit/puzzle', {
      problem_id: submission.problemId,
      block_order: submission.blockOrder,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      isCorrect: data.is_correct,
      results: data.results,
      xpEarned: data.xp_earned,
      newBadges: data.new_badges?.map(b => ({
        code: b.code,
        name: b.name,
        iconUrl: b.icon_url,
        rarity: b.rarity,
      })),
    };
  },

  /**
   * Record problem solve for XP and grass (simple record without validation)
   */
  async recordSolve(submission: RecordSubmission & { difficulty?: string }): Promise<RecordResult> {
    const response = await api.post<{
      success: boolean;
      xp_earned: number;
      message: string;
      new_badges?: Array<{ code: string; name: string; icon_url?: string; rarity: string }>;
    }>('/practice/submit/record', {
      problem_id: submission.problemId,
      base_problem_id: submission.baseProblemId,
      problem_type: submission.problemType,
      difficulty: submission.difficulty,
      is_correct: submission.isCorrect,
      xp_earned: submission.xpEarned,
      problem_name: submission.problemName,
      hints_used: submission.hintsUsed,  // 힌트 사용 횟수
      topics: submission.topics,  // 문제 주제/태그
      attempt_id: submission.attemptId,  // 기존 pending attempt ID
      // ✅ attempts 테이블 완전 저장용 추가 필드
      time_spent: submission.timeSpent,  // 풀이 소요 시간 (초)
      submitted_code: submission.submittedCode,  // 제출한 코드
      session_id: submission.sessionId,  // 세션 ID
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      xpEarned: data.xp_earned,
      message: data.message,
      newBadges: data.new_badges?.map(b => ({
        code: b.code,
        name: b.name,
        iconUrl: b.icon_url,
        rarity: b.rarity,
      })),
    };
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

  /**
   * Get blank hint (역할/이유 설명만, 정답 없음)
   */
  async getBlankHint(request: BlankHintRequest): Promise<BlankHintResult> {
    const response = await api.post<{
      blank_index: number;
      hint_content: string;
      from_cache: boolean;
    }>('/practice/hint/blank', {
      problem_id: request.problemId,
      blank_index: request.blankIndex,
      code_template: request.codeTemplate,
      attempt_id: request.attemptId,  // attempt 추적용
    });
    if (response.error) throw new Error(response.error.message);
    return {
      blankIndex: response.data!.blank_index,
      hintContent: response.data!.hint_content,
      fromCache: response.data!.from_cache,
    };
  },

  /**
   * Get puzzle hint (블록 역할 설명, 순서 알려주지 않음)
   */
  async getPuzzleHint(request: PuzzleHintRequest): Promise<PuzzleHintResult> {
    const response = await api.post<{
      block_index: number;
      hint_content: string;
      from_cache: boolean;
    }>('/practice/hint/puzzle', {
      problem_id: request.problemId,
      block_index: request.blockIndex,
      blocks: request.blocks,
      attempt_id: request.attemptId,  // attempt 추적용
    });
    if (response.error) throw new Error(response.error.message);
    return {
      blockIndex: response.data!.block_index,
      hintContent: response.data!.hint_content,
      fromCache: response.data!.from_cache,
    };
  },

  /**
   * Get guided hint (단계별 도움, 소크라테스식)
   */
  async getGuidedHint(request: GuidedHintRequest): Promise<GuidedHintResult> {
    const response = await api.post<{
      step_index: number;
      hint_content: string;
      from_cache: boolean;
    }>('/practice/hint/guided', {
      problem_id: request.problemId,
      step_index: request.stepIndex,
      steps: request.steps,
      attempt_id: request.attemptId,  // attempt 추적용
    });
    if (response.error) throw new Error(response.error.message);
    return {
      stepIndex: response.data!.step_index,
      hintContent: response.data!.hint_content,
      fromCache: response.data!.from_cache,
    };
  },
};
