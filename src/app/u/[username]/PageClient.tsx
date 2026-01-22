'use client';


import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { StatCards } from '@/components/dashboard/StatCards';
import { GrassHeatmap } from '@/components/dashboard/GrassHeatmap';
import { ArrowLeft, User, UserPlus, Loader2, UserCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  publicProfileApi,
  type PublicProfile,
  type PublicBadge,
  type PublicFarm,
  type ActivityData,
  type PublicProfileAll,
} from '@/lib/api/users';
import { friendsApi } from '@/lib/api/friends';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

// 스켈레톤 컴포넌트들
function ProfileHeaderSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 rounded-full bg-muted" />
        <div className="space-y-2">
          <div className="h-6 w-32 bg-muted rounded" />
          <div className="h-4 w-48 bg-muted rounded" />
        </div>
      </div>
    </div>
  );
}

function StatCardsSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="rounded-lg border border-border bg-card p-4 animate-pulse">
          <div className="h-4 w-16 bg-muted rounded mb-2" />
          <div className="h-8 w-24 bg-muted rounded" />
        </div>
      ))}
    </div>
  );
}

function GrassHeatmapSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 animate-pulse">
      <div className="h-5 w-32 bg-muted rounded mb-4" />
      <div className="h-32 w-full bg-muted rounded" />
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <div className="p-4 space-y-4 animate-pulse">
      <div className="flex flex-col items-center gap-3">
        <div className="h-20 w-20 rounded-full bg-muted" />
        <div className="h-5 w-24 bg-muted rounded" />
        <div className="h-4 w-16 bg-muted rounded" />
      </div>
      <div className="h-2 w-full bg-muted rounded" />
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-10 w-full bg-muted rounded" />
        ))}
      </div>
    </div>
  );
}

export default function PublicProfilePageClient() {
  const params = useParams();
  const username = decodeURIComponent(params.username as string);
  const { profile: myProfile, isAuthenticated } = useAuth();

  // 개별 상태 관리 (점진적 렌더링)
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [badges, setBadges] = useState<PublicBadge[] | null>(null);
  const [farm, setFarm] = useState<PublicFarm | null>(null);
  const [activity, setActivity] = useState<ActivityData | null>(null);

  // 프로필 로딩 상태 (필수 데이터)
  const [profileLoading, setProfileLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 친구 추가 상태
  const [addingFriend, setAddingFriend] = useState(false);
  const [friendRequestSent, setFriendRequestSent] = useState(false);

  // 본인 프로필인지 확인
  const isOwnProfile = myProfile?.username === username;

  // 친구 추가 핸들러
  const handleAddFriend = async () => {
    if (!profile?.id || !isAuthenticated) return;

    setAddingFriend(true);
    try {
      await friendsApi.sendRequest(profile.id);
      setFriendRequestSent(true);
    } catch (err) {
      console.error('친구 요청 실패:', err);
    } finally {
      setAddingFriend(false);
    }
  };

  // 통합 API로 한 번에 모든 데이터 로드 (RPC 함수로 DB 쿼리 최적화)
  useEffect(() => {
    let isMounted = true;

    // username 변경 시 모든 상태 초기화
    setProfile(null);
    setBadges(null);
    setFarm(null);
    setActivity(null);
    setProfileLoading(true);
    setError(null);

    async function loadAllData() {
      try {
        // 한 번의 API 호출로 모든 데이터 로드 (RPC 함수 사용)
        const data = await publicProfileApi.getAll(username, 365);
        if (isMounted) {
          setProfile(data.profile);
          setBadges(data.badges);
          setFarm(data.farm);
          setActivity(data.activity);
        }
      } catch (err) {
        console.error('Profile load failed:', err);
        if (isMounted) {
          setError('사용자를 찾을 수 없습니다.');
        }
      } finally {
        if (isMounted) {
          setProfileLoading(false);
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

  // 사용자 없음 (프로필 로딩 완료 후 에러 발생)
  if (!profileLoading && error) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
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

  // 사이드바용 데이터 (로드된 것만 전달)
  const sidebarData = profile && badges && farm ? { profile, badges, farm } : null;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          {/* SidebarProfile - 스켈레톤 또는 실제 데이터 */}
          {sidebarData ? (
            <SidebarProfile
              username={username}
              publicData={sidebarData}
            />
          ) : (
            <SidebarSkeleton />
          )}
        </aside>
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            {/* 프로필 헤더 - 스켈레톤 또는 실제 데이터 */}
            {profile ? (
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
            ) : (
              <ProfileHeaderSkeleton />
            )}

            {/* 통계 카드 - 스켈레톤 또는 실제 데이터 */}
            {profile && badges ? (
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
            ) : (
              <StatCardsSkeleton />
            )}

            {/* 잔디 히트맵 - 스켈레톤 또는 실제 데이터 */}
            {activity ? (
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
            ) : (
              <GrassHeatmapSkeleton />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
