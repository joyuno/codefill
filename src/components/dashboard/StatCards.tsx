'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Award, Flame, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { usersApi } from '@/lib/api/users';

interface StatCardsProps {
  /** 조회할 사용자 username. 없으면 본인 */
  username?: string;
  /** 부모에서 전달받은 공개 프로필 데이터 (있으면 API 호출 안 함) */
  publicData?: {
    solvedCount: number;
    streak: number;
    badgeCount: number;
  };
}

export function StatCards({ username, publicData }: StatCardsProps) {
  const { profile, isLoading: authLoading, isAuthenticated } = useAuth();
  const [badgeCount, setBadgeCount] = useState(0);

  // 본인 프로필인지 확인
  const isOwnProfile = !username;

  // 본인 프로필일 때만 뱃지 수 가져오기
  useEffect(() => {
    if (isOwnProfile && isAuthenticated) {
      usersApi.getBadges()
        .then(badges => setBadgeCount(badges.length))
        .catch(() => setBadgeCount(0));
    }
  }, [isOwnProfile, isAuthenticated]);

  // 로딩 상태 (본인 프로필일 때만)
  const isLoading = isOwnProfile ? authLoading : false;

  // 표시할 데이터
  const solvedCount = isOwnProfile
    ? (profile?.solved_count ?? 0)
    : (publicData?.solvedCount ?? 0);
  const streak = isOwnProfile
    ? (profile?.streak ?? 0)
    : (publicData?.streak ?? 0);
  const displayBadgeCount = isOwnProfile
    ? badgeCount
    : (publicData?.badgeCount ?? 0);

  const stats = [
    {
      label: '푼 문제',
      value: isLoading ? '-' : solvedCount,
      icon: Trophy,
      color: 'text-primary'
    },
    {
      label: '획득 뱃지',
      value: isLoading ? '-' : displayBadgeCount,
      icon: Award,
      color: 'text-yellow-500'
    },
    {
      label: '연속 학습',
      value: isLoading ? '-' : `${streak}일`,
      icon: Flame,
      color: 'text-orange-500'
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-3">
              <div className={`rounded-lg bg-secondary p-2.5 ${stat.color}`}>
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Icon className="h-5 w-5" />
                )}
              </div>
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
