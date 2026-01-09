'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Swords, Coins, Star, Calendar } from 'lucide-react';
import {
  AdventurerRank,
  QuestSection,
  RankingModal,
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

export default function ChallengePage() {
  // User & Auth
  const [currentUserId, setCurrentUserId] = useState<string | undefined>();
  const isAuthenticated = apiClient.isAuthenticated();

  // Ranking
  const [myRanking, setMyRanking] = useState<MyRankingSummary | null>(null);
  const [isMyRankingLoading, setIsMyRankingLoading] = useState(true);
  const [isRankingModalOpen, setIsRankingModalOpen] = useState(false);

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

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-950/30 via-background to-background">
      <div className="container max-w-2xl mx-auto px-4 py-8">
        {/* 헤더 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <Swords className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="quest-title text-2xl font-bold text-white tracking-wide">
                Quest Board
              </h1>
              <p className="text-sm text-emerald-300/70">
                퀘스트를 완료하고 보상을 획득하세요
              </p>
            </div>
          </div>
        </motion.div>

        {/* 내 순위 (모험가 랭크) */}
        <AdventurerRank
          data={myRanking}
          isLoading={isMyRankingLoading}
          onViewRanking={() => setIsRankingModalOpen(true)}
        />

        {/* 로그인 필요 안내 */}
        {!isAuthenticated ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="quest-card rounded-xl p-8 text-center"
          >
            <Calendar className="w-16 h-16 mx-auto mb-4 text-primary/30" />
            <h2 className="text-lg font-semibold text-white mb-2">
              로그인이 필요합니다
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              퀘스트를 확인하고 보상을 받으려면 로그인해주세요.
            </p>
          </motion.div>
        ) : (
          <>
            {/* 일일 미션 */}
            <QuestSection
              title="Today's Quests"
              variant="daily"
              quests={dailyData?.missions || []}
              isLoading={isMissionsLoading}
              onClaim={handleClaim}
            />

            {/* 주간 챌린지 */}
            <QuestSection
              title="Weekly Challenge"
              variant="weekly"
              quests={weeklyData?.challenges || []}
              isLoading={isMissionsLoading}
              onClaim={handleClaim}
              remainingTime={remainingTime}
            />
          </>
        )}

        {/* 전체 순위 모달 */}
        <RankingModal
          open={isRankingModalOpen}
          onOpenChange={setIsRankingModalOpen}
          currentUserId={currentUserId}
        />
      </div>
    </div>
  );
}
