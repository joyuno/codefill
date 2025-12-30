"""
Legacy vs V2 비교 평가 시스템

두 시스템의 성능을 동일한 기준으로 평가하고 비교합니다.

평가 항목:
1. 응답 품질 (response_quality)
2. 의도 파악 정확도 (intent_accuracy)
3. 정보 수집 효율 (info_efficiency)
4. 응답 시간 (latency)
5. 사용자 경험 (ux_score)
"""
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ComparisonResult:
    """비교 평가 결과"""
    test_case: str
    message: str

    # Legacy 결과
    legacy_response: str
    legacy_intent: str
    legacy_confidence: float
    legacy_latency_ms: float

    # V2 결과
    v2_response: str
    v2_intent: str
    v2_confidence: float
    v2_stage: str
    v2_latency_ms: float

    # 평가 점수 (0-1)
    legacy_score: float
    v2_score: float

    # 세부 평가
    evaluation_detail: Dict[str, Any]

    # 승자
    winner: str  # "legacy", "v2", "tie"

    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ============================================================
# 효율적인 평가 프롬프트
# ============================================================

COMPARISON_EVAL_PROMPT = """당신은 AI 챗봇 응답 품질 평가 전문가입니다.
두 시스템(Legacy, V2)의 응답을 비교 평가해주세요.

## 테스트 케이스
사용자 메시지: {message}
기대 의도: {expected_intent}
기대 동작: {expected_behavior}

## Legacy 시스템 응답
- 분류된 의도: {legacy_intent} (신뢰도: {legacy_confidence:.2f})
- 응답 메시지: {legacy_response}
- 처리 시간: {legacy_latency:.0f}ms

## V2 시스템 응답
- 현재 단계: {v2_stage}
- 분류된 의도: {v2_intent} (신뢰도: {v2_confidence:.2f})
- 응답 메시지: {v2_response}
- 처리 시간: {v2_latency:.0f}ms

## 평가 기준 (각 항목 0.0~1.0)
1. intent_accuracy: 의도 분류가 정확한가?
2. response_relevance: 응답이 요청과 관련있는가?
3. response_helpfulness: 응답이 실제로 도움이 되는가?
4. conversation_flow: 대화 흐름이 자연스러운가?
5. action_clarity: 다음 행동이 명확한가?

## 응답 형식 (JSON)
{{
  "legacy": {{
    "intent_accuracy": 0.0~1.0,
    "response_relevance": 0.0~1.0,
    "response_helpfulness": 0.0~1.0,
    "conversation_flow": 0.0~1.0,
    "action_clarity": 0.0~1.0,
    "total": 0.0~1.0,
    "issues": ["문제점..."]
  }},
  "v2": {{
    "intent_accuracy": 0.0~1.0,
    "response_relevance": 0.0~1.0,
    "response_helpfulness": 0.0~1.0,
    "conversation_flow": 0.0~1.0,
    "action_clarity": 0.0~1.0,
    "total": 0.0~1.0,
    "issues": ["문제점..."]
  }},
  "winner": "legacy" | "v2" | "tie",
  "reasoning": "판단 근거",
  "improvement_suggestions": {{
    "legacy": ["개선점..."],
    "v2": ["개선점..."]
  }}
}}"""


# ============================================================
# 테스트 케이스 정의
# ============================================================

TEST_CASES = [
    {
        "id": "intent_dp",
        "message": "DP 문제 풀고 싶어",
        "expected_intent": "topic_specific",
        "expected_behavior": "DP 관련 문제 검색 또는 추가 정보 요청",
        "category": "problem_search",
    },
    {
        "id": "intent_random",
        "message": "아무거나 추천해줘",
        "expected_intent": "random_recommend",
        "expected_behavior": "랜덤 문제 추천",
        "category": "problem_search",
    },
    {
        "id": "intent_greeting",
        "message": "안녕!",
        "expected_intent": "greeting",
        "expected_behavior": "인사 응답 및 도움 제안",
        "category": "general",
    },
    {
        "id": "intent_difficulty",
        "message": "쉬운 문제로 해줘",
        "expected_intent": "difficulty_change",
        "expected_behavior": "난이도 변경 확인",
        "category": "preference",
    },
    {
        "id": "intent_selection",
        "message": "1번으로 할게",
        "expected_intent": "problem_selection",
        "expected_behavior": "문제 선택 처리",
        "category": "selection",
    },
    {
        "id": "intent_hint",
        "message": "힌트 줘",
        "expected_intent": "hint_request",
        "expected_behavior": "힌트 제공 또는 문제 선택 요청",
        "category": "solving",
    },
    {
        "id": "intent_complex",
        "message": "BFS 쉬운 문제 파이썬으로 풀고 싶어",
        "expected_intent": "topic_specific",
        "expected_behavior": "BFS + easy + python 조건으로 검색",
        "category": "problem_search",
    },
    {
        "id": "intent_thanks",
        "message": "고마워!",
        "expected_intent": "thanks",
        "expected_behavior": "감사 응답",
        "category": "general",
    },
]


# ============================================================
# 비교 평가 함수
# ============================================================

async def run_comparison_test(
    legacy_func,
    v2_func,
    test_case: Dict[str, Any],
) -> ComparisonResult:
    """
    단일 테스트 케이스에 대해 Legacy와 V2 비교 실행
    """
    from ..services.openrouter import openrouter_service

    message = test_case["message"]

    # Legacy 실행
    legacy_start = time.time()
    try:
        legacy_result = await legacy_func(message)
        legacy_latency = (time.time() - legacy_start) * 1000
    except Exception as e:
        legacy_result = {"response": f"Error: {e}", "intent": "error", "confidence": 0}
        legacy_latency = 0

    # V2 실행
    v2_start = time.time()
    try:
        v2_result = await v2_func(message)
        v2_latency = (time.time() - v2_start) * 1000
    except Exception as e:
        v2_result = {"response": f"Error: {e}", "intent": "error", "stage": "error", "confidence": 0}
        v2_latency = 0

    # LLM 평가
    # 응답을 문자열로 안전하게 변환
    legacy_response_str = str(legacy_result.get("response", "") or "")[:500]
    v2_response_str = str(v2_result.get("response", "") or "")[:500]

    eval_prompt = COMPARISON_EVAL_PROMPT.format(
        message=message,
        expected_intent=test_case["expected_intent"],
        expected_behavior=test_case["expected_behavior"],
        legacy_intent=legacy_result.get("intent", "unknown"),
        legacy_confidence=legacy_result.get("confidence", 0),
        legacy_response=legacy_response_str,
        legacy_latency=legacy_latency,
        v2_stage=v2_result.get("stage", "unknown"),
        v2_intent=v2_result.get("intent", "unknown"),
        v2_confidence=v2_result.get("confidence", 0),
        v2_response=v2_response_str,
        v2_latency=v2_latency,
    )

    try:
        eval_response = await openrouter_service.chat_completion(
            messages=[{"role": "user", "content": eval_prompt}],
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        eval_content = openrouter_service.get_content(eval_response)
        evaluation = openrouter_service.parse_json_response(eval_content)
    except Exception as e:
        print(f"[ComparisonEval] Evaluation error: {e}")
        evaluation = {
            "legacy": {"total": 0.5},
            "v2": {"total": 0.5},
            "winner": "tie",
            "reasoning": f"평가 실패: {e}",
        }

    return ComparisonResult(
        test_case=test_case["id"],
        message=message,
        legacy_response=str(legacy_result.get("response", "") or "")[:200],
        legacy_intent=legacy_result.get("intent", "unknown"),
        legacy_confidence=legacy_result.get("confidence", 0),
        legacy_latency_ms=legacy_latency,
        v2_response=str(v2_result.get("response", "") or "")[:200],
        v2_intent=v2_result.get("intent", "unknown"),
        v2_confidence=v2_result.get("confidence", 0),
        v2_stage=v2_result.get("stage", "unknown"),
        v2_latency_ms=v2_latency,
        legacy_score=evaluation.get("legacy", {}).get("total", 0.5),
        v2_score=evaluation.get("v2", {}).get("total", 0.5),
        evaluation_detail=evaluation,
        winner=evaluation.get("winner", "tie"),
    )


async def run_all_comparison_tests(
    legacy_func,
    v2_func,
    test_cases: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    모든 테스트 케이스에 대해 비교 평가 실행
    """
    test_cases = test_cases or TEST_CASES
    results = []

    for tc in test_cases:
        print(f"\n[Test] Running: {tc['id']} - '{tc['message']}'")
        result = await run_comparison_test(legacy_func, v2_func, tc)
        results.append(result)

        # 결과 출력
        status = "🏆" if result.winner == "v2" else "🥈" if result.winner == "legacy" else "🤝"
        print(f"  {status} Winner: {result.winner}")
        print(f"  Legacy: {result.legacy_score:.2f} ({result.legacy_latency_ms:.0f}ms)")
        print(f"  V2: {result.v2_score:.2f} ({result.v2_latency_ms:.0f}ms)")

    # 집계
    legacy_wins = sum(1 for r in results if r.winner == "legacy")
    v2_wins = sum(1 for r in results if r.winner == "v2")
    ties = sum(1 for r in results if r.winner == "tie")

    legacy_avg_score = sum(r.legacy_score for r in results) / len(results)
    v2_avg_score = sum(r.v2_score for r in results) / len(results)

    legacy_avg_latency = sum(r.legacy_latency_ms for r in results) / len(results)
    v2_avg_latency = sum(r.v2_latency_ms for r in results) / len(results)

    summary = {
        "total_tests": len(results),
        "legacy_wins": legacy_wins,
        "v2_wins": v2_wins,
        "ties": ties,
        "legacy_avg_score": legacy_avg_score,
        "v2_avg_score": v2_avg_score,
        "legacy_avg_latency_ms": legacy_avg_latency,
        "v2_avg_latency_ms": v2_avg_latency,
        "overall_winner": "v2" if v2_wins > legacy_wins else "legacy" if legacy_wins > v2_wins else "tie",
        "recommendation": _generate_recommendation(results, legacy_avg_score, v2_avg_score),
    }

    return {
        "summary": summary,
        "results": [asdict(r) for r in results],
        "timestamp": datetime.now().isoformat(),
    }


def _generate_recommendation(
    results: List[ComparisonResult],
    legacy_score: float,
    v2_score: float,
) -> str:
    """최종 추천 생성"""
    diff = v2_score - legacy_score

    if diff > 0.1:
        return "V2 시스템이 전반적으로 우수합니다. V2로 전환을 권장합니다."
    elif diff < -0.1:
        return "Legacy 시스템이 전반적으로 우수합니다. Legacy 유지를 권장합니다."
    else:
        # 카테고리별 분석
        categories = {}
        for r in results:
            cat = r.evaluation_detail.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"legacy": [], "v2": []}
            categories[cat]["legacy"].append(r.legacy_score)
            categories[cat]["v2"].append(r.v2_score)

        return (
            "두 시스템의 성능이 비슷합니다. "
            "V2의 모듈화된 구조가 유지보수에 유리하므로 점진적 전환을 권장합니다."
        )


# ============================================================
# 간편 실행 함수
# ============================================================

async def quick_comparison(message: str) -> Dict[str, Any]:
    """
    단일 메시지에 대한 빠른 비교

    Usage:
        result = await quick_comparison("DP 문제 풀고 싶어")
    """
    from ..graphs import ChatGraph, ChatOrchestrator

    legacy_graph = ChatGraph()
    v2_orchestrator = ChatOrchestrator()

    async def legacy_func(msg):
        result = await legacy_graph.invoke(message=msg)
        return {
            "response": result.get("response_message", ""),
            "intent": result.get("intent_result", {}).get("intent", "unknown"),
            "confidence": result.get("intent_result", {}).get("confidence", 0),
        }

    async def v2_func(msg):
        result = await v2_orchestrator.process(message=msg)
        return {
            "response": result.get("response_message", ""),
            "intent": result.get("intent_result", {}).get("intent", "unknown"),
            "confidence": result.get("intent_result", {}).get("confidence", 0),
            "stage": result.get("stage", "unknown"),
        }

    test_case = {
        "id": "quick_test",
        "message": message,
        "expected_intent": "unknown",
        "expected_behavior": "적절한 응답",
    }

    return await run_comparison_test(legacy_func, v2_func, test_case)
