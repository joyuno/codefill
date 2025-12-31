'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { StatCards } from '@/components/dashboard/StatCards';
import { GrassHeatmap } from '@/components/dashboard/GrassHeatmap';
import { Code2, ArrowLeft, User, UserPlus, Loader2, UserCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  publicProfileApi,
  type PublicProfile,
  type PublicBadge,
  type PublicFarm,
  type ActivityData,
} from '@/lib/api/users';
import { friendsApi } from '@/lib/api/friends';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

// 공개 프로필 전체 데이터 타입
interface PublicProfileData {
  profile: PublicProfile;
  badges: PublicBadge[];
  farm: PublicFarm;
  activity: ActivityData;
}

export default function PublicProfilePage() {
  const params = useParams();
  const username = decodeURIComponent(params.username as string);
  const { profile: myProfile, isAuthenticated } = useAuth();

  // 모든 데이터를 한 번에 관리
  const [data, setData] = useState<PublicProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 친구 추가 상태
  const [addingFriend, setAddingFriend] = useState(false);
  const [friendRequestSent, setFriendRequestSent] = useState(false);

  // 본인 프로필인지 확인
  const isOwnProfile = myProfile?.username === username;

  // 친구 추가 핸들러
  const handleAddFriend = async () => {
    if (!data?.profile.id || !isAuthenticated) return;

    setAddingFriend(true);
    try {
      await friendsApi.sendRequest(data.profile.id);
      setFriendRequestSent(true);
    } catch (err) {
      console.error('친구 요청 실패:', err);
    } finally {
      setAddingFriend(false);
    }
  };

  // 모든 데이터를 한 번에 fetch
  useEffect(() => {
    let isMounted = true;

    async function loadAllData() {
      try {
        setIsLoading(true);
        setError(null);

        // 모든 API를 병렬로 호출 - allSettled로 일부 실패해도 나머지는 처리
        const results = await Promise.allSettled([
          publicProfileApi.getProfile(username),
          publicProfileApi.getBadges(username),
          publicProfileApi.getFarm(username),
          publicProfileApi.getActivity(username, 365),
        ]);

        const [profileResult, badgesResult, farmResult, activityResult] = results;

        // 프로필은 필수 - 실패하면 사용자 없음
        if (profileResult.status === 'rejected') {
          console.error('Profile load failed:', profileResult.reason);
          if (isMounted) {
            setError('사용자를 찾을 수 없습니다.');
          }
          return;
        }

        const profile = profileResult.value;

        // 나머지는 실패해도 기본값 사용
        const badges = badgesResult.status === 'fulfilled' ? badgesResult.value : [];
        const farm: PublicFarm = farmResult.status === 'fulfilled'
          ? farmResult.value
          : { hasCharacter: false, character: null, farmLevel: 1, gold: 0, slots: [] };
        const activity: ActivityData = activityResult.status === 'fulfilled'
          ? activityResult.value
          : { days: [], totalDays: 0 };

        if (isMounted) {
          setData({ profile, badges, farm, activity });
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        if (isMounted) {
          setError('사용자를 찾을 수 없습니다.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    if (username) {
      loadAllData();
    }

    return () => {
      isMounted = false;
    };
  }, [username]);

  // 로딩 중
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Code2 className="h-8 w-8 text-primary" />
        </motion.div>
      </div>
    );
  }

  // 사용자 없음
  if (error || !data) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex items-center justify-center py-20">
          <div className="text-center space-y-4">
            <User className="h-16 w-16 text-muted-foreground mx-auto" />
            <h1 className="text-2xl font-bold">사용자를 찾을 수 없습니다</h1>
            <p className="text-muted-foreground">
              &apos;{username}&apos; 사용자가 존재하지 않습니다.
            </p>
            <Link href="/">
              <Button variant="outline" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                홈으로 돌아가기
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { profile, badges, farm, activity } = data;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          {/* SidebarProfile에 데이터 전달 */}
          <SidebarProfile
            username={username}
            publicData={{ profile, badges, farm }}
          />
        </aside>
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            {/* 프로필 헤더 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl border border-border bg-card p-6"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={profile.avatarUrl || undefined} alt={profile.username} />
                    <AvatarFallback
                      className="text-2xl font-bold text-white"
                      style={{ backgroundColor: profile.avatarColor }}
                    >
                      {profile.username.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h1 className="text-2xl font-bold">{profile.username}</h1>
                    <p className="text-muted-foreground">
                      Lv.{profile.level} &middot; 가입일: {new Date(profile.joinedAt).toLocaleDateString('ko-KR')}
                    </p>
                  </div>
                </div>
                {/* 친구 추가 버튼 (본인 프로필이 아닐 때만) */}
                {!isOwnProfile && isAuthenticated && (
                  <Button
                    onClick={handleAddFriend}
                    disabled={addingFriend || friendRequestSent}
                    className="gap-2"
                    variant={friendRequestSent ? "secondary" : "default"}
                  >
                    {addingFriend ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : friendRequestSent ? (
                      <>
                        <UserCheck className="h-4 w-4" />
                        요청 보냄
                      </>
                    ) : (
                      <>
                        <UserPlus className="h-4 w-4" />
                        친구 추가
                      </>
                    )}
                  </Button>
                )}
              </div>
            </motion.div>

            {/* 통계 카드 - 데이터 전달 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <StatCards
                username={username}
                publicData={{
                  solvedCount: profile.solvedCount,
                  streak: profile.streak,
                  badgeCount: badges.length,
                }}
              />
            </motion.div>

            {/* 잔디 히트맵 - 데이터 전달 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <GrassHeatmap
                username={username}
                publicActivityData={activity}
              />
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
}
