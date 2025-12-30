# Claude Code 무한 재귀 솔루션 생성 시스템

## 개요
이 시스템은 Claude Code가 API 없이 직접 백준 문제 솔루션을 생성하는 무한 재귀 배치 시스템입니다.

## 사용 방법

### 1. 상태 확인
```bash
cd /Users/admin/Downloads/codefill/scripts/batch_solution_system
python3 batch_processor.py status
```

### 2. 다음 배치 가져오기 & 솔루션 생성
아래 명령어를 Claude Code에서 실행 후, 출력된 문제들의 솔루션을 직접 생성합니다:

```bash
python3 batch_processor.py next
```

### 3. Claude Code에게 요청할 프롬프트

다음 배치를 가져온 후, Claude Code에게 이렇게 요청하세요:

```
/Users/admin/Downloads/codefill/scripts/batch_solution_system/batches/pending_<worker_id>.json 파일을 읽고,
각 문제에 대해 Python, Java, C++ 솔루션을 생성해서
batch_<worker_id>.json 파일로 저장한 후
메인 파일에 병합해줘
```

### 4. 무한 재귀 실행

Claude Code에게 계속 반복 요청:
```
솔루션 생성 배치 작업을 계속 진행해줘. 남은 문제가 없을 때까지 반복.
```

## 파일 구조

```
batch_solution_system/
├── config.py           # 설정
├── lock_manager.py     # 배치 간 충돌 방지
├── solution_generator.py # 솔루션 생성 유틸
├── batch_processor.py  # 배치 처리
├── merge_results.py    # 결과 병합
├── checkpoint.json     # 진행 상황 저장
├── locks/              # 워커 락 파일
└── batches/            # 배치 결과 파일
    └── merged/         # 병합 완료된 배치
```

## 충돌 방지 메커니즘

1. **파일 락**: fcntl을 사용한 파일 레벨 락
2. **체크포인트**: 완료된 인덱스 추적
3. **워커 락**: 각 워커가 처리 중인 인덱스 기록
4. **타임아웃**: 5분 이상 된 락은 자동 무시

## 배치 크기 조정

`config.py`에서 `BATCH_SIZE` 수정 (기본값: 10)
