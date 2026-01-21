'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { AnalyticsProvider } from '@/components/AnalyticsProvider';
import { WebSocketProvider } from '@/contexts/WebSocketContext';

// WebSocket을 비활성화할 경로 (문제 풀이 집중 모드)
const WEBSOCKET_DISABLED_PATHS = ['/chat'];

export function Providers({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // /chat 페이지에서는 WebSocket 비활성화 (문제 풀이 집중)
  const isWebSocketDisabled = WEBSOCKET_DISABLED_PATHS.some(
    path => pathname?.startsWith(path)
  );

  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000,      // 5분간 fresh
            gcTime: 30 * 60 * 1000,        // 30분간 캐시 유지
            refetchOnWindowFocus: false,
            refetchOnReconnect: false,
            retry: 1,                       // 재시도 1회로 제한
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WebSocketProvider disabled={isWebSocketDisabled}>
          <AnalyticsProvider>
            {children}
          </AnalyticsProvider>
        </WebSocketProvider>
        <Toaster />
        <Sonner />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
