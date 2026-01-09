'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, Shield, Target, Sparkles, Gift, Check, Loader2, Coins, Star, Sprout } from 'lucide-react';
import { cn } from '@/lib/utils';
import { QuestProgress } from './QuestProgress';
import type { Mission } from '@/lib/api/missions';

interface QuestCardProps {
  quest: Mission;
  variant?: 'daily' | 'weekly';
  onClaim: (questId: string) => Promise<void>;
  index?: number;
}

// 조건 타입별 아이콘
const conditionIcons: Record<string, typeof Swords> = {
  problems: Swords,
  blank: Target,
  puzzle: Sparkles,
  output: Target,
  bug: Shield,
  refactor: Sparkles,
};

// 난이도별 스타일
const difficultyStyles: Record<string, { label: string; color: string }> = {
  easy: { label: '쉬움', color: 'text-emerald-400 border-emerald-400/30' },
  medium: { label: '보통', color: 'text-yellow-400 border-yellow-400/30' },
  hard: { label: '어려움', color: 'text-red-400 border-red-400/30' },
};

export function QuestCard({ quest, variant = 'daily', onClaim, index = 0 }: QuestCardProps) {
  const [isClaiming, setIsClaiming] = useState(false);

  const isCompleted = quest.status === 'completed';
  const isClaimed = quest.status === 'claimed';
  const Icon = conditionIcons[quest.conditionType] || Swords;

  const handleClaim = async () => {
    if (!isCompleted || isClaiming) return;

    setIsClaiming(true);
    try {
      await onClaim(quest.id);
    } finally {
      setIsClaiming(false);
    }
  };

  // 일일 미션: 컴팩트한 가로 카드
  if (variant === 'daily') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05, duration: 0.3 }}
        className={cn(
          'relative rounded-xl overflow-hidden transition-all duration-200',
          'quest-card quest-card-daily',
          isCompleted && !isClaimed && 'quest-card-claimable-daily',
          isClaimed && 'opacity-50'
        )}
      >
        <div className="p-3">
          {/* 상단: 아이콘 + 제목 + 보상 */}
          <div className="flex items-center gap-3 mb-2">
            <div
              className={cn(
                'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                isCompleted || isClaimed
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-primary/20 text-primary'
              )}
            >
              {isClaimed ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm text-white truncate">{quest.name}</h3>
            </div>

            {/* 보상 */}
            <div className="flex items-center gap-2 text-xs flex-shrink-0">
              {quest.rewardGold > 0 && (
                <span className="flex items-center gap-0.5 text-yellow-400">
                  <Coins className="w-3 h-3" />
                  {quest.rewardGold}
                </span>
              )}
              {quest.rewardXp > 0 && (
                <span className="flex items-center gap-0.5 text-blue-400">
                  <Star className="w-3 h-3" />
                  {quest.rewardXp}
                </span>
              )}
            </div>
          </div>

          {/* 프로그레스 + 버튼 */}
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <QuestProgress
                current={quest.currentProgress}
                target={quest.targetValue}
                status={quest.status}
                variant="daily"
                showLabel={false}
                size="sm"
              />
            </div>

            {/* 진행률 텍스트 또는 버튼 */}
            {isCompleted && !isClaimed ? (
              <motion.button
                onClick={handleClaim}
                disabled={isClaiming}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-medium',
                  'bg-primary text-primary-foreground',
                  'glow-primary-pulse',
                  'disabled:opacity-50'
                )}
              >
                {isClaiming ? <Loader2 className="w-3 h-3 animate-spin" /> : '받기'}
              </motion.button>
            ) : (
              <span className={cn(
                'text-xs font-mono',
                isClaimed ? 'text-emerald-400' : 'text-muted-foreground'
              )}>
                {isClaimed ? '완료' : `${quest.currentProgress}/${quest.targetValue}`}
              </span>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  // 주간 챌린지: 큰 세로 카드
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={cn(
        'relative rounded-2xl overflow-hidden transition-all duration-200',
        'quest-card quest-card-weekly',
        isCompleted && !isClaimed && 'quest-card-claimable-weekly',
        isClaimed && 'opacity-50'
      )}
    >
      {/* 골드 테두리 장식 */}
      <div className="absolute top-0 left-0 w-16 h-16 opacity-20">
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-yellow-400 to-transparent" />
        <div className="absolute top-0 left-0 h-full w-[2px] bg-gradient-to-b from-yellow-400 to-transparent" />
      </div>
      <div className="absolute bottom-0 right-0 w-16 h-16 opacity-20">
        <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-yellow-400 to-transparent" />
        <div className="absolute bottom-0 right-0 h-full w-[2px] bg-gradient-to-t from-yellow-400 to-transparent" />
      </div>

      <div className="p-5">
        {/* 상단: 아이콘 + 제목 + 난이도 */}
        <div className="flex items-start gap-4 mb-4">
          <div
            className={cn(
              'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
              isCompleted || isClaimed
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'bg-yellow-500/20 text-yellow-400'
            )}
          >
            {isClaimed ? <Check className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-lg text-white">{quest.name}</h3>
              {quest.difficulty && (
                <span
                  className={cn(
                    'text-[10px] px-1.5 py-0.5 rounded border',
                    difficultyStyles[quest.difficulty]?.color
                  )}
                >
                  {difficultyStyles[quest.difficulty]?.label}
                </span>
              )}
            </div>
            {quest.description && (
              <p className="text-sm text-muted-foreground">{quest.description}</p>
            )}
          </div>
        </div>

        {/* 프로그레스 */}
        <div className="mb-4">
          <QuestProgress
            current={quest.currentProgress}
            target={quest.targetValue}
            status={quest.status}
            variant="weekly"
            size="lg"
          />
        </div>

        {/* 하단: 보상 + 버튼 */}
        <div className="flex items-center justify-between">
          {/* 보상 */}
          <div className="flex items-center gap-4">
            {quest.rewardGold > 0 && (
              <div className="flex items-center gap-1.5 text-yellow-400">
                <Coins className="w-5 h-5" />
                <span className="font-semibold">{quest.rewardGold}</span>
              </div>
            )}
            {quest.rewardXp > 0 && (
              <div className="flex items-center gap-1.5 text-blue-400">
                <Star className="w-5 h-5" />
                <span className="font-semibold">{quest.rewardXp}</span>
              </div>
            )}
            {quest.rewardSeeds && Object.keys(quest.rewardSeeds).length > 0 && (
              <div className="flex items-center gap-1.5 text-emerald-400">
                <Sprout className="w-5 h-5" />
                <span className="font-semibold">
                  {Object.values(quest.rewardSeeds).reduce((a, b) => a + b, 0)}
                </span>
              </div>
            )}
          </div>

          {/* 버튼 */}
          {isCompleted && !isClaimed ? (
            <motion.button
              onClick={handleClaim}
              disabled={isClaiming}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                'px-5 py-2.5 rounded-xl font-semibold',
                'bg-gradient-to-r from-yellow-500 to-amber-500',
                'text-black shadow-lg',
                'glow-gold-pulse',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'flex items-center gap-2'
              )}
            >
              {isClaiming ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Gift className="w-4 h-4" />
                  보상 받기
                </>
              )}
            </motion.button>
          ) : isClaimed ? (
            <span className="text-emerald-400 flex items-center gap-1.5 text-sm">
              <Check className="w-4 h-4" />
              수령 완료
            </span>
          ) : null}
        </div>
      </div>
    </motion.div>
  );
}
