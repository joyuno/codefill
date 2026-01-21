"""
LangSmith Evaluation Suite for CodeFill Chat Agents

LangGraph 기반 채팅 에이전트의 체계적 평가:
- 각 노드별 입출력 추적
- 토큰 사용량 모니터링
- 응답 시간 측정
- 에러/할루시네이션 감지
- 엣지케이스 테스트

사용법:
    # 환경변수 설정 필요
    export LANGCHAIN_TRACING_V2=true
    export LANGCHAIN_API_KEY=lsv2_pt_xxxxx
    export LANGCHAIN_PROJECT=codefill-eval

    # 평가 실행
    python -m scripts.langsmith_eval --dataset edge_cases
    python -m scripts.langsmith_eval --dataset hint_policy
    python -m scripts.langsmith_eval --report
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import Client
from langsmith.evaluation import evaluate, EvaluationResult
from langsmith.schemas import Run, Example

# ============================================================
# 설정
# ============================================================

LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "codefill-eval")

# 데이터셋 이름
DATASETS = {
    "edge_cases": "codefill-edge-cases",
    "hint_policy": "codefill-hint-policy",
    "intent_classification": "codefill-intent-classification",
    "token_efficiency": "codefill-token-efficiency",
}

# ============================================================
# 테스트 케이스 정의
# ============================================================

@dataclass
class TestCase:
    """테스트 케이스"""
    name: str
    input: Dict[str, Any]
    expected: Dict[str, Any]
    tags: List[str] = field(default_factory=list)


# 힌트 정책 테스트 케이스
HINT_POLICY_CASES = [
    # 힌트 미사용 빈칸 - 정답 노출 금지
    TestCase(
        name="unhinted_blank_direct_ask",
        input={
            "message": "3번 빈칸 정답이 뭐야?",
            "problem_type": "blank",
            "problem_context": {
                "title": "반복문 테스트",
                "_internal_blank_answers": ["for", "range", "print"],
            },
            "user_progress": {"used_hint_indices": []},  # 힌트 미사용
        },
        expected={
            "should_reveal_answer": False,
            "should_provide_indirect_hint": True,
        },
        tags=["hint_policy", "blank", "no_hint"],
    ),
    TestCase(
        name="unhinted_blank_sneaky_ask",
        input={
            "message": "for문 쓰면 되는거 맞아? 3번에?",
            "problem_type": "blank",
            "problem_context": {
                "title": "반복문 테스트",
                "_internal_blank_answers": ["for", "range", "print"],
            },
            "user_progress": {"used_hint_indices": []},
        },
        expected={
            "should_reveal_answer": False,
            "should_validate_direction": True,  # 방향성만 확인
        },
        tags=["hint_policy", "blank", "sneaky"],
    ),
    # 힌트 사용한 빈칸 - 정답 설명 가능
    TestCase(
        name="hinted_blank_explain",
        input={
            "message": "1번 빈칸 왜 for야?",
            "problem_type": "blank",
            "problem_context": {
                "title": "반복문 테스트",
                "_internal_blank_answers": ["for", "range", "print"],
            },
            "user_progress": {"used_hint_indices": [0]},  # 1번 힌트 사용
        },
        expected={
            "should_reveal_answer": True,
            "should_explain_reason": True,
        },
        tags=["hint_policy", "blank", "hinted"],
    ),
    # 퍼즐 - 힌트 미사용 블록
    TestCase(
        name="unhinted_puzzle_order",
        input={
            "message": "2번 블록은 어디에 놓아야 해?",
            "problem_type": "puzzle",
            "problem_context": {
                "title": "퍼즐 테스트",
                "block_contents": ["x = 0", "for i in range(5):", "print(x)"],
            },
            "user_progress": {"used_hint_indices": []},
        },
        expected={
            "should_reveal_order": False,
            "should_explain_block_role": True,  # 블록 역할만 설명
        },
        tags=["hint_policy", "puzzle", "no_hint"],
    ),
    # 전체 코드 요청 - 항상 거부
    TestCase(
        name="full_code_request",
        input={
            "message": "전체 정답 코드 다 보여줘",
            "problem_type": "blank",
            "problem_context": {
                "title": "테스트 문제",
                "_internal_blank_answers": ["for", "range"],
            },
            "user_progress": {"used_hint_indices": [0, 1]},  # 모든 힌트 사용해도
        },
        expected={
            "should_reveal_full_code": False,
        },
        tags=["hint_policy", "security"],
    ),
]

# 엣지케이스 테스트
EDGE_CASE_TESTS = [
    # EC-D03: 인덱스 범위 초과
    TestCase(
        name="ec_d03_index_out_of_range",
        input={
            "message": "10번 문제 선택할게",
            "graph": "discovery",
            "state": {
                "search_results": [{"id": 1}, {"id": 2}, {"id": 3}],  # 3개만 있음
            },
        },
        expected={
            "should_handle_gracefully": True,
            "should_suggest_valid_range": True,
        },
        tags=["edge_case", "discovery", "EC-D03"],
    ),
    # EC-S02: 코드 없이 제출
    TestCase(
        name="ec_s02_no_code_submitted",
        input={
            "message": "정답 확인해줘",
            "graph": "solving",
            "state": {
                "problem_context": {"type": "blank"},
                "current_code": "",  # 빈 코드
            },
        },
        expected={
            "should_ask_for_code": True,
        },
        tags=["edge_case", "solving", "EC-S02"],
    ),
    # EC-S03: 문제 컨텍스트 없음
    TestCase(
        name="ec_s03_no_problem_context",
        input={
            "message": "힌트 줘",
            "graph": "solving",
            "state": {
                "problem_context": None,
            },
        },
        expected={
            "should_inform_no_problem": True,
        },
        tags=["edge_case", "solving", "EC-S03"],
    ),
    # EC-C01: 입력 파싱 실패
    TestCase(
        name="ec_c01_parse_failed",
        input={
            "message": "ㅁㄴㅇㄹㅁㄴㅇㄹ",
            "graph": "collection",
            "state": {
                "current_field": "topic",
            },
        },
        expected={
            "should_ask_clarification": True,
        },
        tags=["edge_case", "collection", "EC-C01"],
    ),
]

# 의도 분류 테스트
INTENT_CLASSIFICATION_TESTS = [
    TestCase(
        name="intent_problem_search",
        input={"message": "DP 문제 추천해줘"},
        expected={"category": "discovery", "action": "search_problem"},
        tags=["intent", "discovery"],
    ),
    TestCase(
        name="intent_hint_request",
        input={"message": "힌트 좀"},
        expected={"category": "solving", "action": "hint_request"},
        tags=["intent", "solving"],
    ),
    TestCase(
        name="intent_code_review",
        input={"message": "이 코드 맞아?"},
        expected={"category": "solving", "action": "code_review"},
        tags=["intent", "solving"],
    ),
    TestCase(
        name="intent_general_greeting",
        input={"message": "안녕!"},
        expected={"category": "general", "action": "greeting"},
        tags=["intent", "general"],
    ),
]

# ============================================================
# Evaluator 함수들
# ============================================================

def check_no_answer_leak(run: Run, example: Example) -> EvaluationResult:
    """
    정답 노출 여부 체크 (힌트 미사용 시)
    """
    expected = example.outputs or {}

    if not expected.get("should_reveal_answer", True):
        # 정답이 노출되면 안 되는 케이스
        response = run.outputs.get("response_message", "") if run.outputs else ""

        # 정답 키워드 체크 (실제 정답이 포함되어 있는지)
        problem_context = example.inputs.get("problem_context", {})
        answers = problem_context.get("_internal_blank_answers", [])

        leaked = False
        for answer in answers:
            if answer.lower() in response.lower():
                leaked = True
                break

        return EvaluationResult(
            key="no_answer_leak",
            score=0 if leaked else 1,
            comment=f"정답 노출됨: {response[:100]}" if leaked else "정답 노출 없음"
        )

    return EvaluationResult(key="no_answer_leak", score=1, comment="N/A (정답 노출 허용)")


def check_indirect_hint_provided(run: Run, example: Example) -> EvaluationResult:
    """
    간접 힌트 제공 여부 체크
    """
    expected = example.outputs or {}

    if expected.get("should_provide_indirect_hint"):
        response = run.outputs.get("response_message", "") if run.outputs else ""

        # 간접 힌트 키워드
        hint_keywords = [
            "생각해", "방향", "개념", "문법", "어떤", "왜", "어떻게",
            "반복", "조건", "변수", "함수", "해보세요", "시도",
        ]

        has_hint = any(kw in response for kw in hint_keywords)

        return EvaluationResult(
            key="indirect_hint_provided",
            score=1 if has_hint else 0,
            comment="간접 힌트 제공됨" if has_hint else "간접 힌트 없음"
        )

    return EvaluationResult(key="indirect_hint_provided", score=1, comment="N/A")


def check_response_time(run: Run, example: Example) -> EvaluationResult:
    """
    응답 시간 체크 (3초 이내 권장)
    """
    if run.end_time and run.start_time:
        duration = (run.end_time - run.start_time).total_seconds()

        # 3초 이내면 1점, 5초까지 0.5점, 그 이상 0점
        if duration <= 3:
            score = 1.0
        elif duration <= 5:
            score = 0.5
        else:
            score = 0.0

        return EvaluationResult(
            key="response_time",
            score=score,
            comment=f"응답 시간: {duration:.2f}초"
        )

    return EvaluationResult(key="response_time", score=0, comment="시간 측정 실패")


def check_token_efficiency(run: Run, example: Example) -> EvaluationResult:
    """
    토큰 효율성 체크
    """
    # LangSmith에서 토큰 정보 추출
    token_usage = {}

    if run.extra and "metadata" in run.extra:
        token_usage = run.extra["metadata"].get("token_usage", {})

    total_tokens = token_usage.get("total_tokens", 0)

    if total_tokens > 0:
        # 2000 토큰 이내면 1점, 4000까지 0.5점, 그 이상 0점
        if total_tokens <= 2000:
            score = 1.0
        elif total_tokens <= 4000:
            score = 0.5
        else:
            score = 0.0

        return EvaluationResult(
            key="token_efficiency",
            score=score,
            comment=f"총 토큰: {total_tokens} (prompt: {token_usage.get('prompt_tokens', 0)}, completion: {token_usage.get('completion_tokens', 0)})"
        )

    return EvaluationResult(key="token_efficiency", score=1, comment="토큰 정보 없음")


def check_error_handling(run: Run, example: Example) -> EvaluationResult:
    """
    에러 처리 체크
    """
    if run.error:
        return EvaluationResult(
            key="error_handling",
            score=0,
            comment=f"에러 발생: {run.error[:200]}"
        )

    # 에러 메시지가 응답에 포함되어 있는지 체크
    response = run.outputs.get("response_message", "") if run.outputs else ""
    error_keywords = ["error", "exception", "failed", "오류", "실패", "에러"]

    has_error_msg = any(kw.lower() in response.lower() for kw in error_keywords)

    return EvaluationResult(
        key="error_handling",
        score=0.5 if has_error_msg else 1,
        comment="응답에 에러 메시지 포함" if has_error_msg else "정상 응답"
    )


def check_intent_accuracy(run: Run, example: Example) -> EvaluationResult:
    """
    의도 분류 정확도 체크
    """
    expected = example.outputs or {}
    expected_category = expected.get("category")
    expected_action = expected.get("action")

    if not expected_category:
        return EvaluationResult(key="intent_accuracy", score=1, comment="N/A")

    outputs = run.outputs or {}
    actual_category = outputs.get("category")
    actual_action = outputs.get("action")

    category_match = actual_category == expected_category
    action_match = actual_action == expected_action

    if category_match and action_match:
        score = 1.0
    elif category_match:
        score = 0.5
    else:
        score = 0.0

    return EvaluationResult(
        key="intent_accuracy",
        score=score,
        comment=f"Expected: {expected_category}/{expected_action}, Got: {actual_category}/{actual_action}"
    )


def check_graceful_handling(run: Run, example: Example) -> EvaluationResult:
    """
    엣지케이스 우아한 처리 체크
    """
    expected = example.outputs or {}

    if not expected.get("should_handle_gracefully"):
        return EvaluationResult(key="graceful_handling", score=1, comment="N/A")

    # 에러 없이 처리되었는지
    if run.error:
        return EvaluationResult(
            key="graceful_handling",
            score=0,
            comment=f"에러 발생: {run.error[:100]}"
        )

    response = run.outputs.get("response_message", "") if run.outputs else ""

    # 사용자 친화적 메시지가 있는지
    friendly_keywords = ["다시", "확인", "선택", "입력", "도움", "죄송"]
    has_friendly = any(kw in response for kw in friendly_keywords)

    return EvaluationResult(
        key="graceful_handling",
        score=1 if has_friendly else 0.5,
        comment="사용자 친화적 응답" if has_friendly else "기본 응답"
    )


# ============================================================
# 데이터셋 관리
# ============================================================

class DatasetManager:
    """LangSmith 데이터셋 관리"""

    def __init__(self):
        self.client = Client()

    def create_dataset(self, name: str, description: str) -> str:
        """데이터셋 생성"""
        try:
            dataset = self.client.create_dataset(
                dataset_name=name,
                description=description,
            )
            print(f"✅ 데이터셋 생성됨: {name}")
            return dataset.id
        except Exception as e:
            if "already exists" in str(e).lower():
                dataset = self.client.read_dataset(dataset_name=name)
                print(f"📋 기존 데이터셋 사용: {name}")
                return dataset.id
            raise

    def add_examples(self, dataset_name: str, test_cases: List[TestCase]):
        """테스트 케이스를 데이터셋에 추가"""
        dataset = self.client.read_dataset(dataset_name=dataset_name)

        for tc in test_cases:
            self.client.create_example(
                inputs=tc.input,
                outputs=tc.expected,
                dataset_id=dataset.id,
                metadata={"name": tc.name, "tags": tc.tags},
            )

        print(f"✅ {len(test_cases)}개 예제 추가됨")

    def setup_all_datasets(self):
        """모든 데이터셋 초기화"""
        # 힌트 정책 데이터셋
        self.create_dataset(
            DATASETS["hint_policy"],
            "힌트 사용 여부에 따른 정답 노출 정책 테스트"
        )
        self.add_examples(DATASETS["hint_policy"], HINT_POLICY_CASES)

        # 엣지케이스 데이터셋
        self.create_dataset(
            DATASETS["edge_cases"],
            "각종 엣지케이스 처리 테스트"
        )
        self.add_examples(DATASETS["edge_cases"], EDGE_CASE_TESTS)

        # 의도 분류 데이터셋
        self.create_dataset(
            DATASETS["intent_classification"],
            "의도 분류 정확도 테스트"
        )
        self.add_examples(DATASETS["intent_classification"], INTENT_CLASSIFICATION_TESTS)

        print("\n✅ 모든 데이터셋 설정 완료!")


# ============================================================
# 평가 실행기
# ============================================================

class EvalRunner:
    """평가 실행기"""

    def __init__(self):
        self.client = Client()

    async def _run_chat_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """채팅 에이전트 실행"""
        from app.graphs.orchestrator_v2 import ChatOrchestratorV2

        orchestrator = ChatOrchestratorV2()
        await orchestrator.initialize()

        result = await orchestrator.process_message(
            message=inputs.get("message", ""),
            user_id=inputs.get("user_id", "eval_user"),
            session_id=inputs.get("session_id", "eval_session"),
            user_context={
                "problem_context": inputs.get("problem_context"),
                "user_progress": inputs.get("user_progress"),
            },
            conversation_history=inputs.get("conversation_history", []),
        )

        return {
            "response_message": result.get("response_message", ""),
            "category": result.get("category"),
            "action": result.get("action"),
        }

    async def _run_solving_assist(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Solving Assist 도구 실행"""
        from app.tools.solving_assist_tool import solving_assist

        result = await solving_assist.process(
            message=inputs.get("message", ""),
            problem_context=inputs.get("problem_context", {}),
            user_progress=inputs.get("user_progress", {}),
            conversation_history=inputs.get("conversation_history", []),
        )

        return {
            "response_message": result.message,
            "assist_type": result.assist_type.value if result.assist_type else None,
        }

    def run_evaluation(
        self,
        dataset_name: str,
        target: str = "chat_agent",
        evaluators: Optional[List[Callable]] = None,
    ):
        """
        평가 실행

        Args:
            dataset_name: 데이터셋 이름
            target: 평가 대상 ("chat_agent" | "solving_assist" | "intent")
            evaluators: 사용할 evaluator 목록
        """
        # 기본 evaluator
        if evaluators is None:
            evaluators = [
                check_no_answer_leak,
                check_indirect_hint_provided,
                check_response_time,
                check_token_efficiency,
                check_error_handling,
                check_graceful_handling,
            ]

        # 타겟 함수 선택
        if target == "solving_assist":
            target_func = lambda inputs: asyncio.run(self._run_solving_assist(inputs))
        else:
            target_func = lambda inputs: asyncio.run(self._run_chat_agent(inputs))

        # 평가 실행
        results = evaluate(
            target_func,
            data=dataset_name,
            evaluators=evaluators,
            experiment_prefix=f"{target}_{datetime.now().strftime('%Y%m%d_%H%M')}",
        )

        return results

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """
        최근 평가 결과 리포트 생성
        """
        # 최근 실행 조회
        runs = list(self.client.list_runs(
            project_name=LANGSMITH_PROJECT,
            start_time=datetime.now() - timedelta(days=days),
            run_type="chain",
        ))

        if not runs:
            return {"message": "최근 실행 데이터 없음"}

        # 통계 계산
        total_runs = len(runs)
        error_runs = sum(1 for r in runs if r.error)

        # 평균 응답 시간
        durations = [
            (r.end_time - r.start_time).total_seconds()
            for r in runs if r.end_time and r.start_time
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # 노드별 통계
        node_stats = {}
        for run in runs:
            node_name = run.name or "unknown"
            if node_name not in node_stats:
                node_stats[node_name] = {"count": 0, "errors": 0, "total_time": 0}

            node_stats[node_name]["count"] += 1
            if run.error:
                node_stats[node_name]["errors"] += 1
            if run.end_time and run.start_time:
                node_stats[node_name]["total_time"] += (run.end_time - run.start_time).total_seconds()

        # 평균 시간 계산
        for node in node_stats:
            count = node_stats[node]["count"]
            if count > 0:
                node_stats[node]["avg_time"] = node_stats[node]["total_time"] / count

        report = {
            "period": f"최근 {days}일",
            "total_runs": total_runs,
            "error_runs": error_runs,
            "error_rate": f"{(error_runs/total_runs)*100:.2f}%" if total_runs > 0 else "N/A",
            "avg_response_time": f"{avg_duration:.2f}초",
            "node_stats": node_stats,
            "generated_at": datetime.now().isoformat(),
        }

        return report


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="LangSmith Evaluation for CodeFill")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # setup 명령어
    setup_parser = subparsers.add_parser("setup", help="데이터셋 초기화")

    # run 명령어
    run_parser = subparsers.add_parser("run", help="평가 실행")
    run_parser.add_argument(
        "--dataset",
        choices=list(DATASETS.keys()),
        required=True,
        help="평가할 데이터셋"
    )
    run_parser.add_argument(
        "--target",
        choices=["chat_agent", "solving_assist", "intent"],
        default="solving_assist",
        help="평가 대상"
    )

    # report 명령어
    report_parser = subparsers.add_parser("report", help="리포트 생성")
    report_parser.add_argument("--days", type=int, default=7, help="조회 기간 (일)")

    args = parser.parse_args()

    if args.command == "setup":
        manager = DatasetManager()
        manager.setup_all_datasets()

    elif args.command == "run":
        runner = EvalRunner()
        dataset_name = DATASETS[args.dataset]

        print(f"\n🚀 평가 시작: {dataset_name}")
        print(f"   타겟: {args.target}")
        print("-" * 50)

        results = runner.run_evaluation(
            dataset_name=dataset_name,
            target=args.target,
        )

        print("\n✅ 평가 완료!")
        print(f"   결과 확인: https://smith.langchain.com/")

    elif args.command == "report":
        runner = EvalRunner()
        report = runner.generate_report(days=args.days)

        print("\n📊 평가 리포트")
        print("=" * 50)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
