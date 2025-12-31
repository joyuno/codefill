'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getTierInfo } from '@/lib/constants/tiers';
import type { BaseProblemListItem } from '@/lib/api';

interface ProblemCardProps {
  problem: BaseProblemListItem;
  index: number;
  onPreview: (originalId: string) => void;
}

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
  const tier = getTierInfo(problem.difficulty);
  const TierIcon = tier.Icon;

  // input_output 파싱
  const inputOutput = problem.input_output;
  const hasInputOutput = inputOutput && (inputOutput.inputs?.length || inputOutput.outputs?.length);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      whileHover={{ scale: 1.01 }}
      className="rounded-lg border transition-all bg-card border-border hover:border-primary/30 p-5"
    >
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">{sourceIcon}</span>
              <h3 className="font-semibold">{problem.name}</h3>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {/* 티어 배지 with 아이콘 */}
              <Badge
                variant="outline"
                className={cn(
                  'flex items-center gap-1.5 pr-2.5',
                  tier.bgColor,
                  tier.color,
                  tier.borderColor
                )}
              >
                <TierIcon size={14} />
                <span>{tier.name}</span>
              </Badge>
              {problem.source && (
                <Badge variant="secondary" className="text-xs">
                  {problem.source}
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

        {/* Tags */}
        {problem.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {problem.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full border px-2.5 py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Input/Output Examples */}
        {hasInputOutput && (
          <div className="rounded-lg border transition-all bg-card border-border hover:border-primary/30 p-3 space-y-2">
            <div className="text-xs font-medium text-muted-foreground">예제 입출력</div>
            <div className="grid grid-cols-2 gap-3">
              {inputOutput.inputs && inputOutput.inputs.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">입력</div>
                  <pre className="text-xs bg-muted/50 rounded p-2 overflow-x-auto max-h-20">
                    {typeof inputOutput.inputs[0] === 'string'
                      ? inputOutput.inputs[0]
                      : JSON.stringify(inputOutput.inputs[0])}
                  </pre>
                </div>
              )}
              {inputOutput.outputs && inputOutput.outputs.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">출력</div>
                  <pre className="text-xs bg-muted/50 rounded p-2 overflow-x-auto max-h-20">
                    {typeof inputOutput.outputs[0] === 'string'
                      ? inputOutput.outputs[0]
                      : JSON.stringify(inputOutput.outputs[0])}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
