"""
Blank Problem Hint Agent - 빈칸 채우기 힌트 생성
"""

BLANK_HINT_SYSTEM_PROMPT = """
# 빈칸 힌트 에이전트

## 역할
빈칸 채우기 문제 힌트 제공. **정답 직접 노출 금지**, 단계적 유도.

## 문제 정보
- 제목: {title} | 난이도: {difficulty} | 언어: {language}
- 개념: {topics}

## 코드
```{language}
{code_template}
```

## 현재 상태
- 총 빈칸: {total_blanks}개 | 현재 빈칸: {current_blank_index}번
- 사용자 입력: {user_answers}

## 정답 (노출 금지)
{answers_for_hint}

## 정답 코드 (참고용, 노출 금지)
```{language}
{solution_code}
```

## 힌트 레벨: {hint_level}

## 이전 힌트
{previous_hints}

---

## 레벨별 힌트 원칙

**Level 1 (맥락)**: 빈칸 역할과 주변 코드 맥락 설명
**Level 2 (연산)**: 필요한 연산/개념 유형 제시 ("**산술 연산자** 필요")
**Level 3 (범위)**: 정답 형태/범위 ("**한 단어**, 내장 함수")
**Level 4 (거의 정답)**: 첫 글자 또는 일부 공개 ("**len**으로 시작")

---

## 응답 (JSON)

```json
{{
  "hint_level": {hint_level},
  "hint_content": "힌트 내용 (**강조** 사용)",
  "hint_type": "context|operation|range|almost",
  "encouragement": "격려 메시지"
}}
```

## 규칙
1. 정답 직접 노출 금지 (Level 4도)
2. 현재 빈칸만 힌트
3. 한국어 사용
4. **강조** 마크다운 사용
"""

# 빈칸 유형 패턴
BLANK_TYPE_PATTERNS = {
    "operator": ["+", "-", "*", "/", "%", "//", "**", "==", "!=", "<", ">", "<=", ">=", "and", "or", "not", "in"],
    "builtin_function": ["len", "range", "print", "input", "int", "str", "float", "list", "dict", "sum", "max", "min", "abs", "sorted", "enumerate", "zip", "map", "filter"],
    "method": ["append", "extend", "insert", "remove", "pop", "sort", "reverse", "split", "join", "strip", "replace", "find", "upper", "lower"],
    "keyword": ["if", "else", "elif", "for", "while", "break", "continue", "return", "def", "class", "import", "try", "except", "with", "yield", "lambda"],
    "number": ["0", "1", "2", "-1"],
}

HINT_TYPE_MAP = {
    1: "context",
    2: "operation",
    3: "range",
    4: "almost",
}

def extract_surrounding_code(code_template: str, blank_index: int, context_chars: int = 30) -> str:
    """빈칸 주변 코드 추출"""
    blanks = code_template.split("___")
    if blank_index >= len(blanks) - 1:
        return ""
    before = blanks[blank_index][-context_chars:]
    after = blanks[blank_index + 1][:context_chars]
    return f"...{before}____{after}..."

def generate_answer_hint(answer: str, level: int) -> str:
    """레벨별 정답 힌트 생성"""
    if level == 1:
        return f"{len(answer)}글자"
    elif level == 2:
        for t, patterns in BLANK_TYPE_PATTERNS.items():
            if answer in patterns:
                return {"operator": "연산자", "builtin_function": "내장 함수", "method": "메서드", "keyword": "키워드", "number": "숫자"}.get(t, "식별자")
        return "식별자"
    elif level == 3:
        return f"'{answer[0]}...' ({len(answer)}글자)"
    elif level == 4:
        return f"'{answer[:-1]}_'" if len(answer) > 2 else f"'{answer[0]}_'"
    return ""
