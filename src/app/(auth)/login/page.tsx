'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Code2, Loader2, Eye, EyeOff, MessageCircle, RefreshCcw, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { authApi, RecoveryRequiredResponse } from '@/lib/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Validation schema
const loginSchema = z.object({
  email: z.string().email('올바른 이메일 주소를 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isRecovering, setIsRecovering] = useState(false);
  const [recoveryInfo, setRecoveryInfo] = useState<RecoveryRequiredResponse | null>(null);
  const [recoveryCredentials, setRecoveryCredentials] = useState<{ email: string; password: string } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Check for OAuth error from URL params (e.g., withdrawn user)
  useEffect(() => {
    const error = searchParams.get('error');
    const message = searchParams.get('message');

    if (error) {
      const decodedMessage = message ? decodeURIComponent(message) : '';

      if (error === 'withdrawn') {
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

      // Clean up URL params
      router.replace('/login');
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

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm space-y-6"
      >
        <div className="text-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Code2 className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold">
              Code<span className="text-primary">Fill</span>
            </span>
          </Link>
          <p className="mt-2 text-muted-foreground">다시 만나서 반가워요!</p>
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
            className="w-full bg-white text-gray-700 hover:bg-gray-50 border-gray-300"
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
    </div>
  );
}
