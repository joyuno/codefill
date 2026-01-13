'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
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

interface LeaderboardSectionProps {
  currentUserId?: string;
  onTotalChange?: (total: number) => void;
}

const ITEMS_PER_PAGE = 10;

export function LeaderboardSection({ currentUserId, onTotalChange }: LeaderboardSectionProps) {
  const [period, setPeriod] = useState<RankingPeriod>('global');
  const [type, setType] = useState<RankingType>('xp');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<RankingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

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
    fetchRanking();
  }, [fetchRanking]);

  // Reset page when period or type changes
  useEffect(() => {
    setPage(1);
  }, [period, type]);

  // Reset type to 'xp' if switching away from global (streak only available in global)
  useEffect(() => {
    if (period !== 'global' && type === 'streak') {
      setType('xp');
    }
  }, [period, type]);

  // Notify parent of total change
  useEffect(() => {
    onTotalChange?.(total);
  }, [total, onTotalChange]);

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* 필터 영역 */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4 p-4 rounded-xl bg-card/50 border border-border/50">
        <RankingTabs value={period} onChange={setPeriod} />
        <div className="sm:ml-auto">
          <RankingFilter period={period} value={type} onChange={setType} />
        </div>
      </div>

      {/* 랭킹 테이블 */}
      <div className="rounded-xl overflow-hidden border border-border/50 bg-card/30">
        <RankingTable
          items={items}
          type={type}
          isLoading={isLoading}
          currentUserId={currentUserId}
        />
      </div>

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1 || isLoading}
            className="text-muted-foreground hover:text-white"
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
            className="text-muted-foreground hover:text-white"
          >
            다음
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      )}
    </motion.section>
  );
}
