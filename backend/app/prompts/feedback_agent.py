"""
Feedback Agent
문제 풀이 완료 후 피드백 생성 에이전트

풀이 시간, 힌트 사용량, 시도 횟수 등을 분석하여
학습자에게 맞춤형 피드백과 격려를 제공합니다.
"""

FEEDBACK_SYSTEM_PROMPT = """
# Problem Solving Feedback Agent (문제 풀이 피드백 생성기)

## 역할
당신은 CodeFill의 **문제 풀이 피드백 전문가**입니다.
학습자가 문제를 완료했을 때, 풀이 과정을 분석하여 맞춤형 피드백을 제공합니다.
**긍정적이고 격려하는 톤**으로 피드백을 작성하며, 개선점도 건설적으로 제안합니다.

## 문제 정보
- 제목: {problem_title}
- 난이도: {difficulty}
- 유형: {problem_type}
- 핵심 개념: {topics}

## 풀이 결과
- 정답 여부: {is_correct}
- 최종 점수: {score}/100

## 풀이 통계
- 총 풀이 시간: {solve_time_formatted}
- 시도 횟수: {attempt_count}회
- 힌트 사용: {hints_used}회 (XP 비용: -{hint_xp_cost})
- 획득 XP: +{xp_earned}

## 문제 유형별 추가 통계
{problem_type_stats}

## 힌트 사용 내역
{hint_history}

## 틀린 시도 분석
{wrong_attempts}

## 사용자 레벨
- 현재 레벨: {user_level}
- 총 해결 문제: {total_solved}문제
- 평균 풀이 시간: {avg_solve_time}

---

## 피드백 생성 원칙

### 1. 성과 평가
- 풀이 시간 분석: 빠르면 칭찬, 느리면 격려
- 힌트 사용량 평가: 적게 쓰면 칭찬, 많이 쓰면 학습 과정으로 긍정화
- 시도 횟수 분석: 한 번에 맞추면 칭찬, 여러 번이면 끈기 칭찬

### 2. 학습 포인트
- 이 문제에서 배운 핵심 개념 요약
- 실수한 부분이 있다면 그 원인 분석
- 비슷한 유형에서 주의할 점

### 3. 개선 제안
- 다음에 비슷한 문제를 더 잘 풀기 위한 팁
- 추천하는 연습 방향
- 관련 개념 심화 학습 제안

### 4. 격려 메시지
- 항상 긍정적인 마무리
- 다음 문제에 대한 동기부여

---

## 성과 등급 기준

### 🏆 Perfect (완벽)
- 조건: 힌트 0회, 시도 1회, 시간 < 평균
- 메시지: "완벽한 풀이! 이 개념을 완전히 이해하셨네요!"

### ⭐ Excellent (훌륭)
- 조건: 힌트 ≤1회, 시도 ≤2회
- 메시지: "훌륭해요! 거의 완벽에 가까운 풀이입니다!"

### 👍 Good (좋음)
- 조건: 힌트 ≤2회, 시도 ≤3회
- 메시지: "잘했어요! 좋은 풀이 과정이었습니다!"

### 💪 Keep Going (계속)
- 조건: 힌트 ≤3회 또는 시도 ≤5회
- 메시지: "포기하지 않고 끝까지 풀어냈어요! 이 경험이 실력이 됩니다!"

### 🌱 Learning (학습 중)
- 조건: 그 외
- 메시지: "많이 배우셨네요! 다음엔 더 잘할 수 있을 거예요!"

---

## 시각화 데이터 생성

### 시간 분석 차트
- 본인 풀이 시간 vs 평균 풀이 시간 비교
- 단계별 소요 시간 (가능한 경우)

### 성과 지표
- 이번 풀이 점수 (0-100)
- 효율성 점수: (100 - 힌트비용 - 시도페널티)
- 속도 점수: 평균 대비 시간 비율

---

## 출력 형식

반드시 아래 JSON 형식으로만 출력하세요:

```json
{{
  "grade": "perfect|excellent|good|keep_going|learning",
  "grade_emoji": "🏆|⭐|👍|💪|🌱",
  "grade_message": "등급 메시지",

  "summary": {{
    "title": "피드백 제목 (짧고 인상적인)",
    "highlight": "가장 인상적인 성과 한 줄"
  }},

  "performance_analysis": {{
    "time_feedback": "시간에 대한 피드백",
    "hint_feedback": "힌트 사용에 대한 피드백",
    "attempt_feedback": "시도 횟수에 대한 피드백"
  }},

  "learning_points": [
    "배운 점 1",
    "배운 점 2"
  ],

  "improvements": [
    "개선 제안 1",
    "개선 제안 2"
  ],

  "visualization": {{
    "efficiency_score": 0-100,
    "speed_score": 0-100,
    "understanding_score": 0-100,
    "time_comparison": {{
      "user_time": 풀이시간(초),
      "avg_time": 평균시간(초),
      "percentile": "상위 X%"
    }}
  }},

  "next_steps": {{
    "recommendation": "다음에 추천하는 학습",
    "similar_problems": "비슷한 유형 문제 추천 (있으면)"
  }},

  "encouragement": "격려 메시지 (한국어, 긍정적)"
}}
```

---

## 주의사항

1. **JSON만 출력** - 설명이나 주석 없이 순수 JSON만
2. **항상 긍정적** - 비판보다 격려, 실패보다 학습
3. **한국어 사용** - 모든 피드백은 한국어로
4. **구체적 피드백** - 뻔한 말보다 이 문제에 맞는 구체적 조언
5. **동기부여** - 다음 문제를 풀고 싶게 만드는 메시지
"""

# 성과 등급 판정 헬퍼
def calculate_grade(hints_used: int, attempt_count: int, time_ratio: float) -> tuple:
    """
    성과 등급을 계산합니다.

    Args:
        hints_used: 사용한 힌트 수
        attempt_count: 시도 횟수
        time_ratio: 평균 대비 시간 비율 (1.0 = 평균)

    Returns:
        (grade, emoji, message) 튜플
    """
    if hints_used == 0 and attempt_count == 1 and time_ratio < 1.0:
        return ("perfect", "🏆", "완벽한 풀이! 이 개념을 완전히 이해하셨네요!")
    elif hints_used <= 1 and attempt_count <= 2:
        return ("excellent", "⭐", "훌륭해요! 거의 완벽에 가까운 풀이입니다!")
    elif hints_used <= 2 and attempt_count <= 3:
        return ("good", "👍", "잘했어요! 좋은 풀이 과정이었습니다!")
    elif hints_used <= 3 or attempt_count <= 5:
        return ("keep_going", "💪", "포기하지 않고 끝까지 풀어냈어요! 이 경험이 실력이 됩니다!")
    else:
        return ("learning", "🌱", "많이 배우셨네요! 다음엔 더 잘할 수 있을 거예요!")

# 시간 포맷 헬퍼
def format_solve_time(seconds: int) -> str:
    """풀이 시간을 읽기 좋게 포맷합니다."""
    if seconds < 60:
        return f"{seconds}초"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}분 {secs}초" if secs > 0 else f"{minutes}분"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}시간 {minutes}분"

# 난이도별 설정값
DIFFICULTY_CONFIG = {
    "easy": {
        "hint_penalty": 15,           # 힌트당 페널티 (쉬운 문제는 힌트 사용 시 감점 큼)
        "attempt_penalty": 8,         # 추가 시도당 페널티
        "expected_time_multiplier": 0.8,  # 평균 대비 기대 시간 (80%)
        "base_xp": 10,                # 기본 XP
        "perfect_bonus": 5,           # 완벽 클리어 보너스 XP
    },
    "medium": {
        "hint_penalty": 10,           # 중간 난이도는 표준
        "attempt_penalty": 5,
        "expected_time_multiplier": 1.0,
        "base_xp": 20,
        "perfect_bonus": 10,
    },
    "medium_hard": {
        "hint_penalty": 8,            # 어려울수록 힌트 사용에 관대
        "attempt_penalty": 4,
        "expected_time_multiplier": 1.2,
        "base_xp": 30,
        "perfect_bonus": 15,
    },
    "hard": {
        "hint_penalty": 6,            # 어려운 문제는 힌트 사용해도 OK
        "attempt_penalty": 3,
        "expected_time_multiplier": 1.5,
        "base_xp": 40,
        "perfect_bonus": 20,
    },
    "very_hard": {
        "hint_penalty": 4,            # 매우 어려운 문제는 힌트가 학습의 일부
        "attempt_penalty": 2,
        "expected_time_multiplier": 2.0,
        "base_xp": 50,
        "perfect_bonus": 30,
    },
}


def get_difficulty_config(difficulty: str) -> dict:
    """난이도별 설정 조회"""
    return DIFFICULTY_CONFIG.get(difficulty.lower(), DIFFICULTY_CONFIG["medium"])


# 점수 계산 헬퍼
def calculate_scores(
    hints_used: int,
    attempt_count: int,
    time_seconds: int,
    avg_time: int,
    difficulty: str = "medium",
) -> dict:
    """
    각종 점수를 계산합니다.

    Args:
        hints_used: 사용한 힌트 수
        attempt_count: 시도 횟수
        time_seconds: 실제 풀이 시간 (초)
        avg_time: 평균 풀이 시간 (초)
        difficulty: 난이도 (easy/medium/medium_hard/hard/very_hard)

    Returns:
        {efficiency_score, speed_score, understanding_score, difficulty_bonus} 딕셔너리

    난이도별 차등:
    - easy: 힌트/시도 페널티 높음, 시간 기준 엄격
    - medium: 표준 기준
    - hard: 힌트/시도에 관대, 시간 기준 느슨
    - very_hard: 완주 자체가 대단함, 매우 관대한 기준
    """
    config = get_difficulty_config(difficulty)

    # 효율성: 힌트와 시도 횟수 기반 (난이도별 차등 페널티)
    hint_penalty = hints_used * config["hint_penalty"]
    attempt_penalty = max(0, (attempt_count - 1) * config["attempt_penalty"])
    efficiency = max(0, 100 - hint_penalty - attempt_penalty)

    # 속도: 평균 대비 (난이도별 기대 시간 조정)
    expected_time = avg_time * config["expected_time_multiplier"]
    if expected_time > 0:
        time_ratio = time_seconds / expected_time
        if time_ratio < 0.5:
            speed = 100
        elif time_ratio < 1.0:
            speed = int(80 + (1.0 - time_ratio) * 40)
        elif time_ratio < 2.0:
            speed = int(60 - (time_ratio - 1.0) * 30)
        else:
            speed = max(20, int(30 - (time_ratio - 2.0) * 10))
    else:
        speed = 70  # 평균 없으면 기본값

    # 이해도: 힌트 레벨과 정답률 기반 (난이도별 차등)
    hint_understanding_penalty = hints_used * (config["hint_penalty"] + 5)
    attempt_understanding_penalty = max(0, attempt_count - 1) * (config["attempt_penalty"] + 5)
    understanding = max(0, 100 - hint_understanding_penalty - attempt_understanding_penalty)

    # 난이도 보너스: 어려운 문제일수록 보너스 점수
    difficulty_bonus = {
        "easy": 0,
        "medium": 5,
        "medium_hard": 10,
        "hard": 15,
        "very_hard": 25,
    }.get(difficulty.lower(), 0)

    return {
        "efficiency_score": min(100, efficiency),
        "speed_score": min(100, speed),
        "understanding_score": min(100, understanding),
        "difficulty_bonus": difficulty_bonus,
        "difficulty_config": config,
    }


def calculate_xp(
    is_correct: bool,
    hints_used: int,
    attempt_count: int,
    difficulty: str = "medium",
) -> int:
    """
    획득 XP 계산 (난이도별 차등)

    Args:
        is_correct: 정답 여부
        hints_used: 힌트 사용 수
        attempt_count: 시도 횟수
        difficulty: 난이도

    Returns:
        획득 XP
    """
    if not is_correct:
        return 5  # 오답이어도 시도 보상

    config = get_difficulty_config(difficulty)
    base_xp = config["base_xp"]

    # 힌트 페널티 (난이도별 차등)
    hint_reduction = hints_used * (config["hint_penalty"] // 2)

    # 시도 페널티
    attempt_reduction = max(0, (attempt_count - 1) * (config["attempt_penalty"] // 2))

    # 완벽 보너스
    perfect_bonus = 0
    if hints_used == 0 and attempt_count == 1:
        perfect_bonus = config["perfect_bonus"]

    xp = max(base_xp // 2, base_xp - hint_reduction - attempt_reduction + perfect_bonus)

    return xp


# ============================================================
# 문제 유형별 측정 기준 (4가지 유형 통합)
# ============================================================

PROBLEM_TYPE_METRICS = {
    "blank": {
        "name": "빈칸 채우기",
        "metrics": [
            "blank_accuracy",      # 빈칸 정답률 (맞은 빈칸 / 전체 빈칸)
            "hints_used",          # 힌트 사용 횟수
            "attempt_count",       # 제출 시도 횟수
            "solve_time",          # 풀이 시간
        ],
        "grade_weights": {
            "blank_accuracy": 0.4,
            "hints_used": 0.25,
            "attempt_count": 0.2,
            "solve_time": 0.15,
        },
        "stats_template": """
- 빈칸 정답률: {blank_correct}/{blank_total} ({blank_accuracy}%)
- 첫 시도 정답률: {first_try_accuracy}%
""",
    },
    "puzzle": {
        "name": "퍼즐 (코드 정렬)",
        "metrics": [
            "block_accuracy",      # 블록 위치 정확도
            "hints_used",          # 힌트 사용 횟수
            "attempt_count",       # 제출 시도 횟수
            "solve_time",          # 풀이 시간
        ],
        "grade_weights": {
            "block_accuracy": 0.4,
            "hints_used": 0.25,
            "attempt_count": 0.2,
            "solve_time": 0.15,
        },
        "stats_template": """
- 블록 정렬 정확도: {blocks_correct}/{blocks_total} ({block_accuracy}%)
- 잘못된 위치: {wrong_positions}개
""",
    },
    "guided": {
        "name": "1대1 대화형",
        "metrics": [
            "conversation_count",  # 총 대화 횟수
            "help_requests",       # 도움 요청 횟수 (막힘 표현)
            "checkpoint_progress", # 체크포인트 달성률
            "solve_time",          # 풀이 시간
        ],
        "grade_weights": {
            "conversation_count": 0.2,   # 대화 많아도 괜찮음 (학습이니까)
            "help_requests": 0.3,        # 스스로 해결한 정도
            "checkpoint_progress": 0.35, # 단계별 진행
            "solve_time": 0.15,
        },
        "stats_template": """
- 총 대화 횟수: {conversation_count}회
- 도움 요청: {help_requests}회
- 체크포인트 달성: {checkpoints_completed}/{checkpoints_total}
- 스스로 해결한 단계: {self_solved_steps}개
""",
        "special_rules": {
            "no_hint_button": True,      # 힌트 버튼 없음
            "conversation_is_learning": True,  # 대화 자체가 학습
        },
    },
    "implementation": {
        "name": "구현 (코드 작성)",
        "metrics": [
            "test_pass_rate",      # 테스트 케이스 통과율
            "hints_used",          # 힌트 사용 횟수
            "submission_count",    # 제출 횟수
            "solve_time",          # 풀이 시간
            "code_quality",        # 코드 품질 (선택)
        ],
        "grade_weights": {
            "test_pass_rate": 0.4,
            "hints_used": 0.2,
            "submission_count": 0.2,
            "solve_time": 0.1,
            "code_quality": 0.1,
        },
        "stats_template": """
- 테스트 통과율: {tests_passed}/{tests_total} ({test_pass_rate}%)
- 제출 횟수: {submission_count}회
- 코드 라인 수: {code_lines}줄
""",
    },
}


def get_problem_type_stats(
    problem_type: str,
    stats_data: dict
) -> str:
    """
    문제 유형별 통계 문자열 생성

    Args:
        problem_type: blank|puzzle|guided|implementation
        stats_data: 해당 유형의 통계 데이터

    Returns:
        포맷된 통계 문자열
    """
    config = PROBLEM_TYPE_METRICS.get(problem_type, PROBLEM_TYPE_METRICS["blank"])
    template = config.get("stats_template", "")

    try:
        return template.format(**stats_data)
    except KeyError:
        return f"[{config['name']}] 통계 데이터 없음"


def calculate_type_specific_grade(
    problem_type: str,
    metrics: dict
) -> dict:
    """
    문제 유형별 등급 계산

    Args:
        problem_type: 문제 유형
        metrics: 측정 지표들

    Returns:
        {score, grade, factors} 딕셔너리
    """
    config = PROBLEM_TYPE_METRICS.get(problem_type, PROBLEM_TYPE_METRICS["blank"])
    weights = config.get("grade_weights", {})

    total_score = 0
    factors = {}

    for metric, weight in weights.items():
        value = metrics.get(metric, 0)

        # 각 지표를 0-100 점수로 정규화
        if metric in ["blank_accuracy", "block_accuracy", "test_pass_rate", "checkpoint_progress"]:
            # 이미 퍼센트면 그대로 사용
            normalized = min(100, max(0, value))
        elif metric in ["hints_used", "help_requests"]:
            # 적을수록 좋음 (0개=100점, 4개 이상=0점)
            normalized = max(0, 100 - value * 25)
        elif metric in ["attempt_count", "submission_count"]:
            # 적을수록 좋음 (1회=100점, 5회 이상=20점)
            normalized = max(20, 100 - (value - 1) * 20)
        elif metric == "conversation_count":
            # 1대1 대화형: 대화 많아도 OK (10회까지 만점, 그 이상은 약간 감점)
            normalized = max(70, 100 - max(0, value - 10) * 3)
        elif metric == "solve_time":
            # 시간은 별도 계산 필요 (평균 대비)
            normalized = metrics.get("time_score", 70)
        else:
            normalized = 70  # 기본값

        factors[metric] = {
            "raw": value,
            "normalized": normalized,
            "weight": weight,
            "contribution": normalized * weight,
        }
        total_score += normalized * weight

    return {
        "score": round(total_score, 1),
        "factors": factors,
    }


# 1대1 대화형 특별 규칙
GUIDED_SPECIAL_FEEDBACK = {
    "low_conversation": {
        "threshold": 5,  # 대화 5회 이하
        "message": "짧은 대화로 문제를 해결했어요! 개념을 잘 이해하고 계시네요.",
    },
    "high_self_solve": {
        "threshold": 0.7,  # 70% 이상 스스로 해결
        "message": "대부분의 단계를 스스로 해결했어요! 독립적인 문제 해결 능력이 뛰어나요.",
    },
    "good_learning_pace": {
        "message": "대화를 통해 차근차근 배워나가는 모습이 좋아요! 이게 바로 학습이에요.",
    },
}
