# 배치 락 관리자 - 배치 간 충돌 방지

import os
import json
import time
import fcntl
from datetime import datetime
from config import LOCK_DIR, CHECKPOINT_FILE, MAIN_FILE, BATCH_SIZE

class LockManager:
    """파일 기반 락으로 배치 간 충돌 방지"""

    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.lock_file = os.path.join(LOCK_DIR, f"worker_{worker_id}.lock")

    def get_next_batch(self) -> tuple[int, int] | None:
        """
        다음 처리할 배치의 시작/끝 인덱스 반환
        다른 워커가 처리 중인 배치는 건너뜀
        """
        checkpoint_lock = os.path.join(LOCK_DIR, "checkpoint.lock")

        with open(checkpoint_lock, 'w') as f:
            # 파일 락 획득
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)

            try:
                checkpoint = self._load_checkpoint()
                total_problems = checkpoint.get("total_problems", 0)

                if total_problems == 0:
                    # 첫 실행 시 전체 문제 수 로드
                    with open(MAIN_FILE, 'r') as mf:
                        data = json.load(mf)
                        total_problems = len(data)
                    checkpoint["total_problems"] = total_problems

                # 비어있는 솔루션 인덱스 찾기
                empty_indices = checkpoint.get("empty_indices", None)

                if empty_indices is None:
                    # 첫 실행 시 빈 솔루션 인덱스 수집
                    empty_indices = self._find_empty_indices()
                    checkpoint["empty_indices"] = empty_indices

                # 처리 완료된 인덱스 제외
                completed = set(checkpoint.get("completed_indices", []))
                in_progress = self._get_in_progress_indices()

                # 처리할 인덱스 찾기
                available = [i for i in empty_indices if i not in completed and i not in in_progress]

                if not available:
                    if in_progress:
                        # 진행 중인 작업이 있으면 대기
                        return None
                    else:
                        # 모든 작업 완료
                        return (-1, -1)

                # 배치 할당
                batch_indices = available[:BATCH_SIZE]
                start_idx = batch_indices[0]
                end_idx = batch_indices[-1]

                # 이 워커가 처리 중임을 기록
                self._mark_in_progress(batch_indices)

                self._save_checkpoint(checkpoint)

                return (start_idx, end_idx, batch_indices)

            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _find_empty_indices(self) -> list[int]:
        """빈 솔루션을 가진 문제의 인덱스 목록 반환"""
        with open(MAIN_FILE, 'r') as f:
            data = json.load(f)

        empty_indices = []
        for i, problem in enumerate(data):
            solutions = problem.get('solutions', [])
            if not solutions:
                empty_indices.append(i)
            else:
                # 솔루션이 있어도 placeholder인지 확인
                has_real_code = False
                for sol in solutions:
                    code = sol.get('code', '')
                    # 주석만 있거나 너무 짧은 코드는 placeholder로 간주
                    if code and len(code.strip()) > 50:
                        has_real_code = True
                        break
                if not has_real_code:
                    empty_indices.append(i)

        return empty_indices

    def _get_in_progress_indices(self) -> set[int]:
        """현재 처리 중인 모든 인덱스 반환"""
        in_progress = set()

        for filename in os.listdir(LOCK_DIR):
            if filename.startswith("worker_") and filename.endswith(".lock"):
                lock_path = os.path.join(LOCK_DIR, filename)
                try:
                    with open(lock_path, 'r') as f:
                        data = json.load(f)
                        # 5분 이상 된 락은 무시 (타임아웃)
                        if time.time() - data.get("timestamp", 0) < 300:
                            in_progress.update(data.get("indices", []))
                except (json.JSONDecodeError, FileNotFoundError):
                    pass

        return in_progress

    def _mark_in_progress(self, indices: list[int]):
        """이 워커가 처리 중인 인덱스 기록"""
        with open(self.lock_file, 'w') as f:
            json.dump({
                "worker_id": self.worker_id,
                "indices": indices,
                "timestamp": time.time(),
                "started_at": datetime.now().isoformat()
            }, f)

    def mark_completed(self, indices: list[int]):
        """처리 완료된 인덱스 기록"""
        checkpoint_lock = os.path.join(LOCK_DIR, "checkpoint.lock")

        with open(checkpoint_lock, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)

            try:
                checkpoint = self._load_checkpoint()
                completed = set(checkpoint.get("completed_indices", []))
                completed.update(indices)
                checkpoint["completed_indices"] = list(completed)
                checkpoint["last_updated"] = datetime.now().isoformat()
                self._save_checkpoint(checkpoint)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # 워커 락 파일 삭제
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)

    def _load_checkpoint(self) -> dict:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save_checkpoint(self, checkpoint: dict):
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def get_status(self) -> dict:
        """현재 진행 상황 반환"""
        checkpoint = self._load_checkpoint()
        empty_indices = checkpoint.get("empty_indices", [])
        completed = checkpoint.get("completed_indices", [])
        in_progress = self._get_in_progress_indices()

        return {
            "total_empty": len(empty_indices),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "remaining": len(empty_indices) - len(completed) - len(in_progress)
        }
