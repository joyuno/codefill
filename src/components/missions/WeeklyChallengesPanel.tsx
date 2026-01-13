'use client';

import { MissionCard } from './MissionCard';
import { Loader2, CalendarRange, Award } from 'lucide-react';
import type { WeeklyChallengesResponse } from '@/lib/api/missions';

interface WeeklyChallengesPanelProps {
  data: WeeklyChallengesResponse | null;
  isLoading?: boolean;
  onClaim: (missionId: string) => Promise<void>;
}

export function WeeklyChallengesPanel({ data, isLoading, onClaim }: WeeklyChallengesPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data || data.challenges.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <CalendarRange className="h-12 w-12 mb-4 opacity-50" />
        <p className="text-lg font-medium">이번 주 챌린지가 없습니다</p>
        <p className="text-sm">잠시 후 다시 시도해주세요.</p>
      </div>
    );
  }

  const completedCount = data.challenges.filter(c => c.status === 'completed' || c.status === 'claimed').length;
  const claimedCount = data.challenges.filter(c => c.status === 'claimed').length;

  // 다음 월요일까지 남은 시간 계산 (주간 리셋 기준)
  const now = new Date();
  const dayOfWeek = now.getDay();
  const daysUntilMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek;

  return (
    <div className="space-y-4">
      {/* Header Stats */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <Award className="w-4 h-4 text-purple-500" />
          <span className="text-muted-foreground">
            챌린지 진행: <span className="text-foreground font-medium">{completedCount}/{data.challenges.length}</span>
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {daysUntilMonday}일 남음
        </span>
      </div>

      {/* Challenge List */}
      <div className="space-y-3">
        {data.challenges.map((challenge) => (
          <MissionCard
            key={challenge.id}
            mission={challenge}
            onClaim={onClaim}
            isWeekly={true}
          />
        ))}
      </div>

      {claimedCount > 0 && (
        <p className="text-center text-green-500 text-xs">
          {claimedCount}개 챌린지 보상 수령 완료
        </p>
      )}
    </div>
  );
}
