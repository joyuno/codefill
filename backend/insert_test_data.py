"""테스트 데이터 삽입 스크립트.

BKT 강점/약점 분석을 극단적으로 테스트하기 위한 데이터.
- 강점 토픽: Array, String (연속 정답으로 mastery 0.8+)
- 약점 토픽: DP, Graph (연속 오답으로 mastery 0.3-)
- 중간 토픽: BFS (혼합)
"""

import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
db = create_client(url, key)

USER_ID = "ccb94830-e83e-44b2-be14-67d02475eaf8"


def insert_user_stats():
    """user_stats 삽입."""
    print("1. user_stats 삽입...")

    existing = db.table("user_stats").select("*").eq("user_id", USER_ID).execute()

    stats_data = {
        "user_id": USER_ID,
        "level": 7,
        "problems_solved": 35,
        "current_streak": 5,
        "longest_streak": 12,
        "total_xp": 2500,
    }

    if existing.data:
        db.table("user_stats").update(stats_data).eq("user_id", USER_ID).execute()
        print("   - 기존 데이터 업데이트")
    else:
        db.table("user_stats").insert(stats_data).execute()
        print("   - 새 데이터 삽입")


def insert_extreme_attempts():
    """극단적인 BKT 테스트를 위한 attempts 삽입.

    BKT 공식: 시퀀스 순서가 중요!
    - 연속 정답 → mastery 상승
    - 연속 오답 → mastery 하락
    - 최근 결과가 더 큰 영향
    """
    print("2. 극단적인 attempts 삽입...")

    attempts_data = []
    now = datetime.utcnow()

    # 강점 토픽: Array - 8연속 정답 (mastery 0.85+)
    for i in range(8):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": True,
            "score": 90 + i,
            "time_spent": 60 + i * 10,
            "hints_used": 0,
            "xp_earned": 50,
            "topics": ["Array", "기본 자료구조"],
            "difficulty": "medium" if i < 5 else "hard",
            "problem_name": f"Array 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 0,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=20-i, hours=i)).isoformat(),
        })

    # 강점 토픽: String - 7연속 정답 (mastery 0.80+)
    for i in range(7):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": True,
            "score": 85 + i,
            "time_spent": 70 + i * 10,
            "hints_used": 0 if i > 2 else 1,
            "xp_earned": 50,
            "topics": ["String", "문자열 처리"],
            "difficulty": "easy" if i < 3 else "medium",
            "problem_name": f"String 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 0 if i > 2 else 1,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=18-i, hours=i*2)).isoformat(),
        })

    # 약점 토픽: DP - 10번 중 2번만 정답, 최근 6연속 오답 (mastery 0.25-)
    dp_results = [True, False, True, False, False, False, False, False, False, False]  # 최근으로 갈수록 오답
    for i, is_correct in enumerate(dp_results):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": is_correct,
            "score": 75 if is_correct else 0,
            "time_spent": 300 + i * 30,  # 오래 걸림
            "hints_used": 0 if is_correct else 3,
            "xp_earned": 50 if is_correct else 10,
            "topics": ["DP", "동적 프로그래밍", "점화식"],
            "difficulty": "hard",
            "problem_name": f"DP 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 0 if is_correct else 3,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=15-i, hours=i)).isoformat(),
        })

    # 약점 토픽: Graph - 8번 중 1번만 정답, 최근 5연속 오답 (mastery 0.20-)
    graph_results = [False, True, False, False, False, False, False, False]
    for i, is_correct in enumerate(graph_results):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": is_correct,
            "score": 70 if is_correct else 0,
            "time_spent": 250 + i * 25,
            "hints_used": 0 if is_correct else 2,
            "xp_earned": 50 if is_correct else 10,
            "topics": ["Graph", "그래프 탐색"],
            "difficulty": "hard",
            "problem_name": f"Graph 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 0 if is_correct else 2,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=12-i, hours=i*2)).isoformat(),
        })

    # 중간 토픽: BFS - 6번 중 3번 정답, 혼합 (mastery 0.50-0.60)
    bfs_results = [True, False, True, False, True, False]
    for i, is_correct in enumerate(bfs_results):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": is_correct,
            "score": 80 if is_correct else 0,
            "time_spent": 150 + i * 20,
            "hints_used": 1,
            "xp_earned": 50 if is_correct else 10,
            "topics": ["BFS", "너비 우선 탐색"],
            "difficulty": "medium",
            "problem_name": f"BFS 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 1,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=8-i, hours=i)).isoformat(),
        })

    # 중간 토픽: Sorting - 5번 중 4번 정답 (mastery 0.70-0.75)
    sorting_results = [True, True, False, True, True]
    for i, is_correct in enumerate(sorting_results):
        attempts_data.append({
            "user_id": USER_ID,
            "is_correct": is_correct,
            "score": 85 if is_correct else 0,
            "time_spent": 100 + i * 15,
            "hints_used": 0,
            "xp_earned": 50 if is_correct else 10,
            "topics": ["Sorting", "정렬"],
            "difficulty": "easy" if i < 2 else "medium",
            "problem_name": f"Sorting 문제 {i+1}",
            "problem_type": "fill_blank",
            "total_hints_requested": 0,
            "attempt_number": 1,
            "created_at": (now - timedelta(days=5-i, hours=i)).isoformat(),
        })

    # 기존 데이터 삭제 후 삽입
    db.table("attempts").delete().eq("user_id", USER_ID).execute()
    db.table("attempts").insert(attempts_data).execute()

    print(f"   - {len(attempts_data)}개 시도 삽입")
    print(f"   - 강점 예상: Array(8정답), String(7정답)")
    print(f"   - 약점 예상: DP(2/10), Graph(1/8)")
    print(f"   - 중간 예상: BFS(3/6), Sorting(4/5)")

    return attempts_data


def create_chat_sessions():
    """chat_sessions 생성."""
    print("3. chat_sessions 생성...")

    now = datetime.utcnow()
    sessions = []

    topics = ["Array", "String", "DP", "Graph", "BFS", "Sorting", "DP", "Graph"]
    for i in range(8):
        session_id = str(uuid.uuid4())
        sessions.append({
            "id": session_id,
            "user_id": USER_ID,
            "session_type": "problem_solving",
            "title": f"{topics[i]} 학습 세션",
            "created_at": (now - timedelta(days=8-i, hours=i*2)).isoformat(),
        })

    db.table("chat_sessions").delete().eq("user_id", USER_ID).execute()
    db.table("chat_sessions").insert(sessions).execute()
    print(f"   - {len(sessions)}개 세션 생성")

    return [s["id"] for s in sessions]


def insert_user_memories(session_ids):
    """user_memories 삽입."""
    print("4. user_memories 삽입...")

    memories_data = []
    now = datetime.utcnow()

    session_data = [
        {
            "problem_name": "Array 고급 문제",
            "summary": "배열 조작 문제를 완벽하게 해결했습니다. 투 포인터 기법을 능숙하게 활용했습니다.",
            "key_topics": ["Array", "Two Pointer"],
            "concepts_learned": ["투 포인터", "슬라이딩 윈도우"],
            "concepts_struggling": [],
            "teaching_notes": ["자신감 있게 풀이 진행"],
            "breakthrough_moments": ["투 포인터로 O(n)에 해결"],
            "student_mood": "confident",
            "was_successful": True,
            "hints_needed": 0,
        },
        {
            "problem_name": "String 파싱 문제",
            "summary": "문자열 파싱 문제를 빠르게 해결했습니다.",
            "key_topics": ["String", "파싱"],
            "concepts_learned": ["정규표현식", "문자열 슬라이싱"],
            "concepts_struggling": [],
            "teaching_notes": [],
            "breakthrough_moments": ["split과 join 활용"],
            "student_mood": "confident",
            "was_successful": True,
            "hints_needed": 0,
        },
        {
            "problem_name": "DP 점화식 문제",
            "summary": "DP 점화식 세우는 과정에서 막혔습니다. 상태 정의가 어려웠습니다.",
            "key_topics": ["DP", "점화식"],
            "concepts_learned": [],
            "concepts_struggling": ["상태 정의", "점화식 도출", "메모이제이션"],
            "teaching_notes": ["작은 케이스부터 시작하도록 유도 필요"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "was_successful": False,
            "hints_needed": 3,
        },
        {
            "problem_name": "Graph DFS 문제",
            "summary": "그래프 탐색에서 방문 체크를 놓쳐 무한루프에 빠졌습니다.",
            "key_topics": ["Graph", "DFS"],
            "concepts_learned": [],
            "concepts_struggling": ["방문 체크", "재귀 종료 조건", "그래프 표현"],
            "teaching_notes": ["그래프 시각화가 필요"],
            "breakthrough_moments": [],
            "student_mood": "confused",
            "was_successful": False,
            "hints_needed": 3,
        },
        {
            "problem_name": "BFS 미로 탐색",
            "summary": "BFS로 최단 경로를 찾았지만, 처음엔 헷갈렸습니다.",
            "key_topics": ["BFS", "최단 경로"],
            "concepts_learned": ["큐 활용"],
            "concepts_struggling": ["방향 벡터"],
            "teaching_notes": ["그림으로 설명 효과적"],
            "breakthrough_moments": ["큐에서 꺼낼 때 방문 체크"],
            "student_mood": "curious",
            "was_successful": True,
            "hints_needed": 2,
        },
        {
            "problem_name": "Sorting 알고리즘",
            "summary": "퀵소트 구현을 잘 해냈습니다.",
            "key_topics": ["Sorting", "퀵소트"],
            "concepts_learned": ["파티션", "피벗 선택"],
            "concepts_struggling": [],
            "teaching_notes": [],
            "breakthrough_moments": ["파티션 과정 이해"],
            "student_mood": "confident",
            "was_successful": True,
            "hints_needed": 0,
        },
        {
            "problem_name": "DP 배낭 문제",
            "summary": "배낭 문제에서 2차원 DP 테이블 이해가 안 됐습니다.",
            "key_topics": ["DP", "배낭 문제"],
            "concepts_learned": [],
            "concepts_struggling": ["2차원 DP", "공간 최적화", "역추적"],
            "teaching_notes": ["표로 시각화 필수"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "was_successful": False,
            "hints_needed": 3,
        },
        {
            "problem_name": "Graph 최단경로",
            "summary": "다익스트라 알고리즘 구현에 실패했습니다.",
            "key_topics": ["Graph", "다익스트라"],
            "concepts_learned": [],
            "concepts_struggling": ["우선순위 큐", "relaxation", "음수 가중치"],
            "teaching_notes": ["기초 BFS부터 복습 필요"],
            "breakthrough_moments": [],
            "student_mood": "frustrated",
            "was_successful": False,
            "hints_needed": 3,
        },
    ]

    for i, session in enumerate(session_data):
        memories_data.append({
            "user_id": USER_ID,
            "session_id": session_ids[i % len(session_ids)],
            "problem_name": session["problem_name"],
            "summary": session["summary"],
            "key_topics": session["key_topics"],
            "concepts_learned": session["concepts_learned"],
            "concepts_struggling": session["concepts_struggling"],
            "teaching_notes": session["teaching_notes"],
            "breakthrough_moments": session["breakthrough_moments"],
            "student_mood": session["student_mood"],
            "was_successful": session["was_successful"],
            "hints_needed": session["hints_needed"],
            "learning_insights": {
                "prefers_examples": True,
                "prefers_analogies": True,
                "hint_sensitivity": "high" if session["hints_needed"] >= 2 else "low",
                "pace": "slow" if not session["was_successful"] else "medium",
                "common_errors": ["인덱스 실수", "경계 조건 누락"] if not session["was_successful"] else [],
            },
            "created_at": (now - timedelta(days=8-i, hours=i*2)).isoformat(),
        })

    db.table("user_memories").delete().eq("user_id", USER_ID).execute()
    db.table("user_memories").insert(memories_data).execute()
    print(f"   - {len(memories_data)}개 학습 기록 삽입")


def main():
    print("=" * 60)
    print("극단적 BKT 테스트 데이터 삽입")
    print(f"User ID: {USER_ID}")
    print("=" * 60)
    print()
    print("예상 결과:")
    print("  강점 (mastery >= 0.8): Array, String")
    print("  약점 (mastery < 0.5): DP, Graph")
    print("  중간 (0.5 ~ 0.8): BFS, Sorting")
    print()
    print("=" * 60)

    insert_user_stats()
    insert_extreme_attempts()
    session_ids = create_chat_sessions()
    insert_user_memories(session_ids)

    print()
    print("=" * 60)
    print("테스트 데이터 삽입 완료!")
    print("이제 /analysis 페이지에서 '분석 시작' 버튼을 클릭하세요.")
    print("=" * 60)


if __name__ == "__main__":
    main()
