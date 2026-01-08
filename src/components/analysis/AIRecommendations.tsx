'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Target, ArrowRight, Sparkles } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { RecommendedProblem } from '@/lib/api';

interface AIRecommendationsProps {
  studyPlan?: string;
  problems: RecommendedProblem[];
}

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: 'bg-green-500/10 text-green-500 border-green-500/20',
  medium: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  medium_hard: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  hard: 'bg-red-500/10 text-red-500 border-red-500/20',
  very_hard: 'bg-red-600/10 text-red-600 border-red-600/20',
};

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: '쉬움',
  medium: '보통',
  medium_hard: '보통+',
  hard: '어려움',
  very_hard: '매우 어려움',
};

export function AIRecommendations({ studyPlan, problems }: AIRecommendationsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <Target className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">AI 맞춤 추천</h3>
      </div>

      {/* Study Plan */}
      {studyPlan && (
        <div className="mb-4 flex items-start gap-2 rounded-lg border border-primary/20 bg-primary/5 p-3">
          <Sparkles className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
          <p className="text-sm">{studyPlan}</p>
        </div>
      )}

      {/* Recommended Problems */}
      {problems.length > 0 ? (
        <div className="space-y-2">
          {problems.map((problem, index) => (
            <motion.div
              key={problem.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.05 }}
            >
              <Link
                href={`/problems/${problem.id}`}
                className="group flex items-center justify-between rounded-lg border border-border bg-secondary/30 p-3 transition-colors hover:bg-secondary/50"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{problem.name}</span>
                    <Badge
                      variant="outline"
                      className={`text-xs ${DIFFICULTY_COLORS[problem.difficulty] || DIFFICULTY_COLORS.medium}`}
                    >
                      {DIFFICULTY_LABELS[problem.difficulty] || problem.difficulty}
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {problem.topic}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{problem.reason}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-primary" />
              </Link>
            </motion.div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">추천할 문제가 없습니다</p>
      )}
    </motion.div>
  );
}
