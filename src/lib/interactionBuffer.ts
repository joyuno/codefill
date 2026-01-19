/**
 * Interaction Buffer
 *
 * 프론트엔드에서 사용자 상호작용을 로컬에 버퍼링했다가
 * 일정 개수 또는 시간 간격으로 서버에 배치 전송
 *
 * 장점:
 * - 서버 부하 감소 (개별 요청 대신 배치 전송)
 * - 오프라인 지원 (로컬 스토리지에 저장)
 * - 네트워크 효율 향상
 *
 * 사용 예시:
 * ```typescript
 * import { interactionBuffer } from '@/lib/interactionBuffer';
 *
 * // 클릭 이벤트 기록
 * interactionBuffer.log('click', { button: 'submit', page: 'practice' });
 *
 * // 문제 선택 기록
 * interactionBuffer.log('problem_select', { problemId: '123', topic: 'dp' });
 *
 * // 페이지 이탈 시 강제 전송
 * window.addEventListener('beforeunload', () => {
 *   interactionBuffer.flush();
 * });
 * ```
 */

interface Interaction {
  type: string;
  data: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

interface BufferConfig {
  /** 자동 전송 트리거 개수 (기본: 10) */
  maxSize: number;
  /** 자동 전송 간격 ms (기본: 30000 = 30초) */
  flushInterval: number;
  /** 로컬 스토리지 키 */
  storageKey: string;
  /** API 엔드포인트 */
  apiEndpoint: string;
}

const DEFAULT_CONFIG: BufferConfig = {
  maxSize: 10,
  flushInterval: 30000,
  storageKey: 'codefill_interaction_buffer',
  apiEndpoint: '/api/users/interactions/batch',
};

class InteractionBuffer {
  private buffer: Interaction[] = [];
  private config: BufferConfig;
  private flushTimer: ReturnType<typeof setInterval> | null = null;
  private isFlushing = false;
  private sessionId: string | null = null;

  constructor(config: Partial<BufferConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.restoreFromStorage();
    this.startAutoFlush();
    this.setupUnloadHandler();
  }

  /**
   * 세션 ID 설정 (채팅 세션 등)
   */
  setSessionId(sessionId: string | null): void {
    this.sessionId = sessionId;
  }

  /**
   * 상호작용 기록
   */
  log(
    type: string,
    data: Record<string, unknown> = {},
    metadata?: Record<string, unknown>
  ): void {
    const interaction: Interaction = {
      type,
      data,
      metadata,
      timestamp: new Date().toISOString(),
    };

    this.buffer.push(interaction);
    this.saveToStorage();

    // 버퍼 크기 초과 시 자동 전송
    if (this.buffer.length >= this.config.maxSize) {
      this.flush();
    }
  }

  /**
   * 편의 메서드들
   */
  logClick(element: string, data?: Record<string, unknown>): void {
    this.log('click', { element, ...data });
  }

  logView(page: string, data?: Record<string, unknown>): void {
    this.log('view', { page, ...data });
  }

  logSelect(itemType: string, itemId: string, data?: Record<string, unknown>): void {
    this.log('select', { itemType, itemId, ...data });
  }

  logAction(action: string, data?: Record<string, unknown>): void {
    this.log('action', { action, ...data });
  }

  /**
   * 버퍼 내용을 서버로 전송
   */
  async flush(): Promise<boolean> {
    if (this.isFlushing || this.buffer.length === 0) {
      return true;
    }

    this.isFlushing = true;
    const toSend = [...this.buffer];
    this.buffer = [];
    this.saveToStorage();

    try {
      const response = await fetch(this.config.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          interactions: toSend,
          session_id: this.sessionId,
        }),
      });

      if (!response.ok) {
        // 전송 실패 시 버퍼에 복원
        this.buffer = [...toSend, ...this.buffer];
        this.saveToStorage();
        console.warn('[InteractionBuffer] Flush failed, restored to buffer');
        return false;
      }

      const result = await response.json();
      console.debug(`[InteractionBuffer] Flushed ${result.logged_count} interactions`);
      return true;
    } catch (error) {
      // 네트워크 오류 시 버퍼에 복원
      this.buffer = [...toSend, ...this.buffer];
      this.saveToStorage();
      console.warn('[InteractionBuffer] Flush error, restored to buffer:', error);
      return false;
    } finally {
      this.isFlushing = false;
    }
  }

  /**
   * 버퍼 상태 조회
   */
  getStatus(): {
    buffered: number;
    sessionId: string | null;
    isFlushing: boolean;
  } {
    return {
      buffered: this.buffer.length,
      sessionId: this.sessionId,
      isFlushing: this.isFlushing,
    };
  }

  /**
   * 버퍼 초기화 (주의: 데이터 손실)
   */
  clear(): void {
    this.buffer = [];
    this.saveToStorage();
  }

  /**
   * 자동 전송 중지
   */
  stop(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }

  /**
   * 자동 전송 재시작
   */
  start(): void {
    this.startAutoFlush();
  }

  // === Private Methods ===

  private startAutoFlush(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    this.flushTimer = setInterval(() => {
      if (this.buffer.length > 0) {
        this.flush();
      }
    }, this.config.flushInterval);
  }

  private saveToStorage(): void {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(this.config.storageKey, JSON.stringify(this.buffer));
      }
    } catch {
      // 로컬 스토리지 사용 불가 (private browsing 등)
    }
  }

  private restoreFromStorage(): void {
    try {
      if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem(this.config.storageKey);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) {
            this.buffer = parsed;
          }
        }
      }
    } catch {
      // 복원 실패 시 무시
    }
  }

  private setupUnloadHandler(): void {
    if (typeof window !== 'undefined') {
      // 페이지 이탈 시 동기 전송 시도 (sendBeacon 사용)
      window.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden' && this.buffer.length > 0) {
          this.flushSync();
        }
      });

      window.addEventListener('beforeunload', () => {
        if (this.buffer.length > 0) {
          this.flushSync();
        }
      });
    }
  }

  /**
   * 동기적 전송 (페이지 이탈 시)
   * sendBeacon API 사용으로 페이지 이탈 시에도 전송 보장
   */
  private flushSync(): void {
    if (this.buffer.length === 0) return;

    try {
      const data = JSON.stringify({
        interactions: this.buffer,
        session_id: this.sessionId,
      });

      // sendBeacon은 페이지 종료 시에도 전송 보장
      const success = navigator.sendBeacon(
        this.config.apiEndpoint,
        new Blob([data], { type: 'application/json' })
      );

      if (success) {
        this.buffer = [];
        this.saveToStorage();
      }
    } catch {
      // sendBeacon 실패 시 로컬 스토리지에 남겨둠
      // 다음 세션에서 복원됨
    }
  }
}

// 싱글톤 인스턴스 export
export const interactionBuffer = new InteractionBuffer();

// 클래스도 export (커스텀 설정 필요 시)
export { InteractionBuffer, type Interaction, type BufferConfig };
