/**
 * solved.ac Integration API functions
 */

import { api } from './client';

// Types
export interface SolvedAcOrganization {
  organizationId: number;
  name: string;
  type: string;
  rating: number;
  userCount: number;
  color?: string;
}

export interface SolvedAcProfile {
  handle: string;
  bio?: string;
  profileImageUrl?: string;
  tier: number;
  rating: number;
  class_: number;
  classDecoration?: string;
  solvedCount: number;
  exp: number;
  rank?: number;
  maxStreak: number;
  organizations: SolvedAcOrganization[];
  isLinked: boolean;  // 이미 다른 사용자가 연동했는지 여부
}

export interface SolvedAcProfileDB {
  id: string;
  user_id: string;
  handle: string;
  tier: number;
  rating: number;
  solved_count: number;
  max_streak: number;
  last_synced_at: string;
  created_at: string;
}

export interface LinkSolvedAcRequest {
  handle: string;
}

export interface LinkSolvedAcResponse {
  success: boolean;
  message: string;
  profile?: SolvedAcProfileDB;
}

export interface SyncSolvedAcResponse {
  success: boolean;
  message: string;
  profile?: SolvedAcProfileDB;
}

export interface TierInfo {
  tier: number;
  name: string;
  color: string;
}

// Helper function to convert tier number to name
export function tierToName(tier: number): string {
  if (tier === 0) return 'Unrated';

  const tiers = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby', 'Master'];
  const levels = ['V', 'IV', 'III', 'II', 'I'];

  const tierIndex = Math.floor((tier - 1) / 5);
  const levelIndex = (tier - 1) % 5;

  if (tierIndex >= tiers.length) return 'Master';

  return `${tiers[tierIndex]} ${levels[levelIndex]}`;
}

// Helper function to get tier color
export function getTierColor(tier: number): string {
  if (tier === 0) return '#2D2D2D'; // Unrated
  if (tier <= 5) return '#AD5600'; // Bronze
  if (tier <= 10) return '#435F7A'; // Silver
  if (tier <= 15) return '#EC9A00'; // Gold
  if (tier <= 20) return '#27E2A4'; // Platinum
  if (tier <= 25) return '#00B4FC'; // Diamond
  if (tier <= 30) return '#FF0062'; // Ruby
  return '#B300FF'; // Master
}

// API Functions
export const solvedacApi = {
  /**
   * Lookup solved.ac profile (without linking)
   * Can be used before signup/login to verify the handle
   */
  lookup: async (
    handle: string
  ): Promise<{ data?: SolvedAcProfile; error?: { code: string; message: string } }> => {
    return api.get<SolvedAcProfile>(`/solvedac/lookup/${encodeURIComponent(handle)}`, false);
  },

  /**
   * Link solved.ac profile to current user
   * Requires authentication
   */
  link: async (
    handle: string
  ): Promise<{ data?: LinkSolvedAcResponse; error?: { code: string; message: string } }> => {
    return api.post<LinkSolvedAcResponse>('/solvedac/link', { handle }, true);
  },

  /**
   * Get current user's linked solved.ac profile
   * Requires authentication
   */
  getMyProfile: async (): Promise<{
    data?: SolvedAcProfileDB | null;
    error?: { code: string; message: string };
  }> => {
    return api.get<SolvedAcProfileDB | null>('/solvedac/me', true);
  },

  /**
   * Sync (refresh) current user's solved.ac profile
   * Fetches latest data from solved.ac and updates DB
   * Requires authentication
   */
  sync: async (): Promise<{
    data?: SyncSolvedAcResponse;
    error?: { code: string; message: string };
  }> => {
    return api.post<SyncSolvedAcResponse>('/solvedac/sync', undefined, true);
  },

  /**
   * Unlink solved.ac profile from current user
   * Requires authentication
   */
  unlink: async (): Promise<{
    data?: { success: boolean; message: string };
    error?: { code: string; message: string };
  }> => {
    return api.delete<{ success: boolean; message: string }>('/solvedac/unlink', undefined, true);
  },

  /**
   * Get tier info (name and color) for a tier number
   */
  getTierInfo: (tier: number): TierInfo => {
    return {
      tier,
      name: tierToName(tier),
      color: getTierColor(tier),
    };
  },
};
