'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Shield,
  User,
  Ban,
  Mail,
  Calendar,
  Trophy,
  Flame,
  Target,
  Zap,
  Crown,
  Clock,
  CheckCircle,
  XCircle,
  BookOpen,
  Briefcase,
  GraduationCap,
  AtSign,
  Award,
  Activity,
  Code,
  Puzzle,
  BookMarked,
  Gem,
  Trash2,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { adminApi, type AdminUserDetail } from '@/lib/api/admin';
import { toast } from 'sonner';

// 구독 티어 설정
const subscriptionConfig: Record<string, { label: string; color: string; bgColor: string; icon: React.ReactNode }> = {
  free: { label: 'Free', color: 'text-zinc-400', bgColor: 'bg-zinc-500/10', icon: <User className="h-3 w-3" /> },
  basic: { label: 'Basic', color: 'text-blue-400', bgColor: 'bg-blue-500/10', icon: <Zap className="h-3 w-3" /> },
  pro: { label: 'Pro', color: 'text-amber-400', bgColor: 'bg-amber-500/10', icon: <Crown className="h-3 w-3" /> },
};

// 배지 희귀도 설정
const rarityConfig: Record<string, { color: string; bgColor: string; borderColor: string }> = {
  common: { color: 'text-zinc-400', bgColor: 'bg-zinc-500/10', borderColor: 'border-zinc-500/20' },
  uncommon: { color: 'text-emerald-400', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/20' },
  rare: { color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/20' },
  epic: { color: 'text-purple-400', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/20' },
  legendary: { color: 'text-amber-400', bgColor: 'bg-amber-500/10', borderColor: 'border-amber-500/20' },
};

// XP에서 레벨 진행률 계산 (간단한 공식)
function getLevelProgress(level: number, totalXp: number): number {
  const xpForCurrentLevel = (level - 1) * 100;
  const xpForNextLevel = level * 100;
  const currentLevelXp = totalXp - xpForCurrentLevel;
  const requiredXp = xpForNextLevel - xpForCurrentLevel;
  return Math.min((currentLevelXp / requiredXp) * 100, 100);
}

export default function AdminUserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const userId = params.id as string;

  const [user, setUser] = useState<AdminUserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogAction, setDialogAction] = useState<'role' | 'ban' | 'delete' | null>(null);
  const [banDuration, setBanDuration] = useState<string>('7');  // 정지 기간 (일)
  const [confirmEmail, setConfirmEmail] = useState('');  // 삭제 확인용 이메일
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await adminApi.getUserDetail(userId);
        setUser(data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
        toast.error('사용자 정보를 불러오는데 실패했습니다');
        router.push('/admin/users');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId, router]);

  const handleRoleChange = async () => {
    if (!user) return;

    try {
      const newRole = user.role === 'admin' ? 'user' : 'admin';
      await adminApi.updateUserRole(user.id, newRole);
      toast.success(`역할이 ${newRole === 'admin' ? '관리자' : '일반 사용자'}로 변경되었습니다`);
      setUser({ ...user, role: newRole });
    } catch (error) {
      console.error('Failed to update role:', error);
      toast.error('역할 변경에 실패했습니다');
    } finally {
      setDialogAction(null);
    }
  };

  const handleBanToggle = async () => {
    if (!user) return;

    try {
      const isBanned = isUserBanned(user);
      const newBanState = !isBanned;

      if (newBanState) {
        // 정지할 때: 기간 옵션 전달
        const banDays = banDuration === 'permanent' ? undefined : parseInt(banDuration);
        const result = await adminApi.banUser(user.id, true, { ban_days: banDays });
        toast.success(
          banDuration === 'permanent'
            ? '사용자가 영구 정지되었습니다'
            : `사용자가 ${banDuration}일간 정지되었습니다`
        );
        setUser({
          ...user,
          banned_until: result.banned_until || null,
        });
      } else {
        // 정지 해제
        await adminApi.banUser(user.id, false);
        toast.success('정지가 해제되었습니다');
        setUser({
          ...user,
          banned_until: null,
        });
      }
    } catch (error) {
      console.error('Failed to ban/unban user:', error);
      toast.error('작업에 실패했습니다');
    } finally {
      setDialogAction(null);
      setBanDuration('7');
    }
  };

  const handleDeleteUser = async () => {
    if (!user || confirmEmail !== user.email) return;

    setIsDeleting(true);
    try {
      await adminApi.deleteUser(user.id);
      toast.success('사용자가 완전히 삭제되었습니다');
      router.push('/admin/users');
    } catch (error) {
      console.error('Failed to delete user:', error);
      toast.error('사용자 삭제에 실패했습니다');
    } finally {
      setIsDeleting(false);
      setDialogAction(null);
      setConfirmEmail('');
    }
  };

  // 사용자 정지 여부 체크 (banned_until 기준)
  const isUserBanned = (u: AdminUserDetail): boolean => {
    if (!u.banned_until) return false;
    const bannedUntil = new Date(u.banned_until);
    return bannedUntil > new Date();
  };

  // 정지 만료일 포맷팅
  const formatBannedUntil = (bannedUntil: string): string => {
    const date = new Date(bannedUntil);
    if (date.getFullYear() >= 9999) {
      return '영구 정지';
    }
    return `${date.getFullYear()}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getDate().toString().padStart(2, '0')}까지`;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-white/5 animate-pulse" />
          <div className="space-y-2">
            <div className="h-6 w-48 bg-white/5 animate-pulse rounded" />
            <div className="h-4 w-32 bg-white/5 animate-pulse rounded" />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-white/5 animate-pulse rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) return null;

  const subscription = subscriptionConfig[user.subscription_tier] || subscriptionConfig.free;
  const levelProgress = getLevelProgress(user.level, user.total_xp);
  const solveRate = user.problems_attempted > 0
    ? Math.round((user.problems_solved / user.problems_attempted) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link href="/admin/users">
          <Button variant="ghost" size="icon" className="rounded-xl bg-white/5 hover:bg-white/10">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>

        <div className="flex-1 flex items-start gap-4">
          {/* Avatar */}
          <div className="relative">
            <Avatar className="h-16 w-16 border-2 border-white/10">
              <AvatarImage src={user.avatar_url || undefined} alt={user.name || 'User'} />
              <AvatarFallback className="bg-gradient-to-br from-primary/30 to-primary/10 text-lg font-semibold">
                {(user.name || user.email)?.[0]?.toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            {user.role === 'admin' && (
              <div className="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary border-2 border-background">
                <Shield className="h-3 w-3 text-white" />
              </div>
            )}
          </div>

          {/* User Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold truncate">{user.name || 'Unknown'}</h1>
              {user.username && (
                <span className="text-sm text-muted-foreground">@{user.username}</span>
              )}
            </div>
            <p className="text-sm text-muted-foreground truncate">{user.email}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              {/* Role Badge */}
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                user.role === 'admin'
                  ? 'bg-primary/15 text-primary border border-primary/20'
                  : 'bg-white/5 text-muted-foreground border border-white/10'
              }`}>
                {user.role === 'admin' ? <Shield className="h-3 w-3" /> : <User className="h-3 w-3" />}
                {user.role === 'admin' ? '관리자' : '사용자'}
              </span>

              {/* Subscription Badge */}
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${subscription.bgColor} ${subscription.color} border border-current/20`}>
                {subscription.icon}
                {subscription.label}
              </span>

              {/* Status Badge */}
              {isUserBanned(user) ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                  <XCircle className="h-3 w-3" />
                  {user.banned_until && formatBannedUntil(user.banned_until)}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle className="h-3 w-3" />
                  정상
                </span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="shrink-0">
            <Button
              variant={isUserBanned(user) ? 'outline' : 'destructive'}
              size="sm"
              onClick={() => setDialogAction('ban')}
              className={`rounded-xl ${isUserBanned(user) ? 'bg-white/5 border-white/10 hover:bg-white/10' : ''}`}
            >
              <Ban className="h-4 w-4 mr-1.5" />
              {isUserBanned(user) ? '정지 해제' : '사용자 정지'}
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Level Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-violet-600/5">
              <Trophy className="h-5 w-5 text-violet-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">레벨</p>
              <p className="text-2xl font-bold">{user.level}</p>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">진행률</span>
              <span className="text-violet-400">{Math.round(levelProgress)}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-500 to-violet-400 transition-all"
                style={{ width: `${levelProgress}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              총 {user.total_xp.toLocaleString()} XP
            </p>
          </div>
        </motion.div>

        {/* Problems Solved Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/5">
              <Target className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">푼 문제</p>
              <p className="text-2xl font-bold">{user.problems_solved}</p>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">성공률</span>
              <span className="text-emerald-400">{solveRate}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all"
                style={{ width: `${solveRate}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              {user.problems_attempted}개 시도 중 {user.problems_solved}개 성공
            </p>
          </div>
        </motion.div>

        {/* Streak Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500/20 to-orange-600/5">
              <Flame className="h-5 w-5 text-orange-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">현재 스트릭</p>
              <p className="text-2xl font-bold">{user.current_streak}<span className="text-sm font-normal text-muted-foreground">일</span></p>
            </div>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-white/5">
            <span className="text-xs text-muted-foreground">최장 스트릭</span>
            <span className="text-sm font-medium text-orange-400">{user.longest_streak}일</span>
          </div>
        </motion.div>

        {/* Activity Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/5">
              <Clock className="h-5 w-5 text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">마지막 활동</p>
              <p className="text-sm font-medium">
                {user.last_activity_date
                  ? new Date(user.last_activity_date).toLocaleDateString('ko-KR')
                  : '기록 없음'}
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-white/5">
            <span className="text-xs text-muted-foreground">가입일</span>
            <span className="text-sm font-medium">{new Date(user.created_at).toLocaleDateString('ko-KR')}</span>
          </div>
        </motion.div>
      </div>

      {/* Detail Info */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Account Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <User className="h-4 w-4 text-primary" />
            계정 정보
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">이메일</p>
                <p className="text-sm font-medium truncate">{user.email}</p>
              </div>
            </div>
            {user.username && (
              <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
                <AtSign className="h-4 w-4 text-muted-foreground shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs text-muted-foreground">사용자명</p>
                  <p className="text-sm font-medium">@{user.username}</p>
                </div>
              </div>
            )}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <Shield className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">가입 방법</p>
                <p className="text-sm font-medium capitalize">{user.provider}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">가입일</p>
                <p className="text-sm font-medium">
                  {new Date(user.created_at).toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Onboarding Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-primary" />
            온보딩 정보
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <Briefcase className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">현재 상태</p>
                <p className="text-sm font-medium">{user.current_status || '미설정'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <Target className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">학습 목표</p>
                <p className="text-sm font-medium">{user.learning_goal || '미설정'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/3">
              <GraduationCap className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">경험 수준</p>
                <p className="text-sm font-medium">{user.experience_level || '미설정'}</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Problem Type Breakdown, Badges & Recent Activity */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Problem Type Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            유형별 풀이
          </h3>
          <div className="space-y-3">
            {/* Blank */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-cyan-500/10 to-transparent border border-cyan-500/10">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/15">
                <Code className="h-4 w-4 text-cyan-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-muted-foreground">빈칸 채우기</p>
              </div>
              <p className="text-xl font-bold text-cyan-400">{user.blank_solved || 0}</p>
            </div>
            {/* Puzzle */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-pink-500/10 to-transparent border border-pink-500/10">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-pink-500/15">
                <Puzzle className="h-4 w-4 text-pink-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-muted-foreground">코드 퍼즐</p>
              </div>
              <p className="text-xl font-bold text-pink-400">{user.puzzle_solved || 0}</p>
            </div>
            {/* Guided */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-amber-500/10 to-transparent border border-amber-500/10">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/15">
                <BookMarked className="h-4 w-4 text-amber-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-muted-foreground">가이드</p>
              </div>
              <p className="text-xl font-bold text-amber-400">{user.guided_solved || 0}</p>
            </div>
          </div>
        </motion.div>

        {/* Badges */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Award className="h-4 w-4 text-primary" />
            획득한 배지
            {user.badges && user.badges.length > 0 && (
              <span className="ml-auto text-xs text-muted-foreground">{user.badges.length}개</span>
            )}
          </h3>
          {user.badges && user.badges.length > 0 ? (
            <div className="space-y-2">
              {user.badges.slice(0, 4).map((badge) => {
                const rarity = rarityConfig[badge.rarity] || rarityConfig.common;
                return (
                  <div
                    key={badge.id}
                    className={`flex items-center gap-2.5 p-2.5 rounded-xl ${rarity.bgColor} border ${rarity.borderColor} transition-colors hover:bg-white/5`}
                    title={badge.description || badge.name}
                  >
                    {badge.icon_url ? (
                      <img src={badge.icon_url} alt={badge.name} className="h-7 w-7 shrink-0" />
                    ) : (
                      <div className={`h-7 w-7 rounded-lg flex items-center justify-center ${rarity.bgColor}`}>
                        <Gem className={`h-4 w-4 ${rarity.color}`} />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className={`text-xs font-medium truncate ${rarity.color}`}>{badge.name}</p>
                    </div>
                    <p className="text-[10px] text-muted-foreground shrink-0">
                      {new Date(badge.earned_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                    </p>
                  </div>
                );
              })}
              {user.badges.length > 4 && (
                <p className="text-xs text-muted-foreground text-center pt-1">
                  +{user.badges.length - 4}개 더
                </p>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 mb-2">
                <Award className="h-5 w-5 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground">획득한 배지 없음</p>
            </div>
          )}
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="admin-glass-card rounded-2xl p-5"
        >
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            최근 활동
          </h3>
          {user.recent_activity && user.recent_activity.length > 0 ? (
            <div className="space-y-2">
              {user.recent_activity.slice(0, 4).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white/3 hover:bg-white/5 transition-colors"
                >
                  <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${
                    activity.type === 'badge' ? 'bg-amber-500/15' : 'bg-emerald-500/15'
                  }`}>
                    {activity.type === 'badge' ? (
                      <Award className="h-3.5 w-3.5 text-amber-400" />
                    ) : (
                      <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium truncate">{activity.title}</p>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(activity.timestamp).toLocaleDateString('ko-KR', {
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                      {activity.xp_earned && activity.xp_earned > 0 && (
                        <span className="text-[10px] text-emerald-400 font-medium">
                          +{activity.xp_earned} XP
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 mb-2">
                <Activity className="h-5 w-5 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground">최근 활동 없음</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Admin Role Management Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45 }}
        className="admin-glass-card rounded-2xl p-5 border border-white/5"
      >
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <Shield className="h-4 w-4 text-primary" />
          권한 관리
        </h3>

        {user.role === 'admin' ? (
          <div className="flex items-center justify-between p-4 rounded-xl bg-primary/5 border border-primary/10">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/15">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-primary">관리자 권한 보유</p>
                <p className="text-xs text-muted-foreground">이 사용자는 관리자 권한을 가지고 있습니다</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDialogAction('role')}
              className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10 text-muted-foreground"
            >
              관리자 권한 해제
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/15 shrink-0 mt-0.5">
                  <Shield className="h-4 w-4 text-amber-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-amber-400">관리자 권한 부여 주의사항</p>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    관리자 권한을 부여하면 이 사용자는 모든 사용자 정보 조회, 문제 관리,
                    콘텐츠 삭제 등의 권한을 갖게 됩니다. 신뢰할 수 있는 사용자에게만 부여해주세요.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                onClick={() => setDialogAction('role')}
                className="rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                <Shield className="h-4 w-4 mr-1.5" />
                관리자로 승급
              </Button>
            </div>
          </div>
        )}
      </motion.div>

      {/* Danger Zone - 페이지 하단 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="admin-glass-card rounded-2xl p-5 border border-red-500/10 bg-red-950/10"
      >
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2 text-red-400/80">
          <AlertTriangle className="h-4 w-4" />
          위험 영역
        </h3>
        <div className="flex items-start gap-3 p-3 rounded-xl bg-red-500/5 border border-red-500/10">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-500/10 shrink-0">
            <Trash2 className="h-4 w-4 text-red-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-red-400">계정 완전 삭제</p>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              이 사용자의 계정과 모든 관련 데이터를 영구적으로 삭제합니다.
              <span className="text-red-400/70"> 이 작업은 되돌릴 수 없습니다.</span>
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDialogAction('delete')}
            className="shrink-0 rounded-xl border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
          >
            <Trash2 className="h-3.5 w-3.5 mr-1.5" />
            삭제
          </Button>
        </div>
      </motion.div>

      {/* Role Change Dialog */}
      <AlertDialog
        open={dialogAction === 'role'}
        onOpenChange={() => setDialogAction(null)}
      >
        <AlertDialogContent className="admin-glass-card border-white/10 max-w-md">
          <AlertDialogHeader>
            <div className={`flex items-center justify-center w-12 h-12 rounded-xl mx-auto mb-3 ${
              user.role === 'admin' ? 'bg-white/10' : 'bg-emerald-500/15'
            }`}>
              <Shield className={`h-6 w-6 ${user.role === 'admin' ? 'text-muted-foreground' : 'text-emerald-400'}`} />
            </div>
            <AlertDialogTitle className="text-center">
              {user.role === 'admin' ? '관리자 권한 해제' : '관리자 권한 부여'}
            </AlertDialogTitle>
            <AlertDialogDescription className="text-center">
              {user.role === 'admin' ? (
                <>
                  <strong>{user.name || user.email}</strong>의 관리자 권한을 해제하시겠습니까?<br />
                  <span className="text-muted-foreground/70 text-xs">더 이상 관리 기능에 접근할 수 없습니다.</span>
                </>
              ) : (
                <>
                  <strong>{user.name || user.email}</strong>에게 관리자 권한을 부여하시겠습니까?<br />
                  <span className="text-amber-400/80 text-xs">관리자는 모든 관리 기능에 접근할 수 있습니다.</span>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2 mt-4">
            <AlertDialogCancel className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10">
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRoleChange}
              className={`rounded-xl ${
                user.role === 'admin'
                  ? 'bg-white/10 hover:bg-white/20 text-foreground'
                  : 'bg-emerald-600 hover:bg-emerald-700 text-white'
              }`}
            >
              <Shield className="h-4 w-4 mr-1.5" />
              {user.role === 'admin' ? '권한 해제' : '관리자로 승급'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Ban Dialog */}
      <AlertDialog
        open={dialogAction === 'ban'}
        onOpenChange={(open) => {
          if (!open) {
            setDialogAction(null);
            setBanDuration('7');
          }
        }}
      >
        <AlertDialogContent className="admin-glass-card border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle>
              {isUserBanned(user) ? '정지 해제' : '사용자 정지'}
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-4">
                {isUserBanned(user) ? (
                  <p>
                    <span className="font-medium text-foreground">{user.name || user.email}</span>
                    의 정지를 해제하시겠습니까?
                  </p>
                ) : (
                  <>
                    <p>
                      <span className="font-medium text-foreground">{user.name || user.email}</span>
                      를 정지하시겠습니까? 정지된 사용자는 로그인할 수 없습니다.
                    </p>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">정지 기간</label>
                      <Select value={banDuration} onValueChange={setBanDuration}>
                        <SelectTrigger className="w-full bg-white/5 border-white/10 rounded-xl">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1일</SelectItem>
                          <SelectItem value="3">3일</SelectItem>
                          <SelectItem value="7">7일</SelectItem>
                          <SelectItem value="14">14일</SelectItem>
                          <SelectItem value="30">30일</SelectItem>
                          <SelectItem value="90">90일</SelectItem>
                          <SelectItem value="permanent">영구 정지</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="rounded-xl">취소</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBanToggle}
              className={`rounded-xl ${isUserBanned(user) ? '' : 'bg-destructive hover:bg-destructive/90'}`}
            >
              {isUserBanned(user) ? '해제' : '정지'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete User Dialog - 이메일 입력 확인 필요 */}
      <AlertDialog
        open={dialogAction === 'delete'}
        onOpenChange={(open) => {
          if (!open) {
            setDialogAction(null);
            setConfirmEmail('');
          }
        }}
      >
        <AlertDialogContent className="admin-glass-card border-red-500/20 max-w-md">
          <AlertDialogHeader>
            <div className="flex items-center justify-center w-14 h-14 rounded-xl mx-auto mb-3 bg-red-500/10 border border-red-500/20">
              <AlertTriangle className="h-7 w-7 text-red-400" />
            </div>
            <AlertDialogTitle className="text-center text-red-400">
              계정 완전 삭제
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 text-center">
                  <p className="text-sm text-red-400 font-medium mb-1">
                    이 작업은 되돌릴 수 없습니다
                  </p>
                  <p className="text-xs text-muted-foreground">
                    <strong className="text-foreground">{user.name || user.email}</strong>의 계정과
                    모든 활동 기록, 풀이 내역, 배지 등이 영구적으로 삭제됩니다.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">
                    확인을 위해 사용자의 이메일을 입력하세요
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={confirmEmail}
                      onChange={(e) => setConfirmEmail(e.target.value)}
                      placeholder={user.email}
                      className="w-full px-3 py-2 text-sm rounded-xl bg-white/5 border border-white/10 focus:border-red-500/30 focus:outline-none focus:ring-1 focus:ring-red-500/20 transition-colors"
                    />
                    {confirmEmail === user.email && (
                      <CheckCircle className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-red-400" />
                    )}
                  </div>
                  <p className="text-[10px] text-muted-foreground/60">
                    {user.email}
                  </p>
                </div>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2 mt-4">
            <AlertDialogCancel
              className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
              onClick={() => setConfirmEmail('')}
            >
              취소
            </AlertDialogCancel>
            <Button
              onClick={handleDeleteUser}
              disabled={confirmEmail !== user.email || isDeleting}
              className="rounded-xl bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDeleting ? (
                <>
                  <span className="h-4 w-4 mr-1.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  삭제 중...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-1.5" />
                  완전히 삭제
                </>
              )}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
