/**
 * Analysis API Client
 *
 * API functions for AI-based learning analysis.
 */

import { api, apiClient } from './client';

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
  type?: string; // "methodical | exploratory | hint-dependent | independent | fast-learner | careful-thinker"
  description?: string; // 학습 스타일에 대한 설명
  strategy?: string; // 이 스타일에 맞는 학습 전략
}

// =====================================================
// Learning Analytics Framework Types
// =====================================================

/**
 * BKT (Bayesian Knowledge Tracing) - 토픽별 마스터리 확률
 */
export interface BKTTopicMastery {
  mastery: number;       // 마스터리 확률 (0.0~1.0)
  is_mastered: boolean;  // 80% 이상이면 true
  attempt_count: number; // 총 시도 횟수
  correct_count: number; // 정답 횟수
}

export interface BKTMastery {
  [topic: string]: BKTTopicMastery;
}

/**
 * Bloom's Taxonomy - 인지 단계별 성취도
 */
export interface BloomMetrics {
  apply_rate: number;    // easy 정답률 (Apply 단계)
  analyze_rate: number;  // medium 정답률 (Analyze 단계)
  create_rate: number;   // hard 정답률 (Create 단계)
  current_level: string; // "Remember" | "Apply" | "Analyze" | "Create"
  next_level: string;    // 다음 목표 레벨
  gap_analysis: string;  // 격차 분석 설명
}

/**
 * SRK Error Pattern - 오류 유형별 분석
 */
export interface ErrorPatternDetail {
  count: number;
  rate: number;
  examples: Array<{
    user: string;
    correct: string;
    reason: string;
  }>;
}

export interface ErrorAnalysis {
  dominant_type: "skill" | "rule" | "knowledge" | null;
  summary: string;
  total_errors?: number;
  patterns: {
    skill?: ErrorPatternDetail;
    rule?: ErrorPatternDetail;
    knowledge?: ErrorPatternDetail;
  };
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
  // AI 코칭 피드백 (마크다운 형식의 상세 피드백)
  detailedFeedback?: string;
  // 학습 분석 프레임워크 메트릭
  bktMastery?: BKTMastery;
  bloomMetrics?: BloomMetrics;
  errorAnalysis?: ErrorAnalysis;
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
 * 타임아웃을 120초로 설정 (LLM 호출 때문에 시간이 오래 걸릴 수 있음)
 */
export async function generateAnalysis() {
  return apiClient.request<AnalysisReport>('/analysis/generate', {
    method: 'POST',
    body: {},
    requireAuth: true,
    timeout: 120000, // 2분 타임아웃
  });
}

/**
 * Get recommended problems (separate from analysis)
 * 약점 기반 문제 추천을 별도로 요청
 */
export async function recommendProblems() {
  return apiClient.request<RecommendedProblem[]>('/analysis/recommend-problems', {
    method: 'POST',
    body: {},
    requireAuth: true,
    timeout: 60000, // 1분 타임아웃
  });
}

// Export as namespace
export const analysisApi = {
  getReport,
  generateAnalysis,
  recommendProblems,
};
