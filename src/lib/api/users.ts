/**
 * Users API Functions
 */

import { api } from './client';
import type { User, Badge, ActivityDay, RecentActivity } from '../types';

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

export const usersApi = {
  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/users/me');
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
   * Get user statistics
   */
  async getStats(): Promise<UserStats> {
    const response = await api.get<UserStats>('/users/me/stats');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get user badges
   */
  async getBadges(): Promise<Badge[]> {
    const response = await api.get<Badge[]>('/users/me/badges');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
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
    const response = await api.get<RecentActivity[]>(`/users/me/recent?limit=${limit}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
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
