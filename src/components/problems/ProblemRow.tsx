'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Eye, Play, Check, MessageSquare } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { getTierInfo } from '@/lib/constants/tiers';
import type { BaseProblemListItem } from '@/lib/api';

interface ProblemRowProps {
  problem: BaseProblemListItem;
  index: number;
  onPreview: (originalId: string) => void;
}

const sourceLabels: Record<string, string> = {
  baekjoon: '백준',
  codeforces: 'CF',
  leetcode: 'LC',
  geeksforgeeks: 'GFG',
  hackerrank: 'HR',
};

export function ProblemRow({ problem, index, onPreview }: ProblemRowProps) {
  const tier = getTierInfo(problem.difficulty);
  const TierIcon = tier.Icon;
  const sourceLabel = sourceLabels[problem.source || ''] || problem.source || '-';
  const isSolved = false; // TODO: 실제 풀이 여부 연동

  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.02 }}
      className="group border-b border-border/50 hover:bg-muted/50 transition-colors cursor-pointer"
      onClick={() => onPreview(problem.original_id)}
    >
      {/* 상태 (풀이 여부) */}
      <td className="w-10 py-3 pl-4 pr-2">
        {isSolved ? (
          <Check className="h-4 w-4 text-emerald-500" />
        ) : (
          <div className="h-4 w-4" />
        )}
      </td>

      {/* 제목 - 최대 2줄, 넘으면 ... */}
      <td className="py-3 px-2 max-w-[400px]">
        <span className="font-medium text-foreground group-hover:text-primary transition-colors line-clamp-2">
          {problem.name}
        </span>
      </td>

      {/* 티어 (난이도) */}
      <td className="w-28 py-3 px-2">
        <div className="flex items-center gap-1.5">
          <TierIcon size={16} />
          <span className={cn('text-sm font-medium', tier.color)}>{tier.name}</span>
        </div>
      </td>

      {/* 출처 */}
      <td className="w-20 py-3 px-2 text-sm text-muted-foreground">
        {sourceLabel}
      </td>

      {/* 태그 */}
      <td className="py-3 px-2 hidden lg:table-cell">
        {(() => {
          const maxTags = 2;
          const visibleTags = problem.tags.slice(0, maxTags);
          const remainingCount = problem.tags.length - maxTags;

          return (
            <div className="flex gap-1.5 items-center flex-nowrap">
              {visibleTags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full border px-2.5 py-0.5 text-xs font-medium text-foreground whitespace-nowrap"
                >
                  {tag}
                </span>
              ))}
              {remainingCount > 0 && (
                <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                  +{remainingCount}
                </span>
              )}
            </div>
          );
        })()}
      </td>

      {/* 액션 버튼 - 호버 시에만 표시 */}
      <td className="w-24 py-3 px-2 pr-4">
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-muted/50 group-hover:bg-muted rounded-md p-0.5">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={(e) => {
              e.stopPropagation();
              onPreview(problem.original_id);
            }}
            title="미리보기"
          >
            <Eye className="h-3.5 w-3.5" />
          </Button>
          <Link
            href={`/problems/${problem.original_id}`}
            onClick={(e) => e.stopPropagation()}
          >
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              title="게시글"
            >
              <MessageSquare className="h-3.5 w-3.5" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-primary hover:text-primary"
            onClick={(e) => {
              e.stopPropagation();
              window.location.href = `/practice?id=${problem.original_id}&type=implementation`;
            }}
            title="풀기 시작"
          >
            <Play className="h-3.5 w-3.5" />
          </Button>
        </div>
      </td>
    </motion.tr>
  );
}
