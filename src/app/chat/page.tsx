'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, PanelRightClose, PanelRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';

import { UnifiedPractice } from '@/components/practice/UnifiedPractice';
import { GuidedPractice } from '@/components/practice/types/GuidedPractice';
import { PracticeChatPanel } from '@/components/chat/PracticeChatPanel';

import { practiceApi } from '@/lib/api';
import type { Problem, ProblemType } from '@/lib/types';
import { mockProblems } from '@/lib/mockData';

const difficultyColors = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

export default function ChatPage() {
  const { toast } = useToast();

  // Current problem state
  const [problem, setProblem] = useState<Problem | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  // Practice results
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});
  const [puzzleResults, setPuzzleResults] = useState<Record<string, boolean>>({});
  const [hints, setHints] = useState<string[]>([]);

  // Layout state
  const [showChat, setShowChat] = useState(true);

  // Handle problem selection from chat
  const handleProblemSelect = useCallback((selectedProblem: Problem) => {
    setProblem(selectedProblem);
    setIsSubmitted(false);
    setXpEarned(0);
    setBlankResults({});
    setPuzzleResults({});
    setHints(selectedProblem.blanks?.[0]?.hints || []);
  }, []);

  // Hint request handler
  const handleHintRequest = useCallback(
    async (level: number, blankId?: string) => {
      if (!problem) return;
      // For now, use local hints
      toast({
        title: '힌트 사용',
        description: `-10 XP`,
      });
    },
    [problem, toast]
  );

  // Blank submit handler
  const handleBlankSubmit = useCallback(
    async (answers: Record<string, string>) => {
      if (!problem) return;
      try {
        const result = await practiceApi.submitBlank({
          problemId: problem.id,
          answers,
        });
        setBlankResults(result.results);
        setIsSubmitted(true);
        setXpEarned(result.xpEarned);
        toast({
          title: result.allCorrect ? '정답입니다!' : '일부 오답이 있습니다',
          description: `+${result.xpEarned} XP`,
        });
      } catch (error) {
        // Mock fallback
        const mockResults: Record<string, boolean> = {};
        Object.keys(answers).forEach(key => {
          mockResults[key] = Math.random() > 0.3;
        });
        setBlankResults(mockResults);
        setIsSubmitted(true);
        setXpEarned(50);
        toast({
          title: '제출 완료',
          description: '+50 XP',
        });
      }
    },
    [problem, toast]
  );

  // Puzzle submit handler
  const handlePuzzleSubmit = useCallback(
    async (blockOrder: Array<{ id: string; indentation: number }>) => {
      if (!problem) return;
      try {
        const result = await practiceApi.submitPuzzle({
          problemId: problem.id,
          blockOrder,
        });
        setPuzzleResults(result.results || {});
        setIsSubmitted(true);
        setXpEarned(result.xpEarned);
        toast({
          title: result.isCorrect ? '정답입니다!' : '일부 오답이 있습니다',
          description: `+${result.xpEarned} XP`,
        });
      } catch (error) {
        // Mock fallback
        setPuzzleResults({});
        setIsSubmitted(true);
        setXpEarned(70);
        toast({
          title: '제출 완료',
          description: '+70 XP',
        });
      }
    },
    [problem, toast]
  );

  // Guided complete handler
  const handleGuidedComplete = useCallback(
    (responses: any[]) => {
      const correctCount = responses.filter((r) => r.correct).length;
      const score = Math.round((correctCount / responses.length) * 100);
      const baseXp = 100;
      const earned = Math.round((score / 100) * baseXp);
      setXpEarned(earned);
      setIsSubmitted(true);
      toast({
        title: '1대1 대화형 학습 완료!',
        description: `+${earned} XP`,
      });
    },
    [toast]
  );

  // Implementation submit handler
  const handleImplementationSubmit = useCallback(
    (code: string, results: any[]) => {
      const passedCount = results.filter((r) => r.passed).length;
      const allPassed = passedCount === results.length;
      const baseXp = 80;
      const earned = allPassed ? baseXp : Math.round((passedCount / results.length) * baseXp);
      setXpEarned(earned);
      setIsSubmitted(true);
      toast({
        title: allPassed ? '모든 테스트 통과!' : '일부 테스트 실패',
        description: `+${earned} XP`,
      });
    },
    [toast]
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

    // Guided는 별도 컴포넌트 유지
    if (problem.problemType === 'guided') {
      return problem.guidedData ? (
        <GuidedPractice
          data={problem.guidedData}
          onComplete={handleGuidedComplete}
          onHintRequest={(step) => handleHintRequest(step)}
          onSkip={(step) => {
            toast({
              title: `Step ${step} 건너뜀`,
              description: 'XP가 차감됩니다',
            });
          }}
        />
      ) : null;
    }

    // Blank, Puzzle, Implementation은 통합 컴포넌트 사용
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

      {/* Main Content - 60/40 Split */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Practice Area (60% or 100% when chat hidden) */}
        <main className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-auto p-4">{renderPracticeComponent()}</div>
        </main>

        {/* Right Panel - ChatBot (40%) */}
        <AnimatePresence>
          {showChat && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: '40%', opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="shrink-0 overflow-hidden border-l border-border"
            >
              <div className="h-full p-3">
                <PracticeChatPanel
                  problem={problem}
                  onHintRequest={handleHintRequest}
                  onProblemSelect={handleProblemSelect}
                  hints={hints}
                />
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
