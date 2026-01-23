'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Image from 'next/image';
import { Loader2, Eye, EyeOff, MessageCircle, RefreshCcw, X, Ban, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { authApi, RecoveryRequiredResponse, BannedResponse } from '@/lib/api';
import { ga4Events } from '@/lib/analytics';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Validation schema
const loginSchema = z.object({
  email: z.string().email('올바른 이메일 주소를 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
});

type LoginFormData = z.infer<typeof loginSchema>;

// Wrapper component for Suspense boundary
export default function LoginPage() {
  return (
    <Suspense fallback={<LoginLoadingFallback />}>
      <LoginPageContent />
    </Suspense>
  );
}

function LoginLoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isRecovering, setIsRecovering] = useState(false);
  const [recoveryInfo, setRecoveryInfo] = useState<RecoveryRequiredResponse | null>(null);
  const [recoveryCredentials, setRecoveryCredentials] = useState<{ email: string; password: string } | null>(null);
  // 정지 사용자 상태
  const [bannedInfo, setBannedInfo] = useState<BannedResponse | null>(null);
  const [bannedCredentials, setBannedCredentials] = useState<{ email: string; password: string } | null>(null);
  const [showWithdrawConfirm, setShowWithdrawConfirm] = useState(false);
  const [withdrawConfirmText, setWithdrawConfirmText] = useState('');
  const [isWithdrawing, setIsWithdrawing] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Check for OAuth error from URL params (e.g., withdrawn user, banned user)
  useEffect(() => {
    const error = searchParams.get('error');
    const message = searchParams.get('message');
    const bannedUntil = searchParams.get('banned_until');
    const provider = searchParams.get('provider');
    const providerId = searchParams.get('provider_id');

    if (error) {
      const decodedMessage = message ? decodeURIComponent(message) : '';

      if (error === 'banned' && bannedUntil) {
        // Banned user trying to login via social - show banned modal
        const isPermanent = bannedUntil === 'permanent';
        setBannedInfo({
          banned: true,
          message: decodedMessage,
          email: '',  // OAuth users don't have email in URL
          banned_until: bannedUntil,
          is_permanent: isPermanent,
        });
        // Store OAuth credentials for potential withdrawal
        if (provider && providerId) {
          setBannedCredentials({
            email: `oauth:${provider}:${providerId}`,  // Special format for OAuth
            password: '',
          });
        }
      } else if (error === 'withdrawn') {
        // Withdrawn user trying to login via social
        toast({
          title: '재가입 제한',
          description: decodedMessage || '탈퇴한 계정입니다. 일정 기간 후 재가입이 가능합니다.',
          variant: 'destructive',
          duration: 5000,
        });
      } else {
        // Other OAuth errors
        toast({
          title: '로그인 실패',
          description: decodedMessage || '소셜 로그인 중 문제가 발생했습니다.',
          variant: 'destructive',
        });
      }

      // Clean up URL params (except for banned modal which needs to stay)
      if (error !== 'banned') {
        router.replace('/login');
      }
    }
  }, [searchParams, toast, router]);

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);

    try {
      const result = await authApi.login({
        email: data.email,
        password: data.password,
      });

      if (result.error) {
        toast({
          title: '로그인 실패',
          description: result.error.message,
          variant: 'destructive',
        });
        return;
      }

      // Check if user is banned
      if (result.data && 'banned' in result.data) {
        // Show banned user modal
        setBannedInfo(result.data as BannedResponse);
        setBannedCredentials({ email: data.email, password: data.password });
        return;
      }

      // Check if recovery is required
      if (result.data && 'recovery_required' in result.data) {
        // Show recovery confirmation modal
        setRecoveryInfo(result.data as RecoveryRequiredResponse);
        setRecoveryCredentials({ email: data.email, password: data.password });
        return;
      }

      toast({
        title: '로그인 성공',
        description: '환영합니다!',
      });

      // GA4 로그인 이벤트
      ga4Events.login('email');

      // Redirect to home page
      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '로그인 중 문제가 발생했습니다. 다시 시도해주세요.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecover = async () => {
    if (!recoveryCredentials) return;

    setIsRecovering(true);

    try {
      const result = await authApi.recover({
        email: recoveryCredentials.email,
        password: recoveryCredentials.password,
      });

      if (result.error) {
        toast({
          title: '복구 실패',
          description: result.error.message,
          variant: 'destructive',
        });
        return;
      }

      toast({
        title: '계정이 복구되었습니다',
        description: '다시 돌아오신 것을 환영합니다!',
      });

      setRecoveryInfo(null);
      setRecoveryCredentials(null);
      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '계정 복구 중 문제가 발생했습니다. 다시 시도해주세요.',
        variant: 'destructive',
      });
    } finally {
      setIsRecovering(false);
    }
  };

  const handleCancelRecovery = () => {
    setRecoveryInfo(null);
    setRecoveryCredentials(null);
  };

  const handleCancelBanned = () => {
    setBannedInfo(null);
    setBannedCredentials(null);
    setShowWithdrawConfirm(false);
    setWithdrawConfirmText('');
    router.replace('/login');
  };

  const handleWithdrawBanned = async () => {
    if (withdrawConfirmText !== '탈퇴합니다') {
      toast({
        title: '확인 문구 오류',
        description: "'탈퇴합니다'를 정확히 입력해주세요.",
        variant: 'destructive',
      });
      return;
    }

    if (!bannedCredentials) return;

    setIsWithdrawing(true);

    try {
      let result;

      // Check if OAuth user (special format: oauth:provider:providerId)
      if (bannedCredentials.email.startsWith('oauth:')) {
        const [, provider, providerId] = bannedCredentials.email.split(':');
        result = await authApi.withdrawBannedOAuth({
          provider,
          provider_id: providerId,
          confirmation: withdrawConfirmText,
        });
      } else {
        result = await authApi.withdrawBanned({
          email: bannedCredentials.email,
          password: bannedCredentials.password,
          confirmation: withdrawConfirmText,
        });
      }

      if (result.error) {
        toast({
          title: '탈퇴 실패',
          description: result.error.message,
          variant: 'destructive',
        });
        return;
      }

      toast({
        title: '탈퇴 완료',
        description: '계정과 모든 데이터가 즉시 삭제되었습니다.',
      });

      handleCancelBanned();
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '탈퇴 처리 중 문제가 발생했습니다.',
        variant: 'destructive',
      });
    } finally {
      setIsWithdrawing(false);
    }
  };

  // 정지 만료일 포맷팅
  const formatBannedUntil = (bannedUntil: string): string => {
    if (bannedUntil === 'permanent') {
      return '영구 정지';
    }
    try {
      const date = new Date(bannedUntil);
      return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
    } catch {
      return bannedUntil;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm space-y-6"
      >
        <div className="text-center">
          <Link href="/" className="inline-flex items-center justify-center">
            <Image
              src="/logo.png"
              alt="CodeFill"
              width={270}
              height={72}
              className="h-[72px] w-auto"
              priority
            />
          </Link>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-4 rounded-xl border border-border bg-card p-6"
        >
          <div className="space-y-2">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              className="bg-secondary"
              disabled={isLoading}
              {...register('email')}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">비밀번호</Label>
              <Link
                href="/forgot-password"
                className="text-xs text-muted-foreground hover:text-primary"
              >
                비밀번호를 잊으셨나요?
              </Link>
            </div>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="bg-secondary pr-10"
                disabled={isLoading}
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                로그인 중...
              </>
            ) : (
              '로그인'
            )}
          </Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">또는</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full bg-[#FEE500] text-[#000000] hover:bg-[#FDD835] border-[#FEE500] hover:border-[#FDD835]"
            disabled={isLoading}
            onClick={() => {
              window.location.href = `${API_BASE_URL}/auth/kakao/login`;
            }}
          >
            <MessageCircle className="mr-2 h-4 w-4" />
            카카오로 로그인
          </Button>

          <Button
            type="button"
            variant="outline"
            className="w-full bg-white text-gray-700 hover:bg-gray-100 hover:text-gray-900 border-gray-300"
            disabled={isLoading}
            onClick={() => {
              window.location.href = `${API_BASE_URL}/auth/google/login`;
            }}
          >
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            구글로 로그인
          </Button>

          <Button
            type="button"
            variant="outline"
            className="w-full bg-[#24292f] text-white hover:bg-[#1b1f23] border-[#24292f] hover:border-[#1b1f23]"
            disabled={isLoading}
            onClick={() => {
              window.location.href = `${API_BASE_URL}/auth/github/login`;
            }}
          >
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub로 로그인
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          계정이 없으신가요?{' '}
          <Link href="/onboarding" className="text-primary hover:underline">
            회원가입
          </Link>
        </p>
      </motion.div>

      {/* Recovery Confirmation Modal */}
      <AnimatePresence>
        {recoveryInfo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={handleCancelRecovery}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="w-full max-w-sm rounded-xl border border-border bg-card p-6 space-y-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                  <RefreshCcw className="h-8 w-8 text-primary" />
                </div>
              </div>

              <h2 className="text-xl font-semibold text-center">계정 복구</h2>

              <div className="text-center text-muted-foreground text-sm space-y-2">
                <p>탈퇴한 계정이 발견되었습니다.</p>
                {recoveryInfo.email && (
                  <p className="font-medium text-foreground">
                    {recoveryInfo.email}
                  </p>
                )}
                <p>이 계정을 복구하시겠습니까?</p>
              </div>

              <div className="rounded-lg bg-muted/50 p-3 text-sm text-muted-foreground">
                <p>
                  복구 가능 기간: <span className="font-semibold text-primary">{recoveryInfo.days_remaining}일</span> 남음
                </p>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handleCancelRecovery}
                  disabled={isRecovering}
                >
                  <X className="mr-2 h-4 w-4" />
                  취소
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleRecover}
                  disabled={isRecovering}
                >
                  {isRecovering ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      복구 중...
                    </>
                  ) : (
                    <>
                      <RefreshCcw className="mr-2 h-4 w-4" />
                      복구하기
                    </>
                  )}
                </Button>
              </div>

              <p className="text-xs text-center text-muted-foreground">
                취소하면 로그인이 취소됩니다.
                <br />
                30일이 지나면 계정이 영구 삭제됩니다.
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Banned User Modal */}
      <AnimatePresence>
        {bannedInfo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={handleCancelBanned}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="w-full max-w-sm rounded-xl border border-border bg-card p-6 space-y-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
                  <Ban className="h-8 w-8 text-destructive" />
                </div>
              </div>

              <h2 className="text-xl font-semibold text-center text-destructive">계정 정지</h2>

              <div className="text-center text-muted-foreground text-sm space-y-2">
                <p>{bannedInfo.message || '계정이 정지되었습니다.'}</p>
                {bannedInfo.email && (
                  <p className="font-medium text-foreground">
                    {bannedInfo.email}
                  </p>
                )}
              </div>

              <div className="rounded-lg bg-destructive/5 border border-destructive/20 p-3 text-sm">
                <p className="text-center">
                  {bannedInfo.is_permanent ? (
                    <span className="font-semibold text-destructive">영구 정지</span>
                  ) : (
                    <>
                      <span className="font-semibold text-destructive">
                        {formatBannedUntil(bannedInfo.banned_until)}
                      </span>
                      <span className="text-muted-foreground"> 까지 정지</span>
                    </>
                  )}
                </p>
              </div>

              {!showWithdrawConfirm ? (
                <div className="flex flex-col gap-3 pt-2">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={handleCancelBanned}
                  >
                    <X className="mr-2 h-4 w-4" />
                    닫기
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full text-muted-foreground hover:text-destructive"
                    onClick={() => setShowWithdrawConfirm(true)}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    계정 탈퇴하기
                  </Button>
                </div>
              ) : (
                <div className="space-y-3 pt-2">
                  <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm">
                    <p className="font-medium text-destructive mb-1">즉시 삭제 안내</p>
                    <p className="text-muted-foreground">
                      정지된 계정은 <span className="text-destructive font-medium">복구 기간 없이 즉시 삭제</span>됩니다.
                      <br />
                      모든 데이터가 영구적으로 삭제되며 복구할 수 없습니다.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="withdraw-confirm" className="text-sm">
                      확인을 위해 &apos;탈퇴합니다&apos;를 입력해주세요
                    </Label>
                    <Input
                      id="withdraw-confirm"
                      placeholder="탈퇴합니다"
                      value={withdrawConfirmText}
                      onChange={(e) => setWithdrawConfirmText(e.target.value)}
                      className="bg-secondary"
                      disabled={isWithdrawing}
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => {
                        setShowWithdrawConfirm(false);
                        setWithdrawConfirmText('');
                      }}
                      disabled={isWithdrawing}
                    >
                      취소
                    </Button>
                    <Button
                      variant="destructive"
                      className="flex-1"
                      onClick={handleWithdrawBanned}
                      disabled={isWithdrawing || withdrawConfirmText !== '탈퇴합니다'}
                    >
                      {isWithdrawing ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          처리 중...
                        </>
                      ) : (
                        '탈퇴하기'
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
