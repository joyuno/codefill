'use client';

import { motion } from 'framer-motion';
import { Trophy, Sprout, ChevronRight, Loader2 } from 'lucide-react';
import type { MyRankingSummary } from '@/lib/api/ranking';

interface AdventurerRankProps {
  data: MyRankingSummary | null;
  isLoading?: boolean;
  onViewRanking: () => void;
}

// 레벨별 칭호
function getLevelTitle(level: number): string {
  if (level >= 50) return '전설의 코드 마스터';
  if (level >= 40) return '대마법사';
  if (level >= 30) return '코드 현자';
  if (level >= 20) return '숙련된 기사';
  if (level >= 10) return '견습 모험가';
  return '초보 모험가';
}

// 다음 레벨까지 필요한 XP 계산 (간단한 공식)
function getXpForLevel(level: number): number {
  return level * 500 + (level - 1) * 100;
}

export function AdventurerRank({ data, isLoading, onViewRanking }: AdventurerRankProps) {
  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quest-card rounded-2xl p-6 mb-6"
      >
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </motion.div>
    );
  }

  if (!data) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quest-card rounded-2xl p-6 mb-6"
      >
        <div className="text-center py-8">
          <Sprout className="w-12 h-12 mx-auto mb-3 text-primary/50" />
          <p className="text-muted-foreground">로그인하여 모험을 시작하세요</p>
        </div>
      </motion.div>
    );
  }

  const title = getLevelTitle(data.my_level);
  const currentXp = data.my_total_xp;
  const currentLevelXp = getXpForLevel(data.my_level);
  const nextLevelXp = getXpForLevel(data.my_level + 1);
  const xpProgress = ((currentXp - currentLevelXp) / (nextLevelXp - currentLevelXp)) * 100;
  const percentile = data.global_xp_percentile;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl mb-6"
    >
      {/* 배경 그라데이션 - 어두운 녹색 톤 */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-950/80 via-emerald-900/30 to-background" />

      {/* 장식 패턴 */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-32 h-32 border-l-2 border-t-2 border-primary" />
        <div className="absolute bottom-0 right-0 w-32 h-32 border-r-2 border-b-2 border-primary" />
      </div>

      {/* 콘텐츠 */}
      <div className="relative p-6">
        {/* 헤더 */}
        <div className="flex items-center gap-2 mb-4">
          <Sprout className="w-5 h-5 text-primary" />
          <h2 className="quest-title text-sm font-semibold text-primary uppercase tracking-wider">
            Adventurer Rank
          </h2>
        </div>

        {/* 메인 정보 */}
        <div className="flex items-center gap-6">
          {/* 레벨 뱃지 */}
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-600 to-emerald-800 flex items-center justify-center border-2 border-primary/50 shadow-lg shadow-primary/20">
              <span className="text-2xl font-bold text-white">Lv.{data.my_level}</span>
            </div>
            {/* 글로우 효과 */}
            <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl -z-10" />
          </div>

          {/* 정보 */}
          <div className="flex-1 min-w-0">
            {/* 칭호 & 순위 */}
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-white truncate">{title}</h3>
              <div className="flex items-center gap-1 text-yellow-400">
                <Trophy className="w-4 h-4" />
                <span className="font-bold">#{data.global_xp_rank.toLocaleString()}</span>
              </div>
            </div>

            {/* 상위 퍼센트 */}
            <p className="text-sm text-emerald-300/80 mb-3">
              상위 <span className="text-yellow-400 font-semibold">{percentile}%</span> 모험가
            </p>

            {/* XP 프로그레스 */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-emerald-300/80">경험치</span>
                <span className="text-emerald-200/80 font-mono">
                  {currentXp.toLocaleString()} / {nextLevelXp.toLocaleString()} XP
                </span>
              </div>
              <div className="h-2.5 bg-emerald-950/50 rounded-full overflow-hidden border border-primary/20">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(xpProgress, 100)}%` }}
                  transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
                  className="h-full quest-progress-daily quest-shimmer rounded-full"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 스탯 요약 */}
        <div className="grid grid-cols-3 gap-3 mt-5 pt-5 border-t border-primary/20">
          <div className="text-center">
            <p className="text-xs text-emerald-400/80 mb-1">문제 풀이</p>
            <p className="text-lg font-bold text-white">{data.my_problems_solved}</p>
          </div>
          <div className="text-center border-x border-primary/20">
            <p className="text-xs text-emerald-400/80 mb-1">최장 스트릭</p>
            <p className="text-lg font-bold text-orange-400">{data.my_longest_streak}일</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-emerald-400/80 mb-1">풀이 순위</p>
            <p className="text-lg font-bold text-yellow-400">#{data.global_solve_rank.toLocaleString()}</p>
          </div>
        </div>

        {/* 전체 순위 보기 버튼 */}
        <motion.button
          onClick={onViewRanking}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full mt-5 py-3 px-4 rounded-xl bg-primary/20 hover:bg-primary/30 border border-primary/30 flex items-center justify-center gap-2 text-emerald-200 transition-colors group"
        >
          <Trophy className="w-4 h-4" />
          <span className="font-medium">전체 순위 보기</span>
          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </motion.button>
      </div>
    </motion.div>
  );
}
