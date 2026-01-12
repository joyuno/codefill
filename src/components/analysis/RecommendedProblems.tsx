'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Target, ChevronRight, Zap, Code2, Sparkles, Loader2, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { analysisApi, type RecommendedProblem } from '@/lib/api/analysis';

interface RecommendedProblemsProps {
  initialProblems: RecommendedProblem[];
}

// 난이도에 따른 색상
function getDifficultyColor(difficulty: string) {
  switch (difficulty.toLowerCase()) {
    case 'easy':
      return { text: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.3)' };
    case 'medium':
      return { text: '#eab308', bg: 'rgba(234, 179, 8, 0.1)', border: 'rgba(234, 179, 8, 0.3)' };
    case 'hard':
      return { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)' };
    default:
      return { text: '#71717a', bg: 'rgba(113, 113, 122, 0.1)', border: 'rgba(113, 113, 122, 0.3)' };
  }
}

export function RecommendedProblems({ initialProblems }: RecommendedProblemsProps) {
  const [problems, setProblems] = useState<RecommendedProblem[]>(initialProblems);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await analysisApi.recommendProblems();
      if (response.data) {
        setProblems(response.data);
      } else {
        setError(response.error?.message || '추천 문제를 불러오지 못했습니다');
      }
    } catch (err) {
      setError('추천 문제를 불러오는 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 문제가 없을 때 - 추천받기 버튼 표시
  if (problems.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="text-base font-semibold text-zinc-100">추천 문제</h3>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center py-8">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <p className="text-sm text-zinc-400 mb-4 text-center">
            약점 분석을 기반으로<br />맞춤 문제를 추천받아 보세요
          </p>
          <Button
            onClick={handleFetchRecommendations}
            disabled={isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                문제 검색 중...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                문제 추천받기
              </>
            )}
          </Button>
          {error && (
            <p className="mt-3 text-xs text-red-400">{error}</p>
          )}
        </div>
      </div>
    );
  }

  // 문제가 있을 때
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-primary" />
          <h3 className="text-base font-semibold text-zinc-100">추천 문제</h3>
          <span className="text-xs text-zinc-500">({problems.length}개)</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleFetchRecommendations}
            disabled={isLoading}
            className="text-zinc-400 hover:text-zinc-200 h-8 px-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </Button>
          <Link
            href="/problems"
            className="flex items-center gap-1 text-xs text-zinc-500 hover:text-primary transition-colors"
          >
            전체 보기
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {error && (
        <p className="mb-3 text-xs text-red-400">{error}</p>
      )}

      {/* 수평 스크롤 카드 */}
      <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
        {problems.map((problem, index) => {
          const diffColor = getDifficultyColor(problem.difficulty);

          return (
            <motion.div
              key={problem.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="flex-shrink-0 w-64"
            >
              <Link
                href={`/problems/${problem.originalId || problem.id}`}
                className="block p-4 rounded-lg bg-zinc-900/50 border border-zinc-700/50 hover:border-zinc-600 transition-all duration-200 hover:scale-[1.02] group"
              >
                {/* 헤더 */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-zinc-500" />
                    <span
                      className="text-[10px] font-medium px-2 py-0.5 rounded"
                      style={{
                        color: diffColor.text,
                        backgroundColor: diffColor.bg,
                        border: `1px solid ${diffColor.border}`,
                      }}
                    >
                      {problem.difficulty.toUpperCase()}
                    </span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-primary transition-colors" />
                </div>

                {/* 문제 이름 */}
                <h4 className="text-sm font-medium text-zinc-200 truncate mb-1">
                  {problem.name}
                </h4>

                {/* 토픽 태그 */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                    {problem.topic}
                  </span>
                </div>

                {/* 추천 이유 */}
                <p className="text-xs text-zinc-500 line-clamp-2">
                  {problem.reason}
                </p>

                {/* 시작하기 버튼 */}
                <div className="mt-3 flex items-center gap-1 text-xs text-zinc-500 group-hover:text-primary transition-colors">
                  <Zap className="w-3.5 h-3.5" />
                  <span>문제 풀기</span>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* 스크롤 힌트 */}
      {problems.length > 2 && (
        <div className="mt-2 text-center text-[10px] text-zinc-600">
          ← 스크롤하여 더 많은 문제 보기 →
        </div>
      )}
    </div>
  );
}
