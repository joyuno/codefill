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
  type BannedResponse,
  type RecoverData,
  type RecoverOAuthData,
} from './auth';
export {
  problemsApi,
  type BaseProblemListItem,
  type BaseProblemDetail,
  type BaseProblemListResponse,
  type BaseProblemFilters,
  type ProblemStatsResponse,
  type ProblemLikeResponse,
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
  publicProfileApi,
  type UserProfile,
  type UserStats,
  type ActivityData,
  type DateActivityDetail,
  type SolvedProblem,
  type SolvedAcProfileSimple,
  // Public Profile Types
  type PublicProfile,
  type PublicStats,
  type PublicFarm,
  type PublicFarmCharacter,
  type PublicFarmSlot,
  type PublicBadge,
} from './users';
export {
  agentApi,
  type ChatAgentRequest,
  type ChatAgentResponse,
  type ChatAgentMessage,
  type CollectedInfo,
  type BaseProblemInfo,
  type ProblemGenerationRequest,
  type BlankProblemResponse,
  type PuzzleProblemResponse,
  type GuidedProblemResponse,
  type CodeGenerationResponse,
  type HintAgentRequest,
  type HintAgentResponse,
  type RAGSearchResponse,
  type RecommendResponse,
  // Intent-Based Chat
  type SessionContext,
  type IntentChatRequest,
  type IntentChatResponse,
  type IntentInfo,
} from './agent';
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
  // Core Types
  type CharacterData,
  type UserFarm,
  type FarmItem,
  type InventoryItem,
  type BuyResponse,
  type SellResponse,
  type ExpansionOption,
  type ExpansionCostsResponse,
  type ExpandResponse,
  // Slot-based Farm System Types (신규)
  type FarmSlot,
  type PlantSlotResponse,
  type HarvestSlotResponse,
  // 통합 배치 시스템 (Unified Placement System)
  type UnifiedShopItem,
  type PlacedItem,
  type ItemMetadata,
  type FarmPlotData,
  type UnifiedShopResponse,
  type PlacedItemsResponse,
  type PlaceItemResponse,
  type MoveItemResponse,
  type RemoveItemResponse,
  type PlantCropResponse,
  type HarvestCropResponse,
} from './farm';
export {
  solutionsApi,
  type SolutionAuthor,
  type SolutionListItem,
  type SolutionDetail,
  type SolutionListResponse,
  type CommentItem,
  type CommentListResponse,
  type VoteResponse,
  type OfficialSolution,
  type ProblemDiscussionResponse,
  type SolutionCreateData,
  type SolutionUpdateData,
  type CommentCreateData,
} from './solutions';
export {
  friendsApi,
  type FriendRequest,
  type Friend,
  type FriendListResponse,
  type FriendRequestsResponse,
  type SentRequest,
  type SentRequestsResponse,
  type Message,
  type ConversationResponse,
  type UserSearchResult,
  type UserSearchResponse,
  type UnreadCountResponse,
} from './friends';
export {
  solvedacApi,
  tierToName,
  getTierColor,
  type SolvedAcOrganization,
  type SolvedAcProfile,
  type SolvedAcProfileDB,
  type LinkSolvedAcRequest,
  type LinkSolvedAcResponse,
  type SyncSolvedAcResponse,
  type TierInfo,
} from './solvedac';
export {
  analysisApi,
  type TopicScore,
  type StatsSnapshot,
  type RecommendedProblem,
  type AnalysisReport,
  type AnalysisReportResponse,
} from './analysis';
export {
  rankingApi,
} from './ranking';
export type {
  RankingPeriod,
  RankingType,
  RankingItem,
  RankingListResponse,
  MyRankingSummary,
  ChallengePageData,
} from './ranking';
export {
  missionsApi,
  type Mission,
  type DailyMissionsResponse,
  type WeeklyChallengesResponse,
  type ClaimRewardResponse,
  type MissionsSummary,
  type AllMissionsResponse,
} from './missions';
export {
  adminApi,
  type AdminUser,
  type AdminUserDetail,
  type AdminUserListResponse,
  type AdminProblem,
  type AdminProblemListResponse,
  type AdminProblemDetail,
  type AdminDashboardStats,
  type BlankVariant,
  type PuzzleVariant,
  type GuidedVariant,
  type CreateBaseProblemRequest,
  type CreateBlankProblemRequest,
  type CreatePuzzleProblemRequest,
  type CreateGuidedProblemRequest,
} from './admin';
