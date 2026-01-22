'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Swords, Target, Sparkles, Gift, Check, Loader2, Coins, Star, Code2, Puzzle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { QuestProgress } from './QuestProgress';
import type { Mission, MissionConditionType } from '@/lib/api/missions';
import { CROPS, CROP_ASSET_PATH } from '@/components/farm/config/cropConfig';

interface QuestCardProps {
  quest: Mission;
  variant?: 'daily' | 'weekly';
  onClaim: (questId: string) => Promise<void>;
  index?: number;
}

// 조건 타입별 아이콘 및 색상 (실제 ProblemType과 일치)
const conditionConfig: Record<MissionConditionType, { icon: typeof Swords; color: string; label: string }> = {
  problems: { icon: Swords, color: 'text-primary', label: '문제 풀이' },
  blank: { icon: Target, color: 'text-blue-400', label: '빈칸 채우기' },
  puzzle: { icon: Puzzle, color: 'text-purple-400', label: '퍼즐' },
  guided: { icon: Sparkles, color: 'text-cyan-400', label: '가이디드' },
  implementation: { icon: Code2, color: 'text-orange-400', label: '구현' },
};


// 난이도별 스타일
const difficultyStyles: Record<string, { label: string; color: string }> = {
  easy: { label: '쉬움', color: 'text-emerald-400 border-emerald-400/30' },
  medium: { label: '보통', color: 'text-yellow-400 border-yellow-400/30' },
  hard: { label: '어려움', color: 'text-red-400 border-red-400/30' },
};

// 씨앗 코드에서 작물 정보 가져오기 (seed_carrot -> carrot)
// 보상 이미지는 성숙한 작물 이미지로 표시
function getSeedInfo(seedCode: string): { name: string; image: string } | null {
  const cropCode = seedCode.replace('seed_', '');
  const crop = CROPS[cropCode];
  if (!crop) return null;
  return {
    name: crop.nameKo,
    image: crop.ripeSprite,  // ripeSprite already has full path
  };
}

export function QuestCard({ quest, variant = 'daily', onClaim, index = 0 }: QuestCardProps) {
  const [isClaiming, setIsClaiming] = useState(false);

  const isCompleted = quest.status === 'completed';
  const isClaimed = quest.status === 'claimed';

  // 조건 타입 설정 가져오기
  const config = conditionConfig[quest.conditionType] || conditionConfig.problems;
  const Icon = config.icon;

  const handleClaim = async () => {
    if (!isCompleted || isClaiming) return;

    setIsClaiming(true);
    try {
      await onClaim(quest.id);
    } finally {
      setIsClaiming(false);
    }
  };

  // 일일 미션: 세로 카드 (그리드용)
  if (variant === 'daily') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05, duration: 0.3 }}
        className={cn(
          'relative rounded-xl overflow-hidden transition-all duration-200',
          'bg-gradient-to-br from-cyan-950/60 to-background/80 border border-cyan-500/30',
          isCompleted && !isClaimed && 'border-cyan-500/50 shadow-lg shadow-cyan-500/10',
          isClaimed && 'opacity-50'
        )}
      >
        <div className="p-4 flex flex-col h-full">
          {/* 아이콘 + 배지 */}
          <div className="flex items-start justify-between mb-3">
            <div
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center',
                isCompleted || isClaimed
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-cyan-500/20 text-cyan-400'
              )}
            >
              {isClaimed ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
            </div>
            {quest.requireAllTypes && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">
                All
              </span>
            )}
          </div>

          {/* 제목 + 설명 */}
          <h3 className="font-medium text-sm text-white mb-1">{quest.name}</h3>
          {quest.description && (
            <p className="text-[11px] text-muted-foreground mb-2 line-clamp-1">{quest.description}</p>
          )}

          {/* 보상 */}
          <div className="flex items-center gap-2 text-xs mb-3">
            {quest.rewardGold > 0 && (
              <span className="flex items-center gap-0.5 text-yellow-400">
                <Coins className="w-3.5 h-3.5" />
                {quest.rewardGold}
              </span>
            )}
            {quest.rewardXp > 0 && (
              <span className="flex items-center gap-0.5 text-blue-400">
                <Star className="w-3.5 h-3.5" />
                {quest.rewardXp}
              </span>
            )}
            {quest.rewardSeeds && Object.entries(quest.rewardSeeds).map(([seedCode, amount]) => {
              const seedInfo = getSeedInfo(seedCode);
              if (!seedInfo) return null;
              return (
                <span key={seedCode} className="flex items-center gap-0.5 text-emerald-400" title={`${seedInfo.name} 씨앗`}>
                  <span className="bg-white/15 p-0.5 rounded"><img src={seedInfo.image} alt={seedInfo.name} className="w-4 h-4" style={{ imageRendering: 'pixelated' }} /></span>
                  {amount}
                </span>
              );
            })}
          </div>

          {/* 프로그레스 */}
          <div className="mt-auto">
            <QuestProgress
              current={quest.currentProgress}
              target={quest.targetValue}
              status={quest.status}
              variant="daily"
              showLabel={false}
              size="sm"
            />

            {/* 버튼 또는 진행률 */}
            <div className="flex items-center justify-between mt-2">
              <span className={cn(
                'text-xs font-mono',
                isClaimed ? 'text-emerald-400' : 'text-muted-foreground'
              )}>
                {quest.currentProgress}/{quest.targetValue}
              </span>

              {isCompleted && !isClaimed ? (
                <motion.button
                  onClick={handleClaim}
                  disabled={isClaiming}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    'px-3 py-1 rounded-lg text-xs font-medium',
                    'bg-cyan-500 text-black',
                    'disabled:opacity-50'
                  )}
                >
                  {isClaiming ? <Loader2 className="w-3 h-3 animate-spin" /> : '받기'}
                </motion.button>
              ) : isClaimed ? (
                <span className="text-xs text-emerald-400 font-medium">완료</span>
              ) : null}
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  // 주간 챌린지: 프리미엄 카드
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={cn(
        'relative rounded-2xl overflow-hidden transition-all duration-200',
        'bg-gradient-to-br from-yellow-950/60 via-amber-950/40 to-background/80',
        'border border-yellow-500/30',
        isCompleted && !isClaimed && 'border-yellow-500/50 shadow-lg shadow-yellow-500/10',
        isClaimed && 'opacity-50'
      )}
    >
      {/* 프리미엄 배경 효과 */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-yellow-500/5 via-transparent to-transparent" />

      {/* 골드 테두리 장식 */}
      <div className="absolute top-0 left-0 w-20 h-20">
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-yellow-400/40 to-transparent" />
        <div className="absolute top-0 left-0 h-full w-[2px] bg-gradient-to-b from-yellow-400/40 to-transparent" />
      </div>
      <div className="absolute bottom-0 right-0 w-20 h-20">
        <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-yellow-400/40 to-transparent" />
        <div className="absolute bottom-0 right-0 h-full w-[2px] bg-gradient-to-t from-yellow-400/40 to-transparent" />
      </div>

      <div className="relative p-5">
        {/* 상단: 아이콘 + 배지 */}
        <div className="flex items-start justify-between mb-3">
          <div
            className={cn(
              'w-11 h-11 rounded-xl flex items-center justify-center',
              'bg-gradient-to-br',
              isCompleted || isClaimed
                ? 'from-emerald-500/30 to-emerald-600/20 text-emerald-400'
                : 'from-yellow-500/30 to-amber-600/20 text-yellow-400'
            )}
          >
            {isClaimed ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
          </div>

          <div className="flex items-center gap-1.5">
            {quest.difficulty && (
              <span
                className={cn(
                  'text-[10px] px-2 py-0.5 rounded-full border',
                  difficultyStyles[quest.difficulty]?.color
                )}
              >
                {difficultyStyles[quest.difficulty]?.label}
              </span>
            )}
            {quest.requireAllTypes && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                All
              </span>
            )}
          </div>
        </div>

        {/* 제목 + 설명 */}
        <h3 className="font-semibold text-white mb-1">{quest.name}</h3>
        {quest.description && (
          <p className="text-xs text-muted-foreground mb-4 line-clamp-2">{quest.description}</p>
        )}

        {/* 보상 */}
        <div className="flex items-center gap-3 mb-4 p-2.5 rounded-lg bg-black/20">
          {quest.rewardGold > 0 && (
            <div className="flex items-center gap-1.5 text-yellow-400">
              <Coins className="w-4 h-4" />
              <span className="font-semibold text-sm">{quest.rewardGold}</span>
            </div>
          )}
          {quest.rewardXp > 0 && (
            <div className="flex items-center gap-1.5 text-blue-400">
              <Star className="w-4 h-4" />
              <span className="font-semibold text-sm">{quest.rewardXp}</span>
            </div>
          )}
          {quest.rewardSeeds && Object.entries(quest.rewardSeeds).map(([seedCode, amount]) => {
            const seedInfo = getSeedInfo(seedCode);
            if (!seedInfo) return null;
            return (
              <div key={seedCode} className="flex items-center gap-1.5 text-emerald-400" title={`${seedInfo.name} 씨앗`}>
                <span className="bg-white/15 p-0.5 rounded"><img src={seedInfo.image} alt={seedInfo.name} className="w-4 h-4" style={{ imageRendering: 'pixelated' }} /></span>
                <span className="font-semibold text-sm">{amount}</span>
              </div>
            );
          })}
        </div>

        {/* 프로그레스 */}
        <div className="mb-3">
          <QuestProgress
            current={quest.currentProgress}
            target={quest.targetValue}
            status={quest.status}
            variant="weekly"
            size="md"
          />
        </div>

        {/* 하단: 진행률 + 버튼 */}
        <div className="flex items-center justify-between">
          <span className={cn(
            'text-xs font-mono',
            isClaimed ? 'text-emerald-400' : 'text-muted-foreground'
          )}>
            {quest.currentProgress}/{quest.targetValue}
          </span>

          {isCompleted && !isClaimed ? (
            <motion.button
              onClick={handleClaim}
              disabled={isClaiming}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                'px-4 py-2 rounded-lg font-semibold text-sm',
                'bg-gradient-to-r from-yellow-500 to-amber-500',
                'text-black shadow-lg',
                'glow-gold-pulse',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'flex items-center gap-1.5'
              )}
            >
              {isClaiming ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Gift className="w-4 h-4" />
                  받기
                </>
              )}
            </motion.button>
          ) : isClaimed ? (
            <span className="text-emerald-400 flex items-center gap-1.5 text-sm">
              <Check className="w-4 h-4" />
              완료
            </span>
          ) : null}
        </div>
      </div>
    </motion.div>
  );
}
