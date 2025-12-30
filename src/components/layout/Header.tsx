'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { CreditCard, LogOut, User, Settings, Crown, Users } from 'lucide-react';
import { friendsApi } from '@/lib/api';
import { FriendModal } from '@/components/friends';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useAuth, SUBSCRIPTION_FEATURES } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, profile, isLoading, isAuthenticated, signOut } = useAuth();

  // 친구 모달 상태
  const [friendModalOpen, setFriendModalOpen] = useState(false);
  const [apiUnreadCount, setApiUnreadCount] = useState(0);

  // WebSocket 컨텍스트에서 실시간 읽지 않은 메시지 수
  const { totalUnreadCount: wsUnreadCount } = useWebSocketContext();

  // 인증 페이지에서는 다른 헤더 표시
  const isAuthPage = pathname === '/login' || pathname === '/signup' || pathname === '/onboarding';

  // 미확인 알림 수 조회 (API)
  useEffect(() => {
    if (isAuthenticated && user) {
      friendsApi.getUnreadCounts()
        .then((res) => setApiUnreadCount(res.total))
        .catch(() => setApiUnreadCount(0));
    }
  }, [isAuthenticated, user, friendModalOpen]);

  // 총 읽지 않은 메시지 수 (API + WebSocket 실시간)
  const unreadCount = apiUnreadCount + wsUnreadCount;

  // 로그아웃 처리
  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
    router.refresh();
  };

  // 구독 티어 배지 색상
  const getTierBadgeColor = (tier: string) => {
    switch (tier) {
      case 'pro':
        return 'bg-gradient-to-r from-yellow-400 to-amber-500 text-amber-900';
      case 'basic':
        return 'bg-gradient-to-r from-blue-400 to-blue-500 text-white';
      default:
        return 'bg-secondary text-secondary-foreground';
    }
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div className="flex h-16 items-center justify-between px-6">
        {/* 로고 이미지 */}
        <Link href="/" className="flex items-center">
          <Image
            src="/logo.png"
            alt="CodeFill"
            width={270}
            height={72}
            className="h-[72px] w-auto"
            priority
          />
        </Link>

        <div className="flex items-center gap-3">
          {isLoading ? (
            // 로딩 중
            <div className="h-8 w-24 animate-pulse rounded-lg bg-secondary" />
          ) : isAuthenticated && user ? (
            // 로그인 상태
            <>
              {/* 결제 버튼 */}
              <Link href="/pricing">
                <Button
                  variant="outline"
                  size="sm"
                  className={cn(
                    'gap-2 font-medium',
                    profile?.subscription_tier === 'pro' && 'border-amber-400 text-amber-600 hover:bg-amber-50'
                  )}
                >
                  {profile?.subscription_tier === 'pro' ? (
                    <>
                      <Crown className="h-4 w-4" />
                      <span className="hidden sm:inline">Pro 멤버</span>
                    </>
                  ) : profile?.subscription_tier === 'basic' ? (
                    <>
                      <CreditCard className="h-4 w-4" />
                      <span className="hidden sm:inline">베이직</span>
                    </>
                  ) : (
                    <>
                      <CreditCard className="h-4 w-4" />
                      <span className="hidden sm:inline">업그레이드</span>
                    </>
                  )}
                </Button>
              </Link>

              {/* 사용자 드롭다운 메뉴 */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                      {profile?.username?.slice(0, 2).toUpperCase() || 'U'}
                    </div>
                    <span className="hidden sm:inline max-w-[100px] truncate">
                      {profile?.username || user.email?.split('@')[0]}
                    </span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  {/* 사용자 정보 */}
                  <div className="px-2 py-2">
                    <p className="font-medium">{profile?.username}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                    <div className="mt-2 flex items-center gap-2">
                      <Badge className={getTierBadgeColor(profile?.subscription_tier || 'free')}>
                        {SUBSCRIPTION_FEATURES[profile?.subscription_tier || 'free'].name}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        Lv.{profile?.level || 1}
                      </span>
                    </div>
                  </div>

                  <DropdownMenuSeparator />

                  <DropdownMenuItem asChild>
                    <Link href="/mypage" className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      마이페이지
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem
                    onSelect={() => setFriendModalOpen(true)}
                    className="cursor-pointer"
                  >
                    <Users className="mr-2 h-4 w-4" />
                    친구
                    {unreadCount > 0 && (
                      <Badge
                        variant="destructive"
                        className="ml-auto h-5 px-1.5 text-xs"
                      >
                        {unreadCount}
                      </Badge>
                    )}
                  </DropdownMenuItem>

                  <DropdownMenuItem asChild>
                    <Link href="/pricing" className="cursor-pointer">
                      <CreditCard className="mr-2 h-4 w-4" />
                      구독 관리
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem asChild>
                    <Link href="/settings" className="cursor-pointer">
                      <Settings className="mr-2 h-4 w-4" />
                      설정
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuSeparator />

                  <DropdownMenuItem
                    onClick={handleSignOut}
                    className="cursor-pointer text-destructive focus:text-destructive"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    로그아웃
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            // 비로그인 상태
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  로그인
                </Button>
              </Link>
              <Link href="/onboarding">
                <Button size="sm">
                  시작하기
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {/* 친구 모달 */}
      <FriendModal open={friendModalOpen} onOpenChange={setFriendModalOpen} />
    </motion.header>
  );
}
