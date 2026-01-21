'use client';

import React, { createContext, useContext, useCallback, useState, useEffect, useRef } from 'react';
import { useWebSocket, WSIncomingMessage, WSNewMessage, WSMessagesRead } from '@/hooks/useWebSocket';

/**
 * WebSocket 컨텍스트에서 제공하는 값
 */
interface WebSocketContextValue {
  // 연결 상태
  isConnected: boolean;
  isConnecting: boolean;

  // 메시지 전송
  sendMessage: (receiverId: string, content: string) => void;
  markAsRead: (senderId: string) => void;

  // 읽지 않은 메시지 수
  unreadCounts: Record<string, number>;
  totalUnreadCount: number;

  // 새 메시지 리스너 등록/해제
  addMessageListener: (callback: MessageListener) => void;
  removeMessageListener: (callback: MessageListener) => void;

  // 읽음 처리 리스너 등록/해제
  addReadListener: (callback: ReadListener) => void;
  removeReadListener: (callback: ReadListener) => void;

  // 수동 연결/해제
  connect: () => void;
  disconnect: () => void;
}

type MessageListener = (message: WSNewMessage['message']) => void;
type ReadListener = (readerId: string) => void;

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: React.ReactNode;
  disabled?: boolean;  // /chat 등 특정 페이지에서 WebSocket 비활성화
}

/**
 * WebSocket Provider
 * 앱 전체에서 WebSocket 연결을 공유하고 메시지를 관리
 *
 * @param disabled - true인 경우 WebSocket 연결을 시도하지 않음 (문제 풀이 집중 모드)
 */
export function WebSocketProvider({ children, disabled = false }: WebSocketProviderProps) {
  // 읽지 않은 메시지 수 (sender_id별)
  const [unreadCounts, setUnreadCounts] = useState<Record<string, number>>({});

  // 메시지 리스너들
  const messageListenersRef = useRef<Set<MessageListener>>(new Set());
  const readListenersRef = useRef<Set<ReadListener>>(new Set());

  // 메시지 수신 핸들러
  const handleMessage = useCallback((data: WSIncomingMessage) => {
    if (data.type === 'new_message') {
      const newMessage = data as WSNewMessage;
      const message = newMessage.message;

      // 내가 보낸 메시지가 아닌 경우에만 읽지 않은 메시지 카운트 증가
      if (!message.is_mine && !message.is_read) {
        setUnreadCounts(prev => ({
          ...prev,
          [message.sender_id]: (prev[message.sender_id] || 0) + 1,
        }));
      }

      // 등록된 리스너들에게 알림
      messageListenersRef.current.forEach(listener => {
        listener(message);
      });
    } else if (data.type === 'messages_read') {
      const readData = data as WSMessagesRead;

      // 등록된 리스너들에게 알림
      readListenersRef.current.forEach(listener => {
        listener(readData.reader_id);
      });
    }
  }, []);

  // WebSocket 훅 사용 (disabled=true면 자동 연결 안 함)
  const {
    isConnected,
    isConnecting,
    sendMessage: wsSendMessage,
    connect,
    disconnect,
  } = useWebSocket({
    onMessage: handleMessage,
    onConnect: () => {
      if (!disabled) {
        console.log('WebSocket Provider: Connected');
      }
    },
    onDisconnect: () => {
      if (!disabled) {
        console.log('WebSocket Provider: Disconnected');
      }
    },
    autoConnect: !disabled,  // /chat 페이지 등에서는 WebSocket 비활성화
  });

  // 채팅 메시지 전송
  const sendMessage = useCallback((receiverId: string, content: string) => {
    wsSendMessage({
      type: 'message',
      receiver_id: receiverId,
      content,
    });
  }, [wsSendMessage]);

  // 메시지 읽음 처리
  const markAsRead = useCallback((senderId: string) => {
    wsSendMessage({
      type: 'read',
      sender_id: senderId,
    });

    // 로컬 읽지 않은 메시지 카운트 초기화
    setUnreadCounts(prev => {
      const newCounts = { ...prev };
      delete newCounts[senderId];
      return newCounts;
    });
  }, [wsSendMessage]);

  // 메시지 리스너 등록
  const addMessageListener = useCallback((callback: MessageListener) => {
    messageListenersRef.current.add(callback);
  }, []);

  // 메시지 리스너 해제
  const removeMessageListener = useCallback((callback: MessageListener) => {
    messageListenersRef.current.delete(callback);
  }, []);

  // 읽음 리스너 등록
  const addReadListener = useCallback((callback: ReadListener) => {
    readListenersRef.current.add(callback);
  }, []);

  // 읽음 리스너 해제
  const removeReadListener = useCallback((callback: ReadListener) => {
    readListenersRef.current.delete(callback);
  }, []);

  // 총 읽지 않은 메시지 수 계산
  const totalUnreadCount = Object.values(unreadCounts).reduce((sum, count) => sum + count, 0);

  const value: WebSocketContextValue = {
    isConnected,
    isConnecting,
    sendMessage,
    markAsRead,
    unreadCounts,
    totalUnreadCount,
    addMessageListener,
    removeMessageListener,
    addReadListener,
    removeReadListener,
    connect,
    disconnect,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * WebSocket 컨텍스트 사용 훅
 */
export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
}

/**
 * WebSocket 컨텍스트 사용 훅 (선택적)
 * Provider 외부에서도 사용 가능 (null 반환)
 */
export function useWebSocketContextOptional(): WebSocketContextValue | null {
  return useContext(WebSocketContext);
}
