'use client';

import { motion } from 'framer-motion';
import { Sprout, Trophy, Loader2, Coins, Clock } from 'lucide-react';
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
}

export function QuestSection({
  title,
  variant,
  quests,
  isLoading,
  onClaim,
  remainingTime,
}: QuestSectionProps) {
  const completedCount = quests.filter(
    (q) => q.status === 'completed' || q.status === 'claimed'
  ).length;
  const claimedCount = quests.filter((q) => q.status === 'claimed').length;
  const claimableCount = quests.filter((q) => q.status === 'completed').length;
  const totalGoldEarned = quests
    .filter((q) => q.status === 'claimed')
    .reduce((sum, q) => sum + q.rewardGold, 0);

  const Icon = variant === 'daily' ? Sprout : Trophy;

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: variant === 'daily' ? 0.2 : 0.4 }}
      className="mb-8"
    >
      {/* 섹션 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'w-9 h-9 rounded-xl flex items-center justify-center',
              variant === 'daily'
                ? 'bg-primary/20 text-primary'
                : 'bg-yellow-500/20 text-yellow-400'
            )}
          >
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2
                className={cn(
                  'font-semibold',
                  variant === 'daily' ? 'text-primary' : 'text-yellow-400'
                )}
              >
                {title}
              </h2>
              {claimableCount > 0 && (
                <span
                  className={cn(
                    'px-1.5 py-0.5 text-[10px] font-medium rounded-full',
                    variant === 'daily'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-yellow-500 text-black'
                  )}
                >
                  {claimableCount}
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {completedCount}/{quests.length} 완료
              {claimedCount > 0 && (
                <span className="text-emerald-400 ml-1">
                  · {claimedCount} 수령
                </span>
              )}
            </p>
          </div>
        </div>

        {/* 우측 정보 */}
        <div className="flex items-center gap-3">
          {totalGoldEarned > 0 && (
            <div className="flex items-center gap-1 text-yellow-400 text-sm">
              <Coins className="w-4 h-4" />
              <span className="font-medium">+{totalGoldEarned}</span>
            </div>
          )}

          {variant === 'weekly' && remainingTime && (
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded-lg">
              <Clock className="w-3.5 h-3.5" />
              <span>{remainingTime}</span>
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
              variant === 'daily' ? 'text-primary' : 'text-yellow-400'
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
        // 일일 미션: 세로 리스트 (컴팩트한 카드)
        <div className="space-y-2">
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
        // 주간 챌린지: 큰 카드 리스트
        <div className="space-y-4">
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
