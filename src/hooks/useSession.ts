/**
 * useSession Hook
 *
 * 세션 컨텍스트 관리를 위한 hook
 * - 최근 푼 문제 저장
 * - 현재 풀고 있는 문제 추적
 * - 최근 제안 저장
 */

import { useState, useEffect, useCallback } from 'react';

// ============================================================
// Types
// ============================================================

export interface SolvedProblem {
  id: string;
  name: string;
  code: string;
  language: string;
  difficulty?: string;
  topics?: string[];
  solvedAt: string;
}

export interface CurrentProblem {
  id: string;
  name: string;
  description?: string;
  difficulty?: string;
  topics?: string[];
  startedAt: string;
}

export interface SessionContext {
  last_solved_problem: SolvedProblem | null;
  current_problem: CurrentProblem | null;
  last_suggestion: string | null;
  recent_problems: SolvedProblem[];
}

// Storage keys
const STORAGE_KEYS = {
  LAST_SOLVED: 'codefill_last_solved_problem',
  CURRENT_PROBLEM: 'codefill_current_problem',
  LAST_SUGGESTION: 'codefill_last_suggestion',
  RECENT_PROBLEMS: 'codefill_recent_problems',
} as const;

const MAX_RECENT_PROBLEMS = 10;

// ============================================================
// Hook
// ============================================================

export function useSession() {
  const [lastSolvedProblem, setLastSolvedProblemState] = useState<SolvedProblem | null>(null);
  const [currentProblem, setCurrentProblemState] = useState<CurrentProblem | null>(null);
  const [lastSuggestion, setLastSuggestionState] = useState<string | null>(null);
  const [recentProblems, setRecentProblemsState] = useState<SolvedProblem[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const storedLastSolved = localStorage.getItem(STORAGE_KEYS.LAST_SOLVED);
      const storedCurrent = localStorage.getItem(STORAGE_KEYS.CURRENT_PROBLEM);
      const storedSuggestion = localStorage.getItem(STORAGE_KEYS.LAST_SUGGESTION);
      const storedRecent = localStorage.getItem(STORAGE_KEYS.RECENT_PROBLEMS);

      if (storedLastSolved) {
        setLastSolvedProblemState(JSON.parse(storedLastSolved));
      }
      if (storedCurrent) {
        setCurrentProblemState(JSON.parse(storedCurrent));
      }
      if (storedSuggestion) {
        setLastSuggestionState(storedSuggestion);
      }
      if (storedRecent) {
        setRecentProblemsState(JSON.parse(storedRecent));
      }
    } catch (error) {
      console.error('Failed to load session from localStorage:', error);
    }

    setIsLoaded(true);
  }, []);

  // 문제 풀이 완료 시 호출
  const markProblemSolved = useCallback((problem: Omit<SolvedProblem, 'solvedAt'>) => {
    const solvedProblem: SolvedProblem = {
      ...problem,
      solvedAt: new Date().toISOString(),
    };

    setLastSolvedProblemState(solvedProblem);
    localStorage.setItem(STORAGE_KEYS.LAST_SOLVED, JSON.stringify(solvedProblem));

    // Add to recent problems (최신 순, 최대 10개)
    setRecentProblemsState((prev) => {
      const filtered = prev.filter((p) => p.id !== problem.id);
      const updated = [solvedProblem, ...filtered].slice(0, MAX_RECENT_PROBLEMS);
      localStorage.setItem(STORAGE_KEYS.RECENT_PROBLEMS, JSON.stringify(updated));
      return updated;
    });

    // Clear current problem
    setCurrentProblemState(null);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_PROBLEM);
  }, []);

  // 문제 풀이 시작 시 호출
  const startProblem = useCallback((problem: Omit<CurrentProblem, 'startedAt'>) => {
    const currentProblem: CurrentProblem = {
      ...problem,
      startedAt: new Date().toISOString(),
    };

    setCurrentProblemState(currentProblem);
    localStorage.setItem(STORAGE_KEYS.CURRENT_PROBLEM, JSON.stringify(currentProblem));
  }, []);

  // 현재 문제 취소/초기화
  const clearCurrentProblem = useCallback(() => {
    setCurrentProblemState(null);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_PROBLEM);
  }, []);

  // 마지막 제안 저장
  const setLastSuggestion = useCallback((suggestion: string) => {
    setLastSuggestionState(suggestion);
    localStorage.setItem(STORAGE_KEYS.LAST_SUGGESTION, suggestion);
  }, []);

  // 마지막 제안 클리어
  const clearLastSuggestion = useCallback(() => {
    setLastSuggestionState(null);
    localStorage.removeItem(STORAGE_KEYS.LAST_SUGGESTION);
  }, []);

  // API 요청용 세션 컨텍스트 생성
  const getSessionContext = useCallback((): SessionContext => {
    return {
      last_solved_problem: lastSolvedProblem,
      current_problem: currentProblem,
      last_suggestion: lastSuggestion,
      recent_problems: recentProblems,
    };
  }, [lastSolvedProblem, currentProblem, lastSuggestion, recentProblems]);

  // 전체 세션 초기화
  const clearSession = useCallback(() => {
    setLastSolvedProblemState(null);
    setCurrentProblemState(null);
    setLastSuggestionState(null);
    setRecentProblemsState([]);

    localStorage.removeItem(STORAGE_KEYS.LAST_SOLVED);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_PROBLEM);
    localStorage.removeItem(STORAGE_KEYS.LAST_SUGGESTION);
    localStorage.removeItem(STORAGE_KEYS.RECENT_PROBLEMS);
  }, []);

  return {
    // State
    lastSolvedProblem,
    currentProblem,
    lastSuggestion,
    recentProblems,
    isLoaded,

    // Actions
    markProblemSolved,
    startProblem,
    clearCurrentProblem,
    setLastSuggestion,
    clearLastSuggestion,
    getSessionContext,
    clearSession,
  };
}

export default useSession;
