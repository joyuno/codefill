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
