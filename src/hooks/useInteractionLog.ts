/**
 * useInteractionLog Hook
 *
 * CF 추천 시스템을 위한 사용자-문제 상호작용 로그 수집
 * - 문제 조회, 시도, 풀이, 스킵, 북마크 등 추적
 * - 백그라운드로 비동기 전송 (UX 영향 없음)
 */

import { useCallback, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';

// ============================================================
// Types
// ============================================================

export type ActionType =
  | 'view'           // 문제 조회
  | 'attempt'        // 풀이 시도
  | 'solve'          // 풀이 완료
  | 'skip'           // 건너뛰기
  | 'bookmark'       // 북마크
  | 'hint_request'   // 힌트 요청
  | 'code_submit';   // 코드 제출

export type SourceType =
  | 'rag_search'      // RAG 검색 결과
  | 'recommendation'  // CF 추천
  | 'browse'          // 직접 탐색
  | 'similar_code'    // 비슷한 코드 검색
  | 'intent_chat'     // 챗봇 추천
  | 'random'          // 랜덤 추천
  | 'topic_filter';   // 주제 필터

export interface InteractionData {
  problemId: string;
  actionType: ActionType;
  isCorrect?: boolean;
  timeSpentSeconds?: number;
  attemptCount?: number;
  hintUsedCount?: number;
  problemDifficulty?: string;
  problemTopics?: string[];
  source?: SourceType;
  metadata?: Record<string, unknown>;
}

interface LogEntry extends InteractionData {
  userId: string;
  sessionId: string;
  userLevel?: string;
  timestamp: number;
}

// ============================================================
// Constants
// ============================================================

const BATCH_SIZE = 10;
const FLUSH_INTERVAL = 30000; // 30초마다 flush
const STORAGE_KEY = 'codefill_interaction_queue';

// ============================================================
// Supabase Client (direct insert)
// ============================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

const getSupabaseClient = () => {
  if (!supabaseUrl || !supabaseAnonKey) return null;
  return createClient(supabaseUrl, supabaseAnonKey);
};

// ============================================================
// Hook
// ============================================================

export function useInteractionLog(userId?: string, userLevel?: string) {
  const queueRef = useRef<LogEntry[]>([]);
  const sessionIdRef = useRef<string>(generateSessionId());
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const viewStartTimeRef = useRef<Map<string, number>>(new Map());

  // Generate session ID
  function generateSessionId(): string {
    if (typeof window === 'undefined') return '';
    let sessionId = sessionStorage.getItem('codefill_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      sessionStorage.setItem('codefill_session_id', sessionId);
    }
    return sessionId;
  }

  // Load queue from localStorage on mount
  const loadQueue = useCallback(() => {
    if (typeof window === 'undefined') return;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        queueRef.current = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load interaction queue:', e);
    }
  }, []);

  // Save queue to localStorage
  const saveQueue = useCallback(() => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(queueRef.current));
    } catch (e) {
      console.error('Failed to save interaction queue:', e);
    }
  }, []);

  // Flush queue to Supabase
  const flushQueue = useCallback(async () => {
    if (!userId || queueRef.current.length === 0) return;

    const supabase = getSupabaseClient();
    if (!supabase) return;

    const entries = [...queueRef.current];
    queueRef.current = [];
    saveQueue();

    try {
      const { error } = await supabase
        .from('user_problem_interactions')
        .insert(
          entries.map((entry) => ({
            user_id: entry.userId,
            problem_id: entry.problemId,
            action_type: entry.actionType,
            is_correct: entry.isCorrect,
            time_spent_seconds: entry.timeSpentSeconds,
            attempt_count: entry.attemptCount,
            hint_used_count: entry.hintUsedCount,
            problem_difficulty: entry.problemDifficulty,
            problem_topics: entry.problemTopics,
            source: entry.source,
            session_id: entry.sessionId,
            user_level: entry.userLevel,
            metadata: entry.metadata || {},
          }))
        );

      if (error) {
        console.error('Failed to flush interactions:', error);
        // 실패 시 다시 큐에 추가
        queueRef.current = [...entries, ...queueRef.current];
        saveQueue();
      }
    } catch (e) {
      console.error('Failed to flush interactions:', e);
      queueRef.current = [...entries, ...queueRef.current];
      saveQueue();
    }
  }, [userId, saveQueue]);

  // Add to queue
  const addToQueue = useCallback(
    (entry: LogEntry) => {
      queueRef.current.push(entry);
      saveQueue();

      // Batch size 도달 시 flush
      if (queueRef.current.length >= BATCH_SIZE) {
        flushQueue();
      }
    },
    [saveQueue, flushQueue]
  );

  // Start periodic flush
  const startPeriodicFlush = useCallback(() => {
    if (timerRef.current) return;
    timerRef.current = setInterval(flushQueue, FLUSH_INTERVAL);
  }, [flushQueue]);

  // Stop periodic flush
  const stopPeriodicFlush = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // ============================================================
  // Public API
  // ============================================================

  /**
   * 상호작용 로그 기록
   */
  const logInteraction = useCallback(
    (data: InteractionData) => {
      if (!userId) return;

      const entry: LogEntry = {
        ...data,
        userId,
        sessionId: sessionIdRef.current,
        userLevel,
        timestamp: Date.now(),
      };

      addToQueue(entry);
    },
    [userId, userLevel, addToQueue]
  );

  /**
   * 문제 조회 시작 (시간 측정용)
   */
  const startViewProblem = useCallback((problemId: string) => {
    viewStartTimeRef.current.set(problemId, Date.now());
  }, []);

  /**
   * 문제 조회 완료 (시간 포함 로그)
   */
  const endViewProblem = useCallback(
    (
      problemId: string,
      options?: {
        problemDifficulty?: string;
        problemTopics?: string[];
        source?: SourceType;
      }
    ) => {
      const startTime = viewStartTimeRef.current.get(problemId);
      const timeSpent = startTime
        ? Math.round((Date.now() - startTime) / 1000)
        : undefined;

      viewStartTimeRef.current.delete(problemId);

      logInteraction({
        problemId,
        actionType: 'view',
        timeSpentSeconds: timeSpent,
        ...options,
      });
    },
    [logInteraction]
  );

  /**
   * 문제 풀이 시도
   */
  const logAttempt = useCallback(
    (
      problemId: string,
      options?: {
        attemptCount?: number;
        hintUsedCount?: number;
        problemDifficulty?: string;
        problemTopics?: string[];
        source?: SourceType;
      }
    ) => {
      logInteraction({
        problemId,
        actionType: 'attempt',
        ...options,
      });
    },
    [logInteraction]
  );

  /**
   * 문제 풀이 완료
   */
  const logSolve = useCallback(
    (
      problemId: string,
      isCorrect: boolean,
      options?: {
        timeSpentSeconds?: number;
        attemptCount?: number;
        hintUsedCount?: number;
        problemDifficulty?: string;
        problemTopics?: string[];
        source?: SourceType;
      }
    ) => {
      // view 시간도 포함
      const startTime = viewStartTimeRef.current.get(problemId);
      const totalTime = startTime
        ? Math.round((Date.now() - startTime) / 1000)
        : options?.timeSpentSeconds;

      viewStartTimeRef.current.delete(problemId);

      logInteraction({
        problemId,
        actionType: 'solve',
        isCorrect,
        timeSpentSeconds: totalTime,
        ...options,
      });
    },
    [logInteraction]
  );

  /**
   * 문제 스킵
   */
  const logSkip = useCallback(
    (
      problemId: string,
      options?: {
        timeSpentSeconds?: number;
        source?: SourceType;
      }
    ) => {
      const startTime = viewStartTimeRef.current.get(problemId);
      const timeSpent = startTime
        ? Math.round((Date.now() - startTime) / 1000)
        : options?.timeSpentSeconds;

      viewStartTimeRef.current.delete(problemId);

      logInteraction({
        problemId,
        actionType: 'skip',
        timeSpentSeconds: timeSpent,
        ...options,
      });
    },
    [logInteraction]
  );

  /**
   * 북마크
   */
  const logBookmark = useCallback(
    (problemId: string, source?: SourceType) => {
      logInteraction({
        problemId,
        actionType: 'bookmark',
        source,
      });
    },
    [logInteraction]
  );

  /**
   * 힌트 요청
   */
  const logHintRequest = useCallback(
    (problemId: string, hintLevel: number) => {
      logInteraction({
        problemId,
        actionType: 'hint_request',
        metadata: { hintLevel },
      });
    },
    [logInteraction]
  );

  /**
   * 즉시 flush (페이지 이탈 시)
   */
  const flush = useCallback(() => {
    flushQueue();
  }, [flushQueue]);

  return {
    // Core
    logInteraction,
    flush,

    // Convenience methods
    startViewProblem,
    endViewProblem,
    logAttempt,
    logSolve,
    logSkip,
    logBookmark,
    logHintRequest,

    // Lifecycle
    startPeriodicFlush,
    stopPeriodicFlush,
    loadQueue,
  };
}

export default useInteractionLog;
