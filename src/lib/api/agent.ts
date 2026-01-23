/**
 * Agent API Functions
 * LLM-powered agent endpoints for chat, problem generation, and hints
 */

import { api } from './client';

// ============================================================
// Custom Errors
// ============================================================

export class InsufficientCreditsError extends Error {
  public remainingCredits: number;

  constructor(message: string, remainingCredits: number = 0) {
    super(message);
    this.name = 'InsufficientCreditsError';
    this.remainingCredits = remainingCredits;
  }
}

// ============================================================
// Types
// ============================================================

// Chat Agent
export interface ChatAgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CollectedInfo {
  topics: string[];
  difficulty: string | null;
  language: string | null;
  specific_needs: string | null;
  time_available: number | null;
}

export interface ChatAgentRequest {
  message: string;
  conversation_history: ChatAgentMessage[];
  user_context?: Record<string, unknown>;
  collected_info?: CollectedInfo;  // 이전 턴에서 수집된 정보 (상태 유지용)
}

export interface ChatAgentResponse {
  message: string;
  collected_info: CollectedInfo;
  is_complete: boolean;
  search_query: string | null;
  intent_info?: {
    intent: string;
    confidence: number;
    method: string;
    requires_context: string | null;
    next_action: string | null;
  };
  action_data?: {
    status?: string;
    problems?: BaseProblemInfo[];
    generated_problem?: BaseProblemInfo;
    action_trigger?: string;
    next_action?: string;
    selected_problem?: string;
    selected_problem_index?: number;
  };
}

// Problem Generation
export interface BaseProblemInfo {
  id?: string;
  original_id?: string;  // 원본 문제 ID
  name?: string;  // DB에서 오는 문제 이름
  title?: string;  // 생성된 문제 제목
  description?: string;
  question?: string;  // DB에서 오는 문제 설명
  code?: string;
  solutions?: { language: string; code: string }[];  // DB 문제의 솔루션
  language?: 'python' | 'java' | 'cpp';
  difficulty: 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard';
  topics?: string[];
  tags?: string[];  // DB 문제의 태그
  input_output?: {  // 입출력 예제
    inputs: string[];
    outputs: string[];
  };
  time_complexity?: string;
  space_complexity?: string;
}

export interface ProblemGenerationRequest {
  base_problem: BaseProblemInfo;
  problem_type: 'blank' | 'puzzle' | 'guided';
  user_level: 'beginner' | 'elementary' | 'intermediate' | 'advanced';
  language: 'python' | 'java' | 'cpp';
}

// Blank Problem Response (matches data/examples/problems_blank.json)
export interface BlankProblemResponse {
  original_id: string;
  language: string;
  code_template: string;  // _0_, _1_, _2_ 형식의 빈칸
  answers: string[];      // 순서대로 정답 배열
}

// Puzzle Problem Response (matches data/examples/problems_puzzle.json)
export interface PuzzleBlock {
  id: number;   // 정답 순서 (1, 2, 3, ...)
  code: string;
  indent?: number;  // 들여쓰기 레벨 (레거시)
  indentation?: number;  // 들여쓰기 레벨 (새 형식, 0: 루트, 1: 함수내부, 2: 중첩블록)
}

export interface PuzzleProblemResponse {
  original_id: string;
  language: string;
  fixed_start?: string;  // 고정된 시작 코드 (선택)
  fixed_end?: string;    // 고정된 끝 코드 (선택)
  blocks: PuzzleBlock[]; // id 순서가 정답
}

// 변수 가이드 항목
export interface VariableGuide {
  name: string;          // 변수명
  role: string;          // 역할
  type: string;          // 자료형
  initial_value: string; // 초기값
  why_needed: string;    // 왜 필요한지
}

// 변수 가이드 전체
export interface VariablesGuideResponse {
  total_count: number;
  variables: VariableGuide[];
}

// Guided Problem Response (새 스키마)
export interface GuidedProblemResponse {
  // 문제 식별
  base_problem_id?: string;  // UUID
  language: string;

  // 초기 가이드 (LLM 생성)
  concept_explanation: string;         // 핵심 알고리즘/자료구조 설명
  variables_guide: VariablesGuideResponse;  // 변수 정의
  approach_guide: string;              // 접근법 가이드
  starter_code: string;                // 맛보기 코드 (함수 정의 제외 앞 2줄)

  // DB 저장 후
  guided_problem_id?: string;          // problems_guided.id

  // 레거시 호환 (점진적 마이그레이션용)
  original_id?: string;
  concepts?: string[];
  flow?: string[];
  checkpoints?: string[];
}

// Guided Starter Code (에디터 기반 1대1 대화형)
export interface GuidedStarterRequest {
  original_id: string;
  language: 'python' | 'java' | 'cpp';
}

export interface GuidedStarterResponse {
  original_id: string;
  language: string;
  starter_code: string;      // 에디터에 미리 표시할 코드
  has_starter_code: boolean; // DB에 starter_code가 있었는지 여부
}

// Code Generation
export interface CodeGenerationRequest {
  user_request: Record<string, unknown>;
  similar_problems: Record<string, unknown>[];
  user_status?: string;
  user_goal?: string;
  user_level: 'beginner' | 'elementary' | 'intermediate' | 'advanced';
  strong_algorithms: string[];
}

// Code Generation Stream Request (for PracticeChatPanel)
export interface CodeGenerationStreamRequest {
  collectedInfo: CollectedInfo;
  similarProblems: BaseProblemInfo[];
  userContext?: Record<string, unknown>;
}

export interface CodeGenerationResponse {
  title: string;
  title_en: string;
  description: string;
  code: Record<string, string>;
  input_format: string;
  output_format: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  constraints: string[];
  difficulty: string;
  topics: string[];
  time_complexity: string;
  space_complexity: string;
  key_concepts: string[];
  common_mistakes: string[];
  hints_for_problem_gen: Record<string, string[]>;
}

// Hint Agent
export interface HintAgentRequest {
  problem_id: string;
  base_problem_id?: string;  // base_problems 테이블의 UUID
  problem_type: 'blank' | 'puzzle' | 'guided';  // 문제 유형
  problem_info: Record<string, unknown>;
  user_code?: string;  // guided: 사용자가 작성한 코드
  user_answers?: Record<string, string>;  // blank: 현재 입력한 답들 {"0": "len", "1": ""}
  current_blank_index?: number;  // blank: 현재 질문하는 빈칸 번호 (0부터)
  previous_hints?: string[];  // guided: 이전 힌트 (힌트 횟수 계산용)
  user_level: 'beginner' | 'elementary' | 'intermediate' | 'advanced';
}

export interface RelatedConcept {
  name: string;
  brief: string;
  doc_reference?: string;
}

// Blank 문제 전용 힌트 포커스
export interface BlankFocus {
  blank_index: number;
  surrounding_code?: string;
  expected_role?: string;
}

export interface HintAgentResponse {
  hint_content: string;
  hint_type?: string;  // answer, position, code_line, complete, exhausted 등
  questions?: string[];
  encouragement?: string;
  next_hint_preview?: string;
  code_snippet?: string;
  // Blank 문제 전용 필드
  blank_focus?: BlankFocus;
  // 레거시 호환 (optional)
  hint_level?: number;
  related_concept?: RelatedConcept;
  common_mistake_check?: string;
  wrong_answer_feedback?: string;
}

// RAG Search
export interface RAGSearchRequest {
  query: string;
  topics: string[];
  difficulty?: 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard';
  language?: 'python' | 'java' | 'cpp';
  limit: number;
}

export interface RAGSearchResult {
  id: string;
  title: string;
  description: string;
  similarity_score: number;
  difficulty: string;
  topics: string[];
}

export interface RAGSearchResponse {
  results: RAGSearchResult[];
  query_embedding_used: boolean;
  fallback_to_code_gen: boolean;
}

// Recommend
export interface RecommendResponse {
  status: 'found' | 'fallback';
  problems: Record<string, unknown>[];
  fallback_used: boolean;
  message?: string;
}

// Feedback (문제 풀이 완료 후 피드백)
export interface FeedbackProblemInfo {
  title?: string;
  difficulty?: string;
  topics: string[];
}

export interface FeedbackRequest {
  user_id: string;
  problem_id: string;
  problem_type: 'blank' | 'puzzle' | 'guided';
  is_correct: boolean;
  solve_time_seconds: number;
  hints_used: number;
  xp_earned: number;
  attempt_count?: number;
  problem_info?: FeedbackProblemInfo;
}

export interface FeedbackSummary {
  title: string;
  highlight: string;
}

export interface PerformanceAnalysis {
  time_feedback: string;
  hint_feedback: string;
  attempt_feedback: string;
}

export interface TimeComparison {
  user_time: number;
  avg_time: number;
  percentile: string;
}

export interface FeedbackVisualization {
  efficiency_score: number;
  speed_score: number;
  understanding_score: number;
  time_comparison?: TimeComparison;
}

export interface NextSteps {
  recommendation: string;
  similar_problems?: string;
}

export interface FeedbackResponse {
  grade: 'perfect' | 'excellent' | 'good' | 'keep_going' | 'learning';
  grade_emoji: string;
  grade_message: string;
  summary: FeedbackSummary;
  performance_analysis: PerformanceAnalysis;
  learning_points: string[];
  improvements: string[];
  visualization: FeedbackVisualization;
  next_steps: NextSteps;
  encouragement: string;
}

// ============================================================
// Intent-Based Chat Types
// ============================================================

export interface SessionContext {
  last_solved_problem: {
    id: string;
    name: string;
    code: string;
    language: string;
    difficulty?: string;
    topics?: string[];
    solvedAt: string;
  } | null;
  current_problem: {
    id: string;
    name: string;
    description?: string;
    difficulty?: string;
    topics?: string[];
    startedAt: string;
  } | null;
  last_suggestion: string | null;
  recent_problems: Array<{
    id: string;
    name: string;
    code: string;
    language: string;
    solvedAt: string;
  }>;
}

export interface IntentChatRequest {
  message: string;
  conversation_history: ChatAgentMessage[];
  user_context?: Record<string, unknown>;
  session_context?: SessionContext;
}

export interface IntentInfo {
  intent: string;
  confidence: number;
  method: 'embedding' | 'llm' | 'rule' | 'fallback' | 'llm_verified';
  requires_context?: 'code' | 'problem' | 'previous_suggestion' | null;
  next_action?: string | null;
}

export interface IntentChatResponse {
  message: string;
  intent_info: IntentInfo;
  collected_info?: CollectedInfo;
  is_complete: boolean;
  search_query?: string | null;
  action_data?: Record<string, unknown> | null;
}

// ============================================================
// Chat V2 Types (3-Stage LangGraph)
// ============================================================

export interface ChatV2Request {
  message: string;
  conversation_history: ChatAgentMessage[];
  user_context?: Record<string, unknown>;
  session_state?: {
    collected_info?: CollectedInfo;
    search_results?: BaseProblemInfo[];
    selected_problem?: BaseProblemInfo;
    stage?: string;
    // 정보 수집 단계 상태 (네/아니오 응답용)
    awaiting_confirmation?: boolean;
    suggested_value?: string | null;
    [key: string]: unknown;  // Allow additional properties
  };
  // 세션 ID (DB 기반 히스토리 관리용)
  session_id?: string;
}

// 문제 유형별 생성 결과
export interface GeneratedBlankData {
  problem_type: 'blank';
  original_id: string;
  language: string;
  code_template: string;
  answers: string[];
  title: string;
  description: string;
  difficulty: string;
  topics: string[];
  input_output?: {
    inputs: string[];
    outputs: string[];
  };
}

export interface GeneratedPuzzleData {
  problem_type: 'puzzle';
  original_id: string;
  language: string;
  fixed_start?: string;
  fixed_end?: string;
  blocks: Array<{ id: number; code: string; indent?: number; indentation?: number }>;
  title: string;
  description: string;
  difficulty: string;
  topics: string[];
  input_output?: {
    inputs: string[];
    outputs: string[];
  };
}

export interface GeneratedGuidedData {
  problem_type: 'guided';
  original_id?: string;
  language: string;

  // 새 스키마 필드
  base_problem_id?: string;
  guided_problem_id?: string;
  concept_explanation: string;        // 개념 설명
  variables_guide: VariablesGuideResponse;  // 변수 가이드
  approach_guide: string;             // 접근법 가이드
  starter_code: string;               // 맛보기 코드

  // 레거시 호환
  concepts?: string[];
  flow?: string[];
  checkpoints?: string[];
  final_code?: string;

  // 공통 필드
  title?: string;
  description?: string;
  difficulty?: string;
  topics?: string[];
  input_output?: {
    inputs: string[];
    outputs: string[];
  };
}

export type GeneratedProblemData = GeneratedBlankData | GeneratedPuzzleData | GeneratedGuidedData;

/**
 * 🚀 Agentic 동적 선택지
 * LLM이 생성한 개인화된 추천 버튼
 */
export interface SuggestedAction {
  label: string;        // 버튼 텍스트 (예: "DP (추천)")
  value: string;        // 선택 시 전송할 값 (예: "dp")
  description?: string; // 추가 설명 (예: "연습 필요")
  recommended?: boolean; // 추천 여부 (하이라이트 표시)
}

export interface ChatV2Response {
  stage: string;  // intent, discovery, solving, problem_generation
  message: string;
  intent_info?: IntentInfo;
  collected_info?: CollectedInfo;
  search_results?: BaseProblemInfo[];
  selected_problem?: BaseProblemInfo;
  generated_problem?: BaseProblemInfo;
  // 문제 유형별 생성 결과 (blank/puzzle/guided)
  generated_problem_data?: GeneratedProblemData;
  action_trigger?: string;
  action_data?: Record<string, unknown>;
  next_stage?: string;
  is_complete: boolean;
  hint_level?: number;
  is_correct?: boolean;
  // 정보 수집 단계: 네/아니오 확인 상태
  awaiting_confirmation?: boolean;
  suggested_value?: string;
  // 🚀 Agentic 동적 선택지 (LLM 기반 개인화 추천)
  suggested_actions?: SuggestedAction[];
  // 세션 ID (DB 기반 히스토리 관리용)
  session_id?: string;
}

// ============================================================
// API Client
// ============================================================

export const agentApi = {
  /**
   * Chat Agent - Information Collection
   */
  async chat(request: ChatAgentRequest): Promise<ChatAgentResponse> {
    const response = await api.post<ChatAgentResponse>('/agent/chat', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Intent-Based Chat Agent
   * 의도 분류 + 컨텍스트 인식 채팅
   */
  async intentChat(request: IntentChatRequest): Promise<IntentChatResponse> {
    const response = await api.post<IntentChatResponse>('/agent/chat/intent', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Chat Agent - 정식 LangGraph 기반 채팅
   * 3단계 그래프: Intent → Discovery → Solving
   * 타임아웃: 26초 (기존 20초에서 30% 증가)
   * 타임아웃 시 1회 재시도
   */
  async chatMain(request: ChatV2Request): Promise<ChatV2Response> {
    const TIMEOUT_MS = 26000;  // 30% 증가 (20000 -> 26000)
    const MAX_RETRIES = 1;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      const response = await api.post<ChatV2Response>('/agent/chat', request, false, TIMEOUT_MS);

      if (response.error) {
        // 타임아웃 에러인 경우 재시도
        if (response.error.code === 'TIMEOUT_ERROR' && attempt < MAX_RETRIES) {
          console.warn(`[chatMain] Timeout on attempt ${attempt + 1}, retrying...`);
          lastError = new Error(response.error.message);
          continue;
        }

        // 타임아웃 에러이고 재시도도 실패한 경우 사용자 친화적 메시지
        if (response.error.code === 'TIMEOUT_ERROR') {
          throw new Error('요청 시간이 초과되었습니다. 다시 한번 조금 더 짧게 말씀해주세요.');
        }

        throw new Error(response.error.message);
      }

      return response.data!;
    }

    // 모든 재시도 실패 (이론상 여기 도달 안 함)
    throw lastError || new Error('요청 시간이 초과되었습니다. 다시 한번 조금 더 짧게 말씀해주세요.');
  },

  /**
   * Chat Agent - Streaming
   */
  chatStream(request: ChatAgentRequest): EventSource | null {
    if (typeof window === 'undefined') return null;

    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/agent/chat/stream`;

    // For SSE, we need to use fetch with streaming
    return null; // TODO: Implement SSE properly
  },

  /**
   * Generate Blank Problem (타임아웃: 60초)
   */
  async generateBlank(request: ProblemGenerationRequest): Promise<BlankProblemResponse> {
    const response = await api.post<BlankProblemResponse>('/agent/generate/blank', request, true, 60000);
    if (response.error) {
      if (response.error.code === 'INSUFFICIENT_CREDITS') {
        throw new InsufficientCreditsError(response.error.message);
      }
      throw new Error(response.error.message);
    }
    return response.data!;
  },

  /**
   * Generate Puzzle Problem (타임아웃: 60초)
   */
  async generatePuzzle(request: ProblemGenerationRequest): Promise<PuzzleProblemResponse> {
    const response = await api.post<PuzzleProblemResponse>('/agent/generate/puzzle', request, true, 60000);
    if (response.error) {
      if (response.error.code === 'INSUFFICIENT_CREDITS') {
        throw new InsufficientCreditsError(response.error.message);
      }
      throw new Error(response.error.message);
    }
    return response.data!;
  },

  /**
   * Generate Guided Problem (타임아웃: 60초)
   */
  async generateGuided(request: ProblemGenerationRequest): Promise<GuidedProblemResponse> {
    const response = await api.post<GuidedProblemResponse>('/agent/generate/guided', request, true, 60000);
    if (response.error) {
      if (response.error.code === 'INSUFFICIENT_CREDITS') {
        throw new InsufficientCreditsError(response.error.message);
      }
      throw new Error(response.error.message);
    }
    return response.data!;
  },

  /**
   * Get Guided Starter Code (에디터 기반 1대1 대화형)
   * - DB에 starter_code 있으면 그대로 반환
   * - 없으면 solutions 코드 앞 2줄 반환
   * - LLM 호출 없음
   */
  async getGuidedStarter(request: GuidedStarterRequest): Promise<GuidedStarterResponse> {
    const response = await api.post<GuidedStarterResponse>('/agent/get/guided-starter', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Generate Code (RAG Fallback, 타임아웃: 2분)
   */
  async generateCode(request: CodeGenerationRequest): Promise<CodeGenerationResponse> {
    const response = await api.post<CodeGenerationResponse>('/agent/generate/code', request, false, 120000);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get AI Hint (타임아웃: 60초)
   */
  async getHint(request: HintAgentRequest): Promise<HintAgentResponse> {
    const response = await api.post<HintAgentResponse>('/agent/hint', request, false, 60000);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * RAG Search
   */
  async search(request: RAGSearchRequest): Promise<RAGSearchResponse> {
    const response = await api.post<RAGSearchResponse>('/agent/search', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get Problem Recommendations
   */
  async recommend(
    collectedInfo: CollectedInfo,
    userContext?: Record<string, unknown>
  ): Promise<RecommendResponse> {
    const response = await api.post<RecommendResponse>(
      '/agent/recommend',
      { collected_info: collectedInfo, user_context: userContext },
      false
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get Feedback for completed problem
   * 문제 풀이 완료 후 피드백 생성
   */
  async getFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
    const response = await api.post<FeedbackResponse>('/agent/feedback', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Generate Problem (Streaming) - SSE 스트리밍으로 문제 유형별 생성
   * 실시간 상태 업데이트 + 힌트 사전 생성
   *
   * @param request - 생성 요청 (base_problem, problem_type, user_level, language)
   * @param callbacks - 콜백 함수들
   *   - onStatus: 상태 업데이트 콜백 (status, message)
   *   - onResult: 최종 결과 콜백 (generated problem data)
   *   - onError: 에러 콜백 (error message)
   *   - onDone: 완료 콜백
   */
  async generateProblemStream(
    request: ProblemGenerationRequest,
    callbacks: {
      onStatus?: (status: string, message: string) => void;
      onResult?: (result: BlankProblemResponse | PuzzleProblemResponse | GuidedProblemResponse) => void;
      onError?: (error: string) => void;
      onDone?: () => void;
    }
  ): Promise<void> {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
      const token = localStorage.getItem('access_token');
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_URL}/agent/generate/problem/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          base_problem: request.base_problem,
          problem_type: request.problem_type,
          user_level: request.user_level || 'intermediate',
          language: request.language || 'python',
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('로그인 토큰이 만료되었어요. 다시 로그인해주세요.');
        }
        if (response.status === 403) {
          // Check for insufficient credits error
          const errorData = await response.json().catch(() => ({}));
          if (errorData.detail?.includes('크레딧') || errorData.error?.code === 'INSUFFICIENT_CREDITS') {
            throw new InsufficientCreditsError(errorData.detail || '크레딧이 부족합니다.');
          }
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          callbacks.onDone?.();
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // SSE 이벤트 파싱
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 불완전한 마지막 줄은 버퍼에 보관

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              callbacks.onDone?.();
              return;
            }

            try {
              const event = JSON.parse(data);

              switch (event.type) {
                case 'status':
                  callbacks.onStatus?.(event.status, event.message);
                  break;
                case 'result':
                  callbacks.onResult?.(event.data);
                  break;
                case 'error':
                  callbacks.onError?.(event.message);
                  break;
              }
            } catch {
              // JSON 파싱 실패 무시
            }
          }
        }
      }
    } catch (error) {
      callbacks.onError?.(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  /**
   * Generate Code (Streaming wrapper)
   * 실시간 상태 업데이트를 제공하는 코드 생성
   */
  async generateCodeStream(
    request: CodeGenerationStreamRequest,
    callbacks: {
      onStatus?: (status: string, message: string) => void;
      onChunk?: (content: string) => void;
      onResult?: (result: BaseProblemInfo) => void;
      onComplete?: (result: CodeGenerationResponse) => void;
      onError?: (error: string) => void;
      onDone?: () => void;
    }
  ): Promise<void> {
    try {
      callbacks.onStatus?.('starting', '코드 생성을 시작합니다...');

      callbacks.onStatus?.('analyzing', '문제를 분석하고 있어요...');

      // Convert stream request to API request format
      const apiRequest: CodeGenerationRequest = {
        user_request: request.collectedInfo as unknown as Record<string, unknown>,
        similar_problems: request.similarProblems as unknown as Record<string, unknown>[],
        user_level: (request.userContext?.level as CodeGenerationRequest['user_level']) || 'intermediate',
        strong_algorithms: (request.userContext?.strongAlgorithms as string[]) || [],
        user_status: request.userContext?.status as string,
        user_goal: request.userContext?.goal as string,
      };

      callbacks.onStatus?.('generating', '코드를 생성하고 있어요...');

      const result = await this.generateCode(apiRequest);

      if (result.code) {
        const codeStr = typeof result.code === 'string'
          ? result.code
          : JSON.stringify(result.code, null, 2);
        callbacks.onChunk?.(codeStr);
      }

      callbacks.onStatus?.('finalizing', '마무리하고 있어요...');

      // Convert CodeGenerationResponse to BaseProblemInfo for onResult callback
      const baseProblemInfo: BaseProblemInfo = {
        id: `generated-${Date.now()}`,
        name: result.title,
        title: result.title,
        difficulty: result.difficulty,
        description: result.description,
        question: result.description,
        topics: result.topics,
      };
      callbacks.onResult?.(baseProblemInfo);
      callbacks.onComplete?.(result);
      callbacks.onDone?.();
    } catch (error) {
      callbacks.onError?.(error instanceof Error ? error.message : 'Unknown error');
      callbacks.onDone?.();
    }
  },
};
