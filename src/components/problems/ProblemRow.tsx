'use client';

import { useState, memo } from 'react';
import { Button } from '@/components/ui/button';
import { Eye, Play, Check, MessageSquare, LogIn, Heart, Users } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { getTierInfo } from '@/lib/constants/tiers';
import { apiClient } from '@/lib/api/client';
import type { BaseProblemListItem } from '@/lib/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

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

export const ProblemRow = memo(function ProblemRow({ problem, index, onPreview }: ProblemRowProps) {
  const router = useRouter();
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const tier = getTierInfo(problem.difficulty);
  const TierIcon = tier.Icon;
  const sourceLabel = sourceLabels[problem.source || ''] || problem.source || '-';
  const isSolved = false; // TODO: 실제 풀이 여부 연동

  const handleStartPractice = (e: React.MouseEvent) => {
    e.stopPropagation();

    // Check if user is logged in
    if (!apiClient.isAuthenticated()) {
      setShowLoginDialog(true);
      return;
    }

    // Navigate to chat page
    router.push(`/chat?problem_id=${problem.original_id}`);
  };

  return (
    <>
      {/* Login Required Dialog */}
      <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <LogIn className="h-5 w-5" />
              로그인이 필요합니다
            </DialogTitle>
            <DialogDescription>
              문제를 풀려면 로그인이 필요합니다.<br />
              로그인하면 XP 획득과 잔디 기록이 저장됩니다.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 sm:justify-end">
            <Button variant="outline" onClick={() => setShowLoginDialog(false)}>
              취소
            </Button>
            <Button onClick={() => router.push('/login')}>
              <LogIn className="mr-2 h-4 w-4" />
              로그인하기
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    <tr
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

      {/* 풀이수/좋아요 */}
      <td className="w-24 py-3 px-2 hidden md:table-cell">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1" title="풀이 수">
            <Users className="h-3.5 w-3.5" />
            {problem.solve_count ?? 0}
          </span>
          <span className="flex items-center gap-1" title="좋아요">
            <Heart className="h-3.5 w-3.5" />
            {problem.like_count ?? 0}
          </span>
        </div>
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
            onClick={handleStartPractice}
            title="풀기 시작"
          >
            <Play className="h-3.5 w-3.5" />
          </Button>
        </div>
      </td>
    </tr>
    </>
  );
});
