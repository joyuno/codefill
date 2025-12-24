/**
 * API Module Exports
 */

export { api, apiClient } from './client';
export {
  authApi,
  type SignupData,
  type LoginData,
  type AuthResponse,
  type TokenResponse,
  type OnboardingData,
  type RecoveryRequiredResponse,
  type RecoverData,
  type RecoverOAuthData,
} from './auth';
export { problemsApi, type ProblemFilters, type ProblemListResponse, type HintResponse } from './problems';
export {
  practiceApi,
  type BlankSubmission,
  type PuzzleSubmission,
  type BlankResult,
  type PuzzleResult,
  type RunCodeResult,
} from './practice';
export {
  chatApi,
  type ChatRequest,
  type ChatResponse,
  type CodeSearchResult,
  type SearchResponse,
} from './chat';
export {
  usersApi,
  type UserProfile,
  type UserStats,
  type ActivityData,
} from './users';
