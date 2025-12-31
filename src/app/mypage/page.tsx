'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Award, Flame, Zap, Target, TrendingUp, Loader2, Settings, User, Lock, CreditCard, Trash2, Check, X, Eye, EyeOff, BarChart3, AlertCircle, Camera } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { BadgeIcon } from '@/components/ui/badge-icon';
import { AvatarEditModal } from '@/components/mypage/AvatarEditModal';
import { usersApi, authApi, type UserProfile, type UserStats } from '@/lib/api';
import type { Badge as BadgeType, RecentActivity } from '@/lib/types';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

type TabType = 'profile' | 'settings';

export default function MyPagePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [badges, setBadges] = useState<BadgeType[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Settings states
  const [editingNickname, setEditingNickname] = useState(false);
  const [newNickname, setNewNickname] = useState('');
  const [nicknameLoading, setNicknameLoading] = useState(false);
  const [nicknameError, setNicknameError] = useState('');

  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  // Avatar modal state
  const [avatarModalOpen, setAvatarModalOpen] = useState(false);

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
        setError('사용자 정보를 불러오는데 실패했습니다. 다시 시도해주세요.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // 닉네임 변경 핸들러 (30일에 1회 제한)
  const handleNicknameChange = async () => {
    if (!newNickname.trim()) {
      setNicknameError('닉네임을 입력해주세요');
      return;
    }
    if (newNickname.length < 2 || newNickname.length > 20) {
      setNicknameError('닉네임은 2-20자 사이여야 합니다');
      return;
    }

    setNicknameLoading(true);
    setNicknameError('');

    try {
      // Use the new changeNickname API with 30-day limit
      const result = await usersApi.changeNickname(newNickname);

      if (result.success) {
        // Update profile with new nickname
        if (profile) {
          setProfile({ ...profile, username: newNickname });
        }
        setEditingNickname(false);
        setNewNickname('');
      } else {
        setNicknameError(result.message);
      }
    } catch (error) {
      setNicknameError(error instanceof Error ? error.message : '닉네임 변경에 실패했습니다');
    } finally {
      setNicknameLoading(false);
    }
  };

  // 비밀번호 변경 핸들러
  const handlePasswordChange = async () => {
    setPasswordError('');
    setPasswordSuccess(false);

    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError('모든 필드를 입력해주세요');
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError('새 비밀번호는 8자 이상이어야 합니다');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('새 비밀번호가 일치하지 않습니다');
      return;
    }

    setPasswordLoading(true);

    try {
      const result = await authApi.changePassword(currentPassword, newPassword);
      if (result.error) {
        setPasswordError(result.error.message);
      } else {
        setPasswordSuccess(true);
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setTimeout(() => {
          setShowPasswordForm(false);
          setPasswordSuccess(false);
        }, 2000);
      }
    } catch (error) {
      setPasswordError(error instanceof Error ? error.message : '비밀번호 변경에 실패했습니다');
    } finally {
      setPasswordLoading(false);
    }
  };

  // 프로필 이미지 저장 핸들러 (모달에서 크롭 후 호출)
  const handleAvatarSave = async (file: File) => {
    const result = await usersApi.uploadAvatar(file);
    if (result.success && profile) {
      setProfile({ ...profile, avatarColor: result.avatar_url });
    }
  };

  // 프로필 이미지 삭제 핸들러
  const handleAvatarDelete = async () => {
    await usersApi.deleteAvatar();
    if (profile) {
      setProfile({ ...profile, avatarColor: 'hsl(142, 71%, 45%)' });
    }
  };

  // 회원 탈퇴 핸들러
  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== '탈퇴합니다') {
      setDeleteError("'탈퇴합니다'를 정확히 입력해주세요");
      return;
    }

    setDeleteLoading(true);
    setDeleteError('');

    try {
      const result = await authApi.withdraw(deleteConfirmation);
      if (result.error) {
        setDeleteError(result.error.message);
      } else {
        router.push('/');
      }
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : '회원 탈퇴에 실패했습니다');
    } finally {
      setDeleteLoading(false);
    }
  };

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

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
          <AlertCircle className="h-12 w-12 text-destructive" />
          <h2 className="text-xl font-semibold">정보를 불러올 수 없습니다</h2>
          <p className="text-muted-foreground">{error || '로그인이 필요합니다.'}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-lg bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  const displayUser = profile;
  const displayStats = stats;
  const displayBadges = badges;
  const displayActivity = recentActivity;
  const xpProgress = ((displayUser.currentXP || 0) / (displayUser.requiredXP || 3000)) * 100;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <main className="mx-auto max-w-4xl space-y-6 p-6">
        {/* Tab Navigation */}
        <div className="flex gap-2 border-b border-border pb-2">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'profile'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            <User className="h-4 w-4" />
            프로필
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'settings'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            <Settings className="h-4 w-4" />
            설정
          </button>
        </div>

        <AnimatePresence mode="wait">
        {activeTab === 'profile' ? (
          <motion.div
            key="profile"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
            {/* Avatar with edit button */}
            <button
              type="button"
              onClick={() => setAvatarModalOpen(true)}
              className="relative group cursor-pointer"
            >
              <Avatar className="h-20 w-20">
                <AvatarImage
                  src={displayUser.avatarColor?.startsWith('http') ? displayUser.avatarColor : undefined}
                  alt={displayUser.username}
                />
                <AvatarFallback
                  className="text-3xl font-bold text-primary-foreground"
                  style={{ backgroundColor: displayUser.avatarColor?.startsWith('hsl') ? displayUser.avatarColor : 'hsl(142, 71%, 45%)' }}
                >
                  {displayUser.username.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              {/* Hover overlay */}
              <div className="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                <Camera className="h-6 w-6 text-white" />
              </div>
            </button>
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
                {badge.iconUrl ? (
                  <img
                    src={badge.iconUrl}
                    alt={badge.name}
                    className="h-12 w-12 object-contain"
                  />
                ) : (
                  <BadgeIcon name={badge.name} rarity={badge.rarity} size="lg" />
                )}
                <div className="flex-1 min-w-0">
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
          </motion.div>
        ) : (
          <motion.div
            key="settings"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* 학습 통계 */}
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-4 flex items-center gap-2 font-semibold">
                <BarChart3 className="h-5 w-5 text-primary" />
                학습 통계
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">총 푼 문제</p>
                  <p className="text-2xl font-bold">{displayStats?.totalSolved || displayUser.solvedCount || 0}</p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">정답률</p>
                  <p className="text-2xl font-bold">
                    {displayStats?.totalSolved && displayStats.totalSolved > 0
                      ? Math.round((displayStats.totalSolved / (displayStats.totalSolved + 10)) * 100)
                      : 0}%
                  </p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">현재 스트릭</p>
                  <p className="text-2xl font-bold">{displayStats?.currentStreak || displayUser.streak || 0}일</p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">최고 스트릭</p>
                  <p className="text-2xl font-bold">{displayStats?.maxStreak || 0}일</p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">쉬운 문제</p>
                  <p className="text-2xl font-bold text-green-500">{displayStats?.solvedByDifficulty?.easy || 0}</p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">어려운 문제</p>
                  <p className="text-2xl font-bold text-red-500">{displayStats?.solvedByDifficulty?.hard || 0}</p>
                </div>
              </div>
            </div>

            {/* 구독 상태 */}
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-4 flex items-center gap-2 font-semibold">
                <CreditCard className="h-5 w-5 text-primary" />
                구독 상태
              </h2>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Badge variant={displayUser.subscription === 'pro' ? 'default' : 'secondary'} className="capitalize">
                      {displayUser.subscription} Plan
                    </Badge>
                    {displayUser.subscription === 'free' && (
                      <span className="text-sm text-muted-foreground">무료 플랜 사용 중</span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {displayUser.subscription === 'free'
                      ? 'Pro 플랜으로 업그레이드하면 모든 문제와 기능을 이용할 수 있습니다.'
                      : displayUser.subscription === 'pro'
                      ? '모든 문제와 기능을 이용할 수 있습니다.'
                      : '팀 기능과 함께 모든 기능을 이용할 수 있습니다.'}
                  </p>
                </div>
                {displayUser.subscription === 'free' && (
                  <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                    업그레이드
                  </button>
                )}
              </div>
            </div>

            {/* 닉네임 변경 */}
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-4 flex items-center gap-2 font-semibold">
                <User className="h-5 w-5 text-primary" />
                닉네임 변경
              </h2>
              {editingNickname ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={newNickname}
                    onChange={(e) => setNewNickname(e.target.value)}
                    placeholder="새 닉네임 (2-20자)"
                    className="w-full rounded-lg border border-border bg-background px-4 py-2 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  {nicknameError && <p className="text-sm text-destructive">{nicknameError}</p>}
                  <div className="flex gap-2">
                    <button
                      onClick={handleNicknameChange}
                      disabled={nicknameLoading}
                      className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                    >
                      {nicknameLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                      저장
                    </button>
                    <button
                      onClick={() => { setEditingNickname(false); setNewNickname(''); setNicknameError(''); }}
                      className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                    >
                      <X className="h-4 w-4" />
                      취소
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">현재 닉네임: <span className="font-medium text-foreground">{displayUser.username}</span></p>
                  <button
                    onClick={() => { setEditingNickname(true); setNewNickname(displayUser.username); }}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                  >
                    변경
                  </button>
                </div>
              )}
            </div>

            {/* 비밀번호 변경 */}
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-4 flex items-center gap-2 font-semibold">
                <Lock className="h-5 w-5 text-primary" />
                비밀번호 변경
              </h2>
              {showPasswordForm ? (
                <div className="space-y-3">
                  <div className="relative">
                    <input
                      type={showCurrentPassword ? 'text' : 'password'}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="현재 비밀번호"
                      className="w-full rounded-lg border border-border bg-background px-4 py-2 pr-10 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="새 비밀번호 (8자 이상)"
                      className="w-full rounded-lg border border-border bg-background px-4 py-2 pr-10 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="새 비밀번호 확인"
                    className="w-full rounded-lg border border-border bg-background px-4 py-2 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  {passwordError && <p className="text-sm text-destructive">{passwordError}</p>}
                  {passwordSuccess && <p className="text-sm text-green-500">비밀번호가 변경되었습니다!</p>}
                  <div className="flex gap-2">
                    <button
                      onClick={handlePasswordChange}
                      disabled={passwordLoading}
                      className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                    >
                      {passwordLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                      변경
                    </button>
                    <button
                      onClick={() => { setShowPasswordForm(false); setCurrentPassword(''); setNewPassword(''); setConfirmPassword(''); setPasswordError(''); }}
                      className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                    >
                      <X className="h-4 w-4" />
                      취소
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <p className="text-muted-foreground">비밀번호를 변경하려면 버튼을 클릭하세요</p>
                  <button
                    onClick={() => setShowPasswordForm(true)}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                  >
                    변경
                  </button>
                </div>
              )}
            </div>

            {/* 회원 탈퇴 */}
            <div className="rounded-xl border border-destructive/50 bg-card p-6">
              <h2 className="mb-4 flex items-center gap-2 font-semibold text-destructive">
                <Trash2 className="h-5 w-5" />
                회원 탈퇴
              </h2>
              <p className="mb-4 text-sm text-muted-foreground">
                회원 탈퇴 시 모든 데이터가 삭제되며 복구할 수 없습니다. 신중하게 결정해주세요.
              </p>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90"
              >
                회원 탈퇴
              </button>
            </div>
          </motion.div>
        )}
        </AnimatePresence>

        {/* Delete Account Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mx-4 w-full max-w-md rounded-xl border border-border bg-card p-6"
            >
              <h3 className="mb-4 text-lg font-semibold text-destructive">회원 탈퇴</h3>
              <p className="mb-2 text-sm text-muted-foreground">
                정말로 탈퇴하시겠습니까?
              </p>
              <div className="mb-4 rounded-lg bg-muted/50 p-3 text-sm text-muted-foreground">
                <p className="mb-1">• 탈퇴 후 <span className="font-semibold text-primary">30일 이내</span>에 로그인하시면 계정을 복구할 수 있습니다.</p>
                <p>• 30일이 지나면 모든 데이터가 <span className="font-semibold text-destructive">영구 삭제</span>됩니다.</p>
              </div>
              <p className="mb-4 text-sm text-muted-foreground">
                탈퇴를 원하시면 아래에 <span className="font-semibold text-destructive">'탈퇴합니다'</span>를 입력해주세요.
              </p>
              <input
                type="text"
                value={deleteConfirmation}
                onChange={(e) => setDeleteConfirmation(e.target.value)}
                placeholder="탈퇴합니다"
                className="mb-3 w-full rounded-lg border border-border bg-background px-4 py-2 focus:border-destructive focus:outline-none focus:ring-1 focus:ring-destructive"
              />
              {deleteError && <p className="mb-3 text-sm text-destructive">{deleteError}</p>}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => { setShowDeleteModal(false); setDeleteConfirmation(''); setDeleteError(''); }}
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                >
                  취소
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={deleteLoading || deleteConfirmation !== '탈퇴합니다'}
                  className="flex items-center gap-2 rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50"
                >
                  {deleteLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                  탈퇴하기
                </button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Avatar Edit Modal */}
        <AvatarEditModal
          open={avatarModalOpen}
          onOpenChange={setAvatarModalOpen}
          currentAvatarUrl={displayUser.avatarColor?.startsWith('http') ? displayUser.avatarColor : undefined}
          username={displayUser.username}
          avatarColor={displayUser.avatarColor || 'hsl(142, 71%, 45%)'}
          onSave={handleAvatarSave}
          onDelete={handleAvatarDelete}
        />
      </main>
    </div>
  );
}
