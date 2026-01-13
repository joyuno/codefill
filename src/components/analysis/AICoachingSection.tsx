'use client';

import { motion } from 'framer-motion';
import {
  Bot,
  TrendingUp,
  AlertTriangle,
  ChevronRight,
  BookOpen,
  Zap,
  Target,
  Lightbulb,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { BKTMastery, TopicScore } from '@/lib/api/analysis';

interface AICoachingSectionProps {
  summaryText: string;
  studyPlan?: string;
  detailedFeedback?: string;
  commonErrorPatterns?: string[];
  // BKT 기반 분석
  strengths?: TopicScore[];
  weaknesses?: TopicScore[];
  recommendations?: string[];
  bktMastery?: BKTMastery;
}

export function AICoachingSection({
  summaryText,
  studyPlan,
  detailedFeedback,
  commonErrorPatterns = [],
  strengths = [],
  weaknesses = [],
  recommendations = [],
  bktMastery,
}: AICoachingSectionProps) {
  const hasStrengthsWeaknesses = strengths.length > 0 || weaknesses.length > 0;

  return (
    <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-zinc-800/50 bg-gradient-to-r from-amber-500/5 to-transparent">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-zinc-100">AI Coach</h2>
            <p className="text-xs text-zinc-500">Personalized learning insights</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Summary Quote */}
        {summaryText && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative pl-4 border-l-2 border-amber-500/50"
          >
            <p className="text-zinc-300 leading-relaxed italic">
              "{summaryText}"
            </p>
          </motion.div>
        )}

        {/* BKT 기반 강점/약점 */}
        {hasStrengthsWeaknesses && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* 강점 */}
            {strengths.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                    Strengths
                  </h3>
                </div>
                <div className="space-y-2">
                  {strengths.slice(0, 3).map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.15 + index * 0.05 }}
                      className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-emerald-300">{item.topic}</span>
                        <span className="text-xs font-bold text-emerald-400">
                          {Math.round(item.score * 100)}%
                        </span>
                      </div>
                      <p className="text-xs text-zinc-400 leading-relaxed">{item.insight}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* 약점 */}
            {weaknesses.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-rose-400" />
                  <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                    Areas to Improve
                  </h3>
                </div>
                <div className="space-y-2">
                  {weaknesses.slice(0, 3).map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.15 + index * 0.05 }}
                      className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/20"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-rose-300">{item.topic}</span>
                        <span className="text-xs font-bold text-rose-400">
                          {Math.round(item.score * 100)}%
                        </span>
                      </div>
                      <p className="text-xs text-zinc-400 leading-relaxed">{item.insight}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* 추천 사항 */}
        {recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                Recommendations
              </h3>
            </div>
            <div className="space-y-2">
              {recommendations.slice(0, 3).map((rec, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.05 }}
                  className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/5 border border-blue-500/10"
                >
                  <ChevronRight className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-zinc-300">{rec}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Detailed Feedback - Markdown */}
        {detailedFeedback && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                Detailed Feedback
              </h3>
            </div>
            <div className="p-4 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
              <div className="prose prose-sm prose-invert prose-zinc max-w-none
                prose-headings:text-zinc-200 prose-headings:font-semibold prose-headings:mt-4 prose-headings:mb-2
                prose-p:text-zinc-300 prose-p:leading-relaxed prose-p:my-2
                prose-li:text-zinc-300 prose-li:my-0.5
                prose-strong:text-amber-300 prose-strong:font-medium
                prose-ul:my-2 prose-ol:my-2
              ">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {detailedFeedback}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}

        {/* Common Error Patterns */}
        {commonErrorPatterns.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                Patterns to Watch
              </h3>
            </div>
            <div className="space-y-2">
              {commonErrorPatterns.slice(0, 3).map((pattern, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.35 + index * 0.05 }}
                  className="flex items-start gap-2 p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/10"
                >
                  <ChevronRight className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-zinc-400">{pattern}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Study Plan */}
        {studyPlan && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/5 to-blue-500/5 border border-emerald-500/20"
          >
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-emerald-300 mb-1">
                  Recommended Path
                </h3>
                <p className="text-sm text-zinc-300 leading-relaxed">
                  {studyPlan}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
