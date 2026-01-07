/**
 * Practice Session Hook
 *
 * 풀이 상태를 localStorage에 저장하여 새로고침 시에도 유지
 *
 * 저장되는 상태:
 * - problem: 현재 풀고 있는 문제
 * - blankAnswers: 빈칸 채우기 답변
 * - previousHints: 사용한 힌트
 * - solveStartTime: 풀이 시작 시간
 * - attemptCount: 시도 횟수
 * - attemptId: attempt 추적 ID
 * - chatSessionId: 채팅 세션 ID
 */

import { useState, useEffect, useCallback } from 'react';
import type { ConvertedProblem } from '@/lib/dataTypes';

const STORAGE_KEY = 'codefill_practice_session';
const SESSION_EXPIRY_MS = 30 * 60 * 1000; // 30분

interface PracticeSessionData {
  problem: ConvertedProblem | null;
  blankAnswers: Record<string, string>;
  previousHints: string[];
  solveStartTime: string | null; // ISO string
  attemptCount: number;
  attemptId: string | null;
  chatSessionId: string | null;
  savedAt: number; // timestamp
}

interface UsePracticeSessionReturn {
  // State
  problem: ConvertedProblem | null;
  blankAnswers: Record<string, string>;
  previousHints: string[];
  solveStartTime: Date | null;
  attemptCount: number;
  attemptId: string | null;
  chatSessionId: string | null;
  isRestored: boolean;

  // Setters
  setProblem: (problem: ConvertedProblem | null) => void;
  setBlankAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  setPreviousHints: React.Dispatch<React.SetStateAction<string[]>>;
  setSolveStartTime: (time: Date | null) => void;
  setAttemptCount: React.Dispatch<React.SetStateAction<number>>;
  setAttemptId: (id: string | null) => void;
  setChatSessionId: (id: string | null) => void;

  // Actions
  resetSession: () => void;
  clearSavedSession: () => void;
}

export function usePracticeSession(): UsePracticeSessionReturn {
  const [problem, setProblemState] = useState<ConvertedProblem | null>(null);
  const [blankAnswers, setBlankAnswers] = useState<Record<string, string>>({});
  const [previousHints, setPreviousHints] = useState<string[]>([]);
  const [solveStartTime, setSolveStartTimeState] = useState<Date | null>(null);
  const [attemptCount, setAttemptCount] = useState(0);
  const [attemptId, setAttemptIdState] = useState<string | null>(null);
  const [chatSessionId, setChatSessionIdState] = useState<string | null>(null);
  const [isRestored, setIsRestored] = useState(false);

  // localStorage에서 세션 복원
  useEffect(() => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY);
      if (!savedData) {
        setIsRestored(true);
        return;
      }

      const parsed: PracticeSessionData = JSON.parse(savedData);

      // 만료 확인 (30분)
      if (Date.now() - parsed.savedAt > SESSION_EXPIRY_MS) {
        console.log('[PracticeSession] Session expired, clearing');
        localStorage.removeItem(STORAGE_KEY);
        setIsRestored(true);
        return;
      }

      console.log('[PracticeSession] Restoring session:', {
        problemId: parsed.problem?.id,
        blankAnswersCount: Object.keys(parsed.blankAnswers).length,
        hintsCount: parsed.previousHints.length,
        attemptId: parsed.attemptId,
      });

      // 상태 복원
      if (parsed.problem) {
        setProblemState(parsed.problem);
      }
      if (parsed.blankAnswers) {
        setBlankAnswers(parsed.blankAnswers);
      }
      if (parsed.previousHints) {
        setPreviousHints(parsed.previousHints);
      }
      if (parsed.solveStartTime) {
        setSolveStartTimeState(new Date(parsed.solveStartTime));
      }
      if (typeof parsed.attemptCount === 'number') {
        setAttemptCount(parsed.attemptCount);
      }
      if (parsed.attemptId) {
        setAttemptIdState(parsed.attemptId);
      }
      if (parsed.chatSessionId) {
        setChatSessionIdState(parsed.chatSessionId);
      }

      setIsRestored(true);
    } catch (error) {
      console.error('[PracticeSession] Failed to restore:', error);
      localStorage.removeItem(STORAGE_KEY);
      setIsRestored(true);
    }
  }, []);

  // 상태 변경 시 localStorage에 저장
  const saveToStorage = useCallback(() => {
    if (!isRestored) return; // 초기 복원 완료 전에는 저장하지 않음

    try {
      const data: PracticeSessionData = {
        problem,
        blankAnswers,
        previousHints,
        solveStartTime: solveStartTime?.toISOString() || null,
        attemptCount,
        attemptId,
        chatSessionId,
        savedAt: Date.now(),
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('[PracticeSession] Failed to save:', error);
    }
  }, [problem, blankAnswers, previousHints, solveStartTime, attemptCount, attemptId, chatSessionId, isRestored]);

  // 상태 변경 시 저장 (디바운스 적용)
  useEffect(() => {
    if (!isRestored) return;

    const timeoutId = setTimeout(saveToStorage, 300);
    return () => clearTimeout(timeoutId);
  }, [saveToStorage, isRestored]);

  // Wrapped setters that trigger save
  const setProblem = useCallback((newProblem: ConvertedProblem | null) => {
    setProblemState(newProblem);
  }, []);

  const setSolveStartTime = useCallback((time: Date | null) => {
    setSolveStartTimeState(time);
  }, []);

  const setAttemptId = useCallback((id: string | null) => {
    setAttemptIdState(id);
  }, []);

  const setChatSessionId = useCallback((id: string | null) => {
    setChatSessionIdState(id);
  }, []);

  // 세션 초기화
  const resetSession = useCallback(() => {
    setProblemState(null);
    setBlankAnswers({});
    setPreviousHints([]);
    setSolveStartTimeState(null);
    setAttemptCount(0);
    setAttemptIdState(null);
    // chatSessionId는 유지 (대화 히스토리 재사용)
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  // 저장된 세션 삭제 (로그아웃 시 등)
  const clearSavedSession = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setProblemState(null);
    setBlankAnswers({});
    setPreviousHints([]);
    setSolveStartTimeState(null);
    setAttemptCount(0);
    setAttemptIdState(null);
    setChatSessionIdState(null);
  }, []);

  return {
    // State
    problem,
    blankAnswers,
    previousHints,
    solveStartTime,
    attemptCount,
    attemptId,
    chatSessionId,
    isRestored,

    // Setters
    setProblem,
    setBlankAnswers,
    setPreviousHints,
    setSolveStartTime,
    setAttemptCount,
    setAttemptId,
    setChatSessionId,

    // Actions
    resetSession,
    clearSavedSession,
  };
}
