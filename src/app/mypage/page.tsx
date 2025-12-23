'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { mockUser, mockBadges, mockRecentActivity } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Award, Flame, Zap, Target, TrendingUp, Loader2 } from 'lucide-react';
import { usersApi, type UserProfile, type UserStats } from '@/lib/api';
import type { Badge as BadgeType, RecentActivity } from '@/lib/types';
import { motion } from 'framer-motion';

export default function MyPagePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [badges, setBadges] = useState<BadgeType[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        // Fetch from API (uses mypage-optimized endpoints)
        const [profileData, statsData, badgesData, activityData] = await Promise.all([
          usersApi.getProfile(),
          usersApi.getStats(),
          usersApi.getBadges(),
          usersApi.getRecentActivity(),
        ]);
        setProfile(profileData);
        setStats(statsData);
        setBadges(badgesData);
        setRecentActivity(activityData);
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        setError('Failed to load user data. Using demo data.');
        // Use mock data as fallback for demo
        setProfile({
          id: mockUser.id,
          email: mockUser.email,
          username: mockUser.username,
          avatarShape: mockUser.avatarShape,
          avatarColor: mockUser.avatarColor,
          level: mockUser.level,
          currentXP: mockUser.currentXP,
          requiredXP: mockUser.requiredXP,
          totalXP: mockUser.currentXP + (mockUser.level - 1) * 3000,
          solvedCount: mockUser.solvedCount,
          streak: mockUser.streak,
          maxStreak: mockUser.streak + 5,
          joinedAt: mockUser.joinedAt,
          subscription: mockUser.subscription,
        });
        setStats({
          totalSolved: mockUser.solvedCount,
          solvedByDifficulty: { easy: 50, medium: 60, hard: 32 },
          solvedByType: { blank: 45, puzzle: 35 },
          currentStreak: mockUser.streak,
          maxStreak: mockUser.streak + 5,
          totalXP: mockUser.currentXP + (mockUser.level - 1) * 3000,
          level: mockUser.level,
        });
        setBadges(mockBadges);
        setRecentActivity(mockRecentActivity);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
        <div className="flex min-h-[60vh] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  const displayUser = profile || mockUser;
  const displayStats = stats;
  const displayBadges = badges.length > 0 ? badges : mockBadges;
  const displayActivity = recentActivity.length > 0 ? recentActivity : mockRecentActivity;
  const xpProgress = ((displayUser.currentXP || 0) / (displayUser.requiredXP || 3000)) * 100;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <main className="mx-auto max-w-4xl space-y-6 p-6">
        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
            <div
              className="flex h-20 w-20 items-center justify-center rounded-full text-3xl font-bold text-primary-foreground"
              style={{ backgroundColor: displayUser.avatarColor || 'hsl(142, 71%, 45%)' }}
            >
              {displayUser.username.slice(0, 2).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold">{displayUser.username}</h1>
                <Badge variant="secondary" className="capitalize">
                  {displayUser.subscription} Plan
                </Badge>
              </div>
              <div className="mt-2 flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-primary" />
                  <span className="font-medium">Level {displayUser.level}</span>
                </div>
                <div className="flex-1 max-w-xs">
                  <Progress value={xpProgress} className="h-2" />
                  <p className="mt-1 text-xs text-muted-foreground">
                    {displayUser.currentXP?.toLocaleString()} / {displayUser.requiredXP?.toLocaleString()} XP
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-3 rounded-xl border border-border bg-card p-4"
          >
            <div className="rounded-lg bg-primary/20 p-2">
              <Trophy className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{displayUser.solvedCount}</p>
              <p className="text-sm text-muted-foreground">문제 해결</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="flex items-center gap-3 rounded-xl border border-border bg-card p-4"
          >
            <div className="rounded-lg bg-warning/20 p-2">
              <Award className="h-6 w-6 text-warning" />
            </div>
            <div>
              <p className="text-2xl font-bold">{displayBadges.length}</p>
              <p className="text-sm text-muted-foreground">뱃지</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-3 rounded-xl border border-border bg-card p-4"
          >
            <div className="rounded-lg bg-destructive/20 p-2">
              <Flame className="h-6 w-6 text-destructive" />
            </div>
            <div>
              <p className="text-2xl font-bold">{displayUser.streak}</p>
              <p className="text-sm text-muted-foreground">연속 학습일</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="flex items-center gap-3 rounded-xl border border-border bg-card p-4"
          >
            <div className="rounded-lg bg-emerald-500/20 p-2">
              <TrendingUp className="h-6 w-6 text-emerald-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{displayStats?.totalXP?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">총 XP</p>
            </div>
          </motion.div>
        </div>

        {/* Problem Stats by Type */}
        {displayStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-xl border border-border bg-card p-6"
          >
            <h2 className="mb-4 flex items-center gap-2 font-semibold">
              <Target className="h-5 w-5 text-primary" />
              문제 유형별 통계
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg bg-blue-500/10 p-3">
                <p className="text-sm text-muted-foreground">빈칸 채우기</p>
                <p className="text-xl font-bold text-blue-500">{displayStats.solvedByType?.blank || 0}</p>
              </div>
              <div className="rounded-lg bg-purple-500/10 p-3">
                <p className="text-sm text-muted-foreground">퍼즐 (코드 정렬)</p>
                <p className="text-xl font-bold text-purple-500">{displayStats.solvedByType?.puzzle || 0}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Badges */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <h2 className="mb-4 flex items-center gap-2 font-semibold">
            <Award className="h-5 w-5 text-warning" />
            획득한 뱃지
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {displayBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex items-center gap-3 rounded-lg border border-border p-3 transition-colors hover:border-primary/50"
              >
                <span className="text-2xl">{badge.icon}</span>
                <div>
                  <p className="font-medium">{badge.name}</p>
                  <p className="text-xs text-muted-foreground">{badge.description}</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    badge.rarity === 'legendary'
                      ? 'border-yellow-500 text-yellow-500'
                      : badge.rarity === 'epic'
                      ? 'border-purple-500 text-purple-500'
                      : badge.rarity === 'rare'
                      ? 'border-blue-500 text-blue-500'
                      : 'border-gray-500 text-gray-500'
                  }
                >
                  {badge.rarity}
                </Badge>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <h2 className="mb-4 font-semibold">최근 활동</h2>
          <div className="space-y-3">
            {displayActivity.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between border-b border-border pb-3 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`rounded-lg p-2 ${
                      a.type === 'solved'
                        ? 'bg-primary/20'
                        : a.type === 'badge'
                        ? 'bg-warning/20'
                        : a.type === 'streak'
                        ? 'bg-destructive/20'
                        : 'bg-emerald-500/20'
                    }`}
                  >
                    {a.type === 'solved' && <Trophy className="h-4 w-4 text-primary" />}
                    {a.type === 'badge' && <Award className="h-4 w-4 text-warning" />}
                    {a.type === 'streak' && <Flame className="h-4 w-4 text-destructive" />}
                    {a.type === 'levelup' && <Zap className="h-4 w-4 text-emerald-500" />}
                  </div>
                  <div>
                    <p className="font-medium">{a.title}</p>
                    <p className="text-sm text-muted-foreground">{a.description}</p>
                  </div>
                </div>
                {a.xpGained && (
                  <Badge variant="secondary" className="bg-primary/20 text-primary">
                    +{a.xpGained} XP
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
