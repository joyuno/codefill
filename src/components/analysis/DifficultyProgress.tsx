'use client';

import { motion } from 'framer-motion';
import { BarChart3 } from 'lucide-react';

interface DifficultyProgressProps {
  difficultySnapshot: Record<string, number>;
}

const DIFFICULTY_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  easy: { label: 'Easy', color: 'bg-green-500', bgColor: 'bg-green-500/20' },
  medium: { label: 'Medium', color: 'bg-yellow-500', bgColor: 'bg-yellow-500/20' },
  medium_hard: { label: 'Medium+', color: 'bg-orange-500', bgColor: 'bg-orange-500/20' },
  hard: { label: 'Hard', color: 'bg-red-500', bgColor: 'bg-red-500/20' },
  very_hard: { label: 'Very Hard', color: 'bg-red-600', bgColor: 'bg-red-600/20' },
};

export function DifficultyProgress({ difficultySnapshot }: DifficultyProgressProps) {
  const difficulties = Object.entries(difficultySnapshot || {});

  if (difficulties.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-border bg-card p-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold">난이도별 성공률</h3>
        </div>
        <p className="text-sm text-muted-foreground">아직 데이터가 없습니다</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-blue-500" />
        <h3 className="text-lg font-semibold">난이도별 성공률</h3>
      </div>

      <div className="space-y-4">
        {difficulties.map(([difficulty, rate], index) => {
          const config = DIFFICULTY_CONFIG[difficulty] || {
            label: difficulty,
            color: 'bg-gray-500',
            bgColor: 'bg-gray-500/20',
          };
          const percentage = Math.round(rate * 100);

          return (
            <motion.div
              key={difficulty}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              className="space-y-1"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{config.label}</span>
                <span className="text-muted-foreground">{percentage}%</span>
              </div>
              <div className={`h-3 w-full overflow-hidden rounded-full ${config.bgColor}`}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 0.5, delay: 0.3 + index * 0.05 }}
                  className={`h-full rounded-full ${config.color}`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
