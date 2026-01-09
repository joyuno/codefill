'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, Target, Calendar, CalendarRange, Coins, Star } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import {
  MyRankSummary,
  RankingTabs,
  RankingFilter,
  RankingTable,
  RankingPagination,
} from '@/components/ranking';
import { DailyMissionsPanel } from '@/components/missions/DailyMissionsPanel';
import { WeeklyChallengesPanel } from '@/components/missions/WeeklyChallengesPanel';
import {
  rankingApi,
  usersApi,
  missionsApi,
  type RankingPeriod,
  type RankingType,
  type RankingItem,
  type MyRankingSummary,
  type DailyMissionsResponse,
  type WeeklyChallengesResponse,
} from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

const ITEMS_PER_PAGE = 20;

type MainTab = 'ranking' | 'daily' | 'weekly';

export default function RankingPage() {
  // Main tab state
  const [mainTab, setMainTab] = useState<MainTab>('ranking');

  // Ranking state
  const [period, setPeriod] = useState<RankingPeriod>('global');
  const [type, setType] = useState<RankingType>('xp');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<RankingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [myRanking, setMyRanking] = useState<MyRankingSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMyRankingLoading, setIsMyRankingLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string | undefined>();

  // Missions state
  const [dailyData, setDailyData] = useState<DailyMissionsResponse | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyChallengesResponse | null>(null);
  const [isMissionsLoading, setIsMissionsLoading] = useState(false);

  const isAuthenticated = apiClient.isAuthenticated();

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
    if (!isAuthenticated) {
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
  }, [isAuthenticated]);

  // Fetch missions data
  const fetchMissions = useCallback(async () => {
    if (!isAuthenticated) return;

    setIsMissionsLoading(true);
    try {
      const allData = await missionsApi.getAllMissions();
      if (allData) {
        setDailyData(allData.daily);
        setWeeklyData(allData.weekly);
      }
    } catch (error) {
      console.error('Failed to fetch missions:', error);
    } finally {
      setIsMissionsLoading(false);
    }
  }, [isAuthenticated]);

  // Get current user ID
  useEffect(() => {
    const fetchUserId = async () => {
      if (!isAuthenticated) return;
      try {
        const profile = await usersApi.getProfile();
        setCurrentUserId(profile.id);
      } catch {
        // Ignore error
      }
    };
    fetchUserId();
  }, [isAuthenticated]);

  // Fetch ranking data on mount and when filters change
  useEffect(() => {
    if (mainTab === 'ranking') {
      fetchRanking();
    }
  }, [fetchRanking, mainTab]);

  useEffect(() => {
    fetchMyRanking();
  }, [fetchMyRanking]);

  // Fetch missions when switching to mission tabs
  useEffect(() => {
    if ((mainTab === 'daily' || mainTab === 'weekly') && isAuthenticated) {
      fetchMissions();
    }
  }, [mainTab, isAuthenticated, fetchMissions]);

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

  // Handle mission claim
  const handleClaim = async (missionId: string) => {
    try {
      const result = await missionsApi.claimMissionReward(missionId);
      if (result?.success) {
        toast.success(
          <div className="flex flex-col gap-1">
            <span className="font-medium">보상 획득!</span>
            <div className="flex items-center gap-3 text-sm">
              {result.goldEarned > 0 && (
                <span className="flex items-center gap-1 text-yellow-500">
                  <Coins className="w-3.5 h-3.5" />
                  +{result.goldEarned}
                </span>
              )}
              {result.xpEarned > 0 && (
                <span className="flex items-center gap-1 text-blue-500">
                  <Star className="w-3.5 h-3.5" />
                  +{result.xpEarned}
                </span>
              )}
              {result.seedsEarned && Object.keys(result.seedsEarned).length > 0 && (
                <span className="text-green-500">
                  씨앗 +{Object.values(result.seedsEarned).reduce((a, b) => a + b, 0)}
                </span>
              )}
            </div>
          </div>
        );
        // Reload missions to update status
        await fetchMissions();
      } else {
        toast.error(result?.error || '보상 수령에 실패했습니다.');
      }
    } catch (error) {
      console.error('[Missions] Claim error:', error);
      toast.error('보상 수령 중 오류가 발생했습니다.');
    }
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  // Calculate completed missions count for badges
  const dailyCompletedCount = dailyData?.missions.filter(m => m.status === 'completed').length || 0;
  const weeklyCompletedCount = weeklyData?.challenges.filter(c => c.status === 'completed').length || 0;

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      {/* 헤더 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <Target className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">도전</h1>
        </div>
        <p className="text-muted-foreground">
          순위를 확인하고, 미션을 완료하여 보상을 획득하세요
        </p>
      </motion.div>

      {/* 메인 탭 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <Tabs value={mainTab} onValueChange={(v) => setMainTab(v as MainTab)}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="ranking" className="flex items-center gap-2">
              <Trophy className="w-4 h-4" />
              <span>순위표</span>
            </TabsTrigger>
            <TabsTrigger value="daily" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>일일 미션</span>
              {dailyCompletedCount > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-green-500 text-white rounded-full">
                  {dailyCompletedCount}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="weekly" className="flex items-center gap-2">
              <CalendarRange className="w-4 h-4" />
              <span>주간 챌린지</span>
              {weeklyCompletedCount > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-purple-500 text-white rounded-full">
                  {weeklyCompletedCount}
                </span>
              )}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </motion.div>

      {/* 순위표 탭 콘텐츠 */}
      {mainTab === 'ranking' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {/* 내 순위 요약 (로그인한 경우만) */}
          {isAuthenticated && (
            <MyRankSummary data={myRanking} isLoading={isMyRankingLoading} />
          )}

          {/* 필터 영역 */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <RankingTabs value={period} onChange={setPeriod} />
            <RankingFilter period={period} value={type} onChange={setType} />
          </div>

          {/* 총 인원 */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
            <Users className="h-4 w-4" />
            <span>
              총 <span className="font-medium text-foreground">{total.toLocaleString()}</span>명
            </span>
          </div>

          {/* 랭킹 테이블 */}
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
      )}

      {/* 일일 미션 탭 콘텐츠 */}
      {mainTab === 'daily' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {!isAuthenticated ? (
            <Card className="border-border/50">
              <CardContent className="py-12">
                <div className="flex flex-col items-center justify-center text-center">
                  <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                  <h2 className="text-lg font-semibold mb-2">로그인이 필요합니다</h2>
                  <p className="text-sm text-muted-foreground">
                    일일 미션을 확인하려면 로그인해주세요.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-border/50">
              <CardContent className="py-6">
                <DailyMissionsPanel
                  data={dailyData}
                  isLoading={isMissionsLoading}
                  onClaim={handleClaim}
                />
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* 주간 챌린지 탭 콘텐츠 */}
      {mainTab === 'weekly' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {!isAuthenticated ? (
            <Card className="border-border/50">
              <CardContent className="py-12">
                <div className="flex flex-col items-center justify-center text-center">
                  <CalendarRange className="h-12 w-12 text-muted-foreground mb-4" />
                  <h2 className="text-lg font-semibold mb-2">로그인이 필요합니다</h2>
                  <p className="text-sm text-muted-foreground">
                    주간 챌린지를 확인하려면 로그인해주세요.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-border/50">
              <CardContent className="py-6">
                <WeeklyChallengesPanel
                  data={weeklyData}
                  isLoading={isMissionsLoading}
                  onClaim={handleClaim}
                />
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  );
}
