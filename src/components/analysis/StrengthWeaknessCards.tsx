'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import type { TopicScore } from '@/lib/api';

interface StrengthWeaknessCardsProps {
  strengths: TopicScore[];
  weaknesses: TopicScore[];
}

export function StrengthWeaknessCards({ strengths, weaknesses }: StrengthWeaknessCardsProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* Strengths */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-xl border border-primary/30 bg-primary/5 p-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <div className="rounded-lg bg-primary/10 p-2">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-primary">강점 영역</h3>
        </div>

        {strengths.length > 0 ? (
          <div className="space-y-3">
            {strengths.map((item, index) => (
              <motion.div
                key={item.topic}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
                className="space-y-1"
              >
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{item.topic}</span>
                  <span className="text-primary">{Math.round(item.score * 100)}%</span>
                </div>
                <Progress value={item.score * 100} className="h-2 bg-primary/20" />
              </motion.div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">아직 강점 영역이 없습니다</p>
        )}
      </motion.div>

      {/* Weaknesses */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-orange-500/30 bg-orange-500/5 p-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <div className="rounded-lg bg-orange-500/10 p-2">
            <TrendingDown className="h-5 w-5 text-orange-500" />
          </div>
          <h3 className="text-lg font-semibold text-orange-500">개선 필요 영역</h3>
        </div>

        {weaknesses.length > 0 ? (
          <div className="space-y-3">
            {weaknesses.map((item, index) => (
              <motion.div
                key={item.topic}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + index * 0.05 }}
                className="space-y-1"
              >
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{item.topic}</span>
                  <span className="text-orange-500">{Math.round(item.score * 100)}%</span>
                </div>
                <Progress
                  value={item.score * 100}
                  className="h-2 bg-orange-500/20 [&>div]:bg-orange-500"
                />
              </motion.div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">모든 영역에서 고르게 잘하고 있어요!</p>
        )}
      </motion.div>
    </div>
  );
}
