'use client';

import { motion } from 'framer-motion';
import { Trophy, Target, Flame, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { MyRankingSummary } from '@/lib/api/ranking';

interface MyRankSummaryProps {
  data: MyRankingSummary | null;
  isLoading?: boolean;
}

export function MyRankSummary({ data, isLoading }: MyRankSummaryProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="h-24 bg-muted/50 rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const stats = [
    {
      label: '전체 XP 순위',
      value: `${data.global_xp_rank.toLocaleString()}위`,
      sub: `상위 ${data.global_xp_percentile}%`,
      icon: Trophy,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
    },
    {
      label: '문제 풀이 순위',
      value: `${data.global_solve_rank.toLocaleString()}위`,
      sub: `${data.my_problems_solved}문제 풀이`,
      icon: Target,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10',
    },
    {
      label: '스트릭 순위',
      value: `${data.global_streak_rank.toLocaleString()}위`,
      sub: `최장 ${data.my_longest_streak}일`,
      icon: Flame,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
    {
      label: '총 경험치',
      value: `${data.my_total_xp.toLocaleString()} XP`,
      sub: `Lv.${data.my_level}`,
      icon: TrendingUp,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={cn(
              'relative overflow-hidden rounded-lg border border-border/50 p-4',
              stat.bgColor
            )}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
                <p className={cn('text-xl font-bold', stat.color)}>{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{stat.sub}</p>
              </div>
              <Icon className={cn('h-5 w-5', stat.color)} />
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
