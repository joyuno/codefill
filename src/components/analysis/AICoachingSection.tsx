'use client';

import { motion } from 'framer-motion';
import {
  Bot,
  AlertTriangle,
  BookOpen,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AICoachingSectionProps {
  detailedFeedback?: string;
  commonErrorPatterns?: string[];
}

export function AICoachingSection({
  detailedFeedback,
  commonErrorPatterns = [],
}: AICoachingSectionProps) {
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
            transition={{ delay: 0.2 }}
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
