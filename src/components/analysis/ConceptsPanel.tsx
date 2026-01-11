'use client';

import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, Sparkles, Brain } from 'lucide-react';

interface ConceptsPanelProps {
  conceptsStruggling: string[];
  conceptsLearned: string[];
  breakthroughMoments?: string[];
}

export function ConceptsPanel({
  conceptsStruggling,
  conceptsLearned,
  breakthroughMoments = [],
}: ConceptsPanelProps) {
  const hasContent = conceptsStruggling.length > 0 || conceptsLearned.length > 0;

  if (!hasContent) {
    return (
      <motion.div
        className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Learning Progress
        </h3>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <div className="text-center">
            <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>학습 기록이 쌓이면 개념별 진행 상황이 표시됩니다</p>
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
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
        Learning Progress
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 어려워한 개념 */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-red-400">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">어려워한 개념</span>
            <span className="text-xs text-zinc-500">({conceptsStruggling.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {conceptsStruggling.length > 0 ? (
              conceptsStruggling.map((concept, index) => (
                <motion.span
                  key={concept}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="px-2.5 py-1 text-xs rounded-full bg-red-500/10 text-red-400 border border-red-500/20"
                >
                  {concept}
                </motion.span>
              ))
            ) : (
              <span className="text-xs text-zinc-600">기록 없음</span>
            )}
          </div>
        </div>

        {/* 이해한 개념 */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-sm font-medium">이해한 개념</span>
            <span className="text-xs text-zinc-500">({conceptsLearned.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {conceptsLearned.length > 0 ? (
              conceptsLearned.map((concept, index) => (
                <motion.span
                  key={concept}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="px-2.5 py-1 text-xs rounded-full bg-green-500/10 text-green-400 border border-green-500/20"
                >
                  {concept}
                </motion.span>
              ))
            ) : (
              <span className="text-xs text-zinc-600">기록 없음</span>
            )}
          </div>
        </div>
      </div>

      {/* 돌파 순간 */}
      {breakthroughMoments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-zinc-700/50">
          <div className="flex items-center gap-2 text-yellow-400 mb-3">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm font-medium">Breakthrough Moments</span>
          </div>
          <div className="space-y-2">
            {breakthroughMoments.slice(0, 3).map((moment, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + 0.1 * index }}
                className="flex items-start gap-2 text-xs text-zinc-400"
              >
                <span className="text-yellow-500 mt-0.5">*</span>
                <span>{moment}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
