/**
 * Problems API Functions
 */

import { api } from './client';
import type { Problem, ProblemType, Difficulty, Framework } from '../types';

export interface ProblemFilters {
  framework?: Framework;
  difficulty?: Difficulty;
  problemType?: ProblemType;
  topic?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface ProblemListResponse {
  problems: Problem[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface HintResponse {
  hint: string;
  level: number;
  xpCost: number;
}

// ===========================================
// base_problems API 타입
// ===========================================

export interface BaseProblemListItem {
  id: string;
  original_id: string;
  name: string;
  difficulty: string;
  tags: string[];
  source: string | null;
  input_output: {
    inputs?: string[];
    outputs?: string[];
  } | null;
  solve_count: number;  // 풀이 수 (유저당 1회만)
  like_count: number;  // 좋아요 수
}

export interface BaseProblemDetail {
  id: string;
  original_id: string;
  name: string;
  question: string;
  difficulty: string;
  tags: string[];
  source: string | null;
  url: string | null;
  input_output: {
    inputs?: string[];
    outputs?: string[];
  } | string | null;
  explanation: string | null;
  solutions?: Array<{ language: string; code: string }>;  // 문제 유형 생성 시 필요
}

export interface BaseProblemListResponse {
  items: BaseProblemListItem[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface BaseProblemFilters {
  difficulty?: string;
  source?: string;
  search?: string;
  tags?: string;
  page?: number;
  limit?: number;
}

// 문제 통계 응답
export interface ProblemStatsResponse {
  base_problem_id: string;
  solve_count: number;  // 풀이 수 (유저당 1회만)
  like_count: number;
  is_liked: boolean;
}

// 좋아요 토글 응답
export interface ProblemLikeResponse {
  success: boolean;
  is_liked: boolean;
  like_count: number;
}

export const problemsApi = {
  /**
   * Get list of problems with filters
   */
  async list(filters?: ProblemFilters): Promise<ProblemListResponse> {
    const params = new URLSearchParams();
    if (filters?.framework) params.append('framework', filters.framework);
    if (filters?.difficulty) params.append('difficulty', filters.difficulty);
    if (filters?.problemType) params.append('problem_type', filters.problemType);
    if (filters?.topic) params.append('topic', filters.topic);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.limit) params.append('limit', String(filters.limit));

    const queryString = params.toString();
    const endpoint = `/problems${queryString ? `?${queryString}` : ''}`;

    const response = await api.get<ProblemListResponse>(endpoint, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get single problem by ID
   */
  async get(id: string): Promise<Problem> {
    const response = await api.get<Problem>(`/problems/${id}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Request a hint for a problem
   */
  async getHint(problemId: string, level: number, blankId?: string): Promise<HintResponse> {
    const response = await api.post<HintResponse>(`/problems/${problemId}/hint`, {
      level,
      blank_id: blankId,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // ===========================================
  // base_problems API
  // ===========================================

  /**
   * base_problems 목록 조회
   */
  async listBase(filters?: BaseProblemFilters): Promise<BaseProblemListResponse> {
    const params = new URLSearchParams();
    if (filters?.difficulty) params.append('difficulty', filters.difficulty);
    if (filters?.source) params.append('source', filters.source);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.tags) params.append('tags', filters.tags);
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.limit) params.append('limit', String(filters.limit));

    const queryString = params.toString();
    const endpoint = `/problems/base${queryString ? `?${queryString}` : ''}`;

    const response = await api.get<BaseProblemListResponse>(endpoint, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * base_problems 상세 조회 (Preview용)
   */
  async getBase(originalId: string): Promise<BaseProblemDetail> {
    const response = await api.get<BaseProblemDetail>(`/problems/base/${originalId}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // incrementView 제거됨 - 조회수 대신 풀이수(solve_count) 사용
  // solve_count는 피드백 완료 시점에 백엔드에서 자동 증가

  /**
   * 문제 좋아요 토글 (로그인 필요)
   */
  async toggleLike(baseProblemId: string): Promise<ProblemLikeResponse> {
    const response = await api.post<ProblemLikeResponse>('/practice/problems/like', {
      base_problem_id: baseProblemId,
    }, true);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 문제 통계 조회 (조회수, 좋아요 수, 현재 사용자 좋아요 여부)
   */
  async getStats(baseProblemId: string): Promise<ProblemStatsResponse> {
    const response = await api.get<ProblemStatsResponse>(
      `/practice/problems/${baseProblemId}/stats`,
      false  // 비로그인도 조회 가능
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};
