'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, LogIn, RefreshCw, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';

// JWT 토큰에서 만료 시간 추출
function getTokenExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    return decoded.exp ? decoded.exp * 1000 : null;
  } catch {
    return null;
  }
}

// 만료 N분 전에 경고 (5분)
const WARNING_BEFORE_EXPIRY = 5 * 60 * 1000;
// 체크 간격 (30초)
const CHECK_INTERVAL = 30 * 1000;

export function SessionExpiredModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isExpired, setIsExpired] = useState(false); // 이미 만료됨
  const [remainingTime, setRemainingTime] = useState<number>(0);
  const router = useRouter();
  const checkIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 토큰 만료 시간 체크
  useEffect(() => {
    const checkTokenExpiry = () => {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const expiry = getTokenExpiry(token);
      if (!expiry) return;

      const now = Date.now();
      const timeUntilExpiry = expiry - now;

      // 이미 만료됨
      if (timeUntilExpiry <= 0) {
        setIsExpired(true);
        setIsOpen(true);
        return;
      }

      // 만료 임박 (5분 이내)
      if (timeUntilExpiry <= WARNING_BEFORE_EXPIRY) {
        setIsExpired(false);
        setRemainingTime(Math.floor(timeUntilExpiry / 1000));
        setIsOpen(true);
      }
    };

    // 초기 체크
    checkTokenExpiry();

    // 주기적 체크
    checkIntervalRef.current = setInterval(checkTokenExpiry, CHECK_INTERVAL);

    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current);
      }
    };
  }, []);

  // 남은 시간 카운트다운
  useEffect(() => {
    if (!isOpen || isExpired || remainingTime <= 0) return;

    const countdown = setInterval(() => {
      setRemainingTime(prev => {
        if (prev <= 1) {
          setIsExpired(true);
          clearInterval(countdown);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdown);
  }, [isOpen, isExpired, remainingTime]);

  // 세션 만료 이벤트 리스닝 (API 401 응답 시)
  useEffect(() => {
    const handleSessionExpired = () => {
      setIsExpired(true);
      setIsOpen(true);
    };

    window.addEventListener('session-expired', handleSessionExpired);
    return () => {
      window.removeEventListener('session-expired', handleSessionExpired);
    };
  }, []);

  // 로그인 유지하기 (토큰 갱신 시도)
  const handleRefreshSession = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const success = await apiClient.refreshAccessToken();
      if (success) {
        setIsOpen(false);
        setIsExpired(false);
        setRemainingTime(0);
        // 체크 인터벌 재시작
        if (checkIntervalRef.current) {
          clearInterval(checkIntervalRef.current);
        }
      } else {
        // 갱신 실패 시 로그인 페이지로
        handleGoToLogin();
      }
    } catch {
      handleGoToLogin();
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  // 다시 로그인하기
  const handleGoToLogin = useCallback(() => {
    // 토큰 및 캐시 정리
    apiClient.clearTokens();
    localStorage.removeItem('codefill_farm_cache');
    sessionStorage.removeItem('codefill_profile_cache');
    sessionStorage.removeItem('codefill_badge_count');
    sessionStorage.removeItem('codefill_badges_cache');
    sessionStorage.removeItem('codefill_farm_visited');

    setIsOpen(false);
    router.push('/login');
  }, [router]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 z-[9999]"
            onClick={() => {}} // 배경 클릭으로 닫기 방지
          />

          {/* Modal Container - flex로 안정적 센터링 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className="fixed inset-0 z-[10000] flex items-center justify-center p-4"
          >
            <div className="bg-card border border-border rounded-xl shadow-2xl overflow-hidden w-full max-w-md">
              {/* Header */}
              <div className={`flex items-center gap-3 px-6 py-4 border-b border-border ${isExpired ? 'bg-red-500/10' : 'bg-yellow-500/10'}`}>
                <div className={`p-2 rounded-full ${isExpired ? 'bg-red-500/20' : 'bg-yellow-500/20'}`}>
                  {isExpired ? (
                    <AlertTriangle className="h-6 w-6 text-red-500" />
                  ) : (
                    <Clock className="h-6 w-6 text-yellow-500" />
                  )}
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-foreground">
                    {isExpired ? '세션 만료' : '세션 만료 임박'}
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    {isExpired
                      ? '로그인 세션이 만료되었습니다'
                      : `${Math.floor(remainingTime / 60)}분 ${remainingTime % 60}초 후 자동 로그아웃됩니다`
                    }
                  </p>
                </div>
              </div>

              {/* Content */}
              <div className="px-6 py-5">
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {isExpired
                    ? '보안을 위해 세션이 만료되었습니다. 다시 로그인하거나 로그인 유지를 시도해 주세요.'
                    : '보안을 위해 일정 시간이 지나면 자동으로 로그아웃됩니다. 계속 사용하시려면 로그인을 유지해 주세요.'
                  }
                </p>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 px-6 py-4 bg-muted/30 border-t border-border">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handleGoToLogin}
                  disabled={isRefreshing}
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  다시 로그인하기
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleRefreshSession}
                  disabled={isRefreshing}
                >
                  {isRefreshing ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  {isRefreshing ? '갱신 중...' : '로그인 유지하기'}
                </Button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
