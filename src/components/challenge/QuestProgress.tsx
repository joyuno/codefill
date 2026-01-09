'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface QuestProgressProps {
  current: number;
  target: number;
  status: 'active' | 'completed' | 'claimed';
  variant?: 'daily' | 'weekly';
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function QuestProgress({
  current,
  target,
  status,
  variant = 'daily',
  showLabel = true,
  size = 'md',
}: QuestProgressProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const isComplete = status === 'completed' || status === 'claimed';

  const heights = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">진행</span>
          <span
            className={cn(
              'font-mono font-medium',
              isComplete
                ? 'text-emerald-400'
                : variant === 'daily'
                ? 'text-primary'
                : 'text-yellow-400'
            )}
          >
            {current} / {target}
          </span>
        </div>
      )}

      <div
        className={cn(
          heights[size],
          'w-full rounded-full overflow-hidden',
          'bg-muted/50'
        )}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={cn(
            'h-full rounded-full relative',
            isComplete
              ? 'bg-emerald-500'
              : variant === 'daily'
              ? 'quest-progress-daily quest-shimmer'
              : 'quest-progress-weekly quest-shimmer'
          )}
        />
      </div>
    </div>
  );
}
