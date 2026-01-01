'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Resizer } from '@/components/ui/resizer';
import { ArrowLeft, PanelRightClose, PanelRight, Loader2, LogIn } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';

import { UnifiedPractice } from '@/components/practice/UnifiedPractice';
import { PracticeChatPanel } from '@/components/chat/PracticeChatPanel';
import { CorrectAnswerPopup } from '@/components/practice/CorrectAnswerPopup';

import { practiceApi, agentApi, problemsApi } from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import type { ConvertedProblem, ConvertedProblemType } from '@/lib/dataTypes';
import type { HintAgentResponse, FeedbackResponse, BaseProblemInfo } from '@/lib/api/agent';

const difficultyColors = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

export default function ChatPage() {
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Auth state
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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

  // Current problem state
  const [problem, setProblem] = useState<ConvertedProblem | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  // Initial problem (from URL parameter) - 정보수집 단계 생략용
  const [initialBaseProblem, setInitialBaseProblem] = useState<BaseProblemInfo | null>(null);
  const [isLoadingInitialProblem, setIsLoadingInitialProblem] = useState(false);

  // Practice results
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});
  const [puzzleResults, setPuzzleResults] = useState<Record<string, boolean>>({});
  const [hints, setHints] = useState<string[]>([]);
  const [previousHints, setPreviousHints] = useState<string[]>([]);
  const [currentHintResponse, setCurrentHintResponse] = useState<HintAgentResponse | null>(null);
  const [blankAnswers, setBlankAnswers] = useState<Record<string, string>>({});

  // Feedback popup state
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false);
  const [feedbackData, setFeedbackData] = useState<FeedbackResponse | null>(null);
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(false);
  const [solveStartTime, setSolveStartTime] = useState<Date | null>(null);
  const [attemptCount, setAttemptCount] = useState(0);

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
  const handleProblemSelect = useCallback((selectedProblem: ConvertedProblem) => {
    setProblem(selectedProblem);
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    // keyConcepts를 힌트로 사용
    setHints(selectedProblem.keyConcepts || []);
    // 힌트 상태 초기화
    setPreviousHints([]);
    setCurrentHintResponse(null);
    setBlankAnswers({});
    // 피드백 상태 초기화
    setShowFeedbackPopup(false);
    setFeedbackData(null);
    setSolveStartTime(new Date());
    setAttemptCount(0);
  }, []);

  // Reset session (다음문제 풀기)
  const handleResetSession = useCallback(() => {
    setProblem(null);
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    setHints([]);
    setPreviousHints([]);
    setCurrentHintResponse(null);
    setBlankAnswers({});
    setShowFeedbackPopup(false);
    setFeedbackData(null);
    setSolveStartTime(null);
    setAttemptCount(0);
  }, []);

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
        user_id: 'anonymous', // TODO: Get from auth context
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
  }, [problem, solveStartTime, previousHints.length, attemptCount]);

  // Hint request handler - 실제 API 호출
  const handleHintRequest = useCallback(
    async (level: number, blankId?: string) => {
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

        // 힌트 API 호출
        const response = await agentApi.getHint({
          problem_id: problem.id,
          base_problem_id: undefined,  // 프론트엔드에서는 base_problem_id를 알 수 없음, 백엔드에서 조회
          problem_type: problemType as 'blank' | 'puzzle' | 'guided',
          problem_info: {
            title: problem.title,
            description: problem.description,
            difficulty: problem.difficulty,
            topics: problem.topics || problem.keyConcepts,
            code_template: problem.codeTemplate || problem.codeSnippet,
            language: problem.framework || 'python',
          },
          user_code: problem.codeSnippet,
          user_answers: blankAnswers,
          current_blank_index: currentBlankIndex,
          attempt_count: previousHints.length,
          hint_level: hintLevel,
          previous_hints: previousHints,
          user_level: 'intermediate',
        });

        // 힌트 응답 저장
        setCurrentHintResponse(response);
        setPreviousHints((prev) => [...prev, response.hint_content]);

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
          // Record solve to DB
          try {
            const recordResult = await practiceApi.recordSolve({
              problemId: problem.id,
              problemType: 'blank',
              difficulty: problem.difficulty,
              isCorrect: true,
            });
            if (recordResult.success) {
              setXpEarned(recordResult.xpEarned);
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
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            problemType: 'blank',
            difficulty: problem.difficulty,
            isCorrect: true,
          });
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
            fetchFeedback(true, recordResult.xpEarned);
            return;
          }
        } catch (e) { console.error('Record failed:', e); }
        setXpEarned(40); // fallback
        fetchFeedback(true, 40);
      }
    },
    [problem, toast, fetchFeedback]
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
          // Record solve to DB
          try {
            const recordResult = await practiceApi.recordSolve({
              problemId: problem.id,
              problemType: 'puzzle',
              difficulty: problem.difficulty,
              isCorrect: true,
            });
            if (recordResult.success) {
              setXpEarned(recordResult.xpEarned);
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
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            problemType: 'puzzle',
            difficulty: problem.difficulty,
            isCorrect: true,
          });
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
            fetchFeedback(true, recordResult.xpEarned);
            return;
          }
        } catch (e) { console.error('Record failed:', e); }
        setXpEarned(40); // fallback
        fetchFeedback(true, 40);
      }
    },
    [problem, toast, fetchFeedback]
  );

  // Implementation submit handler
  const handleImplementationSubmit = useCallback(
    async (code: string, results: any[]) => {
      setAttemptCount(prev => prev + 1);

      const passedCount = results.filter((r) => r.passed).length;
      const allPassed = passedCount === results.length;
      setIsSubmitted(true);

      // Record solve to DB for XP and grass (잔디)
      if (problem && allPassed) {
        try {
          const recordResult = await practiceApi.recordSolve({
            problemId: problem.id,
            problemType: (problem.problemType || 'guided') as 'blank' | 'puzzle' | 'guided',
            difficulty: problem.difficulty,
            isCorrect: true,
          });
          console.log('[RecordSolve] Result:', recordResult);
          if (recordResult.success) {
            setXpEarned(recordResult.xpEarned);
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
    [problem, toast, fetchFeedback]
  );

  // Render practice component based on problem type
  const renderPracticeComponent = () => {
    if (!problem) {
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
        onHintRequest={(level) => handleHintRequest(level)}
      />
    );
  };

  // Show loading while checking auth
  if (isAuthChecking) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

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
            <Link href="/">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
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
      />
    </div>
  );
}
