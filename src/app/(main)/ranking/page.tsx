'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Coins, Star, Sprout, Trophy, Crown, Users } from 'lucide-react';
import {
  StatsSummary,
  QuestSection,
  LeaderboardSection,
} from '@/components/challenge';
import {
  rankingApi,
  usersApi,
  missionsApi,
  type MyRankingSummary,
  type DailyMissionsResponse,
  type WeeklyChallengesResponse,
} from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

// 주간 남은 시간 계산
function getRemainingWeekTime(): string {
  const now = new Date();
  const dayOfWeek = now.getDay();
  const daysUntilMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek;

  const nextMonday = new Date(now);
  nextMonday.setDate(now.getDate() + daysUntilMonday);
  nextMonday.setHours(0, 0, 0, 0);

  const diff = nextMonday.getTime() - now.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

  if (days > 0) {
    return `${days}일 ${hours}시간`;
  }
  return `${hours}시간`;
}

type TabType = 'quests' | 'leaderboard';

export default function ChallengePage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('quests');

  // User & Auth
  const [currentUserId, setCurrentUserId] = useState<string | undefined>();
  const isAuthenticated = apiClient.isAuthenticated();

  // Ranking
  const [myRanking, setMyRanking] = useState<MyRankingSummary | null>(null);
  const [isMyRankingLoading, setIsMyRankingLoading] = useState(true);

  // Missions
  const [dailyData, setDailyData] = useState<DailyMissionsResponse | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyChallengesResponse | null>(null);
  const [isMissionsLoading, setIsMissionsLoading] = useState(true);

  // Leaderboard total
  const [leaderboardTotal, setLeaderboardTotal] = useState(0);

  // Fetch current user ID
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

  // Fetch missions
  const fetchMissions = useCallback(async () => {
    if (!isAuthenticated) {
      setIsMissionsLoading(false);
      return;
    }

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

  useEffect(() => {
    fetchMyRanking();
    fetchMissions();
  }, [fetchMyRanking, fetchMissions]);

  // Handle mission claim
  const handleClaim = async (missionId: string) => {
    try {
      const result = await missionsApi.claimMissionReward(missionId);
      if (result?.success) {
        toast.success(
          <div className="flex flex-col gap-1">
            <span className="font-semibold text-yellow-400">보상 획득!</span>
            <div className="flex items-center gap-3 text-sm">
              {result.goldEarned > 0 && (
                <span className="flex items-center gap-1 text-yellow-400">
                  <Coins className="w-3.5 h-3.5" />
                  +{result.goldEarned}
                </span>
              )}
              {result.xpEarned > 0 && (
                <span className="flex items-center gap-1 text-blue-400">
                  <Star className="w-3.5 h-3.5" />
                  +{result.xpEarned}
                </span>
              )}
              {result.seedsEarned && Object.keys(result.seedsEarned).length > 0 && (
                <span className="text-emerald-400">
                  씨앗 +{Object.values(result.seedsEarned).reduce((a, b) => a + b, 0)}
                </span>
              )}
            </div>
          </div>
        );
        // Refresh data
        await Promise.all([fetchMissions(), fetchMyRanking()]);
      } else {
        toast.error(result?.error || '보상 수령에 실패했습니다.');
      }
    } catch (error) {
      console.error('[Challenge] Claim error:', error);
      toast.error('보상 수령 중 오류가 발생했습니다.');
    }
  };

  const remainingTime = getRemainingWeekTime();
  const dailyMissions = dailyData?.missions || [];
  const weeklyMissions = weeklyData?.challenges || [];

  const dailyClaimable = dailyMissions.filter((m) => m.status === 'completed').length;
  const weeklyClaimable = weeklyMissions.filter((m) => m.status === 'completed').length;
  const totalClaimable = dailyClaimable + weeklyClaimable;

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 via-background to-background">
      <div className="container max-w-5xl mx-auto px-4 py-10">
        {/* 헤더 + 탭 (컴팩트) */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between">
            {/* 타이틀 - 탭에 따라 동적 */}
            {activeTab === 'quests' ? (
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-600/20 flex items-center justify-center border border-emerald-500/20">
                  <Sprout className="w-4.5 h-4.5 text-emerald-400" />
                </div>
                <h1 className="text-lg font-semibold text-white tracking-wide">
                  Quests
                </h1>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-600/20 flex items-center justify-center border border-yellow-500/20">
                  <Crown className="w-4.5 h-4.5 text-yellow-400" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-white tracking-wide">
                    Leaderboard
                  </h1>
                  <p className="text-xs text-muted-foreground flex items-center gap-1.5">
                    <Users className="w-3 h-3" />
                    총 <span className="text-white font-medium">{leaderboardTotal.toLocaleString()}</span>명
                  </p>
                </div>
              </div>
            )}

            {/* 탭 */}
            {isAuthenticated && (
              <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/30 border border-border/30">
                <button
                  onClick={() => setActiveTab('quests')}
                  className={cn(
                    'px-4 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-1.5',
                    activeTab === 'quests'
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-white'
                  )}
                >
                  <Sprout className="w-3.5 h-3.5" />
                  퀘스트
                  {totalClaimable > 0 && (
                    <span className="px-1.5 py-0.5 text-[9px] rounded-full bg-white/20 font-bold leading-none">
                      {totalClaimable}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab('leaderboard')}
                  className={cn(
                    'px-4 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-1.5',
                    activeTab === 'leaderboard'
                      ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-black shadow-sm'
                      : 'text-muted-foreground hover:text-white'
                  )}
                >
                  <Crown className="w-3.5 h-3.5" />
                  랭킹
                </button>
              </div>
            )}
          </div>
        </motion.div>

        {/* 로그인 필요 안내 */}
        {!isAuthenticated ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="quest-card rounded-2xl p-16 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-primary/10 flex items-center justify-center">
              <Trophy className="w-10 h-10 text-primary/50" />
            </div>
            <h2 className="quest-title text-xl font-semibold text-white mb-3">
              로그인이 필요합니다
            </h2>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              랭킹을 확인하고 일일 퀘스트에 도전하려면 로그인해주세요.
            </p>
          </motion.div>
        ) : (
          <>
            {/* 퀘스트 탭 */}
            {activeTab === 'quests' && (
              <motion.div
                key="quests"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
              >
                {/* 요약 카드 3개 */}
                <StatsSummary
                  ranking={myRanking}
                  dailyMissions={dailyMissions}
                  weeklyMissions={weeklyMissions}
                  isLoading={isMyRankingLoading || isMissionsLoading}
                  onViewRanking={() => setActiveTab('leaderboard')}
                />

                {/* 2컬럼 그리드: 일일 미션 / 주간 챌린지 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* 일일 미션 - QuestSection 컴포넌트 활용 */}
                  <QuestSection
                    title="Today's Quests"
                    variant="daily"
                    quests={dailyMissions}
                    isLoading={isMissionsLoading}
                    onClaim={handleClaim}
                  />

                  {/* 주간 챌린지 - QuestSection 컴포넌트 활용 */}
                  <QuestSection
                    title="Weekly Challenge"
                    variant="weekly"
                    quests={weeklyMissions}
                    isLoading={isMissionsLoading}
                    onClaim={handleClaim}
                    remainingTime={remainingTime}
                  />
                </div>
              </motion.div>
            )}

            {/* 리더보드 탭 */}
            {activeTab === 'leaderboard' && (
              <motion.div
                key="leaderboard"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                <LeaderboardSection currentUserId={currentUserId} onTotalChange={setLeaderboardTotal} />
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
