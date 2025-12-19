'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatComposer } from './ChatComposer';
import { chatApi } from '@/lib/api';
import type { Message, QuickChip, Problem } from '@/lib/types';
import { Loader2 } from 'lucide-react';

// Initial welcome message
const welcomeMessage: Message = {
  id: 'welcome',
  role: 'assistant',
  content: '안녕하세요! 코딩 테스트 및 알고리즘 연습을 도와드릴게요. 어떤 난이도로 연습하시겠어요?',
  timestamp: new Date().toISOString(),
  chips: [
    { label: 'Easy', value: 'easy', category: 'difficulty' },
    { label: 'Medium', value: 'medium', category: 'difficulty' },
    { label: 'Hard', value: 'hard', category: 'difficulty' },
  ],
};

interface ChatPanelProps {
  onProblemsFound?: (problems: Problem[]) => void;
}

export function ChatPanel({ onProblemsFound }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle chip click - send it as a message
  const handleChipClick = useCallback((chip: QuickChip) => {
    const chipMessage = chip.category === 'framework'
      ? `${chip.label} 연습하고 싶어요`
      : chip.category === 'difficulty'
      ? `${chip.label} 난이도로 해주세요`
      : chip.label;

    handleSendMessage(chipMessage);
  }, []);

  // Generate fallback response when API is unavailable
  const generateFallbackResponse = useCallback((userMessage: string): Message => {
    const lowerMessage = userMessage.toLowerCase();

    // Difficulty detection
    if (lowerMessage.includes('easy') || lowerMessage.includes('쉬운') || lowerMessage.includes('초급')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Easy 난이도로 선택하셨네요! 어떤 유형의 문제를 원하시나요?',
        timestamp: new Date().toISOString(),
        chips: [
          { label: '빈칸 채우기', value: 'blank', category: 'topic' },
          { label: '퍼즐 (코드 정렬)', value: 'puzzle', category: 'topic' },
        ],
      };
    }

    if (lowerMessage.includes('medium') || lowerMessage.includes('중간') || lowerMessage.includes('중급')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Medium 난이도로 선택하셨네요! 어떤 유형의 문제를 원하시나요?',
        timestamp: new Date().toISOString(),
        chips: [
          { label: '빈칸 채우기', value: 'blank', category: 'topic' },
          { label: '퍼즐 (코드 정렬)', value: 'puzzle', category: 'topic' },
        ],
      };
    }

    if (lowerMessage.includes('hard') || lowerMessage.includes('어려운') || lowerMessage.includes('고급')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Hard 난이도로 선택하셨네요! 어떤 유형의 문제를 원하시나요?',
        timestamp: new Date().toISOString(),
        chips: [
          { label: '빈칸 채우기', value: 'blank', category: 'topic' },
          { label: '퍼즐 (코드 정렬)', value: 'puzzle', category: 'topic' },
        ],
      };
    }

    // Problem type detection
    if (lowerMessage.includes('빈칸') || lowerMessage.includes('blank')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '빈칸 채우기 문제를 준비했어요! Problems 페이지에서 "빈칸 채우기" 태그가 붙은 문제를 선택해주세요.',
        timestamp: new Date().toISOString(),
      };
    }

    if (lowerMessage.includes('퍼즐') || lowerMessage.includes('puzzle') || lowerMessage.includes('정렬')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '퍼즐 문제를 준비했어요! Problems 페이지에서 "퍼즐" 태그가 붙은 문제를 선택해주세요.',
        timestamp: new Date().toISOString(),
      };
    }

    // Algorithm topic detection
    if (lowerMessage.includes('배열') || lowerMessage.includes('array')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '배열 관련 알고리즘 문제를 찾아볼게요! Two Sum, Binary Search 등의 문제가 있어요.',
        timestamp: new Date().toISOString(),
      };
    }

    if (lowerMessage.includes('dp') || lowerMessage.includes('동적') || lowerMessage.includes('dynamic')) {
      return {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'DP(동적 프로그래밍) 문제를 찾아볼게요! Fibonacci 등의 문제가 있어요.',
        timestamp: new Date().toISOString(),
      };
    }

    // Default response
    return {
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: '어떤 난이도로 알고리즘 문제를 연습하고 싶으신가요?',
      timestamp: new Date().toISOString(),
      chips: [
        { label: 'Easy', value: 'easy', category: 'difficulty' },
        { label: 'Medium', value: 'medium', category: 'difficulty' },
        { label: 'Hard', value: 'hard', category: 'difficulty' },
      ],
    };
  }, []);

  // Send message to API
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Try to call the API
      const response = await chatApi.sendMessage({
        message: content,
        sessionId: sessionId || undefined,
      });

      // Update session ID if provided
      if (response.sessionId) {
        setSessionId(response.sessionId);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        chips: response.chips,
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Notify parent of found problems
      if (response.problems && response.problems.length > 0 && onProblemsFound) {
        onProblemsFound(response.problems);
      }
    } catch (error) {
      console.error('Chat API error:', error);

      // Use fallback response
      const fallbackMessage = generateFallbackResponse(content);
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId, onProblemsFound, generateFallbackResponse]);

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-semibold">Practice Assistant</h3>
        <p className="text-xs text-muted-foreground">무엇을 연습하고 싶은지 말해주세요</p>
      </div>

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

      <ChatComposer onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
