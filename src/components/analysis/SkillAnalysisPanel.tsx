'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Lightbulb, ChevronRight } from 'lucide-react';

interface TopicScore {
  topic: string;
  score: number;
  insight?: string;
}

interface SkillAnalysisPanelProps {
  strengths: TopicScore[];
  weaknesses: TopicScore[];
  recommendations: string[];
}

export function SkillAnalysisPanel({
  strengths,
  weaknesses,
  recommendations,
}: SkillAnalysisPanelProps) {
  const topStrengths = strengths.slice(0, 3);
  const topWeaknesses = weaknesses.slice(0, 3);
  const topRecommendations = recommendations.slice(0, 3);

  return (
    <div className="flex flex-col h-full">
      {/* 강점 */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        className="p-5 border-b border-zinc-800/50"
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <h4 className="text-sm font-semibold text-zinc-200">강점 영역</h4>
        </div>
        <div className="space-y-2.5">
          {topStrengths.length > 0 ? (
            topStrengths.map((s, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-2.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-zinc-100">{s.topic}</span>
                    <span className="text-xs text-emerald-400 font-mono px-1.5 py-0.5 rounded bg-emerald-500/10">
                      {Math.round(s.score * 100)}%
                    </span>
                  </div>
                  {s.insight && (
                    <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{s.insight}</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-zinc-600">아직 데이터가 부족합니다</p>
          )}
        </div>
      </motion.div>

      {/* 보완 필요 */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="p-5 border-b border-zinc-800/50"
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <TrendingDown className="w-4 h-4 text-amber-400" />
          </div>
          <h4 className="text-sm font-semibold text-zinc-200">보완 필요</h4>
        </div>
        <div className="space-y-2.5">
          {topWeaknesses.length > 0 ? (
            topWeaknesses.map((w, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-zinc-100">{w.topic}</span>
                    <span className="text-xs text-amber-400 font-mono px-1.5 py-0.5 rounded bg-amber-500/10">
                      {Math.round(w.score * 100)}%
                    </span>
                  </div>
                  {w.insight && (
                    <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{w.insight}</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-zinc-600">모든 영역에서 잘하고 있어요!</p>
          )}
        </div>
      </motion.div>

      {/* 추천 */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
        className="p-5 flex-1"
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Lightbulb className="w-4 h-4 text-blue-400" />
          </div>
          <h4 className="text-sm font-semibold text-zinc-200">AI 추천</h4>
        </div>
        <div className="space-y-2">
          {topRecommendations.length > 0 ? (
            topRecommendations.map((rec, i) => (
              <div
                key={i}
                className="flex items-start gap-2 p-2.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-800/80 transition-colors"
              >
                <ChevronRight className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-zinc-300 leading-relaxed">{rec}</p>
              </div>
            ))
          ) : (
            <p className="text-xs text-zinc-600">추천 사항이 없습니다</p>
          )}
        </div>
      </motion.div>
    </div>
  );
}
