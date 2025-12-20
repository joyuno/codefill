'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Code2, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('로그인 처리 중...');

  useEffect(() => {
    const handleCallback = async () => {
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const error = searchParams.get('error');
      const errorMessage = searchParams.get('message');

      if (error) {
        setStatus('error');
        setMessage(errorMessage || '로그인에 실패했습니다.');
        setTimeout(() => router.push('/login'), 2000);
        return;
      }

      if (accessToken && refreshToken) {
        try {
          // Store tokens
          apiClient.setTokens(accessToken, refreshToken);

          setStatus('success');
          setMessage('로그인 성공! 홈으로 이동합니다...');

          // Redirect to home
          setTimeout(() => {
            router.push('/');
            router.refresh();
          }, 1000);
        } catch (err) {
          setStatus('error');
          setMessage('토큰 저장 중 오류가 발생했습니다.');
          setTimeout(() => router.push('/login'), 2000);
        }
      } else {
        setStatus('error');
        setMessage('인증 정보가 없습니다.');
        setTimeout(() => router.push('/login'), 2000);
      }
    };

    handleCallback();
  }, [searchParams, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-sm space-y-6 text-center"
      >
        <div className="flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary">
            <Code2 className="h-6 w-6 text-primary-foreground" />
          </div>
        </div>

        <div className="space-y-4">
          {status === 'loading' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center gap-4"
            >
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-muted-foreground">{message}</p>
            </motion.div>
          )}

          {status === 'success' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <p className="font-medium text-green-600 dark:text-green-400">{message}</p>
            </motion.div>
          )}

          {status === 'error' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
                <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <p className="font-medium text-red-600 dark:text-red-400">{message}</p>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
