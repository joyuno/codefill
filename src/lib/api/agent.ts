/**
 * Agent API Functions
 * LLM-powered agent endpoints for chat, problem generation, and hints
 */

import { api } from './client';

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
}

export interface ChatAgentResponse {
  message: string;
  collected_info: CollectedInfo;
  is_complete: boolean;
  search_query: string | null;
}

// Problem Generation
export interface BaseProblemInfo {
  id?: string;
  title: string;
  description: string;
  code: string;
  language: 'python' | 'java' | 'cpp';
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
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
}

export interface PuzzleProblemResponse {
  original_id: string;
  language: string;
  fixed_start?: string;  // 고정된 시작 코드 (선택)
  fixed_end?: string;    // 고정된 끝 코드 (선택)
  blocks: PuzzleBlock[]; // id 순서가 정답
}

// Guided Problem Response (matches data/examples/problems_guided.json)
export interface GuidedProblemResponse {
  original_id: string;
  language: string;
  concepts: string[];     // 핵심 개념 목록
  flow: string[];         // 학습 흐름 단계
  checkpoints: string[];  // 체크포인트/확인 사항
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
  problem_info: Record<string, unknown>;
  user_code?: string;
  attempt_count: number;
  hint_level: 1 | 2 | 3 | 4;
  previous_hints: string[];
  user_level: 'beginner' | 'elementary' | 'intermediate' | 'advanced';
}

export interface RelatedConcept {
  name: string;
  brief: string;
  doc_reference?: string;
}

export interface HintAgentResponse {
  hint_level: number;
  hint_content: string;
  hint_type: 'direction' | 'approach' | 'specific' | 'final';
  questions: string[];
  related_concept?: RelatedConcept;
  encouragement: string;
  next_hint_preview?: string;
  code_snippet?: string;
  common_mistake_check?: string;
}

// RAG Search
export interface RAGSearchRequest {
  query: string;
  topics: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
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
   * Chat Agent - Streaming
   */
  chatStream(request: ChatAgentRequest): EventSource | null {
    if (typeof window === 'undefined') return null;

    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/agent/chat/stream`;

    // For SSE, we need to use fetch with streaming
    return null; // TODO: Implement SSE properly
  },

  /**
   * Generate Blank Problem
   */
  async generateBlank(request: ProblemGenerationRequest): Promise<BlankProblemResponse> {
    const response = await api.post<BlankProblemResponse>('/agent/generate/blank', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Generate Puzzle Problem
   */
  async generatePuzzle(request: ProblemGenerationRequest): Promise<PuzzleProblemResponse> {
    const response = await api.post<PuzzleProblemResponse>('/agent/generate/puzzle', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Generate Guided Problem
   */
  async generateGuided(request: ProblemGenerationRequest): Promise<GuidedProblemResponse> {
    const response = await api.post<GuidedProblemResponse>('/agent/generate/guided', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Generate Code (RAG Fallback)
   */
  async generateCode(request: CodeGenerationRequest): Promise<CodeGenerationResponse> {
    const response = await api.post<CodeGenerationResponse>('/agent/generate/code', request, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get AI Hint
   */
  async getHint(request: HintAgentRequest): Promise<HintAgentResponse> {
    const response = await api.post<HintAgentResponse>('/agent/hint', request, false);
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
};
