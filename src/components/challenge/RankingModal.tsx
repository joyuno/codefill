'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, X, ChevronLeft, ChevronRight } from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import {
  RankingTable,
  RankingTabs,
  RankingFilter,
} from '@/components/ranking';
import {
  rankingApi,
  type RankingPeriod,
  type RankingType,
  type RankingItem,
} from '@/lib/api';
import { cn } from '@/lib/utils';

interface RankingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentUserId?: string;
}

const ITEMS_PER_PAGE = 15;

export function RankingModal({ open, onOpenChange, currentUserId }: RankingModalProps) {
  const [period, setPeriod] = useState<RankingPeriod>('global');
  const [type, setType] = useState<RankingType>('xp');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<RankingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  const fetchRanking = useCallback(async () => {
    setIsLoading(true);
    try {
      let response;

      switch (period) {
        case 'weekly':
          response = await rankingApi.getWeeklyRanking(
            type === 'streak' ? 'xp' : type,
            page,
            ITEMS_PER_PAGE
          );
          break;
        case 'monthly':
          response = await rankingApi.getMonthlyRanking(
            type === 'streak' ? 'xp' : type,
            page,
            ITEMS_PER_PAGE
          );
          break;
        default:
          response = await rankingApi.getGlobalRanking(type, page, ITEMS_PER_PAGE);
      }

      setItems(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch ranking:', error);
      setItems([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, [period, type, page]);

  useEffect(() => {
    if (open) {
      fetchRanking();
    }
  }, [open, fetchRanking]);

  // Reset page when period or type changes
  useEffect(() => {
    setPage(1);
  }, [period, type]);

  // Reset type to 'xp' if switching away from global
  useEffect(() => {
    if (period !== 'global' && type === 'streak') {
      setType('xp');
    }
  }, [period, type]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-xl bg-gradient-to-b from-purple-950/95 to-background border-purple-500/20 overflow-hidden flex flex-col"
      >
        {/* 헤더 */}
        <SheetHeader className="flex-shrink-0 pb-4 border-b border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <SheetTitle className="quest-title text-purple-200">
                Leaderboard
              </SheetTitle>
              <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                <Users className="w-3 h-3" />
                총 {total.toLocaleString()}명
              </p>
            </div>
          </div>
        </SheetHeader>

        {/* 필터 영역 */}
        <div className="flex-shrink-0 py-4 space-y-3 border-b border-purple-500/10">
          <RankingTabs value={period} onChange={setPeriod} />
          <RankingFilter period={period} value={type} onChange={setType} />
        </div>

        {/* 랭킹 테이블 */}
        <div className="flex-1 overflow-y-auto py-4">
          <RankingTable
            items={items}
            type={type}
            isLoading={isLoading}
            currentUserId={currentUserId}
          />
        </div>

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="flex-shrink-0 pt-4 border-t border-purple-500/20">
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || isLoading}
                className="text-purple-300"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                이전
              </Button>

              <span className="text-sm text-muted-foreground">
                {page} / {totalPages}
              </span>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages || isLoading}
                className="text-purple-300"
              >
                다음
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
