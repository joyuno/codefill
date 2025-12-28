'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { BaseProblemListItem } from '@/lib/api';

interface ProblemCardProps {
  problem: BaseProblemListItem;
  index: number;
  onPreview: (originalId: string) => void;
}

const difficultyColors: Record<string, string> = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

const sourceIcons: Record<string, string> = {
  baekjoon: '🏅',
  codeforces: '⚔️',
  leetcode: '💡',
  geeksforgeeks: '🧑‍💻',
  hackerrank: '💻',
  default: '📝',
};

export function ProblemCard({ problem, index, onPreview }: ProblemCardProps) {
  const sourceIcon = sourceIcons[problem.source || ''] || sourceIcons.default;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      whileHover={{ scale: 1.01 }}
      className="rounded-xl border border-border bg-card p-5 transition-colors hover:border-primary/50"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{sourceIcon}</span>
            <h3 className="font-semibold">{problem.name}</h3>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="outline"
              className={cn('capitalize', difficultyColors[problem.difficulty] || '')}
            >
              {problem.difficulty}
            </Badge>
            {problem.source && (
              <Badge variant="secondary" className="text-xs">
                {problem.source}
              </Badge>
            )}
            {problem.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {problem.tags.length > 3 && (
              <Badge variant="outline" className="text-xs text-muted-foreground">
                +{problem.tags.length - 3}
              </Badge>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPreview(problem.original_id)}
          >
            <Eye className="mr-1.5 h-3.5 w-3.5" />
            Preview
          </Button>
          <Button
            size="sm"
            onClick={() => window.location.href = `/practice?id=${problem.original_id}&type=implementation`}
          >
            <Play className="mr-1.5 h-3.5 w-3.5" />
            Start
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
