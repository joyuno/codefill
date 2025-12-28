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
export {
  problemsApi,
  type ProblemFilters,
  type ProblemListResponse,
  type HintResponse,
  type BaseProblemListItem,
  type BaseProblemDetail,
  type BaseProblemListResponse,
  type BaseProblemFilters,
} from './problems';
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
export {
  translateText,
  detectLanguage,
  getSupportedLanguages,
  LANGUAGE_LABELS,
  type LanguageCode,
  type TranslateResponse,
  type DetectResponse,
} from './translate';
export {
  farmApi,
  type CharacterData,
  type FarmSlot,
  type UserFarm,
  type FarmItem,
  type InventoryItem,
  type PlantResponse,
  type HarvestResponse,
  type BuyResponse,
  type SellResponse,
  type ExpansionOption,
  type ExpansionCostsResponse,
  type ExpandResponse,
} from './farm';
