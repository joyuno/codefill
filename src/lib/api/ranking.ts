/**
 * Ranking API Client
 * 랭킹 시스템 (글로벌, 주간, 월간)
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export type RankingPeriod = 'global' | 'weekly' | 'monthly';
export type RankingType = 'xp' | 'problems' | 'streak';

export interface RankingItem {
  rank: number;
  user_id: string;
  username: string | null;
  profile_image: string | null;
  value: number;
  level: number;
}

export interface RankingListResponse {
  items: RankingItem[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface MyRankingSummary {
  global_xp_rank: number;
  global_xp_percentile: number;
  global_solve_rank: number;
  global_streak_rank: number;
  weekly_xp_rank: number | null;
  weekly_solve_rank: number | null;
  monthly_xp_rank: number | null;
  monthly_solve_rank: number | null;
  total_users: number;
  my_total_xp: number;
  my_problems_solved: number;
  my_longest_streak: number;
  my_level: number;
}

// =====================================================
// Challenge Page Combined Data (Performance Optimized)
// =====================================================

export interface ChallengePageData {
  ranking: MyRankingSummary;
  daily: {
    missions: Array<{
      id: string;
      mission_id: string;
      code: string;
      name: string;
      description: string | null;
      condition_type: string;
      condition_value: number;
      difficulty: string | null;
      current_progress: number;
      target_value: number;
      status: string;
      reward_gold: number;
      reward_xp: number;
      reward_seeds: Record<string, number> | null;
    }>;
    today_completed: number;
    today_claimed: number;
  };
  weekly: {
    challenges: Array<{
      id: string;
      mission_id: string;
      code: string;
      name: string;
      description: string | null;
      condition_type: string;
      condition_value: number;
      difficulty: string | null;
      current_progress: number;
      target_value: number;
      status: string;
      reward_gold: number;
      reward_xp: number;
      reward_seeds: Record<string, number> | null;
    }>;
    week_completed: number;
    week_claimed: number;
  };
  user_id: string;
}

// =====================================================
// API Functions
// =====================================================

export const rankingApi = {
  /**
   * 글로벌 랭킹 조회
   */
  async getGlobalRanking(
    type: RankingType = 'xp',
    page: number = 1,
    limit: number = 20
  ): Promise<RankingListResponse> {
    const params = new URLSearchParams({
      type,
      page: String(page),
      limit: String(limit),
    });

    const response = await api.get<RankingListResponse>(`/ranking/global?${params}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 주간 랭킹 조회
   */
  async getWeeklyRanking(
    type: Exclude<RankingType, 'streak'> = 'xp',
    page: number = 1,
    limit: number = 20
  ): Promise<RankingListResponse> {
    const params = new URLSearchParams({
      type,
      page: String(page),
      limit: String(limit),
    });

    const response = await api.get<RankingListResponse>(`/ranking/weekly?${params}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 월간 랭킹 조회
   */
  async getMonthlyRanking(
    type: Exclude<RankingType, 'streak'> = 'xp',
    page: number = 1,
    limit: number = 20
  ): Promise<RankingListResponse> {
    const params = new URLSearchParams({
      type,
      page: String(page),
      limit: String(limit),
    });

    const response = await api.get<RankingListResponse>(`/ranking/monthly?${params}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 내 순위 조회
   */
  async getMyRanking(): Promise<MyRankingSummary> {
    const response = await api.get<MyRankingSummary>('/ranking/me');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Challenge 페이지 통합 데이터 조회 (성능 최적화)
   * - 내 랭킹 + 일일미션 + 주간챌린지 + userId 한번에 반환
   * - 3개 API 호출 → 1개로 통합하여 지연 시간 3배 감소
   */
  async getChallengePageData(): Promise<ChallengePageData> {
    const response = await api.get<ChallengePageData>('/ranking/challenge-page-data');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};

export default rankingApi;
