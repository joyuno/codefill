'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Swords, Coins, Star, Calendar, Sprout, Trophy, Clock } from 'lucide-react';
import {
  StatsSummary,
  QuestCard,
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
    <div className="min-h-screen bg-gradient-to-b from-emerald-950/20 via-background to-background">
      <div className="container max-w-5xl mx-auto px-4 py-8">
        {/* 헤더 + 탭 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
                <Swords className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h1 className="quest-title text-2xl font-bold text-white tracking-wide">
                  Quest Board
                </h1>
                <p className="text-sm text-muted-foreground">
                  퀘스트를 완료하고 보상을 획득하세요
                </p>
              </div>
            </div>

            {/* 탭 */}
            {isAuthenticated && (
              <div className="flex items-center gap-1 p-1 rounded-xl bg-card/50 border border-border/50">
                <button
                  onClick={() => setActiveTab('quests')}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                    activeTab === 'quests'
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-white hover:bg-muted/50'
                  )}
                >
                  <span className="flex items-center gap-2">
                    <Sprout className="w-4 h-4" />
                    퀘스트
                    {totalClaimable > 0 && (
                      <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-white/20">
                        {totalClaimable}
                      </span>
                    )}
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('leaderboard')}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                    activeTab === 'leaderboard'
                      ? 'bg-purple-600 text-white shadow-sm'
                      : 'text-muted-foreground hover:text-white hover:bg-muted/50'
                  )}
                >
                  <span className="flex items-center gap-2">
                    <Trophy className="w-4 h-4" />
                    리더보드
                  </span>
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
            className="quest-card rounded-xl p-12 text-center"
          >
            <Calendar className="w-16 h-16 mx-auto mb-4 text-primary/30" />
            <h2 className="text-lg font-semibold text-white mb-2">
              로그인이 필요합니다
            </h2>
            <p className="text-sm text-muted-foreground">
              퀘스트를 확인하고 보상을 받으려면 로그인해주세요.
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
                  {/* 일일 미션 */}
                  <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    {/* 섹션 헤더 */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                          <Sprout className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h2 className="font-semibold text-primary">Today&apos;s Quests</h2>
                            {dailyClaimable > 0 && (
                              <span className="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-primary text-primary-foreground">
                                {dailyClaimable}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 일일 미션 목록 */}
                    {isMissionsLoading ? (
                      <div className="space-y-2">
                        {[0, 1, 2].map((i) => (
                          <div
                            key={i}
                            className="h-16 rounded-xl bg-card/50 animate-pulse"
                          />
                        ))}
                      </div>
                    ) : dailyMissions.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-12 text-center quest-card rounded-xl">
                        <Sprout className="w-10 h-10 text-muted-foreground/30 mb-3" />
                        <p className="text-muted-foreground text-sm">
                          오늘의 퀘스트가 아직 없습니다
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {dailyMissions.map((quest, index) => (
                          <QuestCard
                            key={quest.id}
                            quest={quest}
                            variant="daily"
                            onClaim={handleClaim}
                            index={index}
                          />
                        ))}
                      </div>
                    )}
                  </motion.section>

                  {/* 주간 챌린지 */}
                  <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    {/* 섹션 헤더 */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center">
                          <Trophy className="w-4 h-4 text-yellow-400" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h2 className="font-semibold text-yellow-400">Weekly Challenge</h2>
                            {weeklyClaimable > 0 && (
                              <span className="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-yellow-500 text-black">
                                {weeklyClaimable}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded-lg">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{remainingTime}</span>
                      </div>
                    </div>

                    {/* 주간 챌린지 목록 */}
                    {isMissionsLoading ? (
                      <div className="space-y-3">
                        {[0, 1].map((i) => (
                          <div
                            key={i}
                            className="h-32 rounded-xl bg-card/50 animate-pulse"
                          />
                        ))}
                      </div>
                    ) : weeklyMissions.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-12 text-center quest-card rounded-xl">
                        <Trophy className="w-10 h-10 text-muted-foreground/30 mb-3" />
                        <p className="text-muted-foreground text-sm">
                          이번 주 챌린지가 아직 없습니다
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {weeklyMissions.map((quest, index) => (
                          <QuestCard
                            key={quest.id}
                            quest={quest}
                            variant="weekly"
                            onClaim={handleClaim}
                            index={index}
                          />
                        ))}
                      </div>
                    )}
                  </motion.section>
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
                <LeaderboardSection currentUserId={currentUserId} />
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
