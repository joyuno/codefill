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
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isDisconnectingRef = useRef(false);

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

  // 연결
  const connect = useCallback(() => {
    // 이미 연결 중이거나 연결됨
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    // 의도적 연결 해제 중이면 무시
    if (isDisconnectingRef.current) {
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

        // Ping 간격 설정 (30초마다)
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
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

        // 재연결 시도 (비정상 종료 시, 의도적 해제가 아닌 경우)
        if (!isDisconnectingRef.current && event.code !== 1000 && event.code !== 4001) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1;
            console.log(`Reconnecting... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
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
  }, [getWebSocketUrl, reconnectInterval, maxReconnectAttempts]);

  // 이미 연결 시도했는지 추적
  const hasConnectedRef = useRef(false);

  // 연결 해제
  const disconnect = useCallback(() => {
    isDisconnectingRef.current = true;
    hasConnectedRef.current = false; // 재연결 가능하도록 리셋

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
    reconnectAttemptsRef.current = maxReconnectAttempts; // 재연결 방지
  }, [maxReconnectAttempts]);

  // 메시지 전송
  const sendMessage = useCallback((message: WSMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // 자동 연결 (마운트 시 1회만)
  useEffect(() => {
    if (autoConnect && !hasConnectedRef.current) {
      const token = localStorage.getItem('access_token');
      if (token) {
        hasConnectedRef.current = true;
        isDisconnectingRef.current = false;
        connect();
      }
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // 토큰 변경 감지 (로그인/로그아웃)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        if (e.newValue) {
          // 토큰 추가됨 → 연결
          isDisconnectingRef.current = false;
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

  return {
    isConnected,
    isConnecting,
    sendMessage,
    connect,
    disconnect,
  };
}
