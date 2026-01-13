"""
약점 분석 테스트용 샘플 데이터 삽입 스크립트

사용법:
    python insert_test_analysis_data.py <user_uuid>

시나리오:
    - Array, String: 강함 (90%+ 정답률)
    - DP, Graph: 약함 (20-30% 정답률)
    - Binary Search: 중간 (50-60% 정답률)
"""

import sys
import os
from datetime import datetime, timedelta
from uuid import UUID
import random

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
    sys.exit(1)

db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def clear_user_data(user_id: str):
    """기존 테스트 데이터 삭제"""
    print(f"Clearing existing data for user {user_id}...")

    # 순서 중요: FK 제약조건 때문에
    db.table("attempt_details").delete().in_(
        "attempt_id",
        db.table("attempts").select("id").eq("user_id", user_id).execute().data or []
    ).execute()
    db.table("hint_logs").delete().eq("user_id", user_id).execute()
    db.table("attempts").delete().eq("user_id", user_id).execute()
    db.table("user_memories").delete().eq("user_id", user_id).execute()
    db.table("user_analysis_reports").delete().eq("user_id", user_id).execute()

    print("  Done!")


def insert_user_stats(user_id: str):
    """user_stats 업데이트"""
    print("Inserting user_stats...")

    db.table("user_stats").upsert({
        "user_id": user_id,
        "level": 5,
        "total_xp": 1500,
        "problems_solved": 47,
        "problems_attempted": 60,
        "current_streak": 3,
        "longest_streak": 7,
        "last_activity_date": datetime.now().date().isoformat(),
    }, on_conflict="user_id").execute()

    print("  Done!")


def insert_attempts(user_id: str):
    """attempts 테이블에 문제 풀이 기록 삽입"""
    print("Inserting attempts...")

    # 시나리오별 문제 풀이 기록
    attempts_data = []
    base_time = datetime.now() - timedelta(days=30)

    # === Array 문제 (강함: 12개 중 11개 정답) ===
    for i in range(12):
        is_correct = i != 5  # 1개만 오답
        attempts_data.append({
            "user_id": user_id,
            "topics": ["Array", "Implementation"],
            "difficulty": "easy" if i < 6 else "medium",
            "problem_type": "blank",
            "problem_name": f"Array 문제 {i+1}",
            "is_correct": is_correct,
            "hints_used": 0 if is_correct else 1,
            "time_spent": random.randint(60, 180),
            "created_at": (base_time + timedelta(days=i)).isoformat(),
        })

    # === String 문제 (강함: 10개 중 9개 정답) ===
    for i in range(10):
        is_correct = i != 3
        attempts_data.append({
            "user_id": user_id,
            "topics": ["String", "Implementation"],
            "difficulty": "easy" if i < 5 else "medium",
            "problem_type": "blank",
            "problem_name": f"String 문제 {i+1}",
            "is_correct": is_correct,
            "hints_used": 0 if is_correct else 1,
            "time_spent": random.randint(90, 240),
            "created_at": (base_time + timedelta(days=i, hours=2)).isoformat(),
        })

    # === DP 문제 (약함: 15개 중 3개만 정답) ===
    for i in range(15):
        is_correct = i in [2, 7, 12]  # 3개만 정답
        hints = 3 if not is_correct else random.randint(0, 1)
        attempts_data.append({
            "user_id": user_id,
            "topics": ["DP", "Dynamic Programming"],
            "difficulty": "medium" if i < 10 else "hard",
            "problem_type": "blank" if i % 3 != 0 else "guided",
            "problem_name": f"DP 문제 {i+1}" if i < 10 else f"DP 배낭 문제 {i-9}",
            "is_correct": is_correct,
            "hints_used": hints,
            "time_spent": random.randint(300, 600),
            "created_at": (base_time + timedelta(days=i, hours=4)).isoformat(),
        })

    # === Graph 문제 (약함: 12개 중 2개만 정답) ===
    for i in range(12):
        is_correct = i in [4, 9]  # 2개만 정답
        hints = 3 if not is_correct else random.randint(0, 2)
        attempts_data.append({
            "user_id": user_id,
            "topics": ["Graph", "BFS", "DFS"] if i % 2 == 0 else ["Graph", "Dijkstra"],
            "difficulty": "medium" if i < 8 else "hard",
            "problem_type": "guided" if i % 3 == 0 else "blank",
            "problem_name": f"Graph 탐색 {i+1}" if i < 8 else f"Graph 최단경로 {i-7}",
            "is_correct": is_correct,
            "hints_used": hints,
            "time_spent": random.randint(300, 720),
            "created_at": (base_time + timedelta(days=i, hours=6)).isoformat(),
        })

    # === Binary Search 문제 (중간: 8개 중 5개 정답) ===
    for i in range(8):
        is_correct = i in [0, 2, 3, 5, 7]
        attempts_data.append({
            "user_id": user_id,
            "topics": ["Binary Search", "Divide and Conquer"],
            "difficulty": "medium",
            "problem_type": "blank",
            "problem_name": f"Binary Search 문제 {i+1}",
            "is_correct": is_correct,
            "hints_used": 1 if not is_correct else 0,
            "time_spent": random.randint(120, 300),
            "created_at": (base_time + timedelta(days=i, hours=8)).isoformat(),
        })

    # === Stack 문제 (중상: 6개 중 5개 정답) ===
    for i in range(6):
        is_correct = i != 2
        attempts_data.append({
            "user_id": user_id,
            "topics": ["Stack", "Data Structures"],
            "difficulty": "easy" if i < 3 else "medium",
            "problem_type": "blank",
            "problem_name": f"Stack 문제 {i+1}",
            "is_correct": is_correct,
            "hints_used": 0,
            "time_spent": random.randint(60, 180),
            "created_at": (base_time + timedelta(days=i, hours=10)).isoformat(),
        })

    # 삽입
    for attempt in attempts_data:
        db.table("attempts").insert(attempt).execute()

    print(f"  Inserted {len(attempts_data)} attempts")


def insert_user_memories(user_id: str):
    """user_memories 테이블에 학습 세션 기록 삽입"""
    print("Inserting user_memories...")

    memories_data = [
        # DP 실패 세션들
        {
            "user_id": user_id,
            "session_id": f"session_dp_1",
            "session_type": "problem_solving",
            "summary": "DP 배낭 문제 시도. 점화식을 세우는 것에 어려움을 겪었고, 상태 정의를 명확히 하지 못함. 힌트 3개 사용에도 풀이 실패.",
            "key_topics": ["DP", "배낭 문제"],
            "concepts_learned": [],
            "concepts_struggling": ["점화식 도출", "상태 정의", "2차원 DP 테이블"],
            "teaching_notes": ["작은 케이스부터 시작하도록 유도 필요", "dp[i][j]의 의미를 문장으로 먼저 정의하게 해야 함"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "problem_name": "DP 배낭 문제",
            "was_successful": False,
            "hints_needed": 3,
            "time_spent_seconds": 1200,
        },
        {
            "user_id": user_id,
            "session_id": f"session_dp_2",
            "summary": "DP 계단 오르기 문제 시도. 점화식은 이해했으나 초기값 설정에서 실수. 부분 성공.",
            "key_topics": ["DP", "점화식"],
            "concepts_learned": ["1차원 DP 기초"],
            "concepts_struggling": ["초기값 설정", "경계 조건"],
            "teaching_notes": ["n=0, n=1 케이스를 먼저 확인하게 유도"],
            "breakthrough_moments": ["dp[i] = dp[i-1] + dp[i-2] 패턴 이해"],
            "student_mood": "confused",
            "problem_name": "DP 계단 오르기",
            "was_successful": True,
            "hints_needed": 2,
            "time_spent_seconds": 900,
        },
        # Graph 실패 세션들
        {
            "user_id": user_id,
            "session_id": f"session_graph_1",
            "summary": "BFS 미로 탐색 문제. visited 배열 업데이트 위치를 잘못 설정하여 무한 루프 발생. 큐에 넣을 때 vs pop할 때 차이를 이해하지 못함.",
            "key_topics": ["Graph", "BFS", "미로 탐색"],
            "concepts_learned": [],
            "concepts_struggling": ["방문 체크 타이밍", "BFS 큐 사용법", "그래프 표현"],
            "teaching_notes": ["BFS는 큐 삽입 시점에 visited 체크해야 함을 강조", "그래프를 시각화하면서 설명 필요"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "problem_name": "BFS 미로 탐색",
            "was_successful": False,
            "hints_needed": 3,
            "time_spent_seconds": 1500,
        },
        {
            "user_id": user_id,
            "session_id": f"session_graph_2",
            "summary": "DFS 섬 개수 세기 문제. 재귀 호출에서 종료 조건을 잘못 설정하여 스택 오버플로우 발생.",
            "key_topics": ["Graph", "DFS", "재귀"],
            "concepts_learned": [],
            "concepts_struggling": ["재귀 종료 조건", "방문 체크"],
            "teaching_notes": ["base case를 먼저 작성하도록 유도"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "problem_name": "DFS 섬 개수",
            "was_successful": False,
            "hints_needed": 3,
            "time_spent_seconds": 1100,
        },
        # Array 성공 세션
        {
            "user_id": user_id,
            "session_id": f"session_array_1",
            "summary": "배열 정렬 문제 완벽 해결. 투 포인터 기법을 적용하여 효율적으로 풀이.",
            "key_topics": ["Array", "Two Pointers"],
            "concepts_learned": ["투 포인터 기법", "in-place 정렬"],
            "concepts_struggling": [],
            "teaching_notes": [],
            "breakthrough_moments": ["투 포인터로 O(n) 해결 가능함을 깨달음"],
            "student_mood": "confident",
            "problem_name": "배열 정렬하기",
            "was_successful": True,
            "hints_needed": 0,
            "time_spent_seconds": 180,
        },
        # String 성공 세션
        {
            "user_id": user_id,
            "session_id": f"session_string_1",
            "summary": "문자열 슬라이싱 문제 성공. 파이썬 슬라이싱 문법을 잘 활용함.",
            "key_topics": ["String", "Python"],
            "concepts_learned": ["문자열 슬라이싱", "reverse 기법"],
            "concepts_struggling": [],
            "teaching_notes": [],
            "breakthrough_moments": ["s[::-1] 패턴 활용"],
            "student_mood": "confident",
            "problem_name": "문자열 뒤집기",
            "was_successful": True,
            "hints_needed": 0,
            "time_spent_seconds": 120,
        },
        # Binary Search 부분 성공
        {
            "user_id": user_id,
            "session_id": f"session_bs_1",
            "summary": "이분 탐색 문제 시도. 경계값 처리에서 실수가 있었으나 힌트 후 해결.",
            "key_topics": ["Binary Search"],
            "concepts_learned": ["이분 탐색 기본"],
            "concepts_struggling": ["경계값 처리", "left <= right vs left < right"],
            "teaching_notes": ["while 조건과 mid 계산 방식의 관계 설명 필요"],
            "breakthrough_moments": [],
            "student_mood": "curious",
            "problem_name": "이분 탐색 기본",
            "was_successful": True,
            "hints_needed": 1,
            "time_spent_seconds": 300,
        },
    ]

    # 최근 세션 추가
    base_time = datetime.now() - timedelta(days=10)
    for i, mem in enumerate(memories_data):
        mem["created_at"] = (base_time + timedelta(days=i)).isoformat()
        mem["learning_insights"] = {
            "prefers_examples": True,
            "prefers_analogies": False,
            "hint_sensitivity": "medium",
            "pace": "slow",
            "common_errors": ["점화식 도출", "방문 체크"]
        }
        db.table("user_memories").insert(mem).execute()

    print(f"  Inserted {len(memories_data)} memories")


def insert_hint_logs(user_id: str):
    """hint_logs 테이블에 힌트 사용 기록 삽입"""
    print("Inserting hint_logs...")

    hints_data = []
    base_time = datetime.now() - timedelta(days=20)

    # DP 문제에서 힌트 많이 사용
    for i in range(15):
        for level in [1, 2, 3]:  # 레벨 1, 2, 3 힌트 모두 사용
            hints_data.append({
                "user_id": user_id,
                "hint_level": level,
                "xp_cost": level * 5,
                "created_at": (base_time + timedelta(days=i, hours=level)).isoformat(),
            })

    # Graph 문제에서도 힌트 많이 사용
    for i in range(10):
        for level in [1, 2, 3]:
            hints_data.append({
                "user_id": user_id,
                "hint_level": level,
                "xp_cost": level * 5,
                "created_at": (base_time + timedelta(days=i+5, hours=level+3)).isoformat(),
            })

    # Array/String은 힌트 거의 안 씀
    for i in range(3):
        hints_data.append({
            "user_id": user_id,
            "hint_level": 1,
            "xp_cost": 5,
            "created_at": (base_time + timedelta(days=i+10)).isoformat(),
        })

    for hint in hints_data:
        db.table("hint_logs").insert(hint).execute()

    print(f"  Inserted {len(hints_data)} hint logs")


def main():
    if len(sys.argv) < 2:
        print("Usage: python insert_test_analysis_data.py <user_uuid>")
        print("Example: python insert_test_analysis_data.py 12345678-1234-1234-1234-123456789012")
        sys.exit(1)

    user_id = sys.argv[1]

    # UUID 형식 검증
    try:
        UUID(user_id)
    except ValueError:
        print(f"Error: Invalid UUID format: {user_id}")
        sys.exit(1)

    print(f"\n=== Inserting test data for analysis ===")
    print(f"User ID: {user_id}")
    print(f"Scenario: DP/Graph weak, Array/String strong\n")

    # 1. 기존 데이터 삭제
    clear_user_data(user_id)

    # 2. 새 데이터 삽입
    insert_user_stats(user_id)
    insert_attempts(user_id)
    insert_user_memories(user_id)
    insert_hint_logs(user_id)

    print(f"\n=== Done! ===")
    print(f"Now you can test the analysis page for user {user_id}")
    print(f"Expected results:")
    print(f"  - Strengths: Array (90%+), String (90%+), Stack (80%+)")
    print(f"  - Weaknesses: DP (20%), Graph (17%)")
    print(f"  - BKT mastery should show DP and Graph with low mastery")
    print(f"  - concepts_struggling: 점화식 도출, 상태 정의, 방문 체크 등")


if __name__ == "__main__":
    main()
