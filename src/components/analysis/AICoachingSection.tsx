'use client';

import { motion } from 'framer-motion';
import {
  Bot,
  TrendingUp,
  Flame,
  AlertTriangle,
  ChevronRight,
  BookOpen,
  Keyboard,
  GitBranch,
  Brain,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ErrorAnalysis } from '@/lib/api/analysis';

interface AICoachingSectionProps {
  summaryText: string;
  studyPlan?: string;
  detailedFeedback?: string;
  breakthroughMoments?: string[];
  commonErrorPatterns?: string[];
  errorAnalysis?: ErrorAnalysis;
}

// SRK 에러 타입별 설정
const ERROR_TYPE_CONFIG = {
  skill: {
    label: 'Skill (실수)',
    icon: Keyboard,
    color: '#f59e0b',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/20',
    description: '타이핑 실수, 부주의 오류',
  },
  rule: {
    label: 'Rule (규칙)',
    icon: GitBranch,
    color: '#3b82f6',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    description: '경계값, 연산자 오류',
  },
  knowledge: {
    label: 'Knowledge (개념)',
    icon: Brain,
    color: '#ef4444',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/20',
    description: '개념 이해 부족',
  },
};

export function AICoachingSection({
  summaryText,
  studyPlan,
  detailedFeedback,
  breakthroughMoments = [],
  commonErrorPatterns = [],
  errorAnalysis,
}: AICoachingSectionProps) {
  const hasErrorAnalysis = errorAnalysis && errorAnalysis.dominant_type && Object.keys(errorAnalysis.patterns).length > 0;

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

        {/* Breakthrough Moments */}
        {breakthroughMoments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                Breakthrough Moments
              </h3>
            </div>
            <div className="space-y-2">
              {breakthroughMoments.slice(0, 3).map((moment, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="flex items-start gap-2 p-3 rounded-lg bg-orange-500/5 border border-orange-500/10"
                >
                  <ChevronRight className="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-zinc-300">{moment}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Common Error Patterns (legacy) */}
        {commonErrorPatterns.length > 0 && !hasErrorAnalysis && (
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

        {/* SRK Error Analysis (새로운 프레임워크 기반) */}
        {hasErrorAnalysis && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                  Error Pattern Analysis
                </h3>
              </div>
              {errorAnalysis.total_errors && (
                <span className="text-xs text-zinc-500">
                  총 {errorAnalysis.total_errors}개 오류 분석
                </span>
              )}
            </div>

            {/* Dominant Type Badge */}
            {errorAnalysis.dominant_type && ERROR_TYPE_CONFIG[errorAnalysis.dominant_type] && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.35 }}
                className={`p-4 rounded-xl ${ERROR_TYPE_CONFIG[errorAnalysis.dominant_type].bgColor} border ${ERROR_TYPE_CONFIG[errorAnalysis.dominant_type].borderColor}`}
              >
                <div className="flex items-start gap-3">
                  {(() => {
                    const config = ERROR_TYPE_CONFIG[errorAnalysis.dominant_type!];
                    const IconComponent = config.icon;
                    return (
                      <>
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{ backgroundColor: `${config.color}20` }}
                        >
                          <IconComponent className="w-4 h-4" style={{ color: config.color }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span
                              className="text-sm font-semibold"
                              style={{ color: config.color }}
                            >
                              주요 오류: {config.label}
                            </span>
                          </div>
                          <p className="text-sm text-zinc-400 leading-relaxed">
                            {errorAnalysis.summary}
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </motion.div>
            )}

            {/* Error Type Distribution */}
            <div className="grid grid-cols-3 gap-2">
              {Object.entries(errorAnalysis.patterns).map(([type, data], index) => {
                const config = ERROR_TYPE_CONFIG[type as keyof typeof ERROR_TYPE_CONFIG];
                if (!config || !data) return null;

                const IconComponent = config.icon;
                const percentage = Math.round(data.rate * 100);

                return (
                  <motion.div
                    key={type}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className={`p-3 rounded-lg ${config.bgColor} border ${config.borderColor} text-center`}
                  >
                    <IconComponent
                      className="w-4 h-4 mx-auto mb-1"
                      style={{ color: config.color }}
                    />
                    <div
                      className="text-lg font-bold"
                      style={{ color: config.color }}
                    >
                      {percentage}%
                    </div>
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wide">
                      {type}
                    </div>
                    <div className="text-xs text-zinc-600 mt-0.5">
                      ({data.count}건)
                    </div>
                  </motion.div>
                );
              })}
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
