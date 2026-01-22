'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RotateCcw,
  ChevronRight,
  Zap,
  Loader2,
  RefreshCw,
  Lightbulb,
  Clock,
  ArrowUpDown,
  Filter,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { PreviewModal } from '@/components/problems/PreviewModal';
import { analysisApi, type WrongProblem, type WrongProblemsParams } from '@/lib/api/analysis';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

const ITEMS_PER_PAGE = 8;

// 난이도 설정
const DIFFICULTIES = [
  { value: '', label: '전체', color: '#71717a' },
  { value: 'easy', label: '실버', color: '#22c55e' },
  { value: 'medium', label: '골드', color: '#eab308' },
  { value: 'medium_hard', label: '플래티넘', color: '#06b6d4' },
  { value: 'hard', label: '다이아', color: '#8b5cf6' },
  { value: 'very_hard', label: '마스터', color: '#ef4444' },
] as const;

// 정렬 옵션
const SORT_OPTIONS = [
  { value: 'recent', label: '최근 틀린 순', icon: Clock },
  { value: 'difficulty', label: '난이도 순', icon: ArrowUpDown },
  { value: 'hints', label: '힌트 많이 쓴 순', icon: Lightbulb },
] as const;

// 난이도에 따른 색상
function getDifficultyConfig(difficulty: string) {
  const config = DIFFICULTIES.find(d => d.value === difficulty);
  return config || { value: difficulty, label: difficulty, color: '#71717a' };
}

// 문제 유형에 따른 레이블
function getProblemTypeLabel(type: string | undefined) {
  switch (type?.toLowerCase()) {
    case 'blank': return '빈칸';
    case 'puzzle': return '퍼즐';
    case 'guided': return '가이드';
    case 'implementation': return '구현';
    default: return type || '';
  }
}

// 상대 시간 포맷
function formatRelativeTime(dateStr: string | undefined) {
  if (!dateStr) return '';
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true, locale: ko });
  } catch {
    return '';
  }
}

export function WrongProblems() {
  const [problems, setProblems] = useState<WrongProblem[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 필터 상태
  const [sortBy, setSortBy] = useState<'recent' | 'difficulty' | 'hints'>('recent');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [offset, setOffset] = useState(0);

  // 모달 상태
  const [selectedProblemId, setSelectedProblemId] = useState<string | null>(null);

  const fetchProblems = useCallback(async (isLoadMore = false) => {
    if (isLoadMore) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
      setOffset(0);
    }
    setError(null);

    const currentOffset = isLoadMore ? offset : 0;

    try {
      const params: WrongProblemsParams = {
        limit: ITEMS_PER_PAGE,
        offset: currentOffset,
        sortBy,
        difficulty: difficultyFilter || undefined,
      };

      const response = await analysisApi.getWrongProblems(params);

      if (response.data) {
        if (isLoadMore) {
          setProblems(prev => [...prev, ...response.data!.problems]);
        } else {
          setProblems(response.data.problems);
        }
        setTotal(response.data.total);
        setHasMore(response.data.hasMore);
        if (isLoadMore) {
          setOffset(currentOffset + ITEMS_PER_PAGE);
        } else {
          setOffset(ITEMS_PER_PAGE);
        }
      } else {
        setError(response.error?.message || '틀린 문제를 불러오지 못했습니다');
      }
    } catch (err) {
      setError('틀린 문제를 불러오는 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }, [sortBy, difficultyFilter, offset]);

  // 초기 로드 & 필터 변경 시
  useEffect(() => {
    fetchProblems(false);
  }, [sortBy, difficultyFilter]);

  const handleLoadMore = () => {
    fetchProblems(true);
  };

  const currentSort = SORT_OPTIONS.find(s => s.value === sortBy) || SORT_OPTIONS[0];
  const currentDifficulty = DIFFICULTIES.find(d => d.value === difficultyFilter) || DIFFICULTIES[0];

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <RotateCcw className="w-5 h-5 text-rose-400" />
          <h3 className="text-base font-semibold text-zinc-100">틀린 문제 복습</h3>
        </div>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
        </div>
      </div>
    );
  }

  // 문제가 없을 때
  if (problems.length === 0 && !difficultyFilter) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <RotateCcw className="w-5 h-5 text-rose-400" />
            <h3 className="text-base font-semibold text-zinc-100">틀린 문제 복습</h3>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-4">
            <Lightbulb className="w-8 h-8 text-emerald-400" />
          </div>
          <p className="text-sm text-zinc-300 mb-1">
            모든 문제를 맞췄습니다!
          </p>
          <p className="text-xs text-zinc-500">
            틀린 문제가 없거나 모두 복습 완료했습니다
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <RotateCcw className="w-5 h-5 text-rose-400" />
          <h3 className="text-base font-semibold text-zinc-100">틀린 문제 복습</h3>
          <span className="text-xs text-zinc-500">({total}개)</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => fetchProblems(false)}
          disabled={isLoading}
          className="text-zinc-400 hover:text-zinc-200 h-8 px-2"
        >
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* 필터 바 */}
      <div className="flex items-center gap-2 mb-4">
        {/* 정렬 드롭다운 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-3 bg-zinc-900 border-zinc-700 hover:bg-zinc-800 text-zinc-300"
            >
              <currentSort.icon className="w-3.5 h-3.5 mr-1.5" />
              {currentSort.label}
              <ChevronDown className="w-3.5 h-3.5 ml-1.5 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="bg-zinc-900 border-zinc-700">
            {SORT_OPTIONS.map((option) => (
              <DropdownMenuItem
                key={option.value}
                onClick={() => setSortBy(option.value as typeof sortBy)}
                className={`text-sm ${sortBy === option.value ? 'text-primary' : 'text-zinc-300'}`}
              >
                <option.icon className="w-4 h-4 mr-2" />
                {option.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* 난이도 필터 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-3 bg-zinc-900 border-zinc-700 hover:bg-zinc-800"
              style={{ color: currentDifficulty.color }}
            >
              <Filter className="w-3.5 h-3.5 mr-1.5" />
              {currentDifficulty.label}
              <ChevronDown className="w-3.5 h-3.5 ml-1.5 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="bg-zinc-900 border-zinc-700">
            {DIFFICULTIES.map((diff) => (
              <DropdownMenuItem
                key={diff.value}
                onClick={() => setDifficultyFilter(diff.value)}
                className="text-sm"
                style={{ color: diff.color }}
              >
                {diff.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {error && (
        <p className="mb-4 text-xs text-red-400">{error}</p>
      )}

      {/* 필터 적용 후 결과 없음 */}
      {problems.length === 0 && difficultyFilter && (
        <div className="flex flex-col items-center justify-center py-8">
          <p className="text-sm text-zinc-400">
            해당 난이도의 틀린 문제가 없습니다
          </p>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDifficultyFilter('')}
            className="mt-2 text-primary"
          >
            필터 초기화
          </Button>
        </div>
      )}

      {/* 문제 목록 (세로 리스트) */}
      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {problems.map((problem, index) => {
            const diffConfig = getDifficultyConfig(problem.difficulty);
            const typeLabel = getProblemTypeLabel(problem.problemType);
            const relativeTime = formatRelativeTime(problem.lastAttemptAt);

            return (
              <motion.div
                key={problem.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: index * 0.03 }}
              >
                <button
                  onClick={() => setSelectedProblemId(problem.originalId || problem.id)}
                  className="w-full flex items-center gap-4 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 hover:border-rose-500/40 transition-all group text-left"
                >
                  {/* 난이도 인디케이터 */}
                  <div
                    className="w-1 h-10 rounded-full flex-shrink-0"
                    style={{ backgroundColor: diffConfig.color }}
                  />

                  {/* 문제 정보 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium text-zinc-200 truncate">
                        {problem.name}
                      </h4>
                    </div>
                    <div className="flex items-center gap-2 text-[10px]">
                      <span
                        className="px-1.5 py-0.5 rounded"
                        style={{
                          color: diffConfig.color,
                          backgroundColor: `${diffConfig.color}15`,
                        }}
                      >
                        {diffConfig.label}
                      </span>
                      {typeLabel && (
                        <span className="text-zinc-500">{typeLabel}</span>
                      )}
                      {problem.topics.slice(0, 2).map((topic) => (
                        <span key={topic} className="text-zinc-500">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 메타 정보 */}
                  <div className="flex items-center gap-4 flex-shrink-0">
                    {problem.hintsUsed > 0 && (
                      <div className="flex items-center gap-1 text-[10px] text-zinc-500">
                        <Lightbulb className="w-3 h-3" />
                        <span>{problem.hintsUsed}</span>
                      </div>
                    )}
                    {relativeTime && (
                      <span className="text-[10px] text-zinc-600 hidden sm:block">
                        {relativeTime}
                      </span>
                    )}
                    <div className="flex items-center gap-1 text-xs text-zinc-500 group-hover:text-rose-400 transition-colors">
                      <Zap className="w-3.5 h-3.5" />
                      <span className="hidden sm:inline">다시 풀기</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </div>
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* 더 보기 버튼 */}
      {hasMore && (
        <div className="mt-4 flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={handleLoadMore}
            disabled={isLoadingMore}
            className="bg-zinc-900 border-zinc-700 hover:bg-zinc-800 text-zinc-300"
          >
            {isLoadingMore ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                로딩 중...
              </>
            ) : (
              <>
                더 보기 ({problems.length} / {total})
              </>
            )}
          </Button>
        </div>
      )}

      {/* 문제 미리보기 모달 */}
      {selectedProblemId && (
        <PreviewModal
          originalId={selectedProblemId}
          onClose={() => setSelectedProblemId(null)}
        />
      )}
    </div>
  );
}
