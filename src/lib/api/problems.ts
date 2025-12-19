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
};
