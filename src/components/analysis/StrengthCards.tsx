'use client';

import { motion } from 'framer-motion';
import { Trophy, Star, TrendingUp } from 'lucide-react';
import Link from 'next/link';

interface TopicScore {
  topic: string;
  score: number;
  insight?: string;
}

interface StrengthCardsProps {
  strengths: TopicScore[];
  maxCards?: number;
}

// 점수에 따른 등급과 색상
function getGradeInfo(score: number) {
  if (score >= 0.9) return { grade: 'S', color: '#fbbf24', bgColor: 'rgba(251, 191, 36, 0.1)' };
  if (score >= 0.8) return { grade: 'A', color: '#22c55e', bgColor: 'rgba(34, 197, 94, 0.1)' };
  if (score >= 0.7) return { grade: 'B+', color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.1)' };
  if (score >= 0.6) return { grade: 'B', color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.08)' };
  return { grade: 'C', color: '#a855f7', bgColor: 'rgba(168, 85, 247, 0.1)' };
}

export function StrengthCards({ strengths, maxCards = 6 }: StrengthCardsProps) {
  const sortedStrengths = [...strengths]
    .sort((a, b) => b.score - a.score)
    .slice(0, maxCards);

  if (sortedStrengths.length === 0) {
    return (
      <motion.div
        className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Your Strengths
        </h3>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <div className="text-center">
            <Trophy className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>강점이 분석되면 여기에 표시됩니다</p>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
          Your Strengths
        </h3>
        <div className="flex items-center gap-1 text-green-400">
          <Trophy className="w-4 h-4" />
          <span className="text-xs">{sortedStrengths.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {sortedStrengths.map((strength, index) => {
          const gradeInfo = getGradeInfo(strength.score);
          const isTop = index === 0;

          return (
            <motion.div
              key={strength.topic}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * index }}
              className={`relative p-3 rounded-lg border transition-all duration-200 hover:scale-[1.02] ${
                isTop
                  ? 'bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/30'
                  : 'bg-zinc-900/50 border-zinc-700/50 hover:border-zinc-600'
              }`}
            >
              {/* 1등 뱃지 */}
              {isTop && (
                <div className="absolute -top-2 -right-2">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-yellow-500 text-black">
                    <Star className="w-3.5 h-3.5" fill="currentColor" />
                  </div>
                </div>
              )}

              {/* 등급 뱃지 */}
              <div className="flex items-center justify-between mb-2">
                <span
                  className="text-lg font-bold"
                  style={{ color: gradeInfo.color }}
                >
                  {gradeInfo.grade}
                </span>
                <span className="text-sm font-bold text-zinc-100">
                  {Math.round(strength.score * 100)}%
                </span>
              </div>

              {/* 토픽 이름 */}
              <h4 className="text-sm font-medium text-zinc-200 truncate mb-1">
                {strength.topic}
              </h4>

              {/* 인사이트 */}
              {strength.insight && (
                <p className="text-xs text-zinc-500 line-clamp-2 mt-1">
                  {strength.insight}
                </p>
              )}

              {/* 프로그레스 바 */}
              <div className="mt-2 h-1 bg-zinc-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: gradeInfo.color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${strength.score * 100}%` }}
                  transition={{ delay: 0.3 + 0.1 * index, duration: 0.5 }}
                />
              </div>

              {/* 연습하기 링크 */}
              <Link
                href={`/problems?topic=${encodeURIComponent(strength.topic)}`}
                className="mt-2 flex items-center gap-1 text-xs text-zinc-500 hover:text-primary transition-colors"
              >
                <TrendingUp className="w-3 h-3" />
                <span>더 연습하기</span>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
