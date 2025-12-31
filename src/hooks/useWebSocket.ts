'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * WebSocket 메시지 타입
 */
export interface WSMessage {
  type: string;
  [key: string]: unknown;
}

export interface WSNewMessage {
  type: 'new_message';
  message: {
    id: string;
    sender_id: string;
    sender_name: string | null;
    sender_avatar: string | null;
    receiver_id: string;
    content: string;
    is_read: boolean;
    is_mine: boolean;
    created_at: string;
  };
}

export interface WSMessagesRead {
  type: 'messages_read';
  reader_id: string;
}

export type WSIncomingMessage = WSNewMessage | WSMessagesRead | { type: 'connected' | 'pong' | 'error'; [key: string]: unknown };

interface UseWebSocketOptions {
  onMessage?: (message: WSIncomingMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  sendMessage: (message: WSMessage) => void;
  connect: () => void;
  disconnect: () => void;
}

// Ping 간격 (15초 - 브라우저 쓰로틀링 대응)
const PING_INTERVAL = 15000;

/**
 * WebSocket 연결 관리 훅
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isUnmountingRef = useRef(false);

  // 콜백들을 ref로 저장하여 의존성 문제 해결
  const onMessageRef = useRef(onMessage);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onErrorRef = useRef(onError);

  // 콜백 refs 업데이트
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    onConnectRef.current = onConnect;
  }, [onConnect]);

  useEffect(() => {
    onDisconnectRef.current = onDisconnect;
  }, [onDisconnect]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  // WebSocket URL 생성
  const getWebSocketUrl = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wsUrl = apiUrl.replace(/^http/, 'ws');
    return `${wsUrl}/ws?token=${token}`;
  }, []);

  // Ping 전송
  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'ping' }));
    }
  }, []);

  // 연결
  const connect = useCallback(() => {
    // 언마운트 중이면 무시
    if (isUnmountingRef.current) {
      return;
    }

    // 이미 연결 중이거나 연결됨
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const url = getWebSocketUrl();
    if (!url) {
      return;
    }

    setIsConnecting(true);

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0;
        onConnectRef.current?.();

        // Ping 간격 설정 (15초마다)
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(sendPing, PING_INTERVAL);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WSIncomingMessage;
          onMessageRef.current?.(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        wsRef.current = null;
        onDisconnectRef.current?.();

        // Ping 인터벌 정리
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // 재연결 시도 (비정상 종료 시, 언마운트가 아닌 경우)
        if (!isUnmountingRef.current && event.code !== 1000 && event.code !== 4001) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1;
            const delay = Math.min(reconnectInterval * reconnectAttemptsRef.current, 30000);
            console.log(`Reconnecting in ${delay}ms... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, delay);
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnecting(false);
        onErrorRef.current?.(error);
      };

      wsRef.current = ws;
    } catch (e) {
      console.error('Failed to create WebSocket:', e);
      setIsConnecting(false);
    }
  }, [getWebSocketUrl, reconnectInterval, maxReconnectAttempts, sendPing]);

  // 연결 해제 (수동 호출용)
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  // 메시지 전송
  const sendMessage = useCallback((message: WSMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // 자동 연결 (마운트 시)
  useEffect(() => {
    isUnmountingRef.current = false;

    if (autoConnect) {
      const token = localStorage.getItem('access_token');
      if (token) {
        connect();
      }
    }

    return () => {
      // 언마운트 시 정리
      isUnmountingRef.current = true;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }

      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmount');
        wsRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 빈 의존성 - 마운트/언마운트 시에만 실행

  // 토큰 변경 감지 (로그인/로그아웃)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        if (e.newValue) {
          // 토큰 추가됨 → 연결
          reconnectAttemptsRef.current = 0;
          connect();
        } else {
          // 토큰 제거됨 → 연결 해제
          disconnect();
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [connect, disconnect]);

  // 탭 활성화 시 연결 상태 확인 및 재연결
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // 탭이 다시 활성화됨
        const token = localStorage.getItem('access_token');
        if (token && wsRef.current?.readyState !== WebSocket.OPEN) {
          console.log('Tab visible, reconnecting WebSocket...');
          reconnectAttemptsRef.current = 0;
          connect();
        } else if (token && wsRef.current?.readyState === WebSocket.OPEN) {
          // 연결되어 있으면 즉시 ping 전송하여 연결 확인
          sendPing();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [connect, sendPing]);

  return {
    isConnected,
    isConnecting,
    sendMessage,
    connect,
    disconnect,
  };
}
