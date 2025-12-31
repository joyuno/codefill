/**
 * useToast - 토스트 알림 상태 관리 훅
 * 우하단에 스택 형태로 표시되는 알림 시스템
 */

import { useState, useCallback } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
}

interface UseToastReturn {
  toasts: Toast[];
  addToast: (message: string, type?: ToastType) => void;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

// 기본 지속 시간 (ms)
const DEFAULT_DURATION: Record<ToastType, number> = {
  success: 2000,
  error: 3000,
  info: 2500,
};

// 최대 동시 표시 개수
const MAX_TOASTS = 3;

export function useToast(): UseToastReturn {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((message: string, type: ToastType = 'success') => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const duration = DEFAULT_DURATION[type];

    const newToast: Toast = { id, message, type, duration };

    setToasts((prev) => {
      // 최대 개수 초과 시 가장 오래된 것 제거
      const updated = [...prev, newToast];
      if (updated.length > MAX_TOASTS) {
        return updated.slice(-MAX_TOASTS);
      }
      return updated;
    });

    // 자동 제거 타이머
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, [removeToast]);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return { toasts, addToast, removeToast, clearAll };
}
