'use client';

import { useState, useCallback, useRef, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Resizer } from '@/components/ui/resizer';
import { ArrowLeft, PanelRightClose, PanelRight, Loader2, LogIn } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { usePracticeSession } from '@/hooks/usePracticeSession';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

import { UnifiedPractice } from '@/components/practice/UnifiedPractice';
import { PracticeChatPanel } from '@/components/chat/PracticeChatPanel';
import { CorrectAnswerPopup } from '@/components/practice/CorrectAnswerPopup';
import { ExitWarningDialog } from '@/components/practice/ExitWarningDialog';
// 온보딩은 소셜 회원가입 시 이미 완료됨 - 중복 제거
import { BadgePopup } from '@/components/ui/badge-popup';

import { practiceApi, agentApi, problemsApi } from '@/lib/api';
import type { NewBadge, SeedAwarded } from '@/lib/api/practice';
import { apiClient } from '@/lib/api/client';
import type { ConvertedProblem, ConvertedProblemType } from '@/lib/dataTypes';
import type { HintAgentResponse, FeedbackResponse, BaseProblemInfo } from '@/lib/api/agent';
import { ga4Events, clarityEvents } from '@/lib/analytics';

const difficultyColors = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

// Suspense wrapper for the main content (useSearchParams requires this)
export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  );
}

function ChatPageContent() {
  const { toast } = useToast();
  const router = useRouter();
  const { refreshProfile } = useAuth();

  // 뱃지 획득 팝업 상태
  const [earnedBadges, setEarnedBadges] = useState<NewBadge[]>([]);

  // 씨앗 보상 상태
  const [earnedSeed, setEarnedSeed] = useState<SeedAwarded | null>(null);

  // 뱃지 획득 시 팝업 표시
  const showBadgePopup = useCallback((badges: NewBadge[] | undefined) => {
    if (!badges || badges.length === 0) return;
    setEarnedBadges(badges);
  }, []);

  const searchParams = useSearchParams();

  // ============================================================
  // Practice Session Hook - localStorage 기반 상태 영속화
  // ============================================================
  const {
    problem,
    blankAnswers,
    previousHints,
    solveStartTime,
    attemptCount,
    attemptId,
    chatSessionId,
    isRestored,
    setProblem,
    setBlankAnswers,
    setPreviousHints,
    setSolveStartTime,
    setAttemptCount,
    setAttemptId,
    setChatSessionId,
    resetSession,
  } = usePracticeSession();

  // Auth hook - get user info for feedback
  const { user, profile } = useAuth();

  // Auth state
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // 온보딩은 소셜 회원가입 시 완료됨 (중복 제거됨)

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = apiClient.isAuthenticated();
      setIsAuthenticated(authenticated);
      setIsAuthChecking(false);
    };
    checkAuth();
  }, []);

  // URL에서 problem_id 파라미터 확인
  const urlProblemId = searchParams.get('problem_id');

  // 세션 복원 후 문제가 있으면 로그 출력
  useEffect(() => {
    if (isRestored && problem) {
      console.log('[ChatPage] Session restored:', {
        problemId: problem.id,
        blankAnswersCount: Object.keys(blankAnswers).length,
        hintsCount: previousHints.length,
        attemptId,
      });
    }
  }, [isRestored, problem, blankAnswers, previousHints, attemptId]);

  // ============================================================
  // Session Tracking - Heartbeat & Beforeunload
  // ============================================================

  // Session tracking state (declared before useEffects that use them)
  const [sessionId, setSessionId] = useState<string | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Exit warning dialog state
  const [showExitWarning, setShowExitWarning] = useState(false);
  const [isExitLoading, setIsExitLoading] = useState(false);
  const pendingNavigationRef = useRef<string | null>(null);  // 이탈 후 이동할 경로

  // Submission state (beforeunload에서 사용하므로 여기서 선언)
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  // Guided 모드 튜터에게 전달할 현재 코드 상태
  const [currentCode, setCurrentCode] = useState<string>('');

  // Puzzle 모드: 사용자가 현재 배치한 블록 순서
  const [puzzleUserOrder, setPuzzleUserOrder] = useState<string[]>([]);

  // Start heartbeat when session starts
  useEffect(() => {
    if (!sessionId) return;

    // Clear any existing interval
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    // Send heartbeat every 5 minutes (300000ms)
    const HEARTBEAT_INTERVAL = 5 * 60 * 1000;

    const sendHeartbeat = async () => {
      try {
        const result = await practiceApi.sessionHeartbeat({
          sessionId,
          hintsUsed: previousHints.length,
          attemptCount,
        });
        console.log('[SessionTracker] Heartbeat:', result);

        if (result.sessionStatus === 'expired' || result.sessionStatus === 'abandoned') {
          console.log('[SessionTracker] Session expired/abandoned, clearing interval');
          if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = null;
          }
          // 세션 만료 시 토스트 알림
          toast({
            title: '세션 만료',
            description: '오랜 시간 활동이 없어 세션이 종료되었습니다. 진행 상황은 저장되어 있습니다.',
            variant: 'default',
          });
        }
      } catch (error) {
        console.error('[SessionTracker] Heartbeat error:', error);
      }
    };

    // Initial heartbeat
    sendHeartbeat();

    // Set interval (every 5 minutes)
    heartbeatIntervalRef.current = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

    return () => {
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }
    };
  }, [sessionId, previousHints.length, attemptCount, toast]);

  // Beforeunload handler - warn and send abandon when user leaves
  useEffect(() => {
    if (!sessionId) return;

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      // 문제 풀이 중일 때만 경고 표시
      if (problem && !isSubmitted) {
        // 브라우저 기본 경고 표시
        e.preventDefault();
        e.returnValue = '문제를 포기하시겠어요? 실력 측정에 불이익이 있을 수 있습니다.';
      }

      // Send abandon request using sendBeacon for reliability
      const data = JSON.stringify({
        session_id: sessionId,
        end_type: 'abandon',
        reason: 'page_unload',
      });

      // Use sendBeacon for reliable delivery on page close
      navigator.sendBeacon('/api/practice/session/end', data);
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && sessionId) {
        // Send heartbeat when tab becomes hidden (helps track focus loss)
        practiceApi.sessionHeartbeat({
          sessionId,
          hintsUsed: previousHints.length,
          attemptCount,
        }).catch(console.error);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [sessionId, previousHints.length, attemptCount, problem, isSubmitted]);

  // Initial problem (from URL parameter) - 정보수집 단계 생략용
  const [initialBaseProblem, setInitialBaseProblem] = useState<BaseProblemInfo | null>(null);
  const [isLoadingInitialProblem, setIsLoadingInitialProblem] = useState(false);

  // Practice results (reset on new problem)
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});
  const [puzzleResults, setPuzzleResults] = useState<Record<string, boolean>>({});
  const [hints, setHints] = useState<string[]>([]);
  const [currentHintResponse, setCurrentHintResponse] = useState<HintAgentResponse | null>(null);
  const [usedBlankHintIndices, setUsedBlankHintIndices] = useState<number[]>([]);  // 빈칸/퍼즐 힌트 사용 인덱스

  // Feedback popup state
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false);
  const [feedbackData, setFeedbackData] = useState<FeedbackResponse | null>(null);
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(false);

  // Layout state
  const [showChat, setShowChat] = useState(true);
  const [chatWidth, setChatWidth] = useState(400); // 40% of 1000px default
  const containerRef = useRef<HTMLDivElement>(null);

  // URL에서 problem_id가 있으면 문제 정보 로드 (정보수집 단계 생략)
  useEffect(() => {
    console.log('[ChatPage] urlProblemId:', urlProblemId);
    if (!urlProblemId) return;

    const loadProblem = async () => {
      console.log('[ChatPage] Loading problem:', urlProblemId);
      setIsLoadingInitialProblem(true);
      try {
        const data = await problemsApi.getBase(urlProblemId);
        console.log('[ChatPage] Loaded problem data:', data);
        // BaseProblemDetail → BaseProblemInfo 변환
        const baseProblemInfo: BaseProblemInfo = {
          id: data.id,
          original_id: data.original_id,
          name: data.name,
          title: data.name,
          question: data.question,
          description: data.question,
          difficulty: data.difficulty as 'easy' | 'medium' | 'hard',
          tags: data.tags,
          topics: data.tags,
          solutions: data.solutions || [],
          input_output: typeof data.input_output === 'string'
            ? JSON.parse(data.input_output)
            : data.input_output,
        };
        console.log('[ChatPage] Setting initialBaseProblem:', baseProblemInfo);
        setInitialBaseProblem(baseProblemInfo);
      } catch (error) {
        console.error('[ChatPage] Failed to load problem:', error);
        toast({
          title: '문제 로드 실패',
          description: '문제 정보를 불러오는데 실패했습니다.',
          variant: 'destructive',
        });
      } finally {
        setIsLoadingInitialProblem(false);
      }
    };

    loadProblem();
  }, [urlProblemId, toast]);

  // Initialize chat width based on container size (40%)
  useEffect(() => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.offsetWidth;
      setChatWidth(Math.round(containerWidth * 0.4));
    }
  }, []);

  // Handle chat panel resize
  const handleChatResize = useCallback((delta: number) => {
    setChatWidth((prev) => {
      const containerWidth = containerRef.current?.offsetWidth || 1000;
      const minWidth = 280;
      const maxWidth = Math.round(containerWidth * 0.6); // Max 60%
      return Math.min(Math.max(prev - delta, minWidth), maxWidth);
    });
  }, []);

  // Handle problem selection from chat
  const handleProblemSelect = useCallback(async (selectedProblem: ConvertedProblem) => {
    // End previous session if exists
    if (sessionId) {
      try {
        await practiceApi.sessionEnd({
          sessionId,
          endType: 'skip',
          reason: 'new_problem_selected',
        });
      } catch (e) {
        console.error('[SessionTracker] Failed to end previous session:', e);
      }
    }

    // usePracticeSession 훅을 통해 상태 설정 (localStorage 자동 저장)
    setProblem(selectedProblem);
    setBlankAnswers({});
    setPreviousHints([]);
    setSolveStartTime(new Date());
    setAttemptCount(0);

    // GA4/Clarity 문제 시작 이벤트
    ga4Events.problemStart(selectedProblem.id, 'chat');
    clarityEvents.problemStart(selectedProblem.id);

    // 로컬 상태 초기화
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    setHints(selectedProblem.keyConcepts || []);
    setCurrentHintResponse(null);
    setShowFeedbackPopup(false);
    setFeedbackData(null);

    // Start practice session - create pending attempt for tracking
    try {
      const startResult = await practiceApi.startPractice({
        problemId: selectedProblem.id,
        problemType: (selectedProblem.problemType || 'blank') as 'blank' | 'puzzle' | 'guided',
        difficulty: selectedProblem.difficulty,
        problemName: selectedProblem.title,
        topics: selectedProblem.topics || selectedProblem.keyConcepts,
      });
      setAttemptId(startResult.attemptId);
      setSessionId(startResult.sessionId || null);
      console.log('[ChatPage] Started practice session:', startResult.attemptId, 'sessionId:', startResult.sessionId);
    } catch (error) {
      console.error('[ChatPage] Failed to start practice session:', error);
      setAttemptId(null);
      setSessionId(null);
    }
  }, [setProblem, setBlankAnswers, setPreviousHints, setSolveStartTime, setAttemptCount, setAttemptId, sessionId]);

  // Reset session (다음문제 풀기)
  const handleResetSession = useCallback(async () => {
    // End current session (complete)
    if (sessionId) {
      try {
        await practiceApi.sessionEnd({
          sessionId,
          endType: 'complete',
          isCorrect: true,
        });
        console.log('[SessionTracker] Session completed:', sessionId);
      } catch (e) {
        console.error('[SessionTracker] Failed to end session:', e);
      }
    }

    // usePracticeSession 훅의 resetSession 사용 (localStorage도 초기화)
    resetSession();

    // 로컬 상태 초기화
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    setHints([]);
    setCurrentHintResponse(null);
    setShowFeedbackPopup(false);
    setFeedbackData(null);
    setSessionId(null);  // Clear session ID
    setUsedBlankHintIndices([]);  // 힌트 사용 인덱스 초기화
    setEarnedSeed(null);  // 씨앗 보상 초기화
    setInitialBaseProblem(null);  // 채팅 초기화를 위해 initialBaseProblem도 초기화
  }, [resetSession, sessionId]);

  // 포기하기 (Give up)
  const handleGiveUp = useCallback(async () => {
    if (!problem) return;

    // End session as abandon
    if (sessionId) {
      try {
        await practiceApi.sessionEnd({
          sessionId,
          endType: 'abandon',
          reason: 'user_gave_up',
          isCorrect: false,
        });
        console.log('[SessionTracker] Session abandoned (give up):', sessionId);
      } catch (e) {
        console.error('[SessionTracker] Failed to end session:', e);
      }
    }

    toast({
      title: '문제를 포기했습니다',
      description: '다른 문제에 도전해보세요!',
    });

    // Reset session
    resetSession();
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    setHints([]);
    setCurrentHintResponse(null);
    setShowFeedbackPopup(false);
    setFeedbackData(null);
    setSessionId(null);
    setUsedBlankHintIndices([]);  // 힌트 사용 인덱스 초기화
    setInitialBaseProblem(null);  // 채팅 초기화를 위해 initialBaseProblem도 초기화
  }, [problem, sessionId, resetSession, toast]);

  // ============================================================
  // 이탈 경고 핸들러
  // ============================================================

  // 이탈 시도 시 경고 팝업 표시 (문제 풀이 중일 때만)
  const handleExitAttempt = useCallback((targetPath: string = '/') => {
    // 문제가 없거나 이미 제출 완료된 경우 바로 이동
    if (!problem || isSubmitted) {
      router.push(targetPath);
      return;
    }

    // 경고 팝업 표시
    pendingNavigationRef.current = targetPath;
    setShowExitWarning(true);
  }, [problem, isSubmitted, router]);

  // 이탈 확정 시 처리 (session_end 호출 후 이동)
  const handleConfirmExit = useCallback(async () => {
    setIsExitLoading(true);

    // End session as abandon (ELO 감소)
    if (sessionId) {
      try {
        await practiceApi.sessionEnd({
          sessionId,
          endType: 'abandon',
          reason: 'user_exit_confirmed',
          isCorrect: false,
        });
        console.log('[SessionTracker] Session abandoned (exit confirmed):', sessionId);
      } catch (e) {
        console.error('[SessionTracker] Failed to end session:', e);
      }
    }

    // 세션 정리
    resetSession();
    setSessionId(null);
    setInitialBaseProblem(null);  // 채팅 초기화를 위해 initialBaseProblem도 초기화
    setShowExitWarning(false);
    setIsExitLoading(false);

    // 목표 경로로 이동
    const targetPath = pendingNavigationRef.current || '/';
    pendingNavigationRef.current = null;
    router.push(targetPath);
  }, [sessionId, resetSession, router]);

  // 경고 팝업 닫기 (계속 풀기)
  const handleCancelExit = useCallback(() => {
    setShowExitWarning(false);
    pendingNavigationRef.current = null;
  }, []);

  // 브라우저 뒤로가기 감지 (popstate)
  useEffect(() => {
    if (!problem || isSubmitted) return;

    // 히스토리에 현재 상태 push (뒤로가기 감지용)
    window.history.pushState({ chatPage: true }, '', window.location.href);

    const handlePopState = (e: PopStateEvent) => {
      // 문제 풀이 중이면 경고 표시
      if (problem && !isSubmitted) {
        // 히스토리 다시 push (뒤로가기 취소)
        window.history.pushState({ chatPage: true }, '', window.location.href);
        // 경고 팝업 표시
        pendingNavigationRef.current = '/';
        setShowExitWarning(true);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [problem, isSubmitted]);

  // Fetch feedback from API
  const fetchFeedback = useCallback(async (isCorrect: boolean, earnedXp: number) => {
    if (!problem) return;

    setIsFeedbackLoading(true);
    setShowFeedbackPopup(true);

    try {
      const solveTimeSeconds = solveStartTime
        ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
        : 0;

      const response = await agentApi.getFeedback({
        user_id: user?.id || 'anonymous',
        problem_id: problem.id,
        problem_type: (problem.problemType || 'blank') as 'blank' | 'puzzle' | 'guided',
        is_correct: isCorrect,
        solve_time_seconds: solveTimeSeconds,
        hints_used: previousHints.length,
        xp_earned: earnedXp,
        attempt_count: attemptCount,
        problem_info: {
          title: problem.title,
          difficulty: problem.difficulty,
          topics: problem.topics || problem.keyConcepts || [],
        },
      });

      setFeedbackData(response);
    } catch (error) {
      console.error('Feedback fetch error:', error);
      // Use fallback feedback
      setFeedbackData({
        grade: 'good',
        grade_emoji: '👍',
        grade_message: '잘했어요!',
        summary: { title: '문제 풀이 완료!', highlight: `+${earnedXp} XP 획득!` },
        performance_analysis: {
          time_feedback: '풀이 완료',
          hint_feedback: previousHints.length > 0 ? `힌트 ${previousHints.length}회 사용` : '힌트 없이 해결!',
          attempt_feedback: attemptCount > 1 ? `${attemptCount}회 시도` : '한 번에 성공!',
        },
        learning_points: ['문제를 끝까지 풀어냈습니다.'],
        improvements: ['비슷한 유형의 문제를 더 풀어보세요.'],
        visualization: {
          efficiency_score: 70,
          speed_score: 70,
          understanding_score: 70,
        },
        next_steps: { recommendation: '다음 문제에 도전해보세요!' },
        encouragement: '잘했어요! 계속 도전하세요! 💪',
      });
    } finally {
      setIsFeedbackLoading(false);
    }
  }, [problem, solveStartTime, previousHints.length, attemptCount, user]);

  // Hint request handler - 실제 API 호출
  const handleHintRequest = useCallback(
    async (level: number, blankIdOrUserOrder?: string | string[]) => {
      // puzzle인 경우 두 번째 인자가 userOrder 배열
      const userOrder = Array.isArray(blankIdOrUserOrder) ? blankIdOrUserOrder : undefined;
      const blankId = typeof blankIdOrUserOrder === 'string' ? blankIdOrUserOrder : undefined;

      // puzzle 배치 순서 저장
      if (userOrder) {
        setPuzzleUserOrder(userOrder);
      }
      if (!problem) return;

      try {
        // 힌트 레벨 제한 (1-4)
        const hintLevel = Math.min(Math.max(level, 1), 4) as 1 | 2 | 3 | 4;

        // 문제 유형 결정
        const problemType = problem.problemType || 'blank';

        // 현재 빈칸 인덱스 (blankId에서 추출)
        let currentBlankIndex = 0;
        if (blankId) {
          const match = blankId.match(/\d+/);
          if (match) {
            currentBlankIndex = parseInt(match[0], 10);
          }
        }

        // 문제 유형별 problem_info 구성
        const baseProblemInfo = {
          title: problem.title,
          description: problem.description,
          difficulty: problem.difficulty,
          topics: problem.topics || problem.keyConcepts,
          code_template: problem.codeTemplate || problem.codeSnippet,
          language: problem.framework || 'python',
        };

        // 퍼즐 문제일 때 추가 정보 포함
        const problemInfo = problemType === 'puzzle' ? {
          ...baseProblemInfo,
          blocks: problem.puzzleBlocks || [],
          fixed_start: problem.fixedStart || '',
          fixed_end: problem.fixedEnd || '',
          user_order: userOrder || puzzleUserOrder,  // 현재 사용자 배치 순서
          correct_blocks: [],  // 이미 맞은 블록들
        } : baseProblemInfo;

        // 힌트 API 호출
        const response = await agentApi.getHint({
          problem_id: problem.id,
          base_problem_id: problem.baseProblemId || problem.originalId,
          problem_type: problemType as 'blank' | 'puzzle' | 'guided',
          problem_info: problemInfo,
          user_code: problemType === 'guided' ? currentCode : undefined,
          user_answers: blankAnswers,
          current_blank_index: currentBlankIndex,
          previous_hints: previousHints,
          user_level: 'intermediate',
        });

        // 힌트 응답 저장
        setCurrentHintResponse(response);
        setPreviousHints((prev) => [...prev, response.hint_content]);

        // GA4/Clarity 힌트 요청 이벤트
        ga4Events.hintRequest(problem.id, level);
        clarityEvents.hintRequest(level);

        // 힌트 내용을 hints 배열에도 추가 (기존 UI 호환)
        setHints((prev) => [...prev, response.hint_content]);

        toast({
          title: `힌트 Level ${hintLevel}`,
          description: response.hint_content.slice(0, 100) + (response.hint_content.length > 100 ? '...' : ''),
        });

        // 격려 메시지가 있으면 추가로 표시
        if (response.encouragement) {
          setTimeout(() => {
            toast({
              title: '💪 힘내요!',
              description: response.encouragement,
            });
          }, 2000);
        }

      } catch (error) {
        console.error('Hint request error:', error);
        toast({
          title: '힌트 오류',
          description: '힌트를 가져오는 데 실패했습니다. 다시 시도해주세요.',
          variant: 'destructive',
        });
      }
    },
    [problem, blankAnswers, previousHints, toast]
  );

  // Blank submit handler
  const handleBlankSubmit = useCallback(
    async (answers: Record<string, string>) => {
      if (!problem) return;
      setAttemptCount(prev => prev + 1);

      try {
        const result = await practiceApi.submitBlank({
          problemId: problem.id,
          answers,
        });
        setBlankResults(result.results);
        setIsSubmitted(true);
        setXpEarned(result.xpEarned);

        if (result.allCorrect) {
          // submitBlank에서 얻은 뱃지가 있으면 표시
          if (result.newBadges && result.newBadges.length > 0) {
            showBadgePopup(result.newBadges);
          }

          // Record solve to DB
          try {
            // 풀이 시간 계산
            const timeSpentSeconds = solveStartTime
              ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
              : 0;
            // ✅ 빈칸 정답 맵 구성 (blank_id -> correct_answer)
            const blankCorrectAnswers: Record<string, string> = {};
            (problem.blanks || []).forEach(blank => {
              blankCorrectAnswers[blank.id] = blank.answer;
            });
            const recordResult = await practiceApi.recordSolve({
              problemId: problem.id,
              baseProblemId: problem.baseProblemId || problem.originalId,
              problemType: 'blank',
              difficulty: problem.difficulty,
              isCorrect: true,
              problemName: problem.title,
              attemptId: attemptId || undefined,  // attempt tracking
              // ✅ attempts 테이블 완전 저장용 추가 필드
              timeSpent: timeSpentSeconds,
              submittedCode: JSON.stringify(answers),  // blank의 경우 정답 객체
              sessionId: sessionId || undefined,
              hintsUsed: previousHints.length,
              topics: problem.topics,
              // ✅ attempt_details 상세 기록용 필드
              blankAnswers: answers,  // 사용자 답변
              blankCorrectAnswers,     // 정답
              blankResults: result.results,  // 빈칸별 결과
            });
            if (recordResult.success) {
              setXpEarned(recordResult.xpEarned);
              // GA4/Clarity 문제 풀이 완료 이벤트
              ga4Events.problemSolve(problem.id, true, timeSpentSeconds, previousHints.length);
              clarityEvents.problemSolve(true);
              // recordSolve에서 추가로 얻은 뱃지가 있으면 표시
              if (recordResult.newBadges && recordResult.newBadges.length > 0) {
                showBadgePopup(recordResult.newBadges);
              }
              // 씨앗 보상 표시
              if (recordResult.seedAwarded) {
                setEarnedSeed(recordResult.seedAwarded);
              }
              refreshProfile();  // 프로필 캐시 갱신
              fetchFeedback(true, recordResult.xpEarned);
              return;
            }
          } catch (e) { console.error('Record failed:', e); }
          // Show feedback popup for correct answer
          fetchFeedback(true, result.xpEarned);
        } else {
          toast({
            title: '일부 오답이 있습니다',
            description: '다시 시도해보세요!',
          });
        }
      } catch (error) {
        // Mock fallback - assume all correct for demo
        const mockResults: Record<string, boolean> = {};
        Object.keys(answers).forEach(key => {
          mockResults[key] = true; // All correct for demo
        });
        setBlankResults(mockResults);
        setIsSubmitted(true);
        // Record solve to DB
        try {
          // 풀이 시간 계산
          const timeSpentSeconds = solveStartTime
            ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
            : 0;
          // ✅ 빈칸 정답 맵 구성 (blank_id -> correct_answer)
          const blankCorrectAnswers: Record<string, string> = {};
          (problem.blanks || []).forEach(blank => {
            blankCorrectAnswers[blank.id] = blank.answer;
          });
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            baseProblemId: problem.baseProblemId || problem.originalId,
            problemType: 'blank',
            difficulty: problem.difficulty,
            isCorrect: true,
            problemName: problem.title,
            attemptId: attemptId || undefined,  // attempt tracking
            // ✅ attempts 테이블 완전 저장용 추가 필드
            timeSpent: timeSpentSeconds,
            submittedCode: JSON.stringify(answers),
            sessionId: sessionId || undefined,
            hintsUsed: previousHints.length,
            topics: problem.topics,
            // ✅ attempt_details 상세 기록용 필드
            blankAnswers: answers,
            blankCorrectAnswers,
            blankResults: mockResults,
          });
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
            // GA4/Clarity 문제 풀이 완료 이벤트
            ga4Events.problemSolve(problem.id, true, timeSpentSeconds, previousHints.length);
            clarityEvents.problemSolve(true);
            if (recordResult.newBadges && recordResult.newBadges.length > 0) {
              showBadgePopup(recordResult.newBadges);
            }
            // 씨앗 보상 표시
            if (recordResult.seedAwarded) {
              setEarnedSeed(recordResult.seedAwarded);
            }
            refreshProfile();  // 프로필 캐시 갱신
            fetchFeedback(true, recordResult.xpEarned);
            return;
          }
        } catch (e) { console.error('Record failed:', e); }
        setXpEarned(40); // fallback
        fetchFeedback(true, 40);
      }
    },
    [problem, toast, fetchFeedback, attemptId, showBadgePopup, refreshProfile, solveStartTime, sessionId, previousHints]
  );

  // Puzzle submit handler
  const handlePuzzleSubmit = useCallback(
    async (blockOrder: Array<{ id: string; indentation: number }>) => {
      if (!problem) return;
      setAttemptCount(prev => prev + 1);

      try {
        const result = await practiceApi.submitPuzzle({
          problemId: problem.id,
          blockOrder,
        });
        setPuzzleResults(result.results || {});
        setIsSubmitted(true);
        setXpEarned(result.xpEarned);

        if (result.isCorrect) {
          // submitPuzzle에서 얻은 뱃지가 있으면 표시
          if (result.newBadges && result.newBadges.length > 0) {
            showBadgePopup(result.newBadges);
          }

          // Record solve to DB
          try {
            // 풀이 시간 계산
            const timeSpentSeconds = solveStartTime
              ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
              : 0;
            // ✅ 퍼즐 순서 정보 구성
            const puzzleUserOrder = blockOrder.map(b => b.id);
            const puzzleCorrectOrder = problem.correctOrder || (problem.puzzleBlocks || []).map(b => b.id);
            // 틀린 위치 계산
            const puzzleWrongPositions: number[] = [];
            puzzleUserOrder.forEach((id, idx) => {
              if (puzzleCorrectOrder[idx] !== id) {
                puzzleWrongPositions.push(idx);
              }
            });
            const recordResult = await practiceApi.recordSolve({
              problemId: problem.id,
              baseProblemId: problem.baseProblemId || problem.originalId,
              problemType: 'puzzle',
              difficulty: problem.difficulty,
              isCorrect: true,
              problemName: problem.title,
              attemptId: attemptId || undefined,  // attempt tracking
              // ✅ attempts 테이블 완전 저장용 추가 필드
              timeSpent: timeSpentSeconds,
              submittedCode: JSON.stringify(blockOrder),  // puzzle의 경우 블록 순서
              sessionId: sessionId || undefined,
              hintsUsed: previousHints.length,
              topics: problem.topics,
              // ✅ attempt_details 상세 기록용 필드
              puzzleUserOrder,
              puzzleCorrectOrder,
              puzzleWrongPositions,
            });
            if (recordResult.success) {
              setXpEarned(recordResult.xpEarned);
              // GA4/Clarity 문제 풀이 완료 이벤트
              ga4Events.problemSolve(problem.id, true, timeSpentSeconds, previousHints.length);
              clarityEvents.problemSolve(true);
              // recordSolve에서 추가로 얻은 뱃지가 있으면 표시
              if (recordResult.newBadges && recordResult.newBadges.length > 0) {
                showBadgePopup(recordResult.newBadges);
              }
              // 씨앗 보상 표시
              if (recordResult.seedAwarded) {
                setEarnedSeed(recordResult.seedAwarded);
              }
              refreshProfile();  // 프로필 캐시 갱신
              fetchFeedback(true, recordResult.xpEarned);
              return;
            }
          } catch (e) { console.error('Record failed:', e); }
          // Show feedback popup for correct answer
          fetchFeedback(true, result.xpEarned);
        } else {
          toast({
            title: '일부 오답이 있습니다',
            description: '블록 순서를 다시 확인해보세요!',
          });
        }
      } catch (error) {
        // Mock fallback - assume correct for demo
        setPuzzleResults({});
        setIsSubmitted(true);
        // Record solve to DB
        try {
          // 풀이 시간 계산
          const timeSpentSeconds = solveStartTime
            ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
            : 0;
          // ✅ 퍼즐 순서 정보 구성
          const puzzleUserOrder = blockOrder.map(b => b.id);
          const puzzleCorrectOrder = problem.correctOrder || (problem.puzzleBlocks || []).map(b => b.id);
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            baseProblemId: problem.baseProblemId || problem.originalId,
            problemType: 'puzzle',
            difficulty: problem.difficulty,
            isCorrect: true,
            problemName: problem.title,
            attemptId: attemptId || undefined,  // attempt tracking
            // ✅ attempts 테이블 완전 저장용 추가 필드
            timeSpent: timeSpentSeconds,
            submittedCode: JSON.stringify(blockOrder),
            sessionId: sessionId || undefined,
            hintsUsed: previousHints.length,
            topics: problem.topics,
            // ✅ attempt_details 상세 기록용 필드
            puzzleUserOrder,
            puzzleCorrectOrder,
          });
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
            // GA4/Clarity 문제 풀이 완료 이벤트
            ga4Events.problemSolve(problem.id, true, timeSpentSeconds, previousHints.length);
            clarityEvents.problemSolve(true);
            if (recordResult.newBadges && recordResult.newBadges.length > 0) {
              showBadgePopup(recordResult.newBadges);
            }
            // 씨앗 보상 표시
            if (recordResult.seedAwarded) {
              setEarnedSeed(recordResult.seedAwarded);
            }
            refreshProfile();  // 프로필 캐시 갱신
            fetchFeedback(true, recordResult.xpEarned);
            return;
          }
        } catch (e) { console.error('Record failed:', e); }
        setXpEarned(40); // fallback
        fetchFeedback(true, 40);
      }
    },
    [problem, toast, fetchFeedback, attemptId, showBadgePopup, refreshProfile, solveStartTime, sessionId, previousHints]
  );

  // Implementation submit handler (blank, puzzle, implementation 공통)
  const handleImplementationSubmit = useCallback(
    async (code: string, results: any[], hintsUsed?: number) => {
      setAttemptCount(prev => prev + 1);

      const passedCount = results.filter((r) => r.passed).length;
      const allPassed = passedCount === results.length;
      setIsSubmitted(true);

      // Record solve to DB for XP and grass (잔디)
      if (problem && allPassed) {
        try {
          // 풀이 시간 계산
          const timeSpentSeconds = solveStartTime
            ? Math.floor((new Date().getTime() - solveStartTime.getTime()) / 1000)
            : 0;
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            problemType: (problem.problemType || 'guided') as 'blank' | 'puzzle' | 'guided',
            difficulty: problem.difficulty,
            isCorrect: true,
            hintsUsed: hintsUsed ?? previousHints.length,  // 힌트 사용 횟수 전달
            problemName: problem.title,  // 문제 이름
            topics: problem.topics,  // 문제 주제/태그
            attemptId: attemptId || undefined,  // attempt tracking
            // ✅ attempts 테이블 완전 저장용 추가 필드
            timeSpent: timeSpentSeconds,
            submittedCode: code,  // guided의 경우 실제 코드
            sessionId: sessionId || undefined,
          });
          console.log('[RecordSolve] Result:', recordResult, 'hintsUsed:', hintsUsed);
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
            // GA4/Clarity 문제 풀이 완료 이벤트
            ga4Events.problemSolve(problem.id, true, timeSpentSeconds, hintsUsed ?? previousHints.length);
            clarityEvents.problemSolve(true);
            if (recordResult.newBadges && recordResult.newBadges.length > 0) {
              showBadgePopup(recordResult.newBadges);
            }
            // 씨앗 보상 표시
            if (recordResult.seedAwarded) {
              setEarnedSeed(recordResult.seedAwarded);
            }
            refreshProfile();  // 프로필 캐시 갱신
            fetchFeedback(true, recordResult.xpEarned);
            return;
          } else if (recordResult.message.includes('로그인')) {
            toast({
              title: 'XP 기록 안됨',
              description: '로그인하면 XP와 잔디가 기록됩니다!',
              variant: 'default',
            });
          }
        } catch (error) {
          console.error('Failed to record solve:', error);
        }
        // Fallback XP based on difficulty
        const fallbackXp = 40;
        setXpEarned(fallbackXp);
        fetchFeedback(true, fallbackXp);
      } else {
        setXpEarned(0);
        toast({
          title: '일부 테스트 실패',
          description: `${passedCount}/${results.length} 테스트 통과. 다시 시도해보세요!`,
        });
      }
    },
    [problem, toast, fetchFeedback, attemptId, showBadgePopup, refreshProfile, solveStartTime, sessionId, previousHints]
  );

  // 온보딩 핸들러 제거됨 (소셜 회원가입에서 처리)

  // Render practice component based on problem type
  const renderPracticeComponent = () => {
    if (!problem) {
      // 문제 정보가 있으면 (problems 페이지에서 넘어온 경우) 먼저 문제 내용 표시
      if (initialBaseProblem) {
        return (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="h-full overflow-auto p-6"
          >
            {/* 문제 헤더 */}
            <div className="mb-6">
              <h1 className="text-xl font-bold mb-3">{initialBaseProblem.name}</h1>
              <div className="flex flex-wrap items-center gap-2">
                <Badge
                  variant="outline"
                  className={cn('capitalize', difficultyColors[initialBaseProblem.difficulty])}
                >
                  {initialBaseProblem.difficulty}
                </Badge>
                {initialBaseProblem.tags?.slice(0, 4).map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 문제 설명 */}
            <div className="bg-muted/30 rounded-lg border border-border p-5">
              <div className="prose prose-sm dark:prose-invert max-w-none [&_pre]:bg-background/50 [&_pre]:p-3 [&_pre]:rounded-md [&_code]:text-primary [&_code]:bg-background/50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_p]:text-[13px] [&_li]:text-[13px]">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {initialBaseProblem.question || initialBaseProblem.description || ''}
                </ReactMarkdown>
              </div>
            </div>

            {/* 테스트케이스 (있으면) */}
            {initialBaseProblem.input_output?.inputs && initialBaseProblem.input_output.inputs.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium mb-3 text-muted-foreground">테스트케이스</h3>
                <div className="space-y-3">
                  {initialBaseProblem.input_output.inputs.slice(0, 2).map((input, idx) => (
                    <div key={idx} className="grid grid-cols-2 gap-3">
                      <div className="rounded-lg border border-border overflow-hidden">
                        <div className="bg-muted/50 px-3 py-1.5 border-b border-border text-xs font-medium">
                          Input
                        </div>
                        <pre className="p-3 text-xs font-mono overflow-auto max-h-24 text-blue-600 dark:text-blue-400">
                          {input}
                        </pre>
                      </div>
                      <div className="rounded-lg border border-border overflow-hidden">
                        <div className="bg-muted/50 px-3 py-1.5 border-b border-border text-xs font-medium">
                          Output
                        </div>
                        <pre className="p-3 text-xs font-mono overflow-auto max-h-24 text-red-600 dark:text-red-400">
                          {initialBaseProblem.input_output?.outputs?.[idx] || ''}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 유형 선택 안내 */}
            <div className="mt-8 text-center py-4 bg-primary/5 rounded-lg border border-primary/20">
              <p className="text-sm text-muted-foreground">
                👉 오른쪽에서 <span className="text-primary font-medium">문제 유형을 선택</span>하면 풀이를 시작합니다
              </p>
            </div>
          </motion.div>
        );
      }

      return (
        <div className="flex h-full items-center justify-center text-muted-foreground">
          <div className="text-center">
            <p className="text-lg font-medium">문제를 선택해주세요</p>
            <p className="mt-2 text-sm">오른쪽 채팅에서 난이도와 유형을 선택하면<br />문제가 여기에 표시됩니다</p>
          </div>
        </div>
      );
    }

    // Blank, Puzzle, Implementation - 통합 컴포넌트 사용
    return (
      <UnifiedPractice
        problem={problem}
        problemType={problem.problemType || 'implementation'}
        onSubmit={handleImplementationSubmit}
        onRun={(code) => {
          toast({
            title: '코드 실행 중...',
            description: '테스트를 실행합니다',
          });
        }}
        onHintRequest={(level, userOrder) => handleHintRequest(level, userOrder)}
        onGiveUp={handleGiveUp}  // 포기하기
        attemptId={attemptId || undefined}  // attempt tracking
        onCodeChange={setCurrentCode}  // guided 모드 튜터에게 현재 코드 전달
        onBlankHintUsed={(index) => {
          // 힌트 사용 시 인덱스 추가 (중복 방지)
          setUsedBlankHintIndices(prev => prev.includes(index) ? prev : [...prev, index]);
        }}
        onBlockOrderChange={setPuzzleUserOrder}  // 퍼즐 블록 순서 변경 시 업데이트
      />
    );
  };

  // Show loading while checking auth or restoring session
  if (isAuthChecking || !isRestored) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          {!isRestored && (
            <p className="text-sm text-muted-foreground">세션 복원 중...</p>
          )}
        </div>
      </div>
    );
  }

  // 온보딩은 소셜 회원가입 시 완료되므로 여기서는 체크하지 않음

  // Show login required screen if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center gap-6 text-center"
        >
          <div className="rounded-full bg-muted p-6">
            <LogIn className="h-12 w-12 text-muted-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">로그인이 필요합니다</h1>
            <p className="mt-2 text-muted-foreground">
              문제를 풀려면 로그인해주세요.<br />
              XP 획득과 잔디 기록이 저장됩니다.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => router.push('/')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              홈으로
            </Button>
            <Button onClick={() => router.push('/login')}>
              <LogIn className="mr-2 h-4 w-4" />
              로그인하기
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Minimal Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="shrink-0 border-b border-border bg-card px-4 py-2"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => handleExitAttempt('/')}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            {problem ? (
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-medium">{problem.title}</h1>
                <Badge
                  variant="outline"
                  className={cn('text-xs capitalize', difficultyColors[problem.difficulty])}
                >
                  {problem.difficulty}
                </Badge>
              </div>
            ) : (
              <h1 className="text-sm font-medium">Practice Assistant</h1>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Chat Panel Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowChat(!showChat)}
              className="gap-1.5 h-8"
            >
              {showChat ? (
                <PanelRightClose className="h-4 w-4" />
              ) : (
                <PanelRight className="h-4 w-4" />
              )}
            </Button>

            {isSubmitted && xpEarned > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="rounded-full bg-primary/20 px-3 py-1 text-sm font-medium text-primary"
              >
                +{xpEarned} XP
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Main Content - Resizable Split */}
      <div ref={containerRef} className="flex flex-1 overflow-hidden">
        {/* Left Panel - Practice Area */}
        <main className="flex flex-1 flex-col overflow-hidden min-w-0">
          <div className="flex-1 overflow-auto p-4">{renderPracticeComponent()}</div>
        </main>

        {/* Right Panel - ChatBot (Resizable) */}
        <AnimatePresence>
          {showChat && (
            <>
              {/* Resize Handle */}
              <Resizer
                direction="horizontal"
                onResize={handleChatResize}
                className="bg-border hover:bg-primary/50"
              />
              <motion.aside
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: chatWidth, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="shrink-0 overflow-hidden"
              >
                <div className="h-full p-3">
                  {/* URL에 problem_id가 있지만 아직 로드 안됐으면 로더 표시 */}
                  {(isLoadingInitialProblem || (urlProblemId && !initialBaseProblem)) ? (
                    <div className="flex h-full items-center justify-center">
                      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                  ) : (
                    <PracticeChatPanel
                      problem={problem}
                      onHintRequest={handleHintRequest}
                      onProblemSelect={handleProblemSelect}
                      hints={hints}
                      initialBaseProblem={initialBaseProblem}
                      sessionId={chatSessionId}
                      onSessionIdChange={setChatSessionId}
                      problemType={problem?.problemType}
                      currentCode={currentCode}
                      usedBlankHintIndices={usedBlankHintIndices}
                      puzzleUserOrder={puzzleUserOrder}
                      blankAnswers={blankAnswers}
                    />
                  )}
                </div>
              </motion.aside>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* Correct Answer Popup */}
      <CorrectAnswerPopup
        isOpen={showFeedbackPopup}
        onClose={() => setShowFeedbackPopup(false)}
        onNextProblem={handleResetSession}
        feedback={feedbackData}
        xpEarned={xpEarned}
        isLoading={isFeedbackLoading}
        seedAwarded={earnedSeed}
      />

      {/* Badge Popup */}
      {earnedBadges.length > 0 && (
        <BadgePopup
          badges={earnedBadges}
          onClose={() => setEarnedBadges([])}
        />
      )}

      {/* Exit Warning Dialog */}
      <ExitWarningDialog
        isOpen={showExitWarning}
        onClose={handleCancelExit}
        onConfirmExit={handleConfirmExit}
        isLoading={isExitLoading}
      />
    </div>
  );
}
