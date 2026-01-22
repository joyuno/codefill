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
  const normalizeMarkdown = (text: string): string => {
    return text
      .replace(/\\n/g, '\n')
      .replace(/\\t/g, '\t')
      .replace(/\\\\/g, '\\');
  };

  return (
    <div className="rounded-xl bg-zinc-900/80 border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-zinc-800/50 bg-gradient-to-r from-amber-500/5 to-transparent">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Bot className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-xs font-semibold text-zinc-100">AI Coach</h2>
            <p className="text-[9px] text-zinc-500">맞춤형 학습 인사이트</p>
          </div>
        </div>
      </div>

      <div className="p-3 space-y-3">
        {/* Study Plan - 학습 경로 */}
        {studyPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/15"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <Route className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">
                학습 경로
              </span>
            </div>
            <div className="flex items-center gap-1.5 flex-wrap">
              {studyPlan.split('→').map((step, index, arr) => (
                <span key={index} className="flex items-center gap-1.5">
                  <span className="px-2.5 py-1 rounded text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                    {step.trim()}
                  </span>
                  {index < arr.length - 1 && (
                    <ChevronRight className="w-3 h-3 text-emerald-400" />
                  )}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Recommendations - 추천 액션 */}
        {recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.05 }}
            className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/15"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <Lightbulb className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-[10px] font-semibold text-blue-400 uppercase tracking-wider">
                추천 액션
              </span>
            </div>
            <div className="space-y-1.5">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2"
                >
                  <span className="w-4 h-4 rounded text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5 bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    {index + 1}
                  </span>
                  <p className="text-xs leading-relaxed text-zinc-300">
                    {rec}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Common Error Patterns - 주의 패턴 */}
        {commonErrorPatterns.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/15"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span className="text-[10px] font-semibold text-rose-400 uppercase tracking-wider">
                주의 패턴
              </span>
            </div>
            <div className="space-y-1.5">
              {commonErrorPatterns.slice(0, 3).map((pattern, index) => (
                <div key={index} className="flex items-start gap-2">
                  <div className="w-1 h-1 rounded-full bg-rose-400 mt-1.5 flex-shrink-0" />
                  <p className="text-xs text-zinc-400 leading-relaxed">{pattern}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Detailed Feedback - 상세 피드백 */}
        {detailedFeedback && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/15"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <BookOpen className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">
                상세 피드백
              </span>
            </div>
            <div className="text-[11px] leading-relaxed text-zinc-300 [&_h1]:text-xs [&_h1]:font-semibold [&_h1]:text-zinc-200 [&_h1]:mt-2 [&_h1]:mb-1 [&_h2]:text-xs [&_h2]:font-semibold [&_h2]:text-zinc-200 [&_h2]:mt-2 [&_h2]:mb-1 [&_h3]:text-[11px] [&_h3]:font-semibold [&_h3]:text-zinc-200 [&_h3]:mt-2 [&_h3]:mb-1 [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0 [&_strong]:text-amber-300 [&_strong]:font-medium [&_code]:text-[10px] [&_code]:text-amber-400 [&_code]:bg-amber-500/10 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {normalizeMarkdown(detailedFeedback)}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
