'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Play, Check, MessageSquare } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { BaseProblemListItem } from '@/lib/api';

interface ProblemRowProps {
  problem: BaseProblemListItem;
  index: number;
  onPreview: (originalId: string) => void;
}

const difficultyConfig: Record<string, { label: string; color: string; dot: string }> = {
  easy: { label: 'Easy', color: 'text-emerald-500', dot: 'bg-emerald-500' },
  medium: { label: 'Medium', color: 'text-amber-500', dot: 'bg-amber-500' },
  hard: { label: 'Hard', color: 'text-rose-500', dot: 'bg-rose-500' },
};

const sourceLabels: Record<string, string> = {
  baekjoon: '백준',
  codeforces: 'CF',
  leetcode: 'LC',
  geeksforgeeks: 'GFG',
  hackerrank: 'HR',
};

export function ProblemRow({ problem, index, onPreview }: ProblemRowProps) {
  const difficulty = difficultyConfig[problem.difficulty] || difficultyConfig.easy;
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

      {/* 문제 번호 */}
      <td className="w-20 py-3 px-2 text-sm text-muted-foreground font-mono">
        #{problem.original_id.slice(-4)}
      </td>

      {/* 제목 */}
      <td className="py-3 px-2">
        <span className="font-medium text-foreground group-hover:text-primary transition-colors">
          {problem.name}
        </span>
      </td>

      {/* 난이도 */}
      <td className="w-24 py-3 px-2">
        <div className="flex items-center gap-1.5">
          <span className={cn('w-2 h-2 rounded-full', difficulty.dot)} />
          <span className={cn('text-sm', difficulty.color)}>{difficulty.label}</span>
        </div>
      </td>

      {/* 출처 */}
      <td className="w-20 py-3 px-2 text-sm text-muted-foreground">
        {sourceLabel}
      </td>

      {/* 태그 */}
      <td className="py-3 px-2 hidden lg:table-cell">
        <div className="flex gap-1 flex-wrap">
          {problem.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs py-0 px-1.5 font-normal">
              {tag}
            </Badge>
          ))}
          {problem.tags.length > 2 && (
            <span className="text-xs text-muted-foreground">+{problem.tags.length - 2}</span>
          )}
        </div>
      </td>

      {/* 액션 버튼 - 호버 시에만 표시 */}
      <td className="w-28 py-3 px-2 pr-4">
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
