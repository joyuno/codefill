/**
 * Solutions API Client
 * 문제 풀이 게시글 시스템
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export interface SolutionAuthor {
  id: string;
  name: string | null;
  avatar_url: string | null;
}

export interface SolutionListItem {
  id: string;
  user_id: string;
  language: string;
  code: string;
  title: string | null;
  upvotes: number;
  downvotes: number;
  comment_count: number;
  created_at: string;
  author_name: string | null;
  author_avatar: string | null;
}

export interface SolutionDetail {
  id: string;
  base_problem_id: string;
  user_id: string;
  language: string;
  code: string;
  title: string | null;
  description: string | null;
  is_correct: boolean;
  upvotes: number;
  downvotes: number;
  view_count: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  author_name: string | null;
  author_avatar: string | null;
  problem_original_id: string | null;
  problem_name: string | null;
  my_vote: 'up' | 'down' | null;
}

export interface SolutionListResponse {
  items: SolutionListItem[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface CommentItem {
  id: string;
  solution_id: string;
  user_id: string | null;
  parent_id: string | null;
  content: string;
  upvotes: number;
  downvotes: number;
  is_deleted: boolean;
  reply_count: number;
  created_at: string;
  updated_at: string;
  author_name: string | null;
  author_avatar: string | null;
  my_vote: 'up' | 'down' | null;
  replies?: CommentItem[];
}

export interface CommentListResponse {
  items: CommentItem[];
  total: number;
}

export interface VoteResponse {
  success: boolean;
  upvotes: number;
  downvotes: number;
  my_vote: 'up' | 'down' | null;
}

export interface OfficialSolution {
  language: string;
  code: string;
}

export interface ProblemDiscussionResponse {
  problem: {
    id: string;
    original_id: string;
    name: string;
    question: string;
    difficulty: string;
    tags: string[];
    source: string | null;
    url: string | null;
    input_output: {
      inputs: string[];
      outputs: string[];
    } | null;
    solutions: OfficialSolution[];
    explanation: string | null;
  };
  official_solutions: OfficialSolution[];
  user_solutions: SolutionListResponse;
}

export interface SolutionCreateData {
  base_problem_id: string;
  language: string;
  code: string;
  title?: string;
  description?: string;
}

export interface SolutionUpdateData {
  code?: string;
  language?: string;
  title?: string;
  description?: string;
}

export interface CommentCreateData {
  content: string;
  parent_id?: string;
}

// =====================================================
// API Functions
// =====================================================

export const solutionsApi = {
  /**
   * 문제 게시글 페이지 조회
   */
  async getProblemDiscussion(
    originalId: string,
    options?: {
      page?: number;
      limit?: number;
      sort?: 'upvotes' | 'newest' | 'oldest';
    }
  ): Promise<ProblemDiscussionResponse> {
    const params = new URLSearchParams();
    if (options?.page) params.append('page', options.page.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.sort) params.append('sort', options.sort);

    const queryString = params.toString();
    const url = `/solutions/problem/${originalId}${queryString ? `?${queryString}` : ''}`;

    const response = await api.get<ProblemDiscussionResponse>(url, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 풀이 목록 조회
   */
  async listSolutions(options?: {
    base_problem_id?: string;
    user_id?: string;
    language?: string;
    page?: number;
    limit?: number;
    sort?: 'upvotes' | 'newest' | 'oldest';
  }): Promise<SolutionListResponse> {
    const params = new URLSearchParams();
    if (options?.base_problem_id) params.append('base_problem_id', options.base_problem_id);
    if (options?.user_id) params.append('user_id', options.user_id);
    if (options?.language) params.append('language', options.language);
    if (options?.page) params.append('page', options.page.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.sort) params.append('sort', options.sort);

    const queryString = params.toString();
    const response = await api.get<SolutionListResponse>(`/solutions${queryString ? `?${queryString}` : ''}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 풀이 작성
   */
  async createSolution(data: SolutionCreateData): Promise<SolutionDetail> {
    const response = await api.post<SolutionDetail>('/solutions', data);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 풀이 상세 조회
   */
  async getSolution(solutionId: string): Promise<SolutionDetail> {
    const response = await api.get<SolutionDetail>(`/solutions/${solutionId}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 풀이 수정
   */
  async updateSolution(solutionId: string, data: SolutionUpdateData): Promise<SolutionDetail> {
    const response = await api.put<SolutionDetail>(`/solutions/${solutionId}`, data);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 풀이 삭제
   */
  async deleteSolution(solutionId: string): Promise<void> {
    const response = await api.delete<void>(`/solutions/${solutionId}`);
    if (response.error) throw new Error(response.error.message);
  },

  /**
   * 풀이 투표
   */
  async voteSolution(solutionId: string, voteType: 'up' | 'down'): Promise<VoteResponse> {
    const response = await api.post<VoteResponse>(`/solutions/${solutionId}/vote`, { vote_type: voteType });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 댓글 목록 조회
   */
  async listComments(solutionId: string): Promise<CommentListResponse> {
    const response = await api.get<CommentListResponse>(`/solutions/${solutionId}/comments`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 댓글 작성
   */
  async createComment(solutionId: string, data: CommentCreateData): Promise<CommentItem> {
    const response = await api.post<CommentItem>(`/solutions/${solutionId}/comments`, data);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 댓글 수정
   */
  async updateComment(commentId: string, content: string): Promise<CommentItem> {
    const response = await api.put<CommentItem>(`/solutions/comments/${commentId}`, { content });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 댓글 삭제
   */
  async deleteComment(commentId: string): Promise<void> {
    const response = await api.delete<void>(`/solutions/comments/${commentId}`);
    if (response.error) throw new Error(response.error.message);
  },

  /**
   * 댓글 투표
   */
  async voteComment(commentId: string, voteType: 'up' | 'down'): Promise<VoteResponse> {
    const response = await api.post<VoteResponse>(`/solutions/comments/${commentId}/vote`, { vote_type: voteType });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};
