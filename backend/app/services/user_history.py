"""
User History Service
사용자의 풀이 기록과 스킬 프로필을 조회하여 개인화된 추천에 활용
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UserHistoryService:
    """사용자 풀이 히스토리 서비스"""

    def __init__(self, db):
        self.db = db

    async def get_recent_attempts(
        self,
        user_id: str,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        최근 풀이 기록 조회

        Returns:
            List of recent attempts with problem info
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            result = self.db.table('attempts').select(
                'id, problem_id, problem_name, problem_type, difficulty, '
                'topics, is_correct, hints_used, time_spent, created_at'
            ).eq(
                'user_id', user_id
            ).gte(
                'created_at', cutoff_date
            ).order(
                'created_at', desc=True
            ).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching recent attempts: {e}")
            return []

    async def get_skill_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        사용자 스킬 프로필 조회

        Returns:
            Skill profile with weak/strong topics
        """
        try:
            result = self.db.table('user_skill_profiles').select(
                'weak_topics, strong_topics, '
                'recent_topics, updated_at'
            ).eq(
                'user_id', user_id
            ).single().execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"Error fetching skill profile: {e}")
            return None

    async def get_topic_stats(self, user_id: str) -> Dict[str, Any]:
        """
        주제별 통계 계산

        Returns:
            Topic statistics (success rate per topic, attempt counts)
        """
        try:
            # 최근 3개월 데이터
            cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()

            result = self.db.table('attempts').select(
                'topics, is_correct, difficulty'
            ).eq(
                'user_id', user_id
            ).gte(
                'created_at', cutoff_date
            ).not_.is_('is_correct', 'null').execute()

            if not result.data:
                return {}

            # 주제별 통계 계산
            topic_stats = {}
            for attempt in result.data:
                topics = attempt.get('topics') or []
                is_correct = attempt.get('is_correct', False)

                for topic in topics:
                    if topic not in topic_stats:
                        topic_stats[topic] = {
                            'total': 0,
                            'correct': 0,
                            'difficulties': []
                        }
                    topic_stats[topic]['total'] += 1
                    if is_correct:
                        topic_stats[topic]['correct'] += 1
                    topic_stats[topic]['difficulties'].append(attempt.get('difficulty'))

            # 성공률 계산
            for topic, stats in topic_stats.items():
                stats['success_rate'] = (
                    stats['correct'] / stats['total'] * 100
                    if stats['total'] > 0 else 0
                )
                # 가장 많이 푼 난이도
                if stats['difficulties']:
                    stats['common_difficulty'] = max(
                        set(stats['difficulties']),
                        key=stats['difficulties'].count
                    )
                del stats['difficulties']

            return topic_stats

        except Exception as e:
            logger.error(f"Error calculating topic stats: {e}")
            return {}

    async def get_personalization_context(self, user_id: str) -> Dict[str, Any]:
        """
        개인화 컨텍스트 생성 (LLM에 전달할 사용자 히스토리)

        Returns:
            Personalization context for LLM
        """
        # 병렬로 데이터 조회
        recent_attempts = await self.get_recent_attempts(user_id, limit=5)
        skill_profile = await self.get_skill_profile(user_id)

        context = {
            'has_history': len(recent_attempts) > 0,
            'recent_problems': [],
            'skill_summary': None,
            'recommendations': []
        }

        # 최근 풀이 요약
        if recent_attempts:
            for attempt in recent_attempts[:5]:
                context['recent_problems'].append({
                    'name': attempt.get('problem_name', '문제'),
                    'topics': attempt.get('topics', []),
                    'difficulty': attempt.get('difficulty'),
                    'solved': attempt.get('is_correct', False),
                    'type': attempt.get('problem_type'),
                })

            # 최근 주제 추출
            recent_topics = set()
            for attempt in recent_attempts:
                for topic in (attempt.get('topics') or []):
                    recent_topics.add(topic)
            context['recent_topics'] = list(recent_topics)[:5]

        # 스킬 프로필 요약
        if skill_profile:
            context['skill_summary'] = {
                'weak_topics': skill_profile.get('weak_topics', [])[:3],
                'strong_topics': skill_profile.get('strong_topics', [])[:3],
            }

            # 추천 생성 (약점 주제 기반)
            weak_topics = skill_profile.get('weak_topics', [])
            if weak_topics:
                context['recommendations'].append({
                    'type': 'weak_topic',
                    'topics': weak_topics[:2],
                    'reason': '아직 연습이 더 필요한 주제'
                })

        # 최근 풀이 기반 추천
        if recent_attempts:
            last_attempt = recent_attempts[0]
            last_topics = last_attempt.get('topics', [])
            was_correct = last_attempt.get('is_correct', False)
            last_difficulty = last_attempt.get('difficulty', 'easy')

            if was_correct and last_topics:
                # 성공했으면 더 어려운 문제 추천
                next_difficulty = self._get_next_difficulty(last_difficulty)
                context['recommendations'].append({
                    'type': 'level_up',
                    'topics': last_topics,
                    'difficulty': next_difficulty,
                    'reason': f'이전에 {last_topics[0]}를 잘 풀었어요'
                })
            elif not was_correct and last_topics:
                # 실패했으면 같은 주제 다시 추천
                context['recommendations'].append({
                    'type': 'retry',
                    'topics': last_topics,
                    'difficulty': last_difficulty,
                    'reason': f'{last_topics[0]} 연습을 더 해볼까요?'
                })

        return context

    def _get_next_difficulty(self, current: str) -> str:
        """다음 난이도 계산"""
        difficulty_order = ['easy', 'medium', 'medium_hard', 'hard', 'very_hard']
        try:
            idx = difficulty_order.index(current)
            return difficulty_order[min(idx + 1, len(difficulty_order) - 1)]
        except ValueError:
            return 'medium'


def get_user_history_service(db) -> UserHistoryService:
    """UserHistoryService 인스턴스 생성"""
    return UserHistoryService(db)
