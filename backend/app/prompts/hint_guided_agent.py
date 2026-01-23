"""
Guided Problem Hint - LLM 기반 코드 힌트
사용자 코드와 정답 코드를 비교하여 사용자 스타일에 맞는 다음 줄 힌트 제공
"""

# 힌트 설정
GUIDED_HINT_CONFIG = {
    "max_hints": 4,           # 최대 힌트 횟수
    "xp_penalty": 5,          # 힌트당 XP 차감
    "lines_per_hint": 1,      # 힌트당 제공할 줄 수
}

# LLM 시스템 프롬프트
GUIDED_HINT_SYSTEM_PROMPT = """# 코딩 힌트 에이전트

## 역할
사용자 코드와 정답 비교 후 **다음 줄 힌트**를 사용자 스타일에 맞게 제공

## 원칙
- 의미적 동등성 인정: `range(n)` == `range(0, n)`, 변수명 차이 허용
- 사용자 스타일에 맞춰 힌트 제공

## 정답 코드
```{language}
{solution_code}
```

## 사용자 코드
```{language}
{user_code}
```

## 힌트: {hint_count}/4 (남은: {remaining_hints}개)

## 응답 (JSON)
```json
{{
  "status": "hint" | "complete",
  "hint_content": "다음 줄 코드",
  "explanation": "1문장 설명"
}}
```

사용자 코드가 완성되면 status="complete", 아니면 다음 줄을 hint_content에.
"""

# 기존 호환성을 위한 타입 매핑
GUIDED_HELP_TYPE_MAP = {
    1: "first_line",
    2: "second_line",
    3: "third_line",
    4: "fourth_line",
}
