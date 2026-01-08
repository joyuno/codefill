'use client';

import { motion } from 'framer-motion';
import { Lightbulb, CheckCircle } from 'lucide-react';

interface LearningAdviceProps {
  recommendations: string[];
}

export function LearningAdvice({ recommendations }: LearningAdviceProps) {
  if (recommendations.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <Lightbulb className="h-5 w-5 text-yellow-500" />
        <h3 className="text-lg font-semibold">학습 조언</h3>
      </div>

      <div className="space-y-3">
        {recommendations.map((advice, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + index * 0.05 }}
            className="flex items-start gap-3 rounded-lg bg-secondary/30 p-3"
          >
            <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
            <p className="text-sm leading-relaxed">{advice}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
