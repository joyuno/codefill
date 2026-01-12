'use client';

import { motion } from 'framer-motion';
import { Trophy, Flame, Target, TrendingUp, Loader2, Swords, Zap } from 'lucide-react';
import type { MyRankingSummary } from '@/lib/api/ranking';
import type { Mission } from '@/lib/api/missions';

interface StatsSummaryProps {
  ranking: MyRankingSummary | null;
  dailyMissions: Mission[];
  weeklyMissions: Mission[];
  isLoading?: boolean;
  onViewRanking: () => void;
}

// 레벨별 칭호 및 색상
interface LevelInfo {
  title: string;
  color: string;
  bgColor: string;
}

function getLevelInfo(level: number): LevelInfo {
  if (level >= 50) return { title: '전설의 마스터', color: 'text-amber-400', bgColor: 'from-amber-600 to-amber-800' };
  if (level >= 40) return { title: '대마법사', color: 'text-purple-400', bgColor: 'from-purple-600 to-purple-800' };
  if (level >= 30) return { title: '코드 현자', color: 'text-blue-400', bgColor: 'from-blue-600 to-blue-800' };
  if (level >= 20) return { title: '숙련된 기사', color: 'text-cyan-400', bgColor: 'from-cyan-600 to-cyan-800' };
  if (level >= 10) return { title: '견습 모험가', color: 'text-emerald-400', bgColor: 'from-emerald-600 to-emerald-800' };
  return { title: '초보 모험가', color: 'text-gray-400', bgColor: 'from-gray-600 to-gray-700' };
}

// 다음 레벨까지 필요한 XP 계산
function getXpForLevel(level: number): number {
  return level * 500 + (level - 1) * 100;
}

export function StatsSummary({
  ranking,
  dailyMissions,
  weeklyMissions,
  isLoading,
  onViewRanking,
}: StatsSummaryProps) {
  const dailyCompleted = dailyMissions.filter(
    (m) => m.status === 'completed' || m.status === 'claimed'
  ).length;
  const weeklyCompleted = weeklyMissions.filter(
    (m) => m.status === 'completed' || m.status === 'claimed'
  ).length;

  const dailyProgress = dailyMissions.length > 0
    ? Math.round((dailyCompleted / dailyMissions.length) * 100)
    : 0;
  const weeklyProgress = weeklyMissions.length > 0
    ? Math.round((weeklyCompleted / weeklyMissions.length) * 100)
    : 0;

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-32 rounded-xl bg-card/50 animate-pulse flex items-center justify-center"
          >
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {/* 랭크 카드 - 개선된 UI */}
      <motion.button
        onClick={onViewRanking}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98 }}
        className="relative overflow-hidden rounded-xl p-5 text-left transition-all group"
        style={{
          background: 'linear-gradient(135deg, hsl(142 50% 8%), hsl(0 0% 7%))',
          border: '1px solid hsl(142 50% 25% / 0.4)',
        }}
      >
        {/* 배경 장식 */}
        <div className="absolute top-0 right-0 w-24 h-24 opacity-10">
          <div className="absolute top-2 right-2 w-full h-full border-t-2 border-r-2 border-primary rounded-tr-xl" />
        </div>
        <div className="absolute bottom-0 left-0 w-16 h-16 opacity-10">
          <div className="absolute bottom-2 left-2 w-full h-full border-b-2 border-l-2 border-primary rounded-bl-xl" />
        </div>

        {ranking ? (
          <>
            {/* 상단: 레벨 뱃지 + 상위 % */}
            <div className="flex items-start justify-between mb-3">
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${getLevelInfo(ranking.my_level).bgColor} flex items-center justify-center border border-white/20 shadow-lg`}>
                <span className="text-lg font-bold text-white">Lv.{ranking.my_level}</span>
              </div>
              <div className="text-right">
                <span className="text-xs text-muted-foreground">상위</span>
                <p className="text-lg font-bold text-yellow-400">{ranking.global_xp_percentile}%</p>
              </div>
            </div>

            {/* 칭호 + 순위 */}
            <div className="mb-3">
              <h3 className={`text-lg font-bold ${getLevelInfo(ranking.my_level).color}`}>
                {getLevelInfo(ranking.my_level).title}
              </h3>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Trophy className="w-3.5 h-3.5 text-yellow-400" />
                <span>전체 <span className="text-white font-semibold">#{ranking.global_xp_rank.toLocaleString()}</span>위</span>
              </div>
            </div>

            {/* XP 프로그레스 바 */}
            {(() => {
              const currentLevelXp = getXpForLevel(ranking.my_level);
              const nextLevelXp = getXpForLevel(ranking.my_level + 1);
              const xpProgress = Math.min(100, ((ranking.my_total_xp - currentLevelXp) / (nextLevelXp - currentLevelXp)) * 100);
              return (
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Zap className="w-3 h-3 text-primary" />
                      {ranking.my_total_xp.toLocaleString()} XP
                    </span>
                    <span>다음 레벨까지 {(nextLevelXp - ranking.my_total_xp).toLocaleString()}</span>
                  </div>
                  <div className="h-1.5 bg-muted/30 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${xpProgress}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
                      className="h-full rounded-full quest-progress-daily quest-shimmer"
                    />
                  </div>
                </div>
              );
            })()}
          </>
        ) : (
          <>
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <Trophy className="w-5 h-5 text-primary" />
              </div>
            </div>
            <p className="text-lg font-semibold text-white mb-1">로그인 필요</p>
            <p className="text-sm text-muted-foreground">순위를 확인하세요</p>
          </>
        )}

        {/* 호버 화살표 */}
        <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <TrendingUp className="w-4 h-4 text-primary" />
        </div>
      </motion.button>

      {/* 일일 미션 진행률 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="relative overflow-hidden rounded-xl p-5"
        style={{
          background: 'linear-gradient(135deg, hsl(142 50% 8%), hsl(0 0% 7%))',
          border: '1px solid hsl(142 50% 25% / 0.4)',
        }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Target className="w-5 h-5 text-primary" />
          </div>
          <span className="text-xs text-primary/80 font-medium">오늘</span>
        </div>

        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-3xl font-bold text-white">{dailyProgress}%</span>
          <span className="text-sm text-muted-foreground">
            {dailyCompleted}/{dailyMissions.length}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mb-3">일일 미션</p>

        {/* 프로그레스 바 */}
        <div className="h-1.5 bg-muted/30 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${dailyProgress}%` }}
            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.4 }}
            className="h-full rounded-full quest-progress-daily"
          />
        </div>
      </motion.div>

      {/* 주간 챌린지 진행률 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="relative overflow-hidden rounded-xl p-5"
        style={{
          background: 'linear-gradient(135deg, hsl(45 50% 8%), hsl(0 0% 7%))',
          border: '1px solid hsl(45 50% 25% / 0.4)',
        }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
            <Flame className="w-5 h-5 text-yellow-400" />
          </div>
          <span className="text-xs text-yellow-400/80 font-medium">이번 주</span>
        </div>

        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-3xl font-bold text-white">{weeklyProgress}%</span>
          <span className="text-sm text-muted-foreground">
            {weeklyCompleted}/{weeklyMissions.length}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mb-3">주간 챌린지</p>

        {/* 프로그레스 바 */}
        <div className="h-1.5 bg-muted/30 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${weeklyProgress}%` }}
            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.5 }}
            className="h-full rounded-full quest-progress-weekly"
          />
        </div>
      </motion.div>
    </div>
  );
}
