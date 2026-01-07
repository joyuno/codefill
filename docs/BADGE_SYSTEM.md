# CodeFill 뱃지 시스템

## 개요

CodeFill의 뱃지 시스템은 사용자의 학습 활동을 인정하고 동기를 부여하기 위한 보상 체계입니다.

### 희귀도 등급 (5단계)

| 희귀도 | 색상 | 설명 | 획득 난이도 |
|--------|------|------|-------------|
| common | 회색 | 기본 달성 뱃지 | 쉬움 |
| uncommon | 초록색 | 조금 노력이 필요한 뱃지 | 보통 |
| rare | 파란색 | 꾸준한 노력이 필요한 뱃지 | 어려움 |
| epic | 보라색 | 상당한 노력이 필요한 뱃지 | 매우 어려움 |
| legendary | 금색 | 극소수만 달성하는 최고 뱃지 | 극한 |

---

## 마일스톤 뱃지

### 문제 해결

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `first_solve` | First Step | 첫 발걸음 | 1문제 해결 | common |
| `solve_10` | Getting Started | 시작이 반 | 10문제 해결 | common |
| `solve_50` | Half Century | 하프 센츄리 | 50문제 해결 | uncommon |
| `solve_100` | Centurion | 센츄리온 | 100문제 해결 | rare |
| `solve_250` | Problem Solver | 문제 해결사 | 250문제 해결 | epic |
| `solve_500` | Code Master | 코드 마스터 | 500문제 해결 | legendary |

### 스트릭

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `streak_7` | Week Warrior | 일주일 전사 | 7일 연속 학습 | common |
| `streak_14` | Two Weeks | 2주 연속 | 14일 연속 학습 | uncommon |
| `streak_30` | Monthly Master | 월간 마스터 | 30일 연속 학습 | rare |
| `streak_90` | Quarterly Champion | 분기 챔피언 | 90일 연속 학습 | epic |
| `streak_365` | Year Legend | 1년의 전설 | 365일 연속 학습 | legendary |

### 레벨

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `level_5` | Rising Star | 떠오르는 별 | 레벨 5 달성 | common |
| `level_10` | Intermediate | 중급자 | 레벨 10 달성 | uncommon |
| `level_25` | Advanced | 고급자 | 레벨 25 달성 | rare |
| `level_50` | Expert | 전문가 | 레벨 50 달성 | epic |
| `level_100` | Grandmaster | 그랜드마스터 | 레벨 100 달성 | legendary |

---

## 문제 유형별 뱃지

### 빈칸 채우기 (Blank)

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `blank_10` | Blank Beginner | 빈칸 입문자 | 빈칸 10문제 해결 | common |
| `blank_30` | Blank Intermediate | 빈칸 중급자 | 빈칸 30문제 해결 | uncommon |
| `blank_50` | Blank Expert | 빈칸 전문가 | 빈칸 50문제 해결 | rare |
| `blank_100` | Blank Master | 빈칸 마스터 | 빈칸 100문제 해결 | epic |

### 퍼즐 (Puzzle)

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `puzzle_10` | Puzzle Beginner | 퍼즐 입문자 | 퍼즐 10문제 해결 | common |
| `puzzle_30` | Puzzle Intermediate | 퍼즐 중급자 | 퍼즐 30문제 해결 | uncommon |
| `puzzle_50` | Puzzle Expert | 퍼즐 전문가 | 퍼즐 50문제 해결 | rare |
| `puzzle_100` | Puzzle Master | 퍼즐 마스터 | 퍼즐 100문제 해결 | epic |

### 1대1 대화형 (Guided)

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `guided_10` | Guided Beginner | 대화형 입문자 | 대화형 10문제 해결 | common |
| `guided_30` | Guided Intermediate | 대화형 중급자 | 대화형 30문제 해결 | uncommon |
| `guided_50` | Guided Expert | 대화형 전문가 | 대화형 50문제 해결 | rare |
| `guided_100` | Guided Master | 대화형 마스터 | 대화형 100문제 해결 | epic |

### 구현 (Implementation)

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `impl_10` | Builder Beginner | 구현 입문자 | 구현 10문제 해결 | common |
| `impl_30` | Builder Intermediate | 구현 중급자 | 구현 30문제 해결 | uncommon |
| `impl_50` | Builder Expert | 구현 전문가 | 구현 50문제 해결 | rare |
| `impl_100` | Builder Master | 구현 마스터 | 구현 100문제 해결 | epic |

---

## 난이도별 뱃지

### Easy

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `easy_10` | Easy Start | 쉬운 시작 | Easy 10문제 해결 | common |
| `easy_30` | Easy Going | 순조로운 진행 | Easy 30문제 해결 | uncommon |
| `easy_50` | Easy Expert | Easy 전문가 | Easy 50문제 해결 | rare |

### Medium

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `medium_10` | Medium Start | 중급 시작 | Medium 10문제 해결 | uncommon |
| `medium_30` | Medium Grinder | 중급 도전자 | Medium 30문제 해결 | rare |
| `medium_50` | Medium Expert | Medium 전문가 | Medium 50문제 해결 | epic |

### Hard

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `hard_5` | Hard Start | 어려운 시작 | Hard 5문제 해결 | uncommon |
| `hard_10` | Hard Crusher | 고난도 분쇄기 | Hard 10문제 해결 | rare |
| `hard_30` | Hard Expert | Hard 전문가 | Hard 30문제 해결 | epic |
| `hard_50` | Hard Master | Hard 마스터 | Hard 50문제 해결 | legendary |

### 복합

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `all_difficulty` | Difficulty Explorer | 난이도 탐험가 | 각 난이도 10문제씩 해결 | rare |
| `all_difficulty_master` | Difficulty Conqueror | 난이도 정복자 | 각 난이도 50문제씩 해결 | legendary |

---

## 특별 활동 뱃지

### 시간대별

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `night_owl` | Night Owl | 올빼미 | 자정~6시 사이 문제 풀이 | common |
| `early_bird` | Early Bird | 얼리버드 | 6시~9시 사이 문제 풀이 | common |
| `weekend_coder` | Weekend Coder | 주말 코더 | 주말에 문제 풀이 | common |

### 하루 집중

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `daily_3` | Daily Learner | 일일 학습자 | 하루 3문제 해결 | common |
| `daily_5` | Daily Achiever | 일일 성취자 | 하루 5문제 해결 | uncommon |
| `daily_10` | Daily Champion | 일일 챔피언 | 하루 10문제 해결 | rare |
| `daily_20` | Daily Legend | 일일 전설 | 하루 20문제 해결 | epic |

### 정확도

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `first_try_10` | Accurate | 정확한 사람 | 첫 시도 정답 10회 | common |
| `first_try_50` | Sharpshooter | 명사수 | 첫 시도 정답 50회 | rare |
| `first_try_100` | Perfectionist | 완벽주의자 | 첫 시도 정답 100회 | epic |
| `no_hint_50` | Independent | 독립적인 | 힌트 없이 50문제 해결 | rare |
| `no_hint_100` | Self-Reliant | 자립형 | 힌트 없이 100문제 해결 | epic |

### 도전

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `perfect_week` | Perfect Week | 완벽한 한 주 | 일주일간 매일 5문제 해결 | rare |
| `perfect_month` | Perfect Month | 완벽한 한 달 | 한 달간 매일 3문제 해결 | epic |

### 최고 달성

| code | name | 설명 | 조건 | 희귀도 |
|------|------|------|------|--------|
| `thousand` | Thousand Club | 천 문제 클럽 | 1000문제 해결 | legendary |
| `all_rounder` | All Rounder | 올라운더 | 모든 카테고리 뱃지 보유 | legendary |

---

## 요약

### 카테고리별 개수

| 카테고리 | 개수 |
|----------|------|
| 마일스톤 - 문제 해결 | 6개 |
| 마일스톤 - 스트릭 | 5개 |
| 마일스톤 - 레벨 | 5개 |
| 문제 유형별 | 16개 |
| 난이도별 | 12개 |
| 특별 활동 | 16개 |
| **총계** | **60개** |

### 희귀도별 분포

| 희귀도 | 개수 | 비율 |
|--------|------|------|
| common | 14개 | 23% |
| uncommon | 11개 | 18% |
| rare | 15개 | 25% |
| epic | 13개 | 22% |
| legendary | 7개 | 12% |

### Legendary 뱃지 (7개)

극소수만 달성할 수 있는 최고의 뱃지:

| code | name | 조건 |
|------|------|------|
| `solve_500` | Code Master | 500문제 해결 |
| `streak_365` | Year Legend | 365일 연속 학습 |
| `level_100` | Grandmaster | 레벨 100 달성 |
| `hard_50` | Hard Master | Hard 50문제 해결 |
| `all_difficulty_master` | Difficulty Conqueror | 각 난이도 50문제씩 |
| `thousand` | Thousand Club | 1000문제 해결 |
| `all_rounder` | All Rounder | 모든 카테고리 뱃지 |

---

## 구현 참고사항

### 조건 타입 (condition_type)

- `problems` - 총 문제 해결 수
- `streak` - 연속 학습일
- `level` - 사용자 레벨
- `blank` - 빈칸 문제 해결 수
- `puzzle` - 퍼즐 문제 해결 수
- `guided` - 대화형 문제 해결 수
- `implementation` - 구현 문제 해결 수
- `easy` - Easy 난이도 해결 수
- `medium` - Medium 난이도 해결 수
- `hard` - Hard 난이도 해결 수
- `daily` - 하루 해결 수
- `time` - 특정 시간대 활동
- `accuracy` - 첫 시도 정답률
- `no_hint` - 힌트 미사용 횟수
- `special` - 특별 조건

### 희귀도 색상 코드 (프론트엔드)

```typescript
const RARITY_COLORS = {
  common: 'text-gray-500 bg-gray-500/20',
  uncommon: 'text-green-500 bg-green-500/20',
  rare: 'text-blue-500 bg-blue-500/20',
  epic: 'text-purple-500 bg-purple-500/20',
  legendary: 'text-yellow-500 bg-yellow-500/20',
};
```
