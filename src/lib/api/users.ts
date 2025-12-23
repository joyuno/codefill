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
  description: string;
  earnedAt: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export const usersApi = {
  /**
   * Get current user profile (mypage optimized)
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
};
