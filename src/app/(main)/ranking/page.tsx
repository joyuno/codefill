'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users } from 'lucide-react';
import {
  MyRankSummary,
  RankingTabs,
  RankingFilter,
  RankingTable,
  RankingPagination,
} from '@/components/ranking';
import {
  rankingApi,
  usersApi,
  type RankingPeriod,
  type RankingType,
  type RankingItem,
  type MyRankingSummary,
} from '@/lib/api';
import { apiClient } from '@/lib/api/client';

const ITEMS_PER_PAGE = 20;

export default function RankingPage() {
  // State
  const [period, setPeriod] = useState<RankingPeriod>('global');
  const [type, setType] = useState<RankingType>('xp');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<RankingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [myRanking, setMyRanking] = useState<MyRankingSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMyRankingLoading, setIsMyRankingLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string | undefined>();

  // Fetch ranking data
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

  // Fetch my ranking
  const fetchMyRanking = useCallback(async () => {
    if (!apiClient.isAuthenticated()) {
      setIsMyRankingLoading(false);
      return;
    }

    setIsMyRankingLoading(true);
    try {
      const response = await rankingApi.getMyRanking();
      setMyRanking(response);
    } catch (error) {
      console.error('Failed to fetch my ranking:', error);
    } finally {
      setIsMyRankingLoading(false);
    }
  }, []);

  // Get current user ID
  useEffect(() => {
    const fetchUserId = async () => {
      if (!apiClient.isAuthenticated()) return;
      try {
        const profile = await usersApi.getProfile();
        setCurrentUserId(profile.id);
      } catch {
        // Ignore error
      }
    };
    fetchUserId();
  }, []);

  // Fetch data on mount and when filters change
  useEffect(() => {
    fetchRanking();
  }, [fetchRanking]);

  useEffect(() => {
    fetchMyRanking();
  }, [fetchMyRanking]);

  // Reset page when period or type changes
  useEffect(() => {
    setPage(1);
  }, [period, type]);

  // Reset type to 'xp' if switching away from global (no streak for weekly/monthly)
  useEffect(() => {
    if (period !== 'global' && type === 'streak') {
      setType('xp');
    }
  }, [period, type]);

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);
  const isAuthenticated = apiClient.isAuthenticated();

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      {/* 헤더 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <Trophy className="h-8 w-8 text-yellow-500" />
          <h1 className="text-3xl font-bold">랭킹</h1>
        </div>
        <p className="text-muted-foreground">
          CodeFill 사용자들의 순위를 확인하세요
        </p>
      </motion.div>

      {/* 내 순위 요약 (로그인한 경우만) */}
      {isAuthenticated && (
        <MyRankSummary data={myRanking} isLoading={isMyRankingLoading} />
      )}

      {/* 필터 영역 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
      >
        <RankingTabs value={period} onChange={setPeriod} />
        <RankingFilter period={period} value={type} onChange={setType} />
      </motion.div>

      {/* 총 인원 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-2 text-sm text-muted-foreground mb-4"
      >
        <Users className="h-4 w-4" />
        <span>
          총 <span className="font-medium text-foreground">{total.toLocaleString()}</span>명
        </span>
      </motion.div>

      {/* 랭킹 테이블 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <RankingTable
          items={items}
          type={type}
          isLoading={isLoading}
          currentUserId={currentUserId}
        />

        {/* 페이지네이션 */}
        <RankingPagination
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          isLoading={isLoading}
        />
      </motion.div>
    </div>
  );
}
