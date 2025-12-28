'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Code2, Loader2, RefreshCcw, X, MessageCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { authApi } from '@/lib/api';

// Wrapper component for Suspense boundary
export default function RecoverAccountPage() {
  return (
    <Suspense fallback={<RecoverLoadingFallback />}>
      <RecoverAccountPageContent />
    </Suspense>
  );
}

function RecoverLoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

function RecoverAccountPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  // Get query params
  const provider = searchParams.get('provider');
  const providerId = searchParams.get('provider_id');
  const email = searchParams.get('email');
  const daysRemaining = searchParams.get('days');

  // Validate required params
  const isValid = provider && providerId;

  useEffect(() => {
    if (!isValid) {
      toast({
        title: '잘못된 접근',
        description: '유효하지 않은 복구 요청입니다.',
        variant: 'destructive',
      });
      router.push('/login');
    }
  }, [isValid, toast, router]);

  const handleRecover = async () => {
    if (!provider || !providerId) return;

    setIsLoading(true);

    try {
      const result = await authApi.recoverOAuth({
        provider,
        provider_id: providerId,
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

      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '계정 복구 중 문제가 발생했습니다. 다시 시도해주세요.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/login');
  };

  const getProviderName = (provider: string | null) => {
    switch (provider) {
      case 'kakao':
        return '카카오';
      case 'google':
        return '구글';
      default:
        return '소셜';
    }
  };

  const getProviderIcon = (provider: string | null) => {
    switch (provider) {
      case 'kakao':
        return <MessageCircle className="h-5 w-5" />;
      case 'google':
        return (
          <svg className="h-5 w-5" viewBox="0 0 24 24">
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
        );
      default:
        return <RefreshCcw className="h-5 w-5" />;
    }
  };

  if (!isValid) {
    return null; // Will redirect in useEffect
  }

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
        </div>

        <div className="rounded-xl border border-border bg-card p-6 space-y-4">
          <div className="flex justify-center mb-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
              <RefreshCcw className="h-8 w-8 text-primary" />
            </div>
          </div>

          <h2 className="text-xl font-semibold text-center">계정 복구</h2>

          <div className="text-center text-muted-foreground text-sm space-y-2">
            <p>
              탈퇴한 계정이 발견되었습니다.
            </p>
            {email && (
              <p className="font-medium text-foreground">
                {email}
              </p>
            )}
            <p>
              이 계정을 복구하시겠습니까?
            </p>
          </div>

          <div className="rounded-lg bg-muted/50 p-3 text-sm text-muted-foreground">
            <p className="flex items-center gap-2">
              {getProviderIcon(provider)}
              <span>
                {getProviderName(provider)} 계정으로 가입됨
              </span>
            </p>
            {daysRemaining && (
              <p className="mt-2 text-xs">
                복구 가능 기간: <span className="font-semibold text-primary">{daysRemaining}일</span> 남음
              </p>
            )}
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={handleCancel}
              disabled={isLoading}
            >
              <X className="mr-2 h-4 w-4" />
              취소
            </Button>
            <Button
              className="flex-1"
              onClick={handleRecover}
              disabled={isLoading}
            >
              {isLoading ? (
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
            취소하면 로그인 페이지로 돌아갑니다.
            <br />
            30일이 지나면 계정이 영구 삭제됩니다.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
