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

export interface WrongProblem {
  id: string;
  originalId?: string;  // 문제 페이지 이동용
  name: string;
  problemType?: string;
  difficulty: string;
  topics: string[];
  hintsUsed: number;
  lastAttemptAt?: string;
}

export interface WrongProblemsResponse {
  problems: WrongProblem[];
  total: number;
  hasMore: boolean;
}

export interface WrongProblemsParams {
  limit?: number;
  offset?: number;
  sortBy?: 'recent' | 'difficulty' | 'hints';
  difficulty?: string;
  topic?: string;
}

export interface HintUsage {
  total_requested: number;
  by_level?: Record<string, number>; // 레벨별 힌트 사용 횟수 {"1": 5, "2": 3}
  helpful_count: number;
  helpful_rate: number;
  avg_per_problem?: number; // 문제당 평균 힌트 수
  avg_hint_level: number;
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

// =====================================================
// Visualization Types (새로운 시각화용)
// =====================================================

/**
 * 문제 유형별 정답률
 */
export interface ProblemTypeStat {
  type: string;     // blank, puzzle, guided, implementation
  total: number;    // 총 시도 횟수
  success: number;  // 성공 횟수
  rate: number;     // 정답률 (0.0~1.0)
}

/**
 * 최근 시도 기록
 */
export interface RecentAttempt {
  problem_name: string;
  problem_type?: string;
  difficulty?: string;
  topics?: string[];
  is_correct: boolean;
  hints_used: number;
  created_at?: string;
}

/**
 * 힌트 독립성 (힌트 없이 해결한 비율)
 */
export interface HintIndependence {
  solved_without_hint: number;  // 힌트 없이 성공
  solved_with_hint: number;     // 힌트로 성공
  failed_with_hint: number;     // 힌트 줘도 실패
  failed_without_hint: number;  // 힌트 없이 실패
  total: number;
  independence_rate: number;    // 힌트 없이 성공 비율
}

/**
 * ELO 히스토리 엔트리 (DB update_user_elo() 함수 형식)
 */
export interface EloHistoryEntry {
  date: string;
  topic: string;
  before: number;
  after: number;
  change: number;
  problem_elo: number;
  expected: number;
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
  // 추가 데이터
  conceptsStruggling: string[];
  conceptsLearned: string[];
  hintUsage?: HintUsage;
  commonErrorPatterns: string[];
  moodDistribution: Record<string, number>;
  breakthroughMoments: string[];
  teachingNotes: string[];
  // AI 코칭 피드백 (마크다운 형식의 상세 피드백)
  detailedFeedback?: string;
  // 학습 분석 프레임워크 메트릭
  bktMastery?: BKTMastery;
  bloomMetrics?: BloomMetrics;
  // 새로운 시각화 데이터
  problemTypeStats?: ProblemTypeStat[];
  recent10Attempts?: RecentAttempt[];
  recent10Analysis?: string;
  hintIndependence?: HintIndependence;
  // ELO 성장 데이터
  eloHistory?: EloHistoryEntry[];
  eloOverall?: number;
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

/**
 * Get wrong problems for review
 * 틀린 문제 목록 조회 (복습용)
 */
export async function getWrongProblems(params?: WrongProblemsParams) {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.sortBy) searchParams.set('sort_by', params.sortBy);
  if (params?.difficulty) searchParams.set('difficulty', params.difficulty);
  if (params?.topic) searchParams.set('topic', params.topic);

  const query = searchParams.toString();
  const url = `/analysis/wrong-problems${query ? `?${query}` : ''}`;

  return api.get<WrongProblemsResponse>(url, true);
}

// Export as namespace
export const analysisApi = {
  getReport,
  generateAnalysis,
  recommendProblems,
  getWrongProblems,
};
