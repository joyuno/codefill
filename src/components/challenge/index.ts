/**
 * Challenge Page Components
 *
 * 퀘스트 보드 페이지에서 사용되는 컴포넌트들
 */

// 핵심 컴포넌트
export { StatsSummary } from './StatsSummary';
export { QuestSection } from './QuestSection';
export { QuestCard } from './QuestCard';
export { QuestProgress } from './QuestProgress';
export { LeaderboardSection } from './LeaderboardSection';
export { RankingModal } from './RankingModal';

// Legacy (StatsSummary에 기능 통합됨)
/** @deprecated StatsSummary를 대신 사용하세요 */
export { AdventurerRank } from './AdventurerRank';

// 타입 re-export
export type { Mission, MissionConditionType, MissionDifficulty, MissionStatus } from '@/lib/api/missions';
