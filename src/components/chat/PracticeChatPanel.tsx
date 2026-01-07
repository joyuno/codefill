'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatComposer } from './ChatComposer';
import { agentApi } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import type {
  ChatAgentMessage,
  CollectedInfo,
  BaseProblemInfo,
  ChatV2Response,
  GeneratedProblemData,
  GeneratedBlankData,
  GeneratedPuzzleData,
  GeneratedGuidedData,
  SuggestedAction,
} from '@/lib/api/agent';
import type { Message, QuickChip } from '@/lib/types';
import { SuggestedActions } from './SuggestedActions';
import type { ConvertedProblem } from '@/lib/dataTypes';
import { Loader2, Lightbulb, BookOpen, Sparkles, GraduationCap, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PracticeChatPanelProps {
  problem: ConvertedProblem | null;
  onHintRequest?: (level: number, blankId?: string) => void;
  onProblemSelect?: (problem: ConvertedProblem) => void;
  hints?: string[];
  /**
   * Problems 페이지에서 직접 선택한 문제 (정보수집 단계 생략용)
   * 이 값이 있으면 정보수집을 건너뛰고 바로 문제 유형 선택 단계로 시작
   */
  initialBaseProblem?: BaseProblemInfo | null;
  /**
   * 채팅 세션 ID (DB 기반 대화 히스토리 관리용)
   * 백엔드에서 세션을 식별하여 대화 히스토리를 DB에서 로드/저장
   */
  sessionId?: string | null;
  onSessionIdChange?: (sessionId: string) => void;
}

// Session state interface for LangGraph
interface SessionState {
  stage?: string;
  next_stage?: string;
  awaiting_confirmation?: boolean;
  suggested_value?: string | null;
  search_offset?: number;
  [key: string]: unknown;
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
    // _0_, _1_, _2_ 형식을 그대로 유지 (UnifiedPractice에서 _N_ 패턴 매칭)
    const codeSnippet = blankData.code_template;
    return {
      id: blankData.original_id || `generated-${Date.now()}`,
      originalId: blankData.original_id,  // 잔디 클릭 시 문제 정보 표시용
      title: blankData.title,
      description: blankData.description,
      problemType: 'blank',
      difficulty: blankData.difficulty as 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard',
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
      indentation: (b as any).indentation || b.indent || 0,  // API에서 받은 indentation 값 사용
    }));

    return {
      id: puzzleData.original_id || `generated-${Date.now()}`,
      originalId: puzzleData.original_id,  // 잔디 클릭 시 문제 정보 표시용
      title: puzzleData.title,
      description: puzzleData.description,
      problemType: 'puzzle',
      difficulty: puzzleData.difficulty as 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard',
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
      originalId: guidedData.original_id,  // 잔디 클릭 시 문제 정보 표시용
      title: guidedData.title,
      description: guidedData.description,
      problemType: 'guided',
      difficulty: guidedData.difficulty as 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard',
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
    { label: '기초', value: '기초', category: 'topic' },
    { label: 'DP', value: 'DP', category: 'topic' },
    { label: '그래프', value: '그래프', category: 'topic' },
    { label: '정렬', value: '정렬', category: 'topic' },
  ],
};

export function PracticeChatPanel({
  problem,
  onHintRequest,
  onProblemSelect,
  hints = [],
  initialBaseProblem,
  sessionId: propSessionId,
  onSessionIdChange,
}: PracticeChatPanelProps) {
  // 사용자 인증 정보 가져오기 (user_id 포함)
  const { user, profile } = useAuth();

  // 세션 ID 상태 (props에서 전달받거나 응답에서 설정)
  const [sessionId, setSessionId] = useState<string | null>(propSessionId || null);

  // props가 변경되면 상태 업데이트
  useEffect(() => {
    if (propSessionId && propSessionId !== sessionId) {
      setSessionId(propSessionId);
    }
  }, [propSessionId]);

  // initialBaseProblem이 있으면 바로 문제 유형 선택 메시지로 시작
  const [messages, setMessages] = useState<Message[]>(() => {
    if (initialBaseProblem) {
      console.log('[PracticeChatPanel] Initializing with type selection (initialBaseProblem provided)');
      return [{
        id: 'welcome-direct',
        role: 'assistant' as const,
        content: `"${initialBaseProblem.title || initialBaseProblem.name}" 문제를 선택하셨네요!\n\n어떤 형식으로 문제를 풀어볼까요?`,
        timestamp: new Date().toISOString(),
        chips: [
          { label: '빈칸 채우기', value: 'type-blank', category: 'action' as const },
          { label: '퍼즐 (코드 정렬)', value: 'type-puzzle', category: 'action' as const },
          { label: '1대1 대화형', value: 'type-guided', category: 'action' as const },
        ],
      }];
    }
    return [initialWelcomeMessage];
  });
  const [conversationHistory, setConversationHistory] = useState<ChatAgentMessage[]>([]);
  const [collectedInfo, setCollectedInfo] = useState<CollectedInfo>(() => {
    if (initialBaseProblem) {
      return {
        topics: initialBaseProblem.topics || initialBaseProblem.tags || [],
        difficulty: initialBaseProblem.difficulty || null,
        language: null,
        specific_needs: null,
        time_available: null,
      };
    }
    return {
      topics: [],
      difficulty: null,
      language: null,
      specific_needs: null,
      time_available: null,
    };
  });
  const [isLoading, setIsLoading] = useState(false);
  const [hintLevel, setHintLevel] = useState(0);
  const [previousHints, setPreviousHints] = useState<string[]>([]);
  const [recommendedProblems, setRecommendedProblems] = useState<BaseProblemInfo[]>(() =>
    initialBaseProblem ? [initialBaseProblem] : []
  );
  const [selectedBaseProblem, setSelectedBaseProblem] = useState<BaseProblemInfo | null>(
    initialBaseProblem || null
  );
  const [flowState, setFlowState] = useState<'collecting' | 'recommending' | 'type_selection' | 'generating' | 'practicing' | 'guided_learning'>(
    initialBaseProblem ? 'type_selection' : 'collecting'
  );
  const [sessionState, setSessionState] = useState<SessionState>({});  // LangGraph 세션 상태
  const scrollRef = useRef<HTMLDivElement>(null);
  const initialProblemHandledRef = useRef(!!initialBaseProblem);  // initialBaseProblem이 있으면 이미 처리된 것으로 시작

  // Refs to always have latest state (avoid stale closure issues)
  const collectedInfoRef = useRef(collectedInfo);
  const sessionStateRef = useRef(sessionState);
  const recommendedProblemsRef = useRef(recommendedProblems);
  const selectedBaseProblemRef = useRef(selectedBaseProblem);
  const problemRef = useRef(problem);

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

  // Reset chat session when problem becomes null (다음 문제 풀기 클릭 시)
  // 단, initialBaseProblem이 있으면 초기화하지 않음 (Problems 페이지에서 직접 선택한 경우)
  useEffect(() => {
    if (problem === null && !initialBaseProblem) {
      // 채팅 세션 완전 초기화
      setMessages([initialWelcomeMessage]);
      setConversationHistory([]);
      setCollectedInfo({
        topics: [],
        difficulty: null,
        language: null,
        specific_needs: null,
        time_available: null,
      });
      setFlowState('collecting');
      setSessionState({});
      setRecommendedProblems([]);
      setSelectedBaseProblem(null);
      setHintLevel(0);
      setPreviousHints([]);
      setGuidedProblem(null);
      setGuidedFlowStep(0);
      setGuidedCheckpointIndex(0);
      // ref도 초기화 (새 세션에서 다시 initialBaseProblem 처리 가능하도록)
      initialProblemHandledRef.current = false;
    }
  }, [problem, initialBaseProblem]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Note: initialBaseProblem 처리는 useState 초기화에서 수행됨
  // 이 useEffect는 동적으로 initialBaseProblem이 변경되는 경우만 처리 (일반적으로 발생하지 않음)
  useEffect(() => {
    // useState 초기화에서 이미 처리된 경우 스킵
    if (initialProblemHandledRef.current) return;
    if (!initialBaseProblem) return;

    console.log('[PracticeChatPanel] Late initialBaseProblem received, updating state');
    initialProblemHandledRef.current = true;

    setSelectedBaseProblem(initialBaseProblem);
    setRecommendedProblems([initialBaseProblem]);
    setFlowState('type_selection');
    setCollectedInfo({
      topics: initialBaseProblem.topics || initialBaseProblem.tags || [],
      difficulty: initialBaseProblem.difficulty || null,
      language: null,
      specific_needs: null,
      time_available: null,
    });
    setMessages([{
      id: 'welcome-direct',
      role: 'assistant',
      content: `"${initialBaseProblem.title || initialBaseProblem.name}" 문제를 선택하셨네요!\n\n어떤 형식으로 문제를 풀어볼까요?`,
      timestamp: new Date().toISOString(),
      chips: [
        { label: '빈칸 채우기', value: 'type-blank', category: 'action' },
        { label: '퍼즐 (코드 정렬)', value: 'type-puzzle', category: 'action' },
        { label: '1대1 대화형', value: 'type-guided', category: 'action' },
      ],
    }]);
  }, [initialBaseProblem]);

  // Keep refs in sync with state (for use in callbacks)
  useEffect(() => { collectedInfoRef.current = collectedInfo; }, [collectedInfo]);
  useEffect(() => { sessionStateRef.current = sessionState; }, [sessionState]);
  useEffect(() => { recommendedProblemsRef.current = recommendedProblems; }, [recommendedProblems]);
  useEffect(() => { selectedBaseProblemRef.current = selectedBaseProblem; }, [selectedBaseProblem]);
  useEffect(() => { problemRef.current = problem; }, [problem]);

  // Get user context from localStorage (onboarding data) + current search results + auth user
  const getUserContext = useCallback(() => {
    const context: Record<string, unknown> = {};

    // ============================================================
    // 1. 인증된 사용자 ID 추가 (DB 프로필 조회용)
    // ============================================================
    if (user?.id) {
      context.user_id = user.id;
      context.id = user.id;  // 백엔드 호환성
    }

    // ============================================================
    // 2. User profile from localStorage (onboarding data)
    // 백엔드 모델과 키 이름 일치: experience_level, learning_goal, preferred_difficulty 등
    // ============================================================
    if (typeof window !== 'undefined') {
      try {
        const userData = localStorage.getItem('user_profile');
        if (userData) {
          const localProfile = JSON.parse(userData);
          // 백엔드 user_context 키 이름으로 매핑
          context.experience_level = localProfile.level || localProfile.experience_level;        // beginner, elementary, intermediate, advanced
          context.learning_goal = localProfile.goal || localProfile.learning_goal;               // big_tech, mid_startup, skill_up
          context.current_status = localProfile.status || localProfile.current_status;           // student, job_seeker, employed
          context.strong_algorithms = localProfile.strong_algorithms || [];                  // ["DP", "그래프", ...]
          context.preferred_difficulty = localProfile.preferred_difficulty || 'medium';
          context.preferred_language = localProfile.preferred_language || 'python';

          // 레거시 키도 유지 (호환성)
          context.status = localProfile.status;
          context.goal = localProfile.goal;
          context.level = localProfile.level;
          context.desired_job = localProfile.desired_job;
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
        description: problem.description,  // 문제 요약에 필요
        question: problem.description,     // 백엔드 호환성
        difficulty: problem.difficulty,
        topics: problem.topics,
        keyConcepts: problem.keyConcepts,
        problem_type: problem.problemType,
      };
    }

    return context;
  }, [user, recommendedProblems, problem]);

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
        { label: '기초', value: '기초', category: 'topic' },
        { label: 'DP', value: 'DP', category: 'topic' },
        { label: '그래프', value: '그래프', category: 'topic' },
        { label: '정렬', value: '정렬', category: 'topic' },
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
    } else if (chip.value === 'summarize') {
      // 문제 요약 (로컬 처리)
      showProblemSummary();
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
    } else if (chip.value === 'yes') {
      // 네/아니오 칩: "네" - 추천값 수락
      // handleSendMessage가 메시지 추가 + API 호출을 모두 처리함
      handleSendMessage('네, 그걸로 할게요');
    } else if (chip.value === 'no') {
      // 네/아니오 칩: "아니오" - 다른 추천 요청
      handleSendMessage('아니오, 다른 거로 할게요');
    } else if (chip.value === 'more-search') {
      // 더 찾아보기: 다음 5개 문제 검색
      handleSendMessage('비슷한 문제 더 찾아줘');
    } else if (chip.value === 'generate-new') {
      // 새 문제 생성: CodeGen으로 유사 문제 생성
      handleSendMessage('새로운 유사 문제를 생성해줘');
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

      // 디버그: selectedBaseProblem 데이터 확인
      console.log('[handleProblemTypeSelect] selectedBaseProblem data:', {
        id: selectedBaseProblem.id,
        name: selectedBaseProblem.name,
        tags: selectedBaseProblem.tags,
        topics: selectedBaseProblem.topics,
        input_output: (selectedBaseProblem as any).input_output,
      });

      // input_output을 testCases로 변환
      const inputOutput = (selectedBaseProblem as any).input_output;
      const testCases = inputOutput?.inputs && inputOutput?.outputs
        ? inputOutput.inputs.slice(0, inputOutput.outputs.length).map((input: string, idx: number) => ({
            input,
            expected: inputOutput.outputs[idx],
            isHidden: false,
          }))
        : undefined;

      console.log('[handleProblemTypeSelect] Converted testCases:', testCases);

      if (type === 'blank') {
        const result = await agentApi.generateBlank(request);
        // 새 형식: original_id, language, code_template, answers[]
        // _0_, _1_, _2_ 형식을 그대로 유지 (UnifiedPractice에서 _N_ 패턴 매칭)
        const codeSnippet = result.code_template;
        generatedProblem = {
          id: result.original_id || `generated-${Date.now()}`,
          originalId: result.original_id,  // 잔디 클릭 시 문제 정보 표시용
          baseProblemId: selectedBaseProblem.id,  // base_problems UUID
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'blank',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.tags || selectedBaseProblem.topics || [],  // tags 우선
          framework: targetLanguage,
          codeTemplate: result.code_template,
          codeSnippet: codeSnippet,  // UnifiedPractice에서 사용
          blanks: result.answers.map((answer, idx) => ({
            id: `blank-${idx}`,
            position: idx,
            answer: answer,
            placeholder: `_${idx}_`,
          })),
          testCases: testCases || [],  // undefined 대신 빈 배열
        };
      } else if (type === 'puzzle') {
        const result = await agentApi.generatePuzzle(request);
        // 새 형식: original_id, language, fixed_start?, fixed_end?, blocks[]
        const sortedBlocks = [...result.blocks].sort((a, b) => a.id - b.id);
        const convertedBlocks = sortedBlocks.map(b => ({
          id: String(b.id),
          code: b.code,
          correctOrder: b.id,
          indentation: b.indentation || b.indent || 0,  // API에서 받은 indentation 값 사용
        }));
        generatedProblem = {
          id: result.original_id || `generated-${Date.now()}`,
          originalId: result.original_id,  // 잔디 클릭 시 문제 정보 표시용
          baseProblemId: selectedBaseProblem.id,  // base_problems UUID
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'puzzle',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.tags || selectedBaseProblem.topics || [],  // tags 우선
          framework: targetLanguage,
          puzzleBlocks: convertedBlocks,  // UnifiedPractice에서 사용
          blocks: convertedBlocks,
          correctOrder: sortedBlocks.map(b => String(b.id)),
          fixedStart: result.fixed_start,
          fixedEnd: result.fixed_end,
          testCases: testCases || [],  // undefined 대신 빈 배열
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
          originalId: result.original_id,  // 잔디 클릭 시 문제 정보 표시용
          baseProblemId: selectedBaseProblem.id,  // base_problems UUID
          title: selectedBaseProblem.title || selectedBaseProblem.name || 'Problem',
          description: selectedBaseProblem.description || selectedBaseProblem.question || '',
          problemType: 'guided',
          difficulty: selectedBaseProblem.difficulty,
          topics: selectedBaseProblem.topics || selectedBaseProblem.tags || [],
          keyConcepts: selectedBaseProblem.tags || selectedBaseProblem.topics || [],  // tags 우선
          framework: targetLanguage,
          concepts: result.concepts,  // string[]
          flow: result.flow,          // string[]
          checkpoints: result.checkpoints,  // string[]
          finalCodeReveal: extractedCode,  // 원본 코드를 최종 코드로 사용
          testCases: testCases || [],  // undefined 대신 빈 배열
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
      // 빈칸 유형에서는 힌트 보기 칩 제거 (각 빈칸 옆 힌트로 대체)
      const successChips = type === 'blank'
        ? [
            { label: '핵심 개념', value: 'concepts', category: 'action' as const },
            { label: '문제 요약', value: 'summarize', category: 'action' as const },
          ]
        : [
            { label: '힌트 보기', value: 'hint', category: 'action' as const },
            { label: '핵심 개념', value: 'concepts', category: 'action' as const },
            { label: '문제 요약', value: 'summarize', category: 'action' as const },
          ];

      setMessages(prev => {
        const filtered = prev.filter(m => !m.id.startsWith('loading-'));
        return [...filtered, {
          id: `success-${Date.now()}`,
          role: 'assistant' as const,
          content: type === 'blank'
            ? `문제가 준비되었어요! 왼쪽 화면에서 문제를 풀어보세요.\n\n빈칸 옆 ? 버튼을 눌러 힌트를 볼 수 있어요!`
            : `문제가 준비되었어요! 왼쪽 화면에서 문제를 풀어보세요.\n\n막히면 언제든 힌트를 요청해주세요!`,
          timestamp: new Date().toISOString(),
          chips: successChips,
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

  // Request AI hint - uses ref to avoid stale closure
  const handleHintRequestInternal = useCallback(async () => {
    const currentProblem = problemRef.current;
    if (!currentProblem) {
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
      // 문제 유형 결정
      const problemType = (currentProblem.problemType || 'blank') as 'blank' | 'puzzle' | 'guided';

      // 문제 유형별 추가 정보 구성
      const problemInfo: Record<string, unknown> = {
        title: currentProblem.title,
        description: currentProblem.description,
        topics: currentProblem.topics,
        key_concepts: currentProblem.keyConcepts,
        language: currentProblem.framework || 'python',
      };

      // Blank 문제: code_template, answers 정보 추가
      if (problemType === 'blank') {
        problemInfo.code_template = currentProblem.codeTemplate || currentProblem.codeSnippet;
        problemInfo.answers = currentProblem.blanks?.map(b => b.answer) || [];
        problemInfo.blank_count = currentProblem.blanks?.length || 0;
      }

      // Puzzle 문제: blocks, correct_order 정보 추가
      if (problemType === 'puzzle') {
        problemInfo.blocks = currentProblem.puzzleBlocks || currentProblem.blocks;
        problemInfo.correct_order = currentProblem.correctOrder;
        problemInfo.fixed_start = currentProblem.fixedStart;
        problemInfo.fixed_end = currentProblem.fixedEnd;
      }

      // Guided 문제: flow, checkpoints 정보 추가
      if (problemType === 'guided') {
        problemInfo.concepts = currentProblem.concepts;
        problemInfo.flow = currentProblem.flow;
        problemInfo.checkpoints = currentProblem.checkpoints;
        problemInfo.final_code = currentProblem.finalCodeReveal;
      }

      const response = await agentApi.getHint({
        problem_id: currentProblem.id,
        problem_type: problemType,
        problem_info: problemInfo,
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
        `힌트 1: 이 문제는 ${currentProblem.topics?.[0] || '알고리즘'}에 관한 문제입니다.`,
        `힌트 2: ${currentProblem.keyConcepts?.slice(0, 2).join(', ') || '핵심 개념'}를 활용해보세요.`,
        `힌트 3: ${currentProblem.keyConcepts?.join(', ') || '개념들'}를 순서대로 적용해보세요.`,
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
  }, [hintLevel, hints, previousHints, onHintRequest]);

  // Show key concepts - uses ref to avoid stale closure
  const showKeyConcepts = useCallback(() => {
    const currentProblem = problemRef.current;
    if (!currentProblem) {
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
      content: `이 문제의 핵심 개념:\n\n${currentProblem.keyConcepts?.map((c, i) => `${i + 1}. ${c}`).join('\n') || '핵심 개념이 없습니다.'}\n\n관련 토픽: ${currentProblem.topics?.join(', ') || '없음'}`,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage, conceptsMessage]);
  }, []);

  // Show problem summary (문제 요약) - 백엔드 LLM을 통해 한국어 요약 생성
  const showProblemSummary = useCallback(async () => {
    const currentProblem = problemRef.current;
    if (!currentProblem) {
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
      id: `user-summary-${Date.now()}`,
      role: 'user',
      content: '이 문제를 요약해줘',
      timestamp: new Date().toISOString(),
    };

    const loadingMessage: Message = {
      id: `loading-summary-${Date.now()}`,
      role: 'assistant',
      content: '문제를 요약하고 있어요...',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      // 백엔드에서 문제 요약 생성 (solving graph의 summarize_problem 노드 사용)
      const response = await agentApi.chatMain({
        message: '이 문제를 요약해줘',
        conversation_history: [],
        user_context: {
          current_problem: {
            id: currentProblem.id,
            title: currentProblem.title,
            name: currentProblem.title,
            description: currentProblem.description,
            question: currentProblem.description,
            difficulty: currentProblem.difficulty,
            topics: currentProblem.topics,
            keyConcepts: currentProblem.keyConcepts,
            problem_type: currentProblem.problemType,
          },
        },
        session_state: {
          stage: 'practicing',
        },
      });

      // 로딩 메시지 제거하고 요약 결과 표시
      setMessages(prev => {
        const filtered = prev.filter(m => !m.id.startsWith('loading-summary-'));
        return [...filtered, {
          id: `summary-${Date.now()}`,
          role: 'assistant' as const,
          content: response.message,
          timestamp: new Date().toISOString(),
          chips: [
            { label: '힌트 보기', value: 'hint', category: 'action' },
            { label: '핵심 개념', value: 'concepts', category: 'action' },
          ],
        }];
      });

    } catch (error) {
      console.error('Summary generation error:', error);
      // 오류 시 간단한 로컬 요약으로 폴백
      const problemTypeLabel = PROBLEM_TYPE_LABELS[currentProblem.problemType || 'blank'] || '코딩 문제';
      const difficultyLabel = { easy: '쉬움', medium: '보통', hard: '어려움' }[currentProblem.difficulty] || currentProblem.difficulty;

      setMessages(prev => {
        const filtered = prev.filter(m => !m.id.startsWith('loading-summary-'));
        return [...filtered, {
          id: `summary-fallback-${Date.now()}`,
          role: 'assistant' as const,
          content: `## 📋 문제 요약\n\n**${currentProblem.title}** (${problemTypeLabel} | ${difficultyLabel})\n\n주제: ${currentProblem.topics?.join(', ') || '알고리즘'}\n핵심 개념: ${currentProblem.keyConcepts?.join(', ') || ''}`,
          timestamp: new Date().toISOString(),
          chips: [
            { label: '힌트 보기', value: 'hint', category: 'action' },
          ],
        }];
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

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
      // 디버깅: 요청 전 상태 확인 (ref에서 최신값 읽기)
      const currentCollectedInfo = collectedInfoRef.current;
      const currentSessionState = sessionStateRef.current;
      const currentProblems = recommendedProblemsRef.current;
      const currentSelectedProblem = selectedBaseProblemRef.current;

      console.log('[Chat Request]', {
        message: content,
        collectedInfo_before_request: currentCollectedInfo,
        sessionState: currentSessionState,
      });

      // LangGraph API 호출 (refs 사용으로 stale closure 방지)
      // Note: session_id가 있으면 백엔드가 DB에서 대화 히스토리를 로드
      // conversation_history는 fallback용 (비로그인 또는 세션 에러 시)
      const chatResponse = await agentApi.chatMain({
        message: content,
        conversation_history: conversationHistory,
        user_context: getUserContext(),
        session_state: {
          collected_info: currentCollectedInfo,
          search_results: currentProblems,
          selected_problem: currentSelectedProblem || undefined,
          // 정보 수집 단계 상태 (네/아니오 응답용)
          awaiting_confirmation: currentSessionState.awaiting_confirmation || false,
          suggested_value: currentSessionState.suggested_value || null,
          ...currentSessionState,
        },
        // DB 기반 세션 관리용 session_id
        session_id: sessionId || undefined,
      });

      // 백엔드에서 반환한 session_id 저장 (새 세션이 생성된 경우)
      if (chatResponse.session_id && chatResponse.session_id !== sessionId) {
        setSessionId(chatResponse.session_id);
        onSessionIdChange?.(chatResponse.session_id);
        console.log('[Chat] Session ID updated:', chatResponse.session_id);
      }

      const responseMessage = chatResponse.message;
      const responseCollectedInfo = chatResponse.collected_info || {
        topics: [],
        difficulty: null,
        language: null,
        specific_needs: null,
        time_available: null,
      };

      // 세션 상태 업데이트 (awaiting_confirmation, suggested_value 포함)
      setSessionState({
        stage: chatResponse.stage,
        next_stage: chatResponse.next_stage,
        awaiting_confirmation: chatResponse.awaiting_confirmation || false,
        suggested_value: chatResponse.suggested_value || null,
      });

      // action_data 변환
      const backendActionData = chatResponse.action_data as Record<string, unknown> | undefined;
      const actionData = {
        status: chatResponse.search_results?.length ? 'found' : undefined,
        problems: chatResponse.search_results,
        generated_problem: chatResponse.generated_problem,
        action_trigger: chatResponse.action_trigger,
        // 정보 수집 단계 confirmation 정보
        awaiting_confirmation: chatResponse.awaiting_confirmation,
        suggested_value: chatResponse.suggested_value,
        action_data: backendActionData,  // 백엔드에서 전달하는 action_data
        // search 관련 데이터
        search_offset: (backendActionData?.search_offset as number) || 0,
        has_more: backendActionData?.has_more as boolean | undefined,
        is_fallback: backendActionData?.is_fallback as boolean | undefined,
        // 문제 선택 관련 데이터
        selected_problem: backendActionData?.selected_problem as string | undefined,
        selected_problem_index: backendActionData?.selected_problem_index as number | undefined,
      };

      console.log('[Chat Response]', {
        stage: chatResponse.stage,
        intent: chatResponse.intent_info?.intent,
        collected_info: responseCollectedInfo,
        search_results: chatResponse.search_results?.length,
        action_trigger: chatResponse.action_trigger,
        generated_problem_data: chatResponse.generated_problem_data,
        selected_problem: chatResponse.selected_problem,
      });

      // Update collected info
      setCollectedInfo(responseCollectedInfo);

      // Update conversation history
      setConversationHistory([
        ...newHistory,
        { role: 'assistant', content: responseMessage },
      ]);

      // Create assistant message with chips based on state
      let chips: QuickChip[] | undefined;

      // "새 문제 생성" 버튼: generated_problem 우선 처리 (search_results보다 먼저!)
      if (actionData?.action_trigger === 'problem_generated' && actionData?.generated_problem) {
        // CodeGen generated a new problem
        setFlowState('type_selection');
        setRecommendedProblems([actionData.generated_problem]);

        // Fallback 안내 메시지 (is_fallback이 true일 때)
        const isFallback = (actionData as any).is_fallback === true;
        const fallbackNotice = isFallback
          ? '🔍 DB에서 조건에 맞는 문제를 찾지 못해서 새로운 문제를 생성했어요!\n\n'
          : '';

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: `${fallbackNotice}${responseMessage}`,
          timestamp: new Date().toISOString(),
          chips: [{
            label: `${actionData.generated_problem.title || actionData.generated_problem.name} (${actionData.generated_problem.difficulty})`,
            value: 'problem-0',
            category: 'action' as const,
          }],
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (actionData?.status === 'found' && actionData?.problems?.length) {
        // 디버그: 백엔드에서 받은 문제 데이터 확인
        console.log('[processAgentResponse] Received problems from backend:',
          actionData.problems.map((p: any) => ({
            name: p.name,
            tags: p.tags,
            topics: p.topics,
            input_output: p.input_output,
          }))
        );
        setFlowState('type_selection');
        setRecommendedProblems(actionData.problems);

        // search_offset을 세션 상태에 저장
        const currentOffset = actionData.search_offset || 0;
        setSessionState(prev => ({
          ...prev,
          search_offset: currentOffset,
        }));

        // 문제 칩 5개 + 추가 옵션 칩
        const problemChips = actionData.problems.slice(0, 5).map((p, i) => ({
          label: `${p.name || p.title} (${p.difficulty})`,
          value: `problem-${i}`,
          category: 'action' as const,
        }));

        // 추가 옵션 칩들 (더 찾아보기는 has_more가 true일 때만)
        const additionalChips = [];
        if (actionData.has_more !== false) {
          additionalChips.push({ label: '🔍 더 찾아보기', value: 'more-search', category: 'action' as const });
        }
        additionalChips.push({ label: '✨ 새 문제 생성', value: 'generate-new', category: 'action' as const });

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips: [...problemChips, ...additionalChips],
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (actionData?.generated_problem) {
        // CodeGen generated a new problem (fallback from RAG search)
        setFlowState('type_selection');
        setRecommendedProblems([actionData.generated_problem]);

        // Fallback 안내 메시지 (is_fallback이 true일 때)
        const isFallback = actionData.is_fallback === true;
        const fallbackNotice = isFallback
          ? '🔍 DB에서 조건에 맞는 문제를 찾지 못해서 새로운 문제를 생성했어요!\n\n'
          : '';

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: `${fallbackNotice}${responseMessage}`,
          timestamp: new Date().toISOString(),
          chips: [{
            label: `${actionData.generated_problem.title} (${actionData.generated_problem.difficulty})`,
            value: 'problem-0',
            category: 'action' as const,
          }],
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (chatResponse?.action_trigger === 'problem_generated' && chatResponse?.generated_problem_data) {
        // 문제 유형 선택 후 문제가 생성됨 - 프론트엔드에 표시
        const generatedData = chatResponse.generated_problem_data;
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
              { label: '문제 요약', value: 'summarize', category: 'action' },
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

        // Find the selected problem from recommendedProblems (use ref for latest)
        let selectedProblem: BaseProblemInfo | undefined;
        if (selectedIndex !== undefined && currentProblems[selectedIndex - 1]) {
          selectedProblem = currentProblems[selectedIndex - 1];
        } else if (selectedProblemName) {
          selectedProblem = currentProblems.find(
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
      } else if (actionData.awaiting_confirmation && actionData.suggested_value) {
        // 정보 수집 단계: LLM 추천 + 네/아니오 칩
        const confirmationChips: QuickChip[] = [
          { label: '네', value: 'yes', category: 'action' as const },
          { label: '아니오, 다른 거', value: 'no', category: 'action' as const },
        ];

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips: confirmationChips,
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (actionData.action_data?.type === 'selection' && actionData.action_data?.chips) {
        // 정보 수집 단계: 빠른 선택용 칩 (주제/난이도/언어)
        const chipsArray = actionData.action_data.chips as Array<{ label: string; value: string; category: string }>;
        const selectionChips: QuickChip[] = chipsArray.map((chip) => ({
          label: chip.label,
          value: chip.value,
          category: chip.category as 'topic' | 'difficulty' | 'action',
        }));

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips: selectionChips,
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Normal chat flow
        // 🚀 Agentic 동적 선택지 처리
        const suggestedActions = chatResponse.suggested_actions ||
          (backendActionData?.suggested_actions as SuggestedAction[] | undefined);

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseMessage,
          timestamp: new Date().toISOString(),
          chips,
          suggestedActions,  // 🚀 동적 선택지 추가
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
  }, [isLoading, conversationHistory, getUserContext]);  // refs don't need to be in deps (stable references)

  // 🚀 Handle suggested action click (Agentic 동적 선택지)
  const handleSuggestedActionClick = useCallback((action: SuggestedAction) => {
    // suggested action을 메시지로 전송 (label을 그대로 사용)
    handleSendMessage(action.label);
  }, [handleSendMessage]);

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
            {flowState === 'guided_learning' && guidedProblem?.flow ? (
              <Badge variant="outline" className="text-xs bg-green-500/10 text-green-600 border-green-500/30">
                Step {guidedFlowStep + 1}/{guidedProblem.flow.length}
              </Badge>
            ) : problem && problem.problemType !== 'blank' ? (
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
              onSuggestedActionClick={handleSuggestedActionClick}
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
                {/* 빈칸 유형에서는 힌트 버튼 숨김 (각 빈칸 옆 힌트로 대체) */}
                {problem?.problemType !== 'blank' && (
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
                )}
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
