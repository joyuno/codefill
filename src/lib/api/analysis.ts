/**
 * Analysis API Client
 *
 * API functions for AI-based learning analysis.
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export interface TopicScore {
  topic: string;
  score: number;
  insight?: string; // LLM이 생성한 인사이트
}

export interface StatsSnapshot {
  level: number;
  problemsSolved: number;
  accuracy: number;
  streak: number;
}

export interface RecommendedProblem {
  id: string;
  originalId?: string;
  name: string;
  difficulty: string;
  topic: string;
  reason: string;
}

export interface HintUsage {
  total_requested: number;
  by_level?: Record<string, number>; // 레벨별 힌트 사용 횟수 {"1": 5, "2": 3}
  helpful_count: number;
  helpful_rate: number;
  avg_per_problem?: number; // 문제당 평균 힌트 수
  avg_hint_level: number;
}

export interface LearningStyle {
  prefers_examples?: boolean;
  prefers_analogies?: boolean;
  hint_sensitivity?: string; // "low" | "medium" | "high"
  pace?: string; // "slow" | "medium" | "fast"
}

export interface AnalysisReport {
  id?: string;
  summaryText: string;
  strengths: TopicScore[];
  weaknesses: TopicScore[];
  recommendations: string[];
  studyPlan?: string;
  skillSnapshot: Record<string, number>;
  statsSnapshot: StatsSnapshot;
  difficultySnapshot: Record<string, number>;
  recommendedProblems: RecommendedProblem[];
  createdAt?: string;
  // 새로 추가된 필드들
  conceptsStruggling: string[];
  conceptsLearned: string[];
  hintUsage?: HintUsage;
  learningStyle?: LearningStyle;
  commonErrorPatterns: string[];
  moodDistribution: Record<string, number>;
  breakthroughMoments: string[];
  teachingNotes: string[];
}

export interface AnalysisReportResponse {
  hasReport: boolean;
  report?: AnalysisReport;
}

// =====================================================
// API Functions
// =====================================================

/**
 * Get latest analysis report
 */
export async function getReport() {
  return api.get<AnalysisReportResponse>('/analysis/report', true);
}

/**
 * Generate new AI analysis
 */
export async function generateAnalysis() {
  return api.post<AnalysisReport>('/analysis/generate', {}, true);
}

// Export as namespace
export const analysisApi = {
  getReport,
  generateAnalysis,
};
