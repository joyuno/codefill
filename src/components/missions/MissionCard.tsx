'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Check, Gift, Loader2, Coins, Star, Sprout } from 'lucide-react';
import type { Mission } from '@/lib/api/missions';

interface MissionCardProps {
  mission: Mission;
  onClaim: (missionId: string) => Promise<void>;
  isWeekly?: boolean;
}

const conditionTypeLabels: Record<string, string> = {
  problems: '문제',
  blank: '빈칸',
  puzzle: '퍼즐',
  output: '출력 예측',
  bug: '버그 찾기',
  refactor: '리팩토링',
  streak: '연속 풀이',
};

const difficultyLabels: Record<string, string> = {
  easy: '쉬움',
  medium: '보통',
  hard: '어려움',
};

export function MissionCard({ mission, onClaim, isWeekly = false }: MissionCardProps) {
  const [isClaiming, setIsClaiming] = useState(false);

  const progress = (mission.currentProgress / mission.targetValue) * 100;
  const isCompleted = mission.status === 'completed';
  const isClaimed = mission.status === 'claimed';

  const handleClaim = async () => {
    if (!isCompleted || isClaiming) return;
    setIsClaiming(true);
    try {
      await onClaim(mission.id);
    } finally {
      setIsClaiming(false);
    }
  };

  return (
    <Card
      className={cn(
        'transition-all duration-200',
        isCompleted && !isClaimed && 'ring-2 ring-green-500/50 bg-green-950/20',
        isClaimed && 'opacity-60 bg-muted/30'
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          {/* Left: Mission Info */}
          <div className="flex-1 min-w-0">
            {/* Title & Tags */}
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <h3 className="font-medium text-sm">
                {mission.name}
              </h3>
              {isWeekly && (
                <Badge variant="outline" className="text-xs bg-purple-500/10 text-purple-400 border-purple-500/30">
                  주간
                </Badge>
              )}
              {mission.difficulty && (
                <Badge variant="outline" className="text-xs">
                  {difficultyLabels[mission.difficulty] || mission.difficulty}
                </Badge>
              )}
              {isClaimed && (
                <Badge variant="secondary" className="text-xs bg-muted text-muted-foreground">
                  <Check className="w-3 h-3 mr-1" />
                  완료
                </Badge>
              )}
            </div>

            {/* Progress */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>
                  {conditionTypeLabels[mission.conditionType] || mission.conditionType}
                </span>
                <span className={cn(
                  isCompleted && 'text-green-400 font-medium'
                )}>
                  {mission.currentProgress} / {mission.targetValue}
                </span>
              </div>
              <Progress
                value={progress}
                className={cn(
                  'h-2',
                  isCompleted ? '[&>div]:bg-green-500' : '[&>div]:bg-primary'
                )}
              />
            </div>
          </div>

          {/* Right: Rewards & Button */}
          <div className="flex flex-col items-end gap-2">
            {/* Rewards */}
            <div className="flex items-center gap-2 text-xs">
              {mission.rewardGold > 0 && (
                <div className="flex items-center gap-1 text-yellow-400">
                  <Coins className="w-3.5 h-3.5" />
                  <span>{mission.rewardGold}</span>
                </div>
              )}
              {mission.rewardXp > 0 && (
                <div className="flex items-center gap-1 text-blue-400">
                  <Star className="w-3.5 h-3.5" />
                  <span>{mission.rewardXp}</span>
                </div>
              )}
              {mission.rewardSeeds && Object.keys(mission.rewardSeeds).length > 0 && (
                <div className="flex items-center gap-1 text-green-400">
                  <Sprout className="w-3.5 h-3.5" />
                  <span>
                    {Object.values(mission.rewardSeeds).reduce((a, b) => a + b, 0)}
                  </span>
                </div>
              )}
            </div>

            {/* Claim Button */}
            {isCompleted && !isClaimed && (
              <Button
                size="sm"
                onClick={handleClaim}
                disabled={isClaiming}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                {isClaiming ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Gift className="w-4 h-4 mr-1" />
                    받기
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
