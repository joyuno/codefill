'use client';

import { Button } from '@/components/ui/button';
import { Sparkles, Target, Flame } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RankingType, RankingPeriod } from '@/lib/api/ranking';

interface RankingFilterProps {
  period: RankingPeriod;
  value: RankingType;
  onChange: (value: RankingType) => void;
}

export function RankingFilter({ period, value, onChange }: RankingFilterProps) {
  // 주간/월간은 스트릭 필터 없음
  const showStreak = period === 'global';

  const filters: { value: RankingType; label: string; icon: React.ReactNode }[] = [
    {
      value: 'xp',
      label: 'XP',
      icon: <Sparkles className="h-4 w-4" />,
    },
    {
      value: 'problems',
      label: '문제 풀이',
      icon: <Target className="h-4 w-4" />,
    },
    ...(showStreak
      ? [
          {
            value: 'streak' as RankingType,
            label: '스트릭',
            icon: <Flame className="h-4 w-4" />,
          },
        ]
      : []),
  ];

  return (
    <div className="flex items-center gap-2">
      {filters.map((filter) => (
        <Button
          key={filter.value}
          variant={value === filter.value ? 'default' : 'outline'}
          size="sm"
          onClick={() => onChange(filter.value)}
          className={cn(
            'gap-2',
            value === filter.value && 'bg-primary text-primary-foreground'
          )}
        >
          {filter.icon}
          <span className="hidden sm:inline">{filter.label}</span>
        </Button>
      ))}
    </div>
  );
}
