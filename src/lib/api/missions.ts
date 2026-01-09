/**
 * Missions API Client
 * Daily Missions and Weekly Challenges
 */

import { api } from './client';

// ============================================================
// Types
// ============================================================

export interface Mission {
  id: string;
  missionId: string;
  code: string;
  name: string;
  description: string | null;
  conditionType: string; // 'problems', 'blank', 'puzzle', 'output', 'bug', 'refactor'
  conditionValue: number;
  difficulty: string | null; // 'easy', 'medium', 'hard', null=all
  currentProgress: number;
  targetValue: number;
  status: 'active' | 'completed' | 'claimed';
  rewardGold: number;
  rewardXp: number;
  rewardSeeds: Record<string, number> | null;
}

export interface DailyMissionsResponse {
  missions: Mission[];
  todayCompleted: number;
  todayClaimed: number;
}

export interface WeeklyChallengesResponse {
  challenges: Mission[];
  weekCompleted: number;
  weekClaimed: number;
}

export interface ClaimRewardResponse {
  success: boolean;
  goldEarned: number;
  xpEarned: number;
  seedsEarned: Record<string, number> | null;
  newGoldBalance: number;
  error?: string;
}

export interface MissionsSummary {
  dailyActive: number;
  dailyCompleted: number;
  dailyClaimed: number;
  weeklyActive: number;
  weeklyCompleted: number;
  weeklyClaimed: number;
  todayGoldEarned: number;
  todayXpEarned: number;
}

export interface AllMissionsResponse {
  daily: DailyMissionsResponse;
  weekly: WeeklyChallengesResponse;
}

// ============================================================
// API Response Transformers
// ============================================================

function transformMission(data: Record<string, unknown>): Mission {
  return {
    id: data.id as string,
    missionId: data.mission_id as string,
    code: data.code as string,
    name: data.name as string,
    description: data.description as string | null,
    conditionType: data.condition_type as string,
    conditionValue: data.condition_value as number,
    difficulty: data.difficulty as string | null,
    currentProgress: data.current_progress as number,
    targetValue: data.target_value as number,
    status: data.status as 'active' | 'completed' | 'claimed',
    rewardGold: data.reward_gold as number,
    rewardXp: data.reward_xp as number,
    rewardSeeds: data.reward_seeds as Record<string, number> | null,
  };
}

function transformDailyResponse(data: Record<string, unknown>): DailyMissionsResponse {
  const missions = (data.missions as Record<string, unknown>[]) || [];
  return {
    missions: missions.map(transformMission),
    todayCompleted: data.today_completed as number,
    todayClaimed: data.today_claimed as number,
  };
}

function transformWeeklyResponse(data: Record<string, unknown>): WeeklyChallengesResponse {
  const challenges = (data.challenges as Record<string, unknown>[]) || [];
  return {
    challenges: challenges.map(transformMission),
    weekCompleted: data.week_completed as number,
    weekClaimed: data.week_claimed as number,
  };
}

function transformClaimResponse(data: Record<string, unknown>): ClaimRewardResponse {
  return {
    success: data.success as boolean,
    goldEarned: data.gold_earned as number,
    xpEarned: data.xp_earned as number,
    seedsEarned: data.seeds_earned as Record<string, number> | null,
    newGoldBalance: data.new_gold_balance as number,
    error: data.error as string | undefined,
  };
}

// ============================================================
// API Functions
// ============================================================

/**
 * Get today's daily missions (auto-creates if none exist)
 */
export async function getDailyMissions(): Promise<DailyMissionsResponse | null> {
  const response = await api.get<Record<string, unknown>>('/missions/daily');
  if (response.error || !response.data) {
    console.error('[Missions] getDailyMissions error:', response.error);
    return null;
  }
  return transformDailyResponse(response.data);
}

/**
 * Get this week's challenges (auto-creates if none exist)
 */
export async function getWeeklyChallenges(): Promise<WeeklyChallengesResponse | null> {
  const response = await api.get<Record<string, unknown>>('/missions/weekly');
  if (response.error || !response.data) {
    console.error('[Missions] getWeeklyChallenges error:', response.error);
    return null;
  }
  return transformWeeklyResponse(response.data);
}

/**
 * Get all missions (daily + weekly) in one call
 */
export async function getAllMissions(): Promise<AllMissionsResponse | null> {
  const response = await api.get<{
    daily: Record<string, unknown>;
    weekly: Record<string, unknown>;
  }>('/missions/all');

  if (response.error || !response.data) {
    console.error('[Missions] getAllMissions error:', response.error);
    return null;
  }

  return {
    daily: transformDailyResponse(response.data.daily),
    weekly: transformWeeklyResponse(response.data.weekly),
  };
}

/**
 * Claim mission reward
 */
export async function claimMissionReward(missionId: string): Promise<ClaimRewardResponse | null> {
  const response = await api.post<Record<string, unknown>>(`/missions/${missionId}/claim`);
  if (response.error || !response.data) {
    console.error('[Missions] claimMissionReward error:', response.error);
    return {
      success: false,
      goldEarned: 0,
      xpEarned: 0,
      seedsEarned: null,
      newGoldBalance: 0,
      error: response.error?.message || 'Unknown error',
    };
  }
  return transformClaimResponse(response.data);
}

/**
 * Get missions summary (for dashboard/sidebar)
 */
export async function getMissionsSummary(): Promise<MissionsSummary | null> {
  const response = await api.get<{
    daily_active: number;
    daily_completed: number;
    daily_claimed: number;
    weekly_active: number;
    weekly_completed: number;
    weekly_claimed: number;
    today_gold_earned: number;
    today_xp_earned: number;
  }>('/missions/summary');

  if (response.error || !response.data) {
    console.error('[Missions] getMissionsSummary error:', response.error);
    return null;
  }

  const data = response.data;
  return {
    dailyActive: data.daily_active,
    dailyCompleted: data.daily_completed,
    dailyClaimed: data.daily_claimed,
    weeklyActive: data.weekly_active,
    weeklyCompleted: data.weekly_completed,
    weeklyClaimed: data.weekly_claimed,
    todayGoldEarned: data.today_gold_earned,
    todayXpEarned: data.today_xp_earned,
  };
}

// ============================================================
// Export consolidated API object
// ============================================================

export const missionsApi = {
  getDailyMissions,
  getWeeklyChallenges,
  getAllMissions,
  claimMissionReward,
  getMissionsSummary,
};
