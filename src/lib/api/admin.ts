/**
 * Admin API Client
 *
 * 관리자 기능 API 클라이언트
 */

import { api } from './client';

// ============================================================
// Types
// ============================================================

export interface AdminUser {
  id: string;
  email: string;
  name: string | null;
  role: string;
  avatar_url: string | null;
  provider: string;
  created_at: string;
  deleted_at: string | null;
  banned_until: string | null;  // 정지 만료일 (null=정상, 날짜=정지중, 9999-12-31=영구정지)
  level: number;
  total_xp: number;
  problems_solved: number;
}

// 사용자 배지
export interface AdminUserBadge {
  id: string;
  code: string;
  name: string;
  description: string | null;
  icon_url: string | null;
  rarity: string;
  earned_at: string;
}

// 최근 활동
export interface AdminRecentActivity {
  id: string;
  type: string;
  title: string;
  description: string | null;
  timestamp: string;
  xp_earned: number | null;
}

export interface AdminUserDetail extends AdminUser {
  username: string | null;
  subscription_tier: string;
  subscription_expires_at: string | null;
  updated_at: string | null;
  last_activity_date: string | null;
  problems_attempted: number;
  current_streak: number;
  longest_streak: number;
  // Problem type breakdown
  blank_solved: number;
  puzzle_solved: number;
  guided_solved: number;
  // Preferences
  preferred_language: string | null;
  daily_goal: number | null;
  // Onboarding
  current_status: string | null;
  learning_goal: string | null;
  experience_level: string | null;
  // Badges & Activity
  badges: AdminUserBadge[];
  recent_activity: AdminRecentActivity[];
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface AdminProblem {
  id: string;
  original_id: string;
  name: string;
  difficulty: string;
  source: string | null;
  tags: string[];
  solve_count: number;
  like_count: number;
  has_blank: boolean;
  has_puzzle: boolean;
  has_guided: boolean;
  created_at: string | null;
  deleted_at: string | null;
}

export interface AdminProblemListResponse {
  items: AdminProblem[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface BlankVariant {
  id: string;
  language: string;
  code_template: string;
  answers: string[];
  created_at: string | null;
}

export interface PuzzleVariant {
  id: string;
  language: string;
  fixed_start: string | null;
  fixed_end: string | null;
  blocks: { id: number; code: string }[];
  created_at: string | null;
}

export interface VariableGuideItem {
  name: string;
  role: string;
  type: string;
  initial?: string;
}

export interface GuidedVariant {
  id: string;
  language: string;
  concept_explanation: string;
  variables_guide: VariableGuideItem[];
  approach_guide: string;
  starter_code: string;
  status: string;
  attempts_count: number;
  hints_given: number;
  created_at: string | null;
}

export interface AdminProblemDetail {
  id: string;
  original_id: string;
  name: string;
  question: string;
  difficulty: string;
  tags: string[];
  source: string | null;
  url: string | null;
  time_limit: string | null;
  memory_limit: string | null;
  input_output: any;
  solutions: { language: string; code: string }[];
  created_at: string | null;
  deleted_at: string | null;
  blanks: BlankVariant[];
  puzzles: PuzzleVariant[];
  guideds: GuidedVariant[];
}

export interface AdminDashboardStats {
  total_users: number;
  active_users_today: number;
  total_problems: number;
  total_submissions: number;
  new_users_this_week: number;
}

export interface CreateBaseProblemRequest {
  original_id: string;
  name: string;
  question: string;
  difficulty: string;
  tags: string[];
  source?: string;
  url?: string;
  time_limit?: string;
  memory_limit?: string;
  input_output?: any;
  solutions: { language: string; code: string }[];
}

export interface CreateBlankProblemRequest {
  language: string;
  code_template: string;
  answers: string[];
}

export interface CreatePuzzleProblemRequest {
  language: string;
  fixed_start?: string;
  fixed_end?: string;
  blocks: { id: number; code: string }[];
}

export interface CreateGuidedProblemRequest {
  language: string;
  concept_explanation: string;
  variables_guide: VariableGuideItem[];
  approach_guide: string;
  starter_code: string;
}

// Update Requests
export interface UpdateBlankProblemRequest {
  language?: string;
  code_template?: string;
  answers?: string[];
}

export interface UpdatePuzzleProblemRequest {
  language?: string;
  fixed_start?: string;
  fixed_end?: string;
  blocks?: { id: number; code: string }[];
}

export interface UpdateGuidedProblemRequest {
  language?: string;
  concept_explanation?: string;
  variables_guide?: VariableGuideItem[];
  approach_guide?: string;
  starter_code?: string;
}

// ============================================================
// API Functions
// ============================================================

export const adminApi = {
  // Dashboard
  async getDashboardStats(): Promise<AdminDashboardStats> {
    const response = await api.get<AdminDashboardStats>('/admin/dashboard');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // Users
  async listUsers(params?: {
    search?: string;
    role?: string;
    include_banned?: boolean;
    page?: number;
    limit?: number;
  }): Promise<AdminUserListResponse> {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.role) query.append('role', params.role);
    if (params?.include_banned) query.append('include_banned', 'true');
    if (params?.page) query.append('page', String(params.page));
    if (params?.limit) query.append('limit', String(params.limit));

    const queryString = query.toString();
    const response = await api.get<AdminUserListResponse>(
      `/admin/users${queryString ? `?${queryString}` : ''}`
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async getUserDetail(userId: string): Promise<AdminUserDetail> {
    const response = await api.get<AdminUserDetail>(`/admin/users/${userId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async updateUserRole(userId: string, role: 'admin' | 'user'): Promise<void> {
    const response = await api.put(`/admin/users/${userId}/role`, { role });
    if (response.error) throw new Error(response.error.message);
  },

  async banUser(
    userId: string,
    is_banned: boolean,
    options?: { ban_days?: number; reason?: string }
  ): Promise<{ banned_until?: string }> {
    const response = await api.put<{ success: boolean; banned_until?: string }>(
      `/admin/users/${userId}/ban`,
      {
        is_banned,
        ban_days: options?.ban_days,
        reason: options?.reason,
      }
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async deleteUser(userId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.delete<{ success: boolean; message: string }>(
      `/admin/users/${userId}`
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // Problems
  async listProblems(params?: {
    search?: string;
    difficulty?: string;
    source?: string;
    tags?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    include_deleted?: boolean;
    page?: number;
    limit?: number;
  }): Promise<AdminProblemListResponse> {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.difficulty) query.append('difficulty', params.difficulty);
    if (params?.source) query.append('source', params.source);
    if (params?.tags) query.append('tags', params.tags);
    if (params?.sort_by) query.append('sort_by', params.sort_by);
    if (params?.sort_order) query.append('sort_order', params.sort_order);
    if (params?.include_deleted) query.append('include_deleted', 'true');
    if (params?.page) query.append('page', String(params.page));
    if (params?.limit) query.append('limit', String(params.limit));

    const queryString = query.toString();
    const response = await api.get<AdminProblemListResponse>(
      `/admin/problems${queryString ? `?${queryString}` : ''}`
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async getProblemDetail(originalId: string): Promise<AdminProblemDetail> {
    const response = await api.get<AdminProblemDetail>(`/admin/problems/${originalId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async updateProblem(originalId: string, data: Partial<CreateBaseProblemRequest>): Promise<void> {
    const response = await api.put(`/admin/problems/${originalId}`, data);
    if (response.error) throw new Error(response.error.message);
  },

  async deleteProblem(originalId: string): Promise<void> {
    const response = await api.delete(`/admin/problems/${originalId}`);
    if (response.error) throw new Error(response.error.message);
  },

  // Create Problems
  async createBaseProblem(data: CreateBaseProblemRequest): Promise<{ id: string; original_id: string }> {
    const response = await api.post<{ success: boolean; id: string; original_id: string }>(
      '/admin/problems/base',
      data
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async createBlankProblem(originalId: string, data: CreateBlankProblemRequest): Promise<{ id: string }> {
    const response = await api.post<{ success: boolean; id: string }>(
      `/admin/problems/${originalId}/blank`,
      data
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async createPuzzleProblem(originalId: string, data: CreatePuzzleProblemRequest): Promise<{ id: string }> {
    const response = await api.post<{ success: boolean; id: string }>(
      `/admin/problems/${originalId}/puzzle`,
      data
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  async createGuidedProblem(originalId: string, data: CreateGuidedProblemRequest): Promise<{ id: string }> {
    const response = await api.post<{ success: boolean; id: string }>(
      `/admin/problems/${originalId}/guided`,
      data
    );
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // Update Variant Problems
  async updateBlankProblem(originalId: string, blankId: string, data: UpdateBlankProblemRequest): Promise<void> {
    const response = await api.put(`/admin/problems/${originalId}/blank/${blankId}`, data);
    if (response.error) throw new Error(response.error.message);
  },

  async updatePuzzleProblem(originalId: string, puzzleId: string, data: UpdatePuzzleProblemRequest): Promise<void> {
    const response = await api.put(`/admin/problems/${originalId}/puzzle/${puzzleId}`, data);
    if (response.error) throw new Error(response.error.message);
  },

  async updateGuidedProblem(originalId: string, guidedId: string, data: UpdateGuidedProblemRequest): Promise<void> {
    const response = await api.put(`/admin/problems/${originalId}/guided/${guidedId}`, data);
    if (response.error) throw new Error(response.error.message);
  },

  // Delete Variant Problems
  async deleteBlankProblem(originalId: string, blankId: string): Promise<void> {
    const response = await api.delete(`/admin/problems/${originalId}/blank/${blankId}`);
    if (response.error) throw new Error(response.error.message);
  },

  async deletePuzzleProblem(originalId: string, puzzleId: string): Promise<void> {
    const response = await api.delete(`/admin/problems/${originalId}/puzzle/${puzzleId}`);
    if (response.error) throw new Error(response.error.message);
  },

  async deleteGuidedProblem(originalId: string, guidedId: string): Promise<void> {
    const response = await api.delete(`/admin/problems/${originalId}/guided/${guidedId}`);
    if (response.error) throw new Error(response.error.message);
  },

  // Restore Problem
  async restoreProblem(originalId: string): Promise<void> {
    const response = await api.post(`/admin/problems/${originalId}/restore`, {});
    if (response.error) throw new Error(response.error.message);
  },

  // Solutions Management (Admin)
  async deleteSolution(solutionId: string): Promise<void> {
    const response = await api.delete(`/admin/solutions/${solutionId}`);
    if (response.error) throw new Error(response.error.message);
  },

  async deleteComment(commentId: string): Promise<void> {
    const response = await api.delete(`/admin/solutions/comments/${commentId}`);
    if (response.error) throw new Error(response.error.message);
  },
};
