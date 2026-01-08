/**
 * Users API Functions
 */

import { api } from './client';
import type { Badge, ActivityDay, RecentActivity } from '../types';

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  avatarShape: 'hexagon' | 'circle' | 'diamond' | 'pentagon';
  avatarColor: string;
  level: number;
  currentXP: number;
  requiredXP: number;
  totalXP: number;
  solvedCount: number;
  streak: number;
  maxStreak: number;
  joinedAt: string;
  subscription: 'free' | 'pro' | 'enterprise';
  preferences?: {
    preferredFramework?: string;
    preferredLanguage?: string;
    dailyGoal?: number;
    notificationsEnabled?: boolean;
  };
}

export interface UserStats {
  totalSolved: number;
  solvedByDifficulty: {
    easy: number;
    medium: number;
    hard: number;
  };
  solvedByType: {
    blank: number;
    puzzle: number;
  };
  currentStreak: number;
  maxStreak: number;
  totalXP: number;
  level: number;
  rank?: number;
  percentile?: number;
}

export interface ActivityData {
  days: ActivityDay[];
  totalDays: number;
}

export interface SolvedProblem {
  id: string;
  name: string;
  difficulty: string;
  problem_type: string;
  xp_earned: number;
  solved_at: string;
}

export interface DateActivityDetail {
  date: string;
  problems_solved: number;
  xp_earned: number;
  problems: SolvedProblem[];
}

// Backend response types (for transformation)
interface BackendRecentActivity {
  id: string;
  type: 'solved' | 'badge' | 'streak' | 'levelup';
  title: string;
  description: string;
  timestamp: string;
  xp_gained?: number;
}

interface BackendBadge {
  id: string;
  name: string;
  icon: string;
  icon_url?: string;  // from Supabase
  description: string;
  earnedAt: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface ChangeNicknameResponse {
  success: boolean;
  message: string;
  next_change_available_at?: string;
}

// solved.ac 프로필 (간소화)
export interface SolvedAcProfileSimple {
  handle: string;
  tier: number;
  rating: number;
  solved_count: number;
  max_streak: number;
  last_synced_at: string;
}

// 통합 마이페이지 응답
export interface MypageAllResponse {
  profile: UserProfile;
  stats: UserStats;
  badges: Badge[];
  recentActivity: RecentActivity[];
  solvedAc: SolvedAcProfileSimple | null;
}

// 백엔드 응답 타입 (변환용)
interface BackendMypageAllResponse {
  profile: UserProfile;
  stats: UserStats;
  badges: BackendBadge[];
  recentActivity: BackendRecentActivity[];
  solvedAc: SolvedAcProfileSimple | null;
}

export const usersApi = {
  /**
   * Get all mypage data in a single API call (recommended)
   * Replaces: getProfile + getStats + getBadges + getRecentActivity + solvedAc
   */
  async getMypageAll(): Promise<MypageAllResponse> {
    const response = await api.get<BackendMypageAllResponse>('/users/me/mypage-all');
    if (response.error) throw new Error(response.error.message);

    const data = response.data!;

    // Transform backend response to frontend types
    return {
      profile: data.profile,
      stats: data.stats,
      badges: (data.badges || []).map((badge) => ({
        id: badge.id,
        name: badge.name,
        icon: badge.icon,
        iconUrl: badge.icon_url,
        description: badge.description,
        earnedAt: badge.earnedAt,
        rarity: badge.rarity,
      })),
      recentActivity: (data.recentActivity || []).map((activity) => ({
        id: activity.id,
        type: activity.type,
        title: activity.title,
        description: activity.description,
        timestamp: activity.timestamp,
        xpGained: activity.xp_gained,
      })),
      solvedAc: data.solvedAc,
    };
  },

  /**
   * Get current user profile (mypage optimized)
   * @deprecated Use getMypageAll() instead for better performance
   */
  async getProfile(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/users/me/profile');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.put<UserProfile>('/users/me', data);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get user statistics (mypage optimized)
   */
  async getStats(): Promise<UserStats> {
    const response = await api.get<UserStats>('/users/me/mypage-stats');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get user badges (mypage optimized)
   */
  async getBadges(): Promise<Badge[]> {
    const response = await api.get<BackendBadge[]>('/users/me/mypage-badges');
    if (response.error) throw new Error(response.error.message);

    // Transform backend response to frontend Badge type
    return (response.data || []).map((badge) => ({
      id: badge.id,
      name: badge.name,
      icon: badge.icon,
      iconUrl: badge.icon_url,  // snake_case -> camelCase
      description: badge.description,
      earnedAt: badge.earnedAt,
      rarity: badge.rarity,
    }));
  },

  /**
   * Get activity data (for heatmap)
   */
  async getActivity(days: number = 365): Promise<ActivityData> {
    const response = await api.get<ActivityData>(`/users/me/activity?days=${days}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get activity detail for a specific date (잔디 클릭 시)
   */
  async getActivityByDate(date: string): Promise<DateActivityDetail> {
    const response = await api.get<DateActivityDetail>(`/users/me/activity/${date}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get recent activity
   */
  async getRecentActivity(limit: number = 10): Promise<RecentActivity[]> {
    const response = await api.get<BackendRecentActivity[]>(`/users/me/recent?limit=${limit}`);
    if (response.error) throw new Error(response.error.message);

    // Transform backend response to frontend RecentActivity type
    return (response.data || []).map((activity) => ({
      id: activity.id,
      type: activity.type,
      title: activity.title,
      description: activity.description,
      timestamp: activity.timestamp,
      xpGained: activity.xp_gained,
    }));
  },

  /**
   * Update user preferences
   */
  async updatePreferences(
    preferences: UserProfile['preferences']
  ): Promise<UserProfile> {
    const response = await api.put<UserProfile>('/users/me/preferences', preferences);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Change nickname (once per 30 days)
   */
  async changeNickname(newNickname: string): Promise<ChangeNicknameResponse> {
    const response = await api.put<ChangeNicknameResponse>('/users/me/nickname', {
      new_nickname: newNickname,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Upload avatar image
   */
  async uploadAvatar(file: File): Promise<{ success: boolean; avatar_url: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '이미지 업로드에 실패했습니다.');
    }

    return response.json();
  },

  /**
   * Delete avatar image
   */
  async deleteAvatar(): Promise<{ success: boolean; message: string }> {
    const response = await api.delete<{ success: boolean; message: string }>('/users/me/avatar');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};


// =====================================================
// Public Profile Types (공개 프로필)
// =====================================================

export interface PublicProfile {
  id: string;
  username: string;
  avatarUrl: string | null;  // 실제 프로필 이미지 URL
  avatarColor: string;       // 폴백 배경색
  level: number;
  currentXP: number;
  requiredXP: number;
  totalXP: number;
  solvedCount: number;
  streak: number;
  joinedAt: string;
}

export interface PublicStats {
  totalSolved: number;
  solvedByDifficulty: {
    easy: number;
    medium: number;
    hard: number;
  };
  solvedByType: {
    blank: number;
    puzzle: number;
  };
  currentStreak: number;
  maxStreak: number;
  totalXP: number;
  level: number;
}

export interface PublicFarmCharacter {
  name: string;
  hair: string;
  hairColor: string;
  face: string;
  outfit: string;
  outfitColor: string;
  farmName: string;
}

export interface PublicFarmSlot {
  slotIndex: number;
  cropType: string | null;
  stage: number;
  isReady: boolean;
}

export interface PublicFarm {
  hasCharacter: boolean;
  character: PublicFarmCharacter | null;
  farmLevel: number;
  gold: number;
  slots: PublicFarmSlot[];
}

export interface PublicBadge {
  id: string;
  name: string;
  icon: string;
  iconUrl?: string;
  description: string;
  rarity: string;
}

// =====================================================
// Public Profile API (인증 불필요)
// =====================================================

export const publicProfileApi = {
  /**
   * Get public profile by username (인증 불필요)
   */
  async getProfile(username: string): Promise<PublicProfile> {
    const response = await api.get<PublicProfile>(`/users/${encodeURIComponent(username)}/public-profile`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get public stats by username (인증 불필요)
   */
  async getStats(username: string): Promise<PublicStats> {
    const response = await api.get<PublicStats>(`/users/${encodeURIComponent(username)}/public-stats`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get public activity (grass) by username (인증 불필요)
   */
  async getActivity(username: string, days: number = 365): Promise<ActivityData> {
    const response = await api.get<ActivityData>(`/users/${encodeURIComponent(username)}/public-activity?days=${days}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get public farm by username (인증 불필요)
   */
  async getFarm(username: string): Promise<PublicFarm> {
    const response = await api.get<PublicFarm>(`/users/${encodeURIComponent(username)}/public-farm`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get public badges by username (인증 불필요)
   */
  async getBadges(username: string): Promise<PublicBadge[]> {
    const response = await api.get<Array<{
      id: string;
      name: string;
      icon: string;
      icon_url?: string;
      description: string;
      rarity: string;
    }>>(`/users/${encodeURIComponent(username)}/public-badges`, false);
    if (response.error) throw new Error(response.error.message);
    return (response.data || []).map(b => ({
      id: b.id,
      name: b.name,
      icon: b.icon,
      iconUrl: b.icon_url,
      description: b.description,
      rarity: b.rarity,
    }));
  },

  /**
   * Get public activity detail for a specific date (인증 불필요)
   */
  async getActivityByDate(username: string, date: string): Promise<DateActivityDetail> {
    const response = await api.get<DateActivityDetail>(`/users/${encodeURIComponent(username)}/public-activity/${date}`, false);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};
