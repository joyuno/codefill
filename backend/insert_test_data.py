"""테스트 데이터 삽입 스크립트."""

import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
db = create_client(url, key)

USER_ID = "a9e5a793-663a-487d-abf3-f1d231e2159a"

def get_problems():
    """base_problems에서 문제 ID 조회."""
    result = db.table("base_problems").select("id, name, difficulty, tags").limit(15).execute()
    return result.data

def insert_user_stats():
    """user_stats 삽입."""
    print("1. user_stats 삽입...")

    # 기존 데이터 확인
    existing = db.table("user_stats").select("*").eq("user_id", USER_ID).execute()

    if existing.data:
        # 업데이트
        db.table("user_stats").update({
            "level": 5,
            "problems_solved": 25,
            "current_streak": 3,
            "longest_streak": 7,
            "total_xp": 1500,
        }).eq("user_id", USER_ID).execute()
        print("   - 기존 데이터 업데이트")
    else:
        # 삽입
        db.table("user_stats").insert({
            "user_id": USER_ID,
            "level": 5,
            "problems_solved": 25,
            "current_streak": 3,
            "longest_streak": 7,
            "total_xp": 1500,
        }).execute()
        print("   - 새 데이터 삽입")

def insert_attempts(problems):
    """attempts 삽입."""
    print("2. attempts 삽입...")

    attempts_data = []
    now = datetime.utcnow()

    # 다양한 결과로 15개 시도 생성
    results = [
        (True, 120, 85),   # 성공
        (True, 90, 92),    # 성공
        (False, 180, 45),  # 실패
        (True, 150, 78),
        (True, 200, 88),
        (False, 300, 30),
        (True, 100, 95),
        (True, 80, 90),
        (False, 250, 40),
        (True, 110, 82),
        (True, 95, 87),
        (False, 400, 25),
        (True, 130, 80),
        (True, 85, 93),
        (True, 140, 75),
    ]

    for i, problem in enumerate(problems[:15]):
        is_correct, time_spent, score = results[i % len(results)]

        attempts_data.append({
            "user_id": USER_ID,
            "base_problem_id": problem["id"],
            "is_correct": is_correct,
            "score": score if is_correct else 0,
            "time_spent": time_spent,
            "hints_used": i % 3,
            "xp_earned": 50 if is_correct else 10,
            "topics": problem.get("tags", [])[:3],
            "difficulty": problem.get("difficulty", "medium"),
            "problem_name": problem.get("name", f"Problem {i}"),
            "problem_type": "fill_blank",
            "total_hints_requested": i % 4,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=15-i, hours=i)).isoformat(),
        })

    # 기존 데이터 삭제 후 삽입
    db.table("attempts").delete().eq("user_id", USER_ID).execute()
    db.table("attempts").insert(attempts_data).execute()
    print(f"   - {len(attempts_data)}개 시도 삽입")

    return attempts_data

def create_chat_sessions(problems):
    """chat_sessions 생성."""
    print("2.5. chat_sessions 생성...")

    now = datetime.utcnow()
    sessions = []

    for i in range(8):
        problem = problems[i % len(problems)]
        session_id = str(uuid.uuid4())
        sessions.append({
            "id": session_id,
            "user_id": USER_ID,
            "session_type": "problem_solving",
            "title": problem.get("name", f"Problem {i+1}"),
            "created_at": (now - timedelta(days=8-i, hours=i*2)).isoformat(),
        })

    # 기존 세션 삭제 후 삽입
    db.table("chat_sessions").delete().eq("user_id", USER_ID).execute()
    db.table("chat_sessions").insert(sessions).execute()
    print(f"   - {len(sessions)}개 세션 생성")

    return [s["id"] for s in sessions]

def insert_user_memories(problems, session_ids):
    """user_memories 삽입."""
    print("3. user_memories 삽입...")

    memories_data = []
    now = datetime.utcnow()

    moods = ["curious", "confident", "frustrated", "confused", "curious", "confident", "neutral", "curious"]

    session_data = [
        {
            "summary": "BFS 알고리즘을 사용한 미로 탐색 문제를 풀었습니다. 처음에는 방향 벡터 설정에서 어려움을 겪었으나, 큐를 활용한 너비 우선 탐색 개념을 이해한 후 해결했습니다.",
            "concepts_learned": ["BFS", "큐 자료구조", "방향 벡터"],
            "concepts_struggling": ["그래프 순회", "최단 경로"],
            "teaching_notes": ["시각적 다이어그램으로 BFS 진행 과정 설명이 효과적"],
            "breakthrough_moments": ["큐에서 꺼낸 노드가 목표인지 먼저 확인해야 한다는 것을 깨달음"],
            "was_successful": True,
            "hints_needed": 2,
        },
        {
            "summary": "동적 프로그래밍 기초 문제를 풀었습니다. 점화식 세우는 과정에서 고민했지만, 작은 예시부터 패턴을 찾아 해결했습니다.",
            "concepts_learned": ["DP", "메모이제이션", "점화식"],
            "concepts_struggling": ["상태 정의", "최적 부분 구조"],
            "teaching_notes": ["작은 예시로 패턴 발견 후 일반화하는 접근이 효과적"],
            "breakthrough_moments": ["dp[i]가 무엇을 의미하는지 명확히 정의하니 점화식이 보임"],
            "was_successful": True,
            "hints_needed": 1,
        },
        {
            "summary": "이진 탐색 문제에서 경계 조건 처리에 어려움을 겪었습니다. left, right 갱신 조건을 정확히 이해하지 못해 무한 루프가 발생했습니다.",
            "concepts_learned": ["이진 탐색 기본"],
            "concepts_struggling": ["경계 조건", "이진 탐색 변형"],
            "teaching_notes": ["while 조건과 mid 계산 방식의 관계 설명 필요"],
            "breakthrough_moments": [],
            "was_successful": False,
            "hints_needed": 3,
        },
        {
            "summary": "그래프 DFS 문제를 풀었습니다. 재귀 호출과 방문 체크의 순서가 중요함을 배웠습니다.",
            "concepts_learned": ["DFS", "재귀", "방문 배열"],
            "concepts_struggling": ["스택 오버플로우", "재귀 깊이"],
            "teaching_notes": ["재귀 호출 전후의 상태 변화를 그림으로 설명"],
            "breakthrough_moments": ["방문 체크를 재귀 호출 전에 해야 중복 방문을 막을 수 있음을 이해"],
            "was_successful": True,
            "hints_needed": 1,
        },
        {
            "summary": "문자열 처리 문제를 풀었습니다. 슬라이싱과 인덱스 계산에서 실수가 있었습니다.",
            "concepts_learned": ["문자열 슬라이싱", "인덱스 계산"],
            "concepts_struggling": ["off-by-one 에러"],
            "teaching_notes": ["인덱스 범위를 시각적으로 표시하며 설명"],
            "breakthrough_moments": ["파이썬 슬라이싱이 마지막 인덱스를 포함하지 않음을 명확히 이해"],
            "was_successful": True,
            "hints_needed": 0,
        },
        {
            "summary": "정렬 알고리즘 구현 문제. 퀵소트의 파티션 과정을 직접 구현하며 피벗 선택의 중요성을 배웠습니다.",
            "concepts_learned": ["퀵소트", "파티션", "피벗"],
            "concepts_struggling": ["최악 케이스", "시간 복잡도"],
            "teaching_notes": ["파티션 과정을 단계별로 시뮬레이션"],
            "breakthrough_moments": ["피벗보다 작은 원소들을 왼쪽으로 모으는 과정 이해"],
            "was_successful": True,
            "hints_needed": 2,
        },
        {
            "summary": "해시맵을 활용한 문제. O(1) 조회의 장점을 활용해 효율적으로 해결했습니다.",
            "concepts_learned": ["해시맵", "시간 복잡도 최적화"],
            "concepts_struggling": ["해시 충돌"],
            "teaching_notes": ["브루트포스와 해시맵 사용시 시간 복잡도 비교"],
            "breakthrough_moments": ["이중 루프를 해시맵으로 O(n)에 해결 가능함을 깨달음"],
            "was_successful": True,
            "hints_needed": 1,
        },
        {
            "summary": "스택을 활용한 괄호 매칭 문제. 기본적인 스택 활용법을 익혔습니다.",
            "concepts_learned": ["스택", "괄호 매칭", "LIFO"],
            "concepts_struggling": [],
            "teaching_notes": ["스택의 push/pop 연산과 괄호 상태 매칭"],
            "breakthrough_moments": ["닫는 괄호가 나오면 스택 top과 비교하는 패턴 학습"],
            "was_successful": True,
            "hints_needed": 0,
        },
    ]

    for i, session in enumerate(session_data):
        problem = problems[i % len(problems)]

        memories_data.append({
            "user_id": USER_ID,
            "session_id": session_ids[i % len(session_ids)],
            "problem_name": problem.get("name", f"Problem {i+1}"),
            "summary": session["summary"],
            "key_topics": problem.get("tags", [])[:3],
            "concepts_learned": session["concepts_learned"],
            "concepts_struggling": session["concepts_struggling"],
            "teaching_notes": session["teaching_notes"],
            "breakthrough_moments": session["breakthrough_moments"],
            "student_mood": moods[i % len(moods)],
            "was_successful": session["was_successful"],
            "hints_needed": session["hints_needed"],
            "learning_insights": {
                "prefers_examples": True,
                "prefers_analogies": i % 2 == 0,
                "hint_sensitivity": "medium",
                "pace": "medium",
                "common_errors": ["인덱스 실수", "경계 조건 누락"],
            },
            "created_at": (now - timedelta(days=8-i, hours=i*2)).isoformat(),
        })

    # 기존 데이터 삭제 후 삽입
    db.table("user_memories").delete().eq("user_id", USER_ID).execute()
    db.table("user_memories").insert(memories_data).execute()
    print(f"   - {len(memories_data)}개 학습 기록 삽입")

def insert_hint_logs(problems):
    """hint_logs 삽입."""
    print("4. hint_logs 삽입...")

    hint_data = []
    now = datetime.utcnow()

    # 다양한 힌트 레벨로 20개 생성
    for i in range(20):
        problem = problems[i % len(problems)]
        hint_level = (i % 3) + 1  # 1, 2, 3 레벨

        hint_data.append({
            "user_id": USER_ID,
            "problem_id": problem["id"],
            "hint_level": hint_level,
            "xp_cost": hint_level * 5,
            "created_at": (now - timedelta(days=10-i//2, hours=i)).isoformat(),
        })

    # 기존 데이터 삭제 후 삽입
    db.table("hint_logs").delete().eq("user_id", USER_ID).execute()
    db.table("hint_logs").insert(hint_data).execute()
    print(f"   - {len(hint_data)}개 힌트 로그 삽입")

def insert_attempt_details(problems):
    """attempt_details 삽입."""
    print("5. attempt_details 삽입...")

    # 해당 유저의 attempts 조회
    attempts = db.table("attempts").select("id").eq("user_id", USER_ID).execute()

    if not attempts.data:
        print("   - attempts가 없어서 스킵")
        return

    details_data = []

    for i, attempt in enumerate(attempts.data[:10]):
        # 각 시도당 2-4개의 빈칸 상세 생성
        num_blanks = (i % 3) + 2

        for j in range(num_blanks):
            hint_requested = j == 0 and i % 2 == 0  # 일부만 힌트 요청

            details_data.append({
                "attempt_id": attempt["id"],
                "blank_index": j,
                "action_type": "submit",
                "blank_is_correct": j != 1,  # 두 번째 빈칸만 오답
                "blank_hint_level": (j % 3) + 1 if hint_requested else None,
                "hint_was_requested": hint_requested,
                "hint_was_helpful": hint_requested and j % 2 == 0,
            })

    # 기존 데이터 삭제는 attempt_id 기준으로 해야 하는데 복잡하므로 그냥 삽입
    # (중복 방지를 위해 먼저 삭제)
    attempt_ids = [a["id"] for a in attempts.data[:10]]
    for aid in attempt_ids:
        db.table("attempt_details").delete().eq("attempt_id", aid).execute()

    db.table("attempt_details").insert(details_data).execute()
    print(f"   - {len(details_data)}개 상세 기록 삽입")

def main():
    print("=" * 50)
    print("테스트 데이터 삽입 시작")
    print(f"User ID: {USER_ID}")
    print("=" * 50)

    # 1. 문제 목록 조회
    problems = get_problems()
    print(f"문제 {len(problems)}개 조회됨")

    # 2. 데이터 삽입
    insert_user_stats()
    insert_attempts(problems)
    session_ids = create_chat_sessions(problems)
    insert_user_memories(problems, session_ids)
    insert_hint_logs(problems)
    insert_attempt_details(problems)

    print("=" * 50)
    print("테스트 데이터 삽입 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main()
