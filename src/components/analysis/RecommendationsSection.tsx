'use client';

import { motion } from 'framer-motion';
import { Lightbulb, Route, CheckCircle2, ArrowRight } from 'lucide-react';

interface RecommendationsSectionProps {
  recommendations: string[];
  studyPlan?: string;
}

export function RecommendationsSection({
  recommendations,
  studyPlan,
}: RecommendationsSectionProps) {
  const hasContent = recommendations.length > 0 || studyPlan;

  if (!hasContent) {
    return (
      <motion.div
        className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          AI Recommendations
        </h3>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <div className="text-center">
            <Lightbulb className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>분석이 완료되면 맞춤 추천이 표시됩니다</p>
          </div>
        </div>
      </motion.div>
    );
  }

  // 학습 경로 파싱 (예: "추천 학습 경로: Arrays → Strings → Dynamic Programming")
  const studyPathMatch = studyPlan?.match(/추천 학습 경로:\s*(.+)/);
  const studyPathSteps = studyPathMatch
    ? studyPathMatch[1].split('→').map((s) => s.trim())
    : [];

  return (
    <motion.div
      className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
    >
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
        AI Recommendations
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 추천 리스트 */}
        {recommendations.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-yellow-400" />
              <h4 className="text-sm font-medium text-zinc-300">맞춤 조언</h4>
            </div>
            <ul className="space-y-2">
              {recommendations.map((rec, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="flex items-start gap-2 text-sm text-zinc-400"
                >
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>{rec}</span>
                </motion.li>
              ))}
            </ul>
          </div>
        )}

        {/* 학습 경로 */}
        {studyPathSteps.length > 0 ? (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Route className="w-4 h-4 text-blue-400" />
              <h4 className="text-sm font-medium text-zinc-300">추천 학습 경로</h4>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {studyPathSteps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.15 * index }}
                  className="flex items-center gap-2"
                >
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/80 border border-zinc-700/50">
                    <span
                      className="flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold"
                      style={{
                        backgroundColor: index === 0 ? 'rgba(59, 130, 246, 0.2)' : 'rgba(113, 113, 122, 0.2)',
                        color: index === 0 ? '#3b82f6' : '#71717a',
                      }}
                    >
                      {index + 1}
                    </span>
                    <span className={`text-xs ${index === 0 ? 'text-blue-400 font-medium' : 'text-zinc-400'}`}>
                      {step}
                    </span>
                  </div>
                  {index < studyPathSteps.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-zinc-600" />
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        ) : studyPlan ? (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Route className="w-4 h-4 text-blue-400" />
              <h4 className="text-sm font-medium text-zinc-300">학습 계획</h4>
            </div>
            <p className="text-sm text-zinc-400 leading-relaxed">{studyPlan}</p>
          </div>
        ) : null}
      </div>
    </motion.div>
  );
}
