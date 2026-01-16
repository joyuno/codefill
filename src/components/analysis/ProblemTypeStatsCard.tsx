'use client';

import { motion } from 'framer-motion';
import { FileCode, Puzzle, BookOpen, Code2 } from 'lucide-react';
import type { ProblemTypeStat } from '@/lib/api/analysis';

interface ProblemTypeStatsCardProps {
  stats: ProblemTypeStat[];
}

// 문제 유형별 아이콘과 한글명
const TYPE_CONFIG: Record<string, { icon: React.ElementType; label: string; color: string }> = {
  blank: { icon: FileCode, label: '빈칸채우기', color: '#3b82f6' },
  puzzle: { icon: Puzzle, label: '퍼즐', color: '#8b5cf6' },
  guided: { icon: BookOpen, label: '가이드', color: '#10b981' },
  implementation: { icon: Code2, label: '구현', color: '#f59e0b' },
};

function getTypeConfig(type: string) {
  return TYPE_CONFIG[type] || { icon: FileCode, label: type, color: '#6b7280' };
}

function getRateColor(rate: number): string {
  if (rate >= 0.7) return '#22c55e';
  if (rate >= 0.4) return '#eab308';
  return '#ef4444';
}

export function ProblemTypeStatsCard({ stats }: ProblemTypeStatsCardProps) {
  if (!stats || stats.length === 0) {
    return (
      <div className="p-6 text-center text-zinc-500 text-sm">
        문제 풀이 기록이 없습니다.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {stats.map((stat, index) => {
        const config = getTypeConfig(stat.type);
        const Icon = config.icon;
        const ratePercent = Math.round(stat.rate * 100);
        const rateColor = getRateColor(stat.rate);

        return (
          <motion.div
            key={stat.type}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-center gap-3"
          >
            {/* 아이콘 */}
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: `${config.color}20` }}
            >
              <Icon className="w-4 h-4" style={{ color: config.color }} />
            </div>

            {/* 유형명 + 카운트 */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-zinc-200 truncate">
                  {config.label}
                </span>
                <span className="text-xs text-zinc-500">
                  {stat.success}/{stat.total}
                </span>
              </div>

              {/* 프로그레스 바 */}
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${ratePercent}%` }}
                  transition={{ duration: 0.5, delay: index * 0.05 }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: rateColor }}
                />
              </div>
            </div>

            {/* 퍼센트 */}
            <span
              className="text-sm font-semibold w-12 text-right"
              style={{ color: rateColor }}
            >
              {ratePercent}%
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
