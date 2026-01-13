'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { ChatComposer } from '@/components/chat/ChatComposer';
import { practiceApi, type GuidedTutorChatResponse, type InitialGuideData } from '@/lib/api/practice';
import type { Message, QuickChip } from '@/lib/types';
import { Loader2, GraduationCap, BookOpen, Code2, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface GuidedTutorChatProps {
  problemId: string;
  userCode: string;
  onComplete?: () => void;
  sessionId?: string;
  onSessionIdChange?: (sessionId: string) => void;
}

export function GuidedTutorChat({
  problemId,
  userCode,
  onComplete,
  sessionId: propSessionId,
  onSessionIdChange,
}: GuidedTutorChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationHistory, setConversationHistory] = useState<
    Array<{ role: 'user' | 'assistant'; content: string }>
  >([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionId, setSessionId] = useState<string | null>(propSessionId || null);
  const [studentProgress, setStudentProgress] = useState<{
    understandingScore: number;
    conceptsMastered: string[];
    conceptsStruggling: string[];
    currentFocus: string;
    hintsReceived: number;
    attempts: number;
  } | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [initialGuide, setInitialGuide] = useState<InitialGuideData | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const userCodeRef = useRef(userCode);
  const initializedRef = useRef(false);

  // Keep userCode ref updated
  useEffect(() => {
    userCodeRef.current = userCode;
  }, [userCode]);

  // props 세션 ID 변경 시 업데이트
  useEffect(() => {
    if (propSessionId && propSessionId !== sessionId) {
      setSessionId(propSessionId);
    }
  }, [propSessionId, sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Initialize tutor session
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    const initTutor = async () => {
      try {
        setIsLoading(true);
        const response = await practiceApi.startGuidedTutor({
          problemId,
          sessionId: sessionId || undefined,
        });

        // 초기 가이드 저장
        if (response.initialGuide) {
          setInitialGuide(response.initialGuide);
        }

        // 학생 진행 상황 저장
        if (response.studentProgress) {
          setStudentProgress(response.studentProgress);
        }

        // 초기 메시지 표시
        const initialMessage: Message = {
          id: `tutor-init-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          chips: [
            { label: '이해했어요', value: 'understood', category: 'action' },
            { label: '잘 모르겠어요', value: 'need-help', category: 'action' },
          ],
        };

        setMessages([initialMessage]);
        setConversationHistory([
          { role: 'assistant', content: response.response },
        ]);
      } catch (error) {
        console.error('Failed to initialize guided tutor:', error);
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: '튜터 세션을 시작하는 중 오류가 발생했어요. 페이지를 새로고침해주세요.',
          timestamp: new Date().toISOString(),
        };
        setMessages([errorMessage]);
      } finally {
        setIsLoading(false);
      }
    };

    initTutor();
  }, [problemId]);

  // Handle sending message
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // 대화 히스토리 업데이트
    const newHistory = [
      ...conversationHistory,
      { role: 'user' as const, content },
    ];

    try {
      const response = await practiceApi.chatGuidedTutor({
        problemId,
        message: content,
        userCode: userCodeRef.current,
        sessionId: sessionId || undefined,
        conversationHistory: newHistory,
      });

      // 학생 진행 상황 업데이트
      if (response.studentProgress) {
        setStudentProgress(response.studentProgress);
      }

      // 완료 상태 확인
      if (response.isComplete) {
        setIsComplete(true);
        onComplete?.();
      }

      // 튜터 응답 메시지
      const assistantMessage: Message = {
        id: `tutor-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        chips: response.isComplete
          ? [
              { label: '정답 코드 확인', value: 'show-solution', category: 'action' },
              { label: '다른 문제 풀기', value: 'next-problem', category: 'action' },
            ]
          : [
              { label: '이해했어요', value: 'understood', category: 'action' },
              { label: '코드 확인해주세요', value: 'check-code', category: 'action' },
              { label: '힌트 더 주세요', value: 'more-hint', category: 'action' },
            ],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setConversationHistory([
        ...newHistory,
        { role: 'assistant', content: response.response },
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '메시지 전송 중 오류가 발생했어요. 다시 시도해주세요.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [problemId, sessionId, conversationHistory, isLoading, onComplete]);

  // Handle chip click
  const handleChipClick = useCallback((chip: QuickChip) => {
    const chipMessages: Record<string, string> = {
      'understood': '이해했어요! 다음 단계로 넘어갈게요.',
      'need-help': '잘 모르겠어요. 좀 더 설명해주세요.',
      'check-code': '제 코드를 확인해주세요.',
      'more-hint': '힌트를 좀 더 주세요.',
      'show-solution': '정답 코드를 보여주세요.',
      'next-problem': '다음 문제로 넘어갈게요.',
    };

    const message = chipMessages[chip.value] || chip.label;
    handleSendMessage(message);
  }, [handleSendMessage]);

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-green-500" />
            <div>
              <h3 className="font-semibold text-sm">1대1 대화형 튜터</h3>
              <p className="text-xs text-muted-foreground">함께 문제를 풀어봐요</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {studentProgress && (
              <Badge
                variant="outline"
                className={cn(
                  'text-xs',
                  studentProgress.understandingScore >= 0.7
                    ? 'bg-green-500/10 text-green-600 border-green-500/30'
                    : studentProgress.understandingScore >= 0.4
                    ? 'bg-yellow-500/10 text-yellow-600 border-yellow-500/30'
                    : 'bg-red-500/10 text-red-600 border-red-500/30'
                )}
              >
                이해도: {Math.round(studentProgress.understandingScore * 100)}%
              </Badge>
            )}
            {isComplete && (
              <Badge className="bg-green-500 text-white text-xs">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                완료
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Initial Guide Summary (collapsible) */}
      {initialGuide && (
        <details className="border-b border-border">
          <summary className="px-4 py-2 cursor-pointer text-xs font-medium text-muted-foreground hover:bg-secondary/50 flex items-center gap-2">
            <BookOpen className="h-3 w-3" />
            학습 가이드 보기
          </summary>
          <div className="px-4 pb-3 space-y-3 text-xs">
            {/* 핵심 개념 */}
            {initialGuide.conceptsExplanation.length > 0 && (
              <div>
                <p className="font-medium text-foreground mb-1">핵심 개념</p>
                <div className="space-y-1">
                  {initialGuide.conceptsExplanation.map((c, idx) => (
                    <div key={idx} className="text-muted-foreground">
                      <span className="text-foreground">{c.concept}</span>: {c.explanation}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 변수 가이드 */}
            {initialGuide.variablesGuide.variables.length > 0 && (
              <div>
                <p className="font-medium text-foreground mb-1 flex items-center gap-1">
                  <Code2 className="h-3 w-3" />
                  필요한 변수 ({initialGuide.variablesGuide.totalCount}개)
                </p>
                <div className="space-y-1">
                  {initialGuide.variablesGuide.variables.map((v, idx) => (
                    <div key={idx} className="text-muted-foreground flex items-center gap-2">
                      <code className="bg-secondary px-1 rounded text-foreground">
                        {v.suggestedName}
                      </code>
                      <span className="text-[10px] text-muted-foreground">({v.type})</span>
                      <span>- {v.role}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 학습 흐름 */}
            {initialGuide.flowOverview.length > 0 && (
              <div>
                <p className="font-medium text-foreground mb-1">학습 흐름</p>
                <ol className="list-decimal list-inside text-muted-foreground space-y-0.5">
                  {initialGuide.flowOverview.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </details>
      )}

      {/* Mastered/Struggling Concepts */}
      {studentProgress && (studentProgress.conceptsMastered.length > 0 || studentProgress.conceptsStruggling.length > 0) && (
        <div className="border-b border-border px-4 py-2 flex flex-wrap gap-1">
          {studentProgress.conceptsMastered.map((c) => (
            <Badge key={c} variant="outline" className="text-[10px] bg-green-500/10 text-green-600 border-green-500/30">
              {c}
            </Badge>
          ))}
          {studentProgress.conceptsStruggling.map((c) => (
            <Badge key={c} variant="outline" className="text-[10px] bg-orange-500/10 text-orange-600 border-orange-500/30">
              {c}
            </Badge>
          ))}
        </div>
      )}

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onChipClick={handleChipClick}
            />
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">생각 중...</span>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Chat Composer */}
      <ChatComposer onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
