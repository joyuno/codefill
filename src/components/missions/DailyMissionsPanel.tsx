'use client';

import { MissionCard } from './MissionCard';
import { Loader2, Calendar, Trophy } from 'lucide-react';
import type { DailyMissionsResponse } from '@/lib/api/missions';

interface DailyMissionsPanelProps {
  data: DailyMissionsResponse | null;
  isLoading?: boolean;
  onClaim: (missionId: string) => Promise<void>;
}

export function DailyMissionsPanel({ data, isLoading, onClaim }: DailyMissionsPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data || data.missions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <Calendar className="h-12 w-12 mb-4 opacity-50" />
        <p className="text-lg font-medium">오늘의 미션이 없습니다</p>
        <p className="text-sm">잠시 후 다시 시도해주세요.</p>
      </div>
    );
  }

  const completedCount = data.missions.filter(m => m.status === 'completed' || m.status === 'claimed').length;
  const claimedCount = data.missions.filter(m => m.status === 'claimed').length;

  return (
    <div className="space-y-4">
      {/* Header Stats */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-yellow-500" />
          <span className="text-muted-foreground">
            진행률: <span className="text-foreground font-medium">{completedCount}/{data.missions.length}</span>
          </span>
        </div>
        {claimedCount > 0 && (
          <span className="text-green-500 text-xs">
            {claimedCount}개 보상 수령 완료
          </span>
        )}
      </div>

      {/* Mission List */}
      <div className="space-y-3">
        {data.missions.map((mission) => (
          <MissionCard
            key={mission.id}
            mission={mission}
            onClaim={onClaim}
            isWeekly={false}
          />
        ))}
      </div>
    </div>
  );
}
