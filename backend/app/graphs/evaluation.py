"""
LangGraph Evaluation Module

각 그래프 단계별 성능을 LLM으로 평가합니다.

평가 항목:
1. Intent Graph: 의도 분류 정확도, 정보 수집 완성도
2. Discovery Graph: 검색 결과 적절성, 문제 선택 정확도
3. Solving Graph: 힌트 품질, 피드백 적절성

사용법:
```python
from backend.app.graphs.evaluation import evaluate_stage

result = await evaluate_stage(
    stage="intent",
    input_data={"message": "DP 문제 풀고 싶어"},
    output_data={"intent": "topic_specific", "topics": ["DP"]},
)
# result: {"score": 0.9, "issues": [], "suggestions": [...]}
```
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class EvaluationResult:
    """평가 결과"""
    def __init__(
        self,
        stage: str,
        score: float,
        metrics: Dict[str, float],
        issues: List[str],
        suggestions: List[str],
        latency_ms: float,
        timestamp: str,
    ):
        self.stage = stage
        self.score = score  # 0.0 ~ 1.0
        self.metrics = metrics
        self.issues = issues
        self.suggestions = suggestions
        self.latency_ms = latency_ms
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "score": self.score,
            "metrics": self.metrics,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }

    @property
    def needs_improvement(self) -> bool:
        return self.score < 0.7 or len(self.issues) > 0


# ============================================================
# Stage-specific Evaluation Prompts
# ============================================================

INTENT_EVAL_PROMPT = """당신은 AI 챗봇의 의도 분류 품질을 평가하는 전문가입니다.

## 입력
사용자 메시지: {message}
대화 히스토리: {conversation_history}

## 출력
분류된 의도: {intent}
신뢰도: {confidence}
수집된 정보: {collected_info}
응답 메시지: {response_message}

## 평가 기준
1. intent_accuracy: 의도 분류가 정확한가? (0.0~1.0)
2. info_completeness: 필요한 정보가 충분히 수집되었는가? (0.0~1.0)
3. response_quality: 응답이 자연스럽고 도움이 되는가? (0.0~1.0)
4. context_awareness: 대화 맥락을 잘 이해했는가? (0.0~1.0)

## 응답 형식 (JSON)
{{
  "metrics": {{
    "intent_accuracy": 0.0~1.0,
    "info_completeness": 0.0~1.0,
    "response_quality": 0.0~1.0,
    "context_awareness": 0.0~1.0
  }},
  "issues": ["발견된 문제점들..."],
  "suggestions": ["개선 제안들..."],
  "reasoning": "평가 근거"
}}"""

DISCOVERY_EVAL_PROMPT = """당신은 AI 챗봇의 문제 검색/선택 품질을 평가하는 전문가입니다.

## 입력
사용자 요청: {collected_info}
검색 쿼리: {query}

## 출력
검색 결과 수: {result_count}
검색된 문제들: {search_results}
선택된 문제: {selected_problem}
응답 메시지: {response_message}

## 평가 기준
1. search_relevance: 검색 결과가 요청과 관련있는가? (0.0~1.0)
2. result_diversity: 결과가 다양한가? (0.0~1.0)
3. difficulty_match: 난이도가 요청과 일치하는가? (0.0~1.0)
4. topic_match: 주제가 요청과 일치하는가? (0.0~1.0)

## 응답 형식 (JSON)
{{
  "metrics": {{
    "search_relevance": 0.0~1.0,
    "result_diversity": 0.0~1.0,
    "difficulty_match": 0.0~1.0,
    "topic_match": 0.0~1.0
  }},
  "issues": ["발견된 문제점들..."],
  "suggestions": ["개선 제안들..."],
  "reasoning": "평가 근거"
}}"""

SOLVING_EVAL_PROMPT = """당신은 AI 튜터의 힌트/피드백 품질을 평가하는 전문가입니다.

## 입력
문제 정보: {problem_context}
사용자 진행 상황: {user_progress}
사용자 메시지: {message}

## 출력
분류된 의도: {intent}
힌트 레벨: {hint_level}
응답 메시지: {response_message}
정답 여부: {is_correct}

## 평가 기준
1. hint_quality: 힌트가 적절하고 도움이 되는가? (0.0~1.0)
2. pedagogical_value: 교육적 가치가 있는가? (0.0~1.0)
3. progression: 점진적 힌트 제공이 잘 되는가? (0.0~1.0)
4. encouragement: 학습 동기 부여가 되는가? (0.0~1.0)

## 응답 형식 (JSON)
{{
  "metrics": {{
    "hint_quality": 0.0~1.0,
    "pedagogical_value": 0.0~1.0,
    "progression": 0.0~1.0,
    "encouragement": 0.0~1.0
  }},
  "issues": ["발견된 문제점들..."],
  "suggestions": ["개선 제안들..."],
  "reasoning": "평가 근거"
}}"""


# ============================================================
# Evaluation Functions
# ============================================================

async def evaluate_intent_stage(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    latency_ms: float = 0,
) -> EvaluationResult:
    """
    Intent Graph 평가
    """
    from ..services.openrouter import openrouter_service

    prompt = INTENT_EVAL_PROMPT.format(
        message=input_data.get("message", ""),
        conversation_history=json.dumps(input_data.get("conversation_history", []), ensure_ascii=False),
        intent=output_data.get("intent_result", {}).get("intent", "unknown"),
        confidence=output_data.get("intent_result", {}).get("confidence", 0),
        collected_info=json.dumps(output_data.get("collected_info", {}), ensure_ascii=False),
        response_message=output_data.get("response_message", ""),
    )

    try:
        response = await openrouter_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        metrics = result.get("metrics", {})
        avg_score = sum(metrics.values()) / len(metrics) if metrics else 0.5

        return EvaluationResult(
            stage="intent",
            score=avg_score,
            metrics=metrics,
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        print(f"[Evaluation] Intent eval error: {e}")
        return _default_evaluation("intent", latency_ms)


async def evaluate_discovery_stage(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    latency_ms: float = 0,
) -> EvaluationResult:
    """
    Discovery Graph 평가
    """
    from ..services.openrouter import openrouter_service

    search_results = output_data.get("search_results", [])
    search_results_summary = [
        {"name": p.get("name"), "difficulty": p.get("difficulty"), "tags": p.get("tags", [])}
        for p in search_results[:5]
    ]

    prompt = DISCOVERY_EVAL_PROMPT.format(
        collected_info=json.dumps(input_data.get("collected_info", {}), ensure_ascii=False),
        query=input_data.get("message", ""),
        result_count=len(search_results),
        search_results=json.dumps(search_results_summary, ensure_ascii=False),
        selected_problem=output_data.get("selected_problem", {}).get("name") if output_data.get("selected_problem") else "없음",
        response_message=output_data.get("response_message", ""),
    )

    try:
        response = await openrouter_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        metrics = result.get("metrics", {})
        avg_score = sum(metrics.values()) / len(metrics) if metrics else 0.5

        return EvaluationResult(
            stage="discovery",
            score=avg_score,
            metrics=metrics,
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        print(f"[Evaluation] Discovery eval error: {e}")
        return _default_evaluation("discovery", latency_ms)


async def evaluate_solving_stage(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    latency_ms: float = 0,
) -> EvaluationResult:
    """
    Solving Graph 평가
    """
    from ..services.openrouter import openrouter_service

    problem_context = input_data.get("problem_context", {})
    problem_summary = {
        "title": problem_context.get("title"),
        "difficulty": problem_context.get("difficulty"),
        "type": problem_context.get("problem_type"),
    }

    prompt = SOLVING_EVAL_PROMPT.format(
        problem_context=json.dumps(problem_summary, ensure_ascii=False),
        user_progress=json.dumps(input_data.get("user_progress", {}), ensure_ascii=False),
        message=input_data.get("message", ""),
        intent=output_data.get("intent_result", {}).get("intent", "unknown"),
        hint_level=output_data.get("hint_level"),
        response_message=output_data.get("response_message", ""),
        is_correct=output_data.get("is_correct"),
    )

    try:
        response = await openrouter_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        metrics = result.get("metrics", {})
        avg_score = sum(metrics.values()) / len(metrics) if metrics else 0.5

        return EvaluationResult(
            stage="solving",
            score=avg_score,
            metrics=metrics,
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        print(f"[Evaluation] Solving eval error: {e}")
        return _default_evaluation("solving", latency_ms)


def _default_evaluation(stage: str, latency_ms: float) -> EvaluationResult:
    """기본 평가 결과 (평가 실패 시)"""
    return EvaluationResult(
        stage=stage,
        score=0.5,
        metrics={},
        issues=["평가 실패"],
        suggestions=[],
        latency_ms=latency_ms,
        timestamp=datetime.now().isoformat(),
    )


# ============================================================
# Unified Evaluation Function
# ============================================================

async def evaluate_stage(
    stage: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    latency_ms: float = 0,
) -> EvaluationResult:
    """
    통합 평가 함수

    Args:
        stage: "intent", "discovery", "solving"
        input_data: 그래프 입력 데이터
        output_data: 그래프 출력 데이터
        latency_ms: 처리 시간 (밀리초)

    Returns:
        EvaluationResult
    """
    if stage == "intent":
        return await evaluate_intent_stage(input_data, output_data, latency_ms)
    elif stage == "discovery":
        return await evaluate_discovery_stage(input_data, output_data, latency_ms)
    elif stage == "solving":
        return await evaluate_solving_stage(input_data, output_data, latency_ms)
    else:
        return _default_evaluation(stage, latency_ms)


# ============================================================
# Evaluation Logger
# ============================================================

class EvaluationLogger:
    """평가 결과 로깅 및 집계"""

    def __init__(self):
        self.evaluations: List[EvaluationResult] = []

    def log(self, result: EvaluationResult):
        """평가 결과 로깅"""
        self.evaluations.append(result)

        # 콘솔 출력
        status = "✅" if result.score >= 0.7 else "⚠️" if result.score >= 0.5 else "❌"
        print(f"[Eval] {status} {result.stage}: {result.score:.2f} ({result.latency_ms:.0f}ms)")

        if result.issues:
            for issue in result.issues:
                print(f"  └─ Issue: {issue}")

    def get_summary(self) -> Dict[str, Any]:
        """집계 요약"""
        if not self.evaluations:
            return {"total": 0, "avg_score": 0}

        by_stage = {}
        for e in self.evaluations:
            if e.stage not in by_stage:
                by_stage[e.stage] = []
            by_stage[e.stage].append(e.score)

        return {
            "total": len(self.evaluations),
            "avg_score": sum(e.score for e in self.evaluations) / len(self.evaluations),
            "by_stage": {
                stage: {
                    "count": len(scores),
                    "avg": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }
                for stage, scores in by_stage.items()
            },
            "issues_count": sum(len(e.issues) for e in self.evaluations),
        }

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """개선이 필요한 항목 추출"""
        suggestions = []
        for e in self.evaluations:
            if e.needs_improvement:
                suggestions.append({
                    "stage": e.stage,
                    "score": e.score,
                    "issues": e.issues,
                    "suggestions": e.suggestions,
                    "timestamp": e.timestamp,
                })
        return suggestions


# Global logger instance
evaluation_logger = EvaluationLogger()
