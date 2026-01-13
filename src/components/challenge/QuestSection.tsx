'use client';

import { motion } from 'framer-motion';
import { Target, Trophy, Loader2, Coins, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { QuestCard } from './QuestCard';
import type { Mission } from '@/lib/api/missions';

interface QuestSectionProps {
  title: string;
  variant: 'daily' | 'weekly';
  quests: Mission[];
  isLoading?: boolean;
  onClaim: (questId: string) => Promise<void>;
  remainingTime?: string;
  className?: string;
}

export function QuestSection({
  title,
  variant,
  quests,
  isLoading,
  onClaim,
  remainingTime,
  className,
}: QuestSectionProps) {
  const completedCount = quests.filter(
    (q) => q.status === 'completed' || q.status === 'claimed'
  ).length;
  const claimedCount = quests.filter((q) => q.status === 'claimed').length;
  const claimableCount = quests.filter((q) => q.status === 'completed').length;
  const totalGoldEarned = quests
    .filter((q) => q.status === 'claimed')
    .reduce((sum, q) => sum + q.rewardGold, 0);

  const Icon = variant === 'daily' ? Target : Trophy;

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: variant === 'daily' ? 0.1 : 0.2 }}
      className={cn('', className)}
    >
      {/* 섹션 헤더 */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'w-10 h-10 rounded-xl flex items-center justify-center',
              variant === 'daily'
                ? 'bg-cyan-500/20 text-cyan-400'
                : 'bg-yellow-500/20 text-yellow-400'
            )}
          >
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2
                className={cn(
                  'text-lg font-semibold',
                  variant === 'daily' ? 'text-cyan-400' : 'text-yellow-400'
                )}
              >
                {title}
              </h2>
              {claimableCount > 0 && (
                <span
                  className={cn(
                    'px-2 py-0.5 text-[10px] font-bold rounded-full animate-pulse',
                    variant === 'daily'
                      ? 'bg-cyan-500 text-black'
                      : 'bg-yellow-500 text-black'
                  )}
                >
                  {claimableCount}
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              <span className="font-medium text-white">{completedCount}</span>/{quests.length} 완료
              {claimedCount > 0 && (
                <span className="text-emerald-400 ml-2">
                  +{claimedCount} 수령
                </span>
              )}
            </p>
          </div>
        </div>

        {/* 우측 정보 */}
        <div className="flex items-center gap-3">
          {totalGoldEarned > 0 && (
            <div className="flex items-center gap-1.5 text-yellow-400 text-sm bg-yellow-500/10 px-3 py-1.5 rounded-lg">
              <Coins className="w-4 h-4" />
              <span className="font-semibold">+{totalGoldEarned}</span>
            </div>
          )}

          {variant === 'weekly' && remainingTime && (
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/50 px-3 py-1.5 rounded-lg border border-border/50">
              <Clock className="w-3.5 h-3.5" />
              <span className="font-medium">{remainingTime}</span>
            </div>
          )}
        </div>
      </div>

      {/* 퀘스트 목록 */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className={cn(
              'w-8 h-8 animate-spin',
              variant === 'daily' ? 'text-cyan-400' : 'text-yellow-400'
            )} />
            <p className="text-sm text-muted-foreground">퀘스트를 불러오는 중...</p>
          </div>
        </div>
      ) : quests.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center quest-card rounded-xl">
          <Icon className="w-10 h-10 text-muted-foreground/30 mb-3" />
          <p className="text-muted-foreground text-sm">
            {variant === 'daily'
              ? '오늘의 퀘스트가 아직 없습니다'
              : '이번 주 챌린지가 아직 없습니다'}
          </p>
        </div>
      ) : variant === 'daily' ? (
        // 일일 미션: 가로 그리드 (3개)
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {quests.map((quest, index) => (
            <QuestCard
              key={quest.id}
              quest={quest}
              variant="daily"
              onClaim={onClaim}
              index={index}
            />
          ))}
        </div>
      ) : (
        // 주간 챌린지: 프리미엄 카드 그리드
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {quests.map((quest, index) => (
            <QuestCard
              key={quest.id}
              quest={quest}
              variant="weekly"
              onClaim={onClaim}
              index={index}
            />
          ))}
        </div>
      )}
    </motion.section>
  );
}
