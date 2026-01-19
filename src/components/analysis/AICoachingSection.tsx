'use client';

import { motion } from 'framer-motion';
import {
  Bot,
  AlertTriangle,
  BookOpen,
  Lightbulb,
  Route,
  ChevronRight,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AICoachingSectionProps {
  detailedFeedback?: string;
  commonErrorPatterns?: string[];
  recommendations?: string[];
  studyPlan?: string;
}

export function AICoachingSection({
  detailedFeedback,
  commonErrorPatterns = [],
  recommendations = [],
  studyPlan,
}: AICoachingSectionProps) {
  // 이스케이프된 문자열을 실제 줄바꿈으로 변환
  const normalizeMarkdown = (text: string): string => {
    return text
      .replace(/\\n/g, '\n')
      .replace(/\\t/g, '\t')
      .replace(/\\\\/g, '\\');
  };

  return (
    <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-zinc-800/50 bg-gradient-to-r from-amber-500/5 to-transparent">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Bot className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-100">AI Coach</h2>
            <p className="text-[10px] text-zinc-500">Personalized learning insights</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Study Plan - 학습 경로 */}
        {studyPlan && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <Route className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                학습 경로
              </h3>
            </div>
            <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border border-emerald-500/20">
              <div className="flex items-center gap-2 flex-wrap">
                {studyPlan.split('→').map((step, index, arr) => (
                  <span key={index} className="flex items-center gap-2">
                    <span className="px-3 py-1.5 rounded-lg bg-zinc-800/80 text-sm text-zinc-200 font-medium">
                      {step.trim()}
                    </span>
                    {index < arr.length - 1 && (
                      <ChevronRight className="w-4 h-4 text-emerald-400" />
                    )}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Recommendations - 추천 액션 */}
        {recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                추천 액션
              </h3>
            </div>
            <div className="space-y-2">
              {recommendations.map((rec, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + index * 0.05 }}
                  className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/5 border border-blue-500/10"
                >
                  <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-400">{index + 1}</span>
                  </div>
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
            transition={{ delay: 0.1 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                상세 피드백
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
                  {normalizeMarkdown(detailedFeedback)}
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
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wide">
                주의 패턴
              </h3>
            </div>
            <div className="space-y-2">
              {commonErrorPatterns.slice(0, 3).map((pattern, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 + index * 0.05 }}
                  className="flex items-start gap-2 p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/10"
                >
                  <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-zinc-400">{pattern}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
