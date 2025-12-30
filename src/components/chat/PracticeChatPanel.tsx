'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatComposer } from './ChatComposer';
import { agentApi } from '@/lib/api';
import type {
  ChatAgentMessage,
  CollectedInfo,
  BaseProblemInfo,
  ChatV2Response,
  GeneratedProblemData,
  GeneratedBlankData,
  GeneratedPuzzleData,
  GeneratedGuidedData,
} from '@/lib/api/agent';
import type { Message, QuickChip } from '@/lib/types';
import type { ConvertedProblem } from '@/lib/dataTypes';
import { Loader2, Lightbulb, BookOpen, Sparkles, GraduationCap, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PracticeChatPanelProps {
  problem: ConvertedProblem | null;
  onHintRequest?: (level: number, blankId?: string) => void;
  onProblemSelect?: (problem: ConvertedProblem) => void;
  hints?: string[];
}

// Problem type labels
const PROBLEM_TYPE_LABELS: Record<string, string> = {
  blank: '빈칸 채우기',
  puzzle: '퍼즐 (코드 정렬)',
  guided: '1대1 대화형',
};

// Helper function to convert input_output to testCases
function convertInputOutputToTestCases(inputOutput?: { inputs: string[]; outputs: string[] }) {
  if (!inputOutput || !inputOutput.inputs || !inputOutput.outputs) {
    return undefined;
  }
  const testCases = [];
  const length = Math.min(inputOutput.inputs.length, inputOutput.outputs.length);
  for (let i = 0; i < length; i++) {
    testCases.push({
      input: inputOutput.inputs[i],
      expected: inputOutput.outputs[i],
      isHidden: false,
    });
  }
  return testCases.length > 0 ? testCases : undefined;
}

// Helper function to convert generated problem data to ConvertedProblem
function convertGeneratedDataToProblem(data: GeneratedProblemData): ConvertedProblem {
  if (data.problem_type === 'blank') {
    const blankData = data as GeneratedBlankData;
    // 연속된 언더스코어(2개 이상)를 모두 ___ (3개)로 정규화 (UnifiedPractice에서 ___ 패턴 매칭)
    const codeSnippet = blankData.code_template.replace(/_{2,}/g, '___');
    return {
      id: blankData.original_id || `generated-${Date.now()}`,
      title: blankData.title,
      description: blankData.description,
      problemType: 'blank',
      difficulty: blankData.difficulty as 'easy' | 'medium' | 'hard',
      topics: blankData.topics,
      keyConcepts: blankData.topics,
      framework: blankData.language as 'python' | 'java' | 'cpp' | 'javascript',
      codeTemplate: blankData.code_template,
      codeSnippet: codeSnippet,
      blanks: blankData.answers.map((answer, idx) => ({
        id: `blank-${idx}`,
        position: idx,
        answer: answer,
        placeholder: `_${idx}_`,
      })),
      testCases: convertInputOutputToTestCases(blankData.input_output),
    };
  } else if (data.problem_type === 'puzzle') {
    const puzzleData = data as GeneratedPuzzleData;
    // 블록 변환 (id를 정답 순서대로 정렬)
    const sortedBlocks = [...puzzleData.blocks].sort((a, b) => a.id - b.id);
    const convertedBlocks = sortedBlocks.map(b => ({
      id: String(b.id),
      code: b.code,
      correctOrder: b.id,
      indentation: 0,
    }));

    return {
      id: puzzleData.original_id || `generated-${Date.now()}`,
      title: puzzleData.title,
      description: puzzleData.description,
      problemType: 'puzzle',
      difficulty: puzzleData.difficulty as 'easy' | 'medium' | 'hard',
      topics: puzzleData.topics,
      keyConcepts: puzzleData.topics,
      framework: puzzleData.language as 'python' | 'java' | 'cpp' | 'javascript',
      // puzzleBlocks와 blocks 둘 다 설정 (UnifiedPractice에서 puzzleBlocks 사용)
      puzzleBlocks: convertedBlocks,
      blocks: convertedBlocks,
      correctOrder: sortedBlocks.map(b => String(b.id)),
      fixedStart: puzzleData.fixed_start,
      fixedEnd: puzzleData.fixed_end,
      testCases: convertInputOutputToTestCases(puzzleData.input_output),
    };
  } else {
    // guided
    const guidedData = data as GeneratedGuidedData;
    return {
      id: guidedData.original_id || `generated-${Date.now()}`,
      title: guidedData.title,
      description: guidedData.description,
      problemType: 'guided',
      difficulty: guidedData.difficulty as 'easy' | 'medium' | 'hard',
      topics: guidedData.topics,
      keyConcepts: guidedData.topics,
      framework: guidedData.language as 'python' | 'java' | 'cpp' | 'javascript',
      concepts: guidedData.concepts,
      flow: guidedData.flow,
      checkpoints: guidedData.checkpoints,
      finalCodeReveal: guidedData.final_code,
      testCases: convertInputOutputToTestCases(guidedData.input_output),
    };
  }
}

// Initial welcome message
const initialWelcomeMessage: Message = {
  id: 'welcome',
  role: 'assistant',
  content: '안녕하세요! 코딩 연습을 도와드릴게요.\n\n어떤 알고리즘을 연습하고 싶으신가요? 원하는 주제나 난이도를 말씀해주세요!',
  timestamp: new Date().toISOString(),
  chips: [
    { label: 'DP 연습하고 싶어요', value: 'dp', category: 'topic' },
    { label: '그래프 문제 풀래요', value: 'graph', category: 'topic' },
    { label: '쉬운 문제로 시작', value: 'easy', category: 'difficulty' },
  ],
};

export function PracticeChatPanel({ problem, onHintRequest, onProblemSelect, hints = [] }: PracticeChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([initialWelcomeMessage]);
  const [conversationHistory, setConversationHistory] = useState<ChatAgentMessage[]>([]);
  const [collectedInfo, setCollectedInfo] = useState<CollectedInfo>({
    topics: [],
    difficulty: null,
    language: null,
    specific_needs: null,
    time_available: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [hintLevel, setHintLevel] = useState(0);
  const [previousHints, setPreviousHints] = useState<string[]>([]);
  const [recommendedProblems, setRecommendedProblems] = useState<BaseProblemInfo[]>([]);
  const [selectedBaseProblem, setSelectedBaseProblem] = useState<BaseProblemInfo | null>(null);
  const [flowState, setFlowState] = useState<'collecting' | 'recommending' | 'type_selection' | 'generating' | 'practicing' | 'guided_learning'>('collecting');
  const [useV2, setUseV2] = useState(true);  // V3 API 기본 사용 (개선된 LangGraph)
  const [v2SessionState, setV2SessionState] = useState<Record<string, unknown>>({});  // V2 세션 상태
  const scrollRef = useRef<HTMLDivElement>(null);

  // Guided 모드 상태
  const [guidedFlowStep, setGuidedFlowStep] = useState(0);
  const [guidedCheckpointIndex, setGuidedCheckpointIndex] = useState(0);
  const [guidedProblem, setGuidedProblem] = useState<ConvertedProblem | null>(null);

  // Reset hint level when problem changes
  useEffect(() => {
    if (problem) {
      setHintLevel(0);
      setPreviousHints([]);
      setFlowState('practicing');
    }
  }, [problem?.id]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Get user context from localStorage (onboarding data) + current search results
  const getUserContext = useCallback(() => {
    const context: Record<string, unknown> = {};

    // User profile from localStorage
    if (typeof window !== 'undefined') {
      try {
        const userData = localStorage.getItem('user_profile');
        if (userData) {
          const profile = JSON.parse(userData);
          context.status = profile.status;
          context.goal = profile.goal;
          context.level = profile.level;
          context.strong_algorithms = profile.strong_algorithms;
          context.desired_job = profile.desired_job;
        }
      } catch {
        // Ignore
      }
    }

    // Include search_results for problem selection
    if (recommendedProblems.length > 0) {
      context.search_results = recommendedProblems;
    }

    // Include current problem if exists
    if (problem) {
      context.current_problem = {
        id: problem.id,
        title: problem.title,
        difficulty: problem.difficulty,
        topics: problem.topics,
      };
    }

    return context;
  }, [recommendedProblems, problem]);

  // Handle guided flow progression (새 형식: string[] 배열)
  const handleGuidedProgress = useCallback((understood: boolean) => {
    if (!guidedProblem || !guidedProblem.flow) return;

    // flow는 이제 string[] 형식
    const currentStepContent = typeof guidedProblem.flow[guidedFlowStep] === 'string'
      ? guidedProblem.flow[guidedFlowStep] as string
      : (guidedProblem.flow[guidedFlowStep] as { tutor_message?: string })?.tutor_message || '';

    if (!understood) {
      // 힌트 제공 (새 형식은 힌트가 없으므로 현재 단계 반복)
      const hintMsg: Message = {
        id: `guided-hint-${Date.now()}`,
        role: 'assistant',
        content: `${currentStepContent}\n\n천천히 다시 읽어보세요!`,
        timestamp: new Date().toISOString(),
        chips: [
          { label: '이해했어요', value: 'guided-understood', category: 'action' },
          { label: '여전히 어려워요', value: 'guided-stuck', category: 'action' },
        ],
      };
      setMessages(prev => [...prev, hintMsg]);
      return;
    }

    // 다음 단계로 이동
    const nextStepIndex = guidedFlowStep + 1;

    // 체크포인트 확인 (새 형식: string[])
    const checkpoints = guidedProblem.checkpoints || [];
    if (guidedCheckpointIndex < checkpoints.length && guidedFlowStep > 0 && guidedFlowStep % 2 === 0) {
      const checkpointContent = typeof checkpoints[guidedCheckpointIndex] === 'string'
        ? checkpoints[guidedCheckpointIndex] as string
        : (checkpoints[guidedCheckpointIndex] as { question?: string })?.question || '';

      const checkpointMsg: Message = {
        id: `checkpoint-${Date.now()}`,
        role: 'assistant',
        content: `확인 질문: ${checkpointContent}`,
        timestamp: new Date().toISOString(),
        chips: [
          { label: '정답 확인', value: 'guided-check-answer', category: 'action' },
        ],
      };
      setMessages(prev => [...prev, checkpointMsg]);
      setGuidedCheckpointIndex(guidedCheckpointIndex + 1);
      return;
    }

    if (nextStepIndex >= guidedProblem.flow.length) {
      // 모든 단계 완료
      const completeMsg: Message = {
        id: `guided-complete-${Date.now()}`,
        role: 'assistant',
        content: `축하합니다! 모든 단계를 완료했어요!\n\n최종 코드를 확인해볼까요?`,
        timestamp: new Date().toISOString(),
        chips: [
          { label: '최종 코드 보기', value: 'guided-show-code', category: 'action' },
          { label: '다른 문제 풀기', value: 'guided-new-problem', category: 'action' },
        ],
      };
      setMessages(prev => [...prev, completeMsg]);
      return;
    }

    // 다음 단계 메시지
    const nextStepContent = typeof guidedProblem.flow[nextStepIndex] === 'string'
      ? guidedProblem.flow[nextStepIndex] as string
      : (guidedProblem.flow[nextStepIndex] as { tutor_message?: string })?.tutor_message || '';

    setGuidedFlowStep(nextStepIndex);

    const nextMsg: Message = {
      id: `guided-step-${nextStepIndex}-${Date.now()}`,
      role: 'assistant',
      content: `**Step ${nextStepIndex + 1}**\n\n${nextStepContent}`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '이해했어요', value: 'guided-understood', category: 'action' },
        { label: '잘 모르겠어요', value: 'guided-stuck', category: 'action' },
      ],
    };
    setMessages(prev => [...prev, nextMsg]);
  }, [guidedProblem, guidedFlowStep, guidedCheckpointIndex]);

  // Show final code for guided problem
  const showGuidedFinalCode = useCallback(() => {
    if (!guidedProblem) return;

    const codeMsg: Message = {
      id: `guided-code-${Date.now()}`,
      role: 'assistant',
      content: `최종 코드:\n\n\`\`\`python\n${guidedProblem.finalCodeReveal || '# 코드 없음'}\n\`\`\`\n\n이 코드를 분석하면서 배운 내용을 복습해보세요!`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '다른 문제 풀기', value: 'guided-new-problem', category: 'action' },
        { label: '다른 유형으로 풀기', value: 'guided-different-type', category: 'action' },
      ],
    };
    setMessages(prev => [...prev, codeMsg]);
  }, [guidedProblem]);

  // Reset to start new problem
  const resetToNewProblem = useCallback(() => {
    setFlowState('collecting');
    setGuidedProblem(null);
    setGuidedFlowStep(0);
    setGuidedCheckpointIndex(0);
    setSelectedBaseProblem(null);
    setRecommendedProblems([]);
    setCollectedInfo({
      topics: [],
      difficulty: null,
      language: null,
      specific_needs: null,
      time_available: null,
    });

    const resetMsg: Message = {
      id: `reset-${Date.now()}`,
      role: 'assistant',
      content: '새로운 문제를 시작할게요!\n\n어떤 알고리즘을 연습하고 싶으신가요?',
      timestamp: new Date().toISOString(),
      chips: [
        { label: 'DP 연습하고 싶어요', value: 'dp', category: 'topic' },
        { label: '그래프 문제 풀래요', value: 'graph', category: 'topic' },
        { label: '쉬운 문제로 시작', value: 'easy', category: 'difficulty' },
      ],
    };
    setMessages(prev => [...prev, resetMsg]);
  }, []);

  // Show problem type selection UI (정의를 handleChipClick보다 먼저 위치)
  const showProblemTypeSelection = useCallback((baseProblem: BaseProblemInfo) => {
    setFlowState('type_selection');

    const userMsg: Message = {
      id: `user-select-${Date.now()}`,
      role: 'user',
      content: `"${baseProblem.title}" 문제를 선택할게요`,
      timestamp: new Date().toISOString(),
    };

    const assistantMsg: Message = {
      id: `type-select-${Date.now()}`,
      role: 'assistant',
      content: `좋은 선택이에요! "${baseProblem.title}" 문제를 어떤 형식으로 풀어볼까요?`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '빈칸 채우기', value: 'type-blank', category: 'action' },
        { label: '퍼즐 (코드 정렬)', value: 'type-puzzle', category: 'action' },
        { label: '1대1 대화형', value: 'type-guided', category: 'action' },
      ],
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
  }, []);

  // Handle chip click
  const handleChipClick = useCallback((chip: QuickChip) => {
    if (chip.value === 'hint') {
      handleHintRequestInternal();
    } else if (chip.value === 'concepts') {
      showKeyConcepts();
    } else if (chip.value === 'guided-understood') {
      // Guided 모드: 이해했음
      const userMsg: Message = {
        id: `user-understood-${Date.now()}`,
        role: 'user',
        content: '이해했어요!',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMsg]);
      handleGuidedProgress(true);
    } else if (chip.value === 'guided-stuck') {
      // Guided 모드: 모르겠음
      const userMsg: Message = {
        id: `user-stuck-${Date.now()}`,
        role: 'user',
        content: '잘 모르겠어요...',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMsg]);
      handleGuidedProgress(false);
    } else if (chip.value === 'guided-check-answer') {
      // Guided 모드: 체크포인트 정답 확인
      handleGuidedProgress(true);
    } else if (chip.value === 'guided-show-code') {
      // Guided 모드: 최종 코드 보기
      const userMsg: Message = {
        id: `user-show-code-${Date.now()}`,
        role: 'user',
        content: '최종 코드를 보여주세요',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMsg]);
      showGuidedFinalCode();
    } else if (chip.value === 'guided-new-problem') {
      // Guided 모드: 새 문제 시작
      const userMsg: Message = {
        id: `user-new-problem-${Date.now()}`,
        role: 'user',
        content: '다른 문제를 풀고 싶어요',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMsg]);
      resetToNewProblem();
    } else if (chip.value === 'guided-different-type') {
      // Guided 모드: 같은 문제 다른 유형으로
      if (selectedBaseProblem) {
        const userMsg: Message = {
          id: `user-diff-type-${Date.now()}`,
          role: 'user',
          content: '다른 유형으로 풀어볼게요',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, userMsg]);
        setGuidedProblem(null);
        setGuidedFlowStep(0);
        setFlowState('type_selection');
        showProblemTypeSelection(selectedBaseProblem);
      }
    } else if (chip.value.startsWith('problem-')) {
      // Problem selection
      const problemIndex = parseInt(chip.value.replace('problem-', ''), 10);
      const selected = recommendedProblems[problemIndex];
      if (selected) {
        setSelectedBaseProblem(selected);
        showProblemTypeSelection(selected);
      }
    } else if (chip.value.startsWith('type-')) {
      // Problem type selection
      const type = chip.value.replace('type-', '') as 'blank' | 'puzzle' | 'guided';
      if (selectedBaseProblem) {
        handleProblemTypeSelect(type);
      }
    } else {
      // Send as regular message
      handleSendMessage(chip.label);
    }
  }, [recommendedProblems, selectedBaseProblem, handleGuidedProgress, showGuidedFinalCode, resetToNewProblem, showProblemTypeSelection]);

  // Handle problem type selection and generate problem
  const handleProblemTypeSelect = useCallback(async (type: 'blank' | 'puzzle' | 'guided') => {
    if (!selectedBaseProblem) return;

    setFlowState('generating');

    const userMsg: Message = {
      id: `user-type-${Date.now()}`,
      role: 'user',
      content: `${PROBLEM_TYPE_LABELS[type]}로 할게요`,
      timestamp: new Date().toISOString(),
    };

    const loadingMsg: Message = {
      id: `loading-${Date.now()}`,
      role: 'assistant',
      content: `${PROBLEM_TYPE_LABELS[type]} 문제를 생성 중입니다...`,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setIsLoading(true);

    try {
      // Extract code from solutions array if not directly available
      const targetLanguage = (selectedBaseProblem.language || 'python') as 'python' | 'java' | 'cpp';
      const extractedCode = selectedBaseProblem.code ||
        selectedBaseProblem.solutions?.find(s => s.language === targetLanguage)?.code ||
        selectedBaseProblem.solutions?.[0]?.code || '';

      // Validate that we have code to work with
      if (!extractedCode) {
        throw new Error('이 문제에는 솔루션 코드가 없어요. 다른 문제를 선택해주세요!');
      }

      const request = {
        base_problem: {
          ...selectedBaseProblem,
          code: extractedCode,
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
        },
        problem_type: type,
        user_level: 'intermediate' as const,
        language: targetLanguage,
      };

      let generatedProblem: ConvertedProblem;

      // input_output을 testCases로 변환
      const inputOutput = (selectedBaseProblem as any).input_output;
      const testCases = inputOutput?.inputs && inputOutput?.outputs
        ? inputOutput.inputs.slice(0, inputOutput.outputs.length).map((input: string, idx: number) => ({
            input,
            expected: inputOutput.outputs[idx],
            isHidden: false,
          }))
        : undefined;

      if (type === 'blank') {
        const result = await agentApi.generateBlank(request);
        // 새 형식: original_id, language, code_template, answers[]
        // 연속된 언더스코어를 ___ (3개)로 정규화
        const codeSnippet = result.code_template.replace(/_{2,}/g, '___');
        generatedProblem = {
          id: result.original_id || `generated-${Date.now()}`,
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'blank',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          framework: targetLanguage,
          codeTemplate: result.code_template,
          codeSnippet: codeSnippet,  // UnifiedPractice에서 사용
          blanks: result.answers.map((answer, idx) => ({
            id: `blank-${idx}`,
            position: idx,
            answer: answer,
            placeholder: `_${idx}_`,
          })),
          testCases,
        };
      } else if (type === 'puzzle') {
        const result = await agentApi.generatePuzzle(request);
        // 새 형식: original_id, language, fixed_start?, fixed_end?, blocks[]
        const sortedBlocks = [...result.blocks].sort((a, b) => a.id - b.id);
        const convertedBlocks = sortedBlocks.map(b => ({
          id: String(b.id),
          code: b.code,
          correctOrder: b.id,
          indentation: 0,  // 기본 들여쓰기
        }));
        generatedProblem = {
          id: result.original_id || `generated-${Date.now()}`,
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'puzzle',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          framework: targetLanguage,
          puzzleBlocks: convertedBlocks,  // UnifiedPractice에서 사용
          blocks: convertedBlocks,
          correctOrder: sortedBlocks.map(b => String(b.id)),
          fixedStart: result.fixed_start,
          fixedEnd: result.fixed_end,
          testCases,
        };
      } else {
        const result = await agentApi.generateGuided(request);
        // 새 형식: original_id, language, concepts[], flow[], checkpoints[]
        // 코드 추출 (code가 객체일 수 있음)
        const extractedCode = typeof selectedBaseProblem.code === 'string'
          ? selectedBaseProblem.code
          : (selectedBaseProblem.code as Record<string, string>)?.[targetLanguage]
            || selectedBaseProblem.solutions?.[0]?.code
            || '';

        generatedProblem = {
          id: result.original_id || `generated-${Date.now()}`,
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'guided',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          framework: targetLanguage,
          concepts: result.concepts,  // string[]
          flow: result.flow,          // string[]
          checkpoints: result.checkpoints,  // string[]
          finalCodeReveal: extractedCode,  // 원본 코드를 최종 코드로 사용
          testCases,
        };
      }

      console.log('[handleProblemTypeSelect] Generated problem:', {
        type,
        id: generatedProblem.id,
        title: generatedProblem.title,
        problemType: generatedProblem.problemType,
        codeSnippet: (generatedProblem as any).codeSnippet?.substring(0, 100),
        puzzleBlocks: (generatedProblem as any).puzzleBlocks?.length,
        blanks: (generatedProblem as any).blanks?.length,
        testCases: generatedProblem.testCases?.length,
      });

      // Guided 문제인 경우: 채팅 UI에서 계속 진행
      if (type === 'guided' && generatedProblem.flow && generatedProblem.flow.length > 0) {
        setGuidedProblem(generatedProblem);
        setGuidedFlowStep(0);
        setGuidedCheckpointIndex(0);

        // 첫 번째 개념 설명과 flow step 시작 (새 형식: string[] 배열)
        const concepts = generatedProblem.concepts || [];
        const conceptIntro = concepts.length > 0
          ? `먼저 핵심 개념을 알아볼까요?\n\n${concepts.map((c, idx) =>
              typeof c === 'string' ? `${idx + 1}. **${c}**` : `**${c.name}**: ${c.explanation}`
            ).join('\n')}\n\n---\n\n`
          : '';

        // flow는 이제 string[] 형식
        const firstStepContent = typeof generatedProblem.flow[0] === 'string'
          ? generatedProblem.flow[0] as string
          : (generatedProblem.flow[0] as { tutor_message?: string })?.tutor_message || '';

        setMessages(prev => {
          const filtered = prev.filter(m => !m.id.startsWith('loading-'));
          return [...filtered, {
            id: `guided-start-${Date.now()}`,
            role: 'assistant' as const,
            content: `${conceptIntro}**Step 1**\n\n${firstStepContent}`,
            timestamp: new Date().toISOString(),
            chips: [
              { label: '이해했어요', value: 'guided-understood', category: 'action' },
              { label: '잘 모르겠어요', value: 'guided-stuck', category: 'action' },
            ],
          }];
        });

        setFlowState('guided_learning');

        // Guided 모드에서는 onProblemSelect를 호출하지 않음 (채팅 UI 유지)
        return;
      }

      // Blank/Puzzle 문제: 기존 로직 (연습 화면으로 이동)
      setMessages(prev => {
        const filtered = prev.filter(m => !m.id.startsWith('loading-'));
        return [...filtered, {
          id: `success-${Date.now()}`,
          role: 'assistant' as const,
          content: `문제가 준비되었어요! 왼쪽 화면에서 문제를 풀어보세요.\n\n막히면 언제든 힌트를 요청해주세요!`,
          timestamp: new Date().toISOString(),
          chips: [
            { label: '힌트 보기', value: 'hint', category: 'action' },
            { label: '핵심 개념', value: 'concepts', category: 'action' },
          ],
        }];
      });

      if (onProblemSelect) {
        onProblemSelect(generatedProblem);
      }

      setFlowState('practicing');

    } catch (error) {
      console.error('Problem generation error:', error);
      setMessages(prev => {
        const filtered = prev.filter(m => !m.id.startsWith('loading-'));
        return [...filtered, {
          id: `error-${Date.now()}`,
          role: 'assistant' as const,
          content: `문제 생성 중 오류가 발생했어요. 다시 시도해주세요.\n\n오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
          timestamp: new Date().toISOString(),
        }];
      });
      setFlowState('type_selection');
    } finally {
      setIsLoading(false);
    }
  }, [selectedBaseProblem, onProblemSelect]);

  // Request AI hint
  const handleHintRequestInternal = useCallback(async () => {
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

    if (hintLevel >= 4) {
      const maxHintMsg: Message = {
        id: `max-hint-${Date.now()}`,
        role: 'assistant',
        content: '모든 힌트를 이미 사용했어요. 정답 코드를 확인하고 싶으시면 말씀해주세요!',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, maxHintMsg]);
      return;
    }

    const userMessage: Message = {
      id: `user-hint-${Date.now()}`,
      role: 'user',
      content: '힌트를 보여주세요',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await agentApi.getHint({
        problem_id: problem.id,
        problem_info: {
          title: problem.title,
          description: problem.description,
          topics: problem.topics,
          key_concepts: problem.keyConcepts,
          problem_type: problem.problemType,
        },
        user_code: undefined,
        attempt_count: hintLevel,
        hint_level: (hintLevel + 1) as 1 | 2 | 3 | 4,
        previous_hints: previousHints,
        user_level: 'intermediate',
      });

      const hintMessage: Message = {
        id: `hint-${Date.now()}`,
        role: 'assistant',
        content: `${response.hint_content}\n\n${response.encouragement}`,
        timestamp: new Date().toISOString(),
        chips: response.hint_level < 4 ? [
          { label: '다음 힌트', value: 'hint', category: 'action' },
        ] : undefined,
      };

      setMessages(prev => [...prev, hintMessage]);
      setHintLevel(prev => prev + 1);
      setPreviousHints(prev => [...prev, response.hint_content]);

      if (onHintRequest) {
        onHintRequest(response.hint_level);
      }

    } catch (error) {
      // Fallback to local hints
      const hintTexts = [
        `힌트 1: 이 문제는 ${problem.topics[0] || '알고리즘'}에 관한 문제입니다.`,
        `힌트 2: ${problem.keyConcepts.slice(0, 2).join(', ')}를 활용해보세요.`,
        `힌트 3: ${problem.keyConcepts.join(', ')}를 순서대로 적용해보세요.`,
        `힌트 4 (마지막): 정답에 매우 가까워요! 한 번 더 시도해보세요.`,
      ];

      const hintMessage: Message = {
        id: `hint-fallback-${Date.now()}`,
        role: 'assistant',
        content: hints[hintLevel] || hintTexts[hintLevel] || '더 이상의 힌트가 없습니다.',
        timestamp: new Date().toISOString(),
        chips: hintLevel < 3 ? [
          { label: '다음 힌트', value: 'hint', category: 'action' },
        ] : undefined,
      };

      setMessages(prev => [...prev, hintMessage]);
      setHintLevel(prev => Math.min(prev + 1, 4));
    } finally {
      setIsLoading(false);
    }
  }, [problem, hintLevel, hints, previousHints, onHintRequest]);

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

  // Send message to Chat Agent
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

    // Update conversation history
    const newHistory: ChatAgentMessage[] = [
      ...conversationHistory,
      { role: 'user', content },
    ];

    try {
      // V2 또는 V1 API 선택
      let responseMessage: string;
      let responseCollectedInfo: CollectedInfo;
      let actionData: {
        status?: string;
        problems?: BaseProblemInfo[];
        generated_problem?: BaseProblemInfo;
        action_trigger?: string;
        selected_problem?: string;
        selected_problem_index?: number;
      } | undefined;
      let v2Response: ChatV2Response | undefined;

      if (useV2) {
        // 정식 LangGraph API 사용
        v2Response = await agentApi.chatMain({
          message: content,
          conversation_history: conversationHistory,
          user_context: getUserContext(),
          session_state: {
            collected_info: collectedInfo,
            search_results: recommendedProblems,
            selected_problem: selectedBaseProblem || undefined,
            ...v2SessionState,
          },
        });

        responseMessage = v2Response.message;
        responseCollectedInfo = v2Response.collected_info || {
          topics: [],
          difficulty: null,
          language: null,
          specific_needs: null,
          time_available: null,
        };

        // V2 세션 상태 업데이트
        setV2SessionState({
          stage: v2Response.stage,
          next_stage: v2Response.next_stage,
        });

        // V2 action_data 변환
        actionData = {
          status: v2Response.search_results?.length ? 'found' : undefined,
          problems: v2Response.search_results,
          generated_problem: v2Response.generated_problem,
          action_trigger: v2Response.action_trigger,
        };

        console.log('[V2 Response]', {
          stage: v2Response.stage,
          intent: v2Response.intent_info?.intent,
          collected_info: responseCollectedInfo,
          search_results: v2Response.search_results?.length,
          action_trigger: v2Response.action_trigger,
          generated_problem_data: v2Response.generated_problem_data,
          selected_problem: v2Response.selected_problem,
        });
      } else {
        // V1: 기존 API 사용
        const response = await agentApi.chat({
          message: content,
          conversation_history: conversationHistory,
          user_context: getUserContext(),
          collected_info: collectedInfo,  // 이전 턴에서 수집된 정보 전달 (상태 유지!)
        });

        responseMessage = response.message;
        responseCollectedInfo = response.collected_info;
        actionData = response.action_data as typeof actionData;
      }

      // Update collected info
      setCollectedInfo(responseCollectedInfo);

      // Update conversation history
      setConversationHistory([
        ...newHistory,
        { role: 'assistant', content: responseMessage },
      ]);

      // Create assistant message with chips based on state
      let chips: QuickChip[] | undefined;

      // If action_data has problems from auto-search, use them directly
      if (actionData?.status === 'found' && actionData?.problems?.length) {
        setFlowState('type_selection');
        setRecommendedProblems(actionData.problems);

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips: actionData.problems.slice(0, 4).map((p, i) => ({
            label: `${p.name || p.title} (${p.difficulty})`,
            value: `problem-${i}`,
            category: 'action' as const,
          })),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (actionData?.generated_problem) {
        // CodeGen generated a new problem
        setFlowState('type_selection');
        setRecommendedProblems([actionData.generated_problem]);

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips: [{
            label: `${actionData.generated_problem.title} (${actionData.generated_problem.difficulty})`,
            value: 'problem-0',
            category: 'action' as const,
          }],
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (v2Response?.action_trigger === 'problem_generated' && v2Response?.generated_problem_data) {
        // 문제 유형 선택 후 문제가 생성됨 - 프론트엔드에 표시
        const generatedData = v2Response.generated_problem_data;
        console.log('[PracticeChatPanel] Generated problem data:', generatedData);
        const convertedProblem = convertGeneratedDataToProblem(generatedData);
        console.log('[PracticeChatPanel] Converted problem:', convertedProblem);

        if (convertedProblem.problemType === 'guided') {
          // Guided 모드: 채팅 UI에서 계속 진행
          setGuidedProblem(convertedProblem);
          setGuidedFlowStep(0);
          setGuidedCheckpointIndex(0);

          // 첫 번째 개념 설명과 flow step 시작
          const concepts = convertedProblem.concepts || [];
          const conceptIntro = concepts.length > 0
            ? `먼저 핵심 개념을 알아볼까요?\n\n${concepts.map((c, idx) =>
                typeof c === 'string' ? `${idx + 1}. **${c}**` : `**${(c as {name: string}).name}**: ${(c as {explanation: string}).explanation}`
              ).join('\n')}\n\n---\n\n`
            : '';

          const firstStepContent = typeof convertedProblem.flow?.[0] === 'string'
            ? convertedProblem.flow[0] as string
            : '';

          const assistantMessage: Message = {
            id: `guided-start-${Date.now()}`,
            role: 'assistant',
            content: `${conceptIntro}**Step 1**\n\n${firstStepContent}`,
            timestamp: new Date().toISOString(),
            chips: [
              { label: '이해했어요', value: 'guided-understood', category: 'action' },
              { label: '잘 모르겠어요', value: 'guided-stuck', category: 'action' },
            ],
          };
          setMessages(prev => [...prev, assistantMessage]);
          setFlowState('guided_learning');
        } else {
          // Blank/Puzzle: 연습 화면으로 이동
          const assistantMessage: Message = {
            id: `success-${Date.now()}`,
            role: 'assistant',
            content: responseMessage,
            timestamp: new Date().toISOString(),
            chips: [
              { label: '힌트 보기', value: 'hint', category: 'action' },
              { label: '핵심 개념', value: 'concepts', category: 'action' },
            ],
          };
          setMessages(prev => [...prev, assistantMessage]);

          if (onProblemSelect) {
            onProblemSelect(convertedProblem);
          }
          setFlowState('practicing');
        }
      } else if (actionData?.action_trigger === 'select_problem_type') {
        // User selected a problem, show type selection
        const selectedProblemName = actionData.selected_problem;
        const selectedIndex = actionData.selected_problem_index;

        // Find the selected problem from recommendedProblems
        let selectedProblem: BaseProblemInfo | undefined;
        if (selectedIndex !== undefined && recommendedProblems[selectedIndex - 1]) {
          selectedProblem = recommendedProblems[selectedIndex - 1];
        } else if (selectedProblemName) {
          selectedProblem = recommendedProblems.find(
            p => p.name === selectedProblemName || p.title === selectedProblemName
          );
        }

        if (selectedProblem) {
          setSelectedBaseProblem(selectedProblem);
          showProblemTypeSelection(selectedProblem);
        } else {
          // Fallback - just show the message
          const assistantMessage: Message = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: responseMessage,
            timestamp: new Date().toISOString(),
            chips: [
              { label: '빈칸 채우기', value: 'type-blank', category: 'action' },
              { label: '퍼즐 (코드 정렬)', value: 'type-puzzle', category: 'action' },
              { label: '1대1 대화형', value: 'type-guided', category: 'action' },
            ],
          };
          setMessages(prev => [...prev, assistantMessage]);
          setFlowState('type_selection');
        }
      } else {
        // Normal chat flow
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips,
        };
        setMessages(prev => [...prev, assistantMessage]);

      }

    } catch (error) {
      console.error('Chat error:', error);
      // Fallback to simple response
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
  }, [isLoading, conversationHistory, getUserContext]);

  // Fetch problem recommendations
  const fetchRecommendations = useCallback(async (info: CollectedInfo) => {
    setIsLoading(true);

    try {
      const response = await agentApi.recommend(info, getUserContext());

      if (response.status === 'found' && response.problems.length > 0) {
        const problems = response.problems as unknown as BaseProblemInfo[];
        setRecommendedProblems(problems);

        const recommendMsg: Message = {
          id: `recommend-${Date.now()}`,
          role: 'assistant',
          content: `요청하신 조건에 맞는 문제들을 찾았어요! 아래에서 선택해주세요:`,
          timestamp: new Date().toISOString(),
          chips: problems.slice(0, 4).map((p, i) => ({
            label: `${p.title} (${p.difficulty})`,
            value: `problem-${i}`,
            category: 'action' as const,
          })),
        };
        setMessages(prev => [...prev, recommendMsg]);
      } else {
        // Fallback - need to generate new code
        const fallbackMsg: Message = {
          id: `fallback-${Date.now()}`,
          role: 'assistant',
          content: response.message || '요청하신 조건에 맞는 문제를 찾지 못했어요. 다른 조건으로 다시 시도해주시겠어요?',
          timestamp: new Date().toISOString(),
          chips: [
            { label: 'DP 문제', value: 'dp', category: 'topic' },
            { label: '그래프 문제', value: 'graph', category: 'topic' },
            { label: '쉬운 문제', value: 'easy', category: 'difficulty' },
          ],
        };
        setMessages(prev => [...prev, fallbackMsg]);
        setFlowState('collecting');
      }
    } catch (error) {
      console.error('Recommendation error:', error);
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '문제를 찾는 중 오류가 발생했어요. 다시 시도해주세요.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
      setFlowState('collecting');
    } finally {
      setIsLoading(false);
    }
  }, [getUserContext]);

  // Generate fallback response
  const generateFallbackResponse = (userMessage: string): string => {
    const lower = userMessage.toLowerCase();

    if (lower.includes('힌트') || lower.includes('hint')) {
      return '아래 "힌트" 버튼을 클릭해서 단계별 힌트를 받을 수 있어요!';
    }
    if (lower.includes('어려') || lower.includes('모르')) {
      return '천천히 문제를 다시 읽어보세요. 힌트가 필요하면 말씀해주세요!';
    }

    return '어떤 알고리즘 주제를 연습하고 싶으신가요? (예: DP, 그래프, 정렬 등)';
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {flowState === 'guided_learning' ? (
              <GraduationCap className="h-4 w-4 text-green-500" />
            ) : (
              <Sparkles className="h-4 w-4 text-primary" />
            )}
            <div>
              <h3 className="font-semibold text-sm">
                {flowState === 'guided_learning' ? '1대1 대화형 학습' : 'AI 코딩 튜터'}
              </h3>
              {flowState === 'guided_learning' && guidedProblem ? (
                <p className="text-xs text-muted-foreground mt-0.5">{guidedProblem.title}</p>
              ) : problem ? (
                <p className="text-xs text-muted-foreground mt-0.5">{problem.title}</p>
              ) : (
                <p className="text-xs text-muted-foreground mt-0.5">무엇이든 물어보세요</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* V2 테스트 토글 */}
            <Button
              variant={useV2 ? "default" : "outline"}
              size="sm"
              onClick={() => setUseV2(!useV2)}
              className="text-xs h-6 px-2"
            >
              {useV2 ? 'V2' : 'V1'}
            </Button>
            {flowState === 'guided_learning' && guidedProblem?.flow ? (
              <Badge variant="outline" className="text-xs bg-green-500/10 text-green-600 border-green-500/30">
                Step {guidedFlowStep + 1}/{guidedProblem.flow.length}
              </Badge>
            ) : problem ? (
              <Badge variant="outline" className="text-xs">
                힌트 {hintLevel}/4
              </Badge>
            ) : null}
          </div>
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
              <span className="text-sm">
                {flowState === 'generating' ? '문제 생성 중...' : '생각 중...'}
              </span>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Quick Actions - show when problem is selected OR in guided learning mode */}
      {(problem || flowState === 'guided_learning') && (
        <div className="border-t border-border px-4 py-2">
          <div className="flex gap-2">
            {flowState === 'guided_learning' ? (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1.5 text-xs"
                  onClick={showGuidedFinalCode}
                >
                  <Code className="h-3.5 w-3.5" />
                  코드 미리보기
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1.5 text-xs"
                  onClick={resetToNewProblem}
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  다른 문제
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1.5 text-xs"
                  onClick={handleHintRequestInternal}
                  disabled={hintLevel >= 4 || isLoading}
                >
                  <Lightbulb className="h-3.5 w-3.5" />
                  힌트 ({4 - hintLevel}개 남음)
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
              </>
            )}
          </div>
        </div>
      )}

      <ChatComposer onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
