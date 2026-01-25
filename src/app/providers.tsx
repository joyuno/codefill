'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { AnalyticsProvider } from '@/components/AnalyticsProvider';
import { WebSocketProvider } from '@/contexts/WebSocketContext';

// WebSocket을 활성화할 경로 (친구/DM 기능이 필요한 곳만)
const WEBSOCKET_ENABLED_PATHS = ['/friends'];

export function Providers({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // /friends 페이지에서만 WebSocket 활성화
  const isWebSocketEnabled = WEBSOCKET_ENABLED_PATHS.some(
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
        <WebSocketProvider disabled={!isWebSocketEnabled}>
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
