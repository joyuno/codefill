'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatComposer } from './ChatComposer';
import { chatApi } from '@/lib/api';
import type { Message, QuickChip } from '@/lib/types';
import type { ConvertedProblem } from '@/lib/dataTypes';
import { getProblems } from '@/lib/problemLoader';
import { Loader2, Lightbulb, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PracticeChatPanelProps {
  problem: ConvertedProblem | null;
  onHintRequest?: (level: number, blankId?: string) => void;
  onProblemSelect?: (problem: ConvertedProblem) => void;
  hints?: string[];
}

// Initial welcome message
const initialWelcomeMessage: Message = {
  id: 'welcome',
  role: 'assistant',
  content: '안녕하세요! 코딩 테스트 및 알고리즘 연습을 도와드릴게요.\n\n어떤 난이도로 시작할까요?',
  timestamp: new Date().toISOString(),
  chips: [
    { label: 'Easy', value: 'easy', category: 'difficulty' },
    { label: 'Medium', value: 'medium', category: 'difficulty' },
    { label: 'Hard', value: 'hard', category: 'difficulty' },
  ],
};

export function PracticeChatPanel({ problem, onHintRequest, onProblemSelect, hints = [] }: PracticeChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([initialWelcomeMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hintLevel, setHintLevel] = useState(0);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Reset hint level when problem changes
  useEffect(() => {
    if (problem) {
      setHintLevel(0);
    }
  }, [problem?.id]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle chip click
  const handleChipClick = useCallback((chip: QuickChip) => {
    if (chip.category === 'difficulty') {
      handleDifficultySelect(chip.value);
    } else if (chip.category === 'topic') {
      handleTypeSelect(chip.value);
    } else if (chip.value === 'hint') {
      handleHintRequestInternal();
    } else if (chip.value === 'concepts') {
      showKeyConcepts();
    } else if (chip.value.startsWith('problem-')) {
      const problemId = chip.value.replace('problem-', '');
      const problems = getProblems();
      const selectedProblem = problems.find(p => p.id === problemId);
      if (selectedProblem && onProblemSelect) {
        onProblemSelect(selectedProblem);
        addProblemStartMessage(selectedProblem);
      }
    } else {
      handleSendMessage(chip.label);
    }
  }, [problem, hintLevel, selectedDifficulty]);

  // Handle difficulty selection
  const handleDifficultySelect = useCallback((difficulty: string) => {
    setSelectedDifficulty(difficulty);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: `${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} 난이도로 할게요`,
      timestamp: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: `${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} 난이도를 선택하셨네요!\n\n어떤 유형의 문제를 풀어볼까요?`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '빈칸 채우기', value: 'blank', category: 'topic' },
        { label: '퍼즐 (코드 정렬)', value: 'puzzle', category: 'topic' },
        { label: '1대1 대화형', value: 'guided', category: 'topic' },
        { label: '구현', value: 'implementation', category: 'topic' },
      ],
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
  }, []);

  // Handle problem type selection
  const handleTypeSelect = useCallback((type: string) => {
    const typeLabels: Record<string, string> = {
      blank: '빈칸 채우기',
      puzzle: '퍼즐',
      guided: '1대1 대화형',
      implementation: '구현',
    };

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: `${typeLabels[type] || type}로 할게요`,
      timestamp: new Date().toISOString(),
    };

    // Find matching problems
    const problems = getProblems();
    const matchingProblems = problems.filter(p =>
      p.problemType === type &&
      (!selectedDifficulty || p.difficulty === selectedDifficulty)
    );

    let assistantMessage: Message;

    if (matchingProblems.length > 0) {
      assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: `좋아요! 다음 문제들 중에서 선택해주세요:`,
        timestamp: new Date().toISOString(),
        chips: matchingProblems.slice(0, 4).map(p => ({
          label: `${p.title} (${p.difficulty})`,
          value: `problem-${p.id}`,
          category: 'action' as const,
        })),
      };
    } else {
      // Fallback: select first matching type problem
      const fallbackProblem = problems.find(p => p.problemType === type);
      if (fallbackProblem && onProblemSelect) {
        onProblemSelect(fallbackProblem);
        assistantMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: `"${fallbackProblem.title}" 문제를 시작합니다!\n\n${fallbackProblem.description}\n\n오른쪽 편집기에서 문제를 풀어보세요. 도움이 필요하면 힌트를 요청해주세요!`,
          timestamp: new Date().toISOString(),
          chips: [
            { label: '힌트 보기', value: 'hint', category: 'action' },
            { label: '핵심 개념', value: 'concepts', category: 'action' },
          ],
        };
      } else {
        assistantMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: '해당하는 문제를 찾을 수 없습니다. 다른 유형을 선택해주세요.',
          timestamp: new Date().toISOString(),
        };
      }
    }

    setMessages(prev => [...prev, userMessage, assistantMessage]);
  }, [selectedDifficulty, onProblemSelect]);

  // Add problem start message
  const addProblemStartMessage = useCallback((selectedProblem: ConvertedProblem) => {
    const assistantMessage: Message = {
      id: `problem-start-${Date.now()}`,
      role: 'assistant',
      content: `"${selectedProblem.title}" 문제를 시작합니다!\n\n${selectedProblem.description}\n\n오른쪽 편집기에서 문제를 풀어보세요. 도움이 필요하면 힌트를 요청해주세요!`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '힌트 보기', value: 'hint', category: 'action' },
        { label: '핵심 개념', value: 'concepts', category: 'action' },
      ],
    };
    setMessages(prev => [...prev, assistantMessage]);
  }, []);

  // Request hint (internal)
  const handleHintRequestInternal = useCallback(() => {
    if (!problem) {
      const noProblemmsg: Message = {
        id: `no-problem-${Date.now()}`,
        role: 'assistant',
        content: '먼저 문제를 선택해주세요!',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, noProblemmsg]);
      return;
    }

    const newLevel = Math.min(hintLevel, 2);

    const userMessage: Message = {
      id: `user-hint-${Date.now()}`,
      role: 'user',
      content: '힌트를 보여주세요',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    if (onHintRequest) {
      onHintRequest(newLevel);
    }

    const hintTexts = [
      `힌트 1: 이 문제는 ${problem.topics[0] || '알고리즘'}에 관한 문제입니다. ${problem.keyConcepts[0] || '기본 개념'}을 생각해보세요.`,
      `힌트 2: ${problem.keyConcepts.slice(0, 2).join(', ')}를 활용해야 합니다.`,
      `힌트 3 (마지막): 정답에 가까운 힌트입니다. ${problem.keyConcepts.join(', ')}를 순서대로 적용해보세요.`,
    ];

    const hintMessage: Message = {
      id: `hint-${Date.now()}`,
      role: 'assistant',
      content: hints[newLevel] || hintTexts[newLevel] || '더 이상의 힌트가 없습니다.',
      timestamp: new Date().toISOString(),
      chips: newLevel < 2 ? [
        { label: '다음 힌트', value: 'hint', category: 'action' },
      ] : undefined,
    };

    setMessages(prev => [...prev, hintMessage]);
    setHintLevel(prev => Math.min(prev + 1, 3));
  }, [problem, hintLevel, hints, onHintRequest]);

  // Show key concepts
  const showKeyConcepts = useCallback(() => {
    if (!problem) {
      const noProblemmsg: Message = {
        id: `no-problem-${Date.now()}`,
        role: 'assistant',
        content: '먼저 문제를 선택해주세요!',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, noProblemmsg]);
      return;
    }

    const userMessage: Message = {
      id: `user-concepts-${Date.now()}`,
      role: 'user',
      content: '핵심 개념을 알려주세요',
      timestamp: new Date().toISOString(),
    };

    const conceptsMessage: Message = {
      id: `concepts-${Date.now()}`,
      role: 'assistant',
      content: `이 문제의 핵심 개념:\n\n${problem.keyConcepts.map((c, i) => `${i + 1}. ${c}`).join('\n')}\n\n관련 토픽: ${problem.topics.join(', ')}`,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage, conceptsMessage]);
  }, [problem]);

  // Send message
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: content,
        sessionId: sessionId || undefined,
      });

      if (response.sessionId) {
        setSessionId(response.sessionId);
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        chips: response.chips,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const fallbackMessage: Message = {
        id: `fallback-${Date.now()}`,
        role: 'assistant',
        content: generateFallbackResponse(content),
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId]);

  // Generate fallback response
  const generateFallbackResponse = (userMessage: string): string => {
    const lower = userMessage.toLowerCase();

    if (lower.includes('힌트') || lower.includes('hint')) {
      return '아래 "힌트" 버튼을 클릭해서 단계별 힌트를 받을 수 있어요!';
    }
    if (lower.includes('어려') || lower.includes('모르')) {
      return '천천히 문제를 다시 읽어보세요. 힌트가 필요하면 말씀해주세요!';
    }
    if (lower.includes('easy') || lower.includes('쉬운')) {
      handleDifficultySelect('easy');
      return '';
    }
    if (lower.includes('medium') || lower.includes('중간')) {
      handleDifficultySelect('medium');
      return '';
    }
    if (lower.includes('hard') || lower.includes('어려운')) {
      handleDifficultySelect('hard');
      return '';
    }

    return '무엇이든 물어보세요! 난이도를 선택하거나 힌트를 요청할 수 있어요.';
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-sm">Practice Assistant</h3>
            {problem ? (
              <p className="text-xs text-muted-foreground mt-0.5">{problem.title}</p>
            ) : (
              <p className="text-xs text-muted-foreground mt-0.5">문제를 선택해주세요</p>
            )}
          </div>
          {problem && (
            <Badge variant="outline" className="text-xs">
              힌트 {hintLevel}/3
            </Badge>
          )}
        </div>
      </div>

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

      {/* Quick Actions - only show when problem is selected */}
      {problem && (
        <div className="border-t border-border px-4 py-2">
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5 text-xs"
              onClick={handleHintRequestInternal}
              disabled={hintLevel >= 3}
            >
              <Lightbulb className="h-3.5 w-3.5" />
              힌트 ({3 - hintLevel}개 남음)
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5 text-xs"
              onClick={showKeyConcepts}
            >
              <BookOpen className="h-3.5 w-3.5" />
              핵심 개념
            </Button>
          </div>
        </div>
      )}

      <ChatComposer onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
