'use client';

import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Lightbulb, MessageSquare } from 'lucide-react';
import type { RecentAttempt } from '@/lib/api/analysis';

interface RecentAttemptsCardProps {
  attempts: RecentAttempt[];
  analysis?: string;
}

export function RecentAttemptsCard({ attempts, analysis }: RecentAttemptsCardProps) {
  if (!attempts || attempts.length === 0) {
    return (
      <div className="p-6 text-center text-zinc-500 text-sm">
        최근 풀이 기록이 없습니다.
      </div>
    );
  }

  // 역순으로 표시 (가장 최근이 오른쪽)
  const reversedAttempts = [...attempts].reverse();

  return (
    <div className="p-4 space-y-4">
      {/* 시각화: 결과 스트릭 */}
      <div className="flex items-center justify-between gap-1">
        <span className="text-xs text-zinc-500 flex-shrink-0">과거</span>
        <div className="flex items-center gap-1 flex-1 justify-center">
          {reversedAttempts.map((attempt, index) => {
            const isCorrect = attempt.is_correct;
            const hasHints = (attempt.hints_used || 0) > 0;

            return (
              <motion.div
                key={index}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.03 }}
                className="relative group"
              >
                {/* 결과 아이콘 */}
                <div
                  className={`
                    w-8 h-8 rounded-lg flex items-center justify-center transition-transform
                    group-hover:scale-110
                    ${isCorrect
                      ? 'bg-emerald-500/20 border border-emerald-500/30'
                      : 'bg-red-500/20 border border-red-500/30'
                    }
                  `}
                >
                  {isCorrect ? (
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                </div>

                {/* 힌트 사용 표시 */}
                {hasHints && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full flex items-center justify-center">
                    <Lightbulb className="w-2 h-2 text-amber-900" />
                  </div>
                )}

                {/* 툴팁 */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-zinc-800 rounded text-xs text-zinc-300 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  {attempt.problem_name || '문제'}
                  {hasHints && ` (힌트 ${attempt.hints_used})`}
                </div>
              </motion.div>
            );
          })}
        </div>
        <span className="text-xs text-zinc-500 flex-shrink-0">최근</span>
      </div>

      {/* 범례 */}
      <div className="flex items-center justify-center gap-4 text-xs text-zinc-500">
        <span className="flex items-center gap-1">
          <CheckCircle className="w-3 h-3 text-emerald-400" />
          정답
        </span>
        <span className="flex items-center gap-1">
          <XCircle className="w-3 h-3 text-red-400" />
          오답
        </span>
        <span className="flex items-center gap-1">
          <div className="w-3 h-3 bg-amber-500 rounded-full flex items-center justify-center">
            <Lightbulb className="w-2 h-2 text-amber-900" />
          </div>
          힌트 사용
        </span>
      </div>

      {/* LLM 분석 결과 */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-3 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50"
        >
          <div className="flex items-start gap-2">
            <MessageSquare className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
            <p className="text-sm text-zinc-300 leading-relaxed">
              {analysis}
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
