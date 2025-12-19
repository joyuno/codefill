#!/usr/bin/env python3
"""
Algorithm Dataset to TACO Format Converter

1_algorithm 폴더의 JSON 파일들을 TACO 데이터셋 형식으로 변환합니다.

TACO 필드 구조:
- question: 문제 설명 (전체 텍스트)
- solutions: 정답 코드 배열
- starter_code: 시작 코드 템플릿
- input_output: 테스트 케이스 {inputs: [], outputs: []}
- difficulty: EASY, MEDIUM, HARD, VERY_HARD, MEDIUM_HARD
- raw_tags: 원본 태그
- name: 문제 이름
- source: 출처 플랫폼
- tags: 알고리즘 태그
- skill_types: 필요 기술 유형
- url: 원본 문제 URL
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# 경로 설정
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'data' / '1_algorithm'
OUTPUT_DIR = BASE_DIR / 'data' / '1_algorithm_taco'


# 난이도 매핑 (소문자 → TACO 대문자 형식)
DIFFICULTY_MAP = {
    'easy': 'EASY',
    'medium': 'MEDIUM',
    'hard': 'HARD',
    'very_hard': 'VERY_HARD',
    'medium_hard': 'MEDIUM_HARD',
    None: 'UNKNOWN_DIFFICULTY',
    '': 'UNKNOWN_DIFFICULTY'
}


def build_question_text(question_obj: Dict) -> str:
    """
    question 객체의 여러 필드를 하나의 문자열로 결합합니다.
    
    TACO 형식에서는 문제 설명, 입력 형식, 출력 형식이 모두 하나의 
    'question' 필드에 포함됩니다.
    """
    parts = []
    
    # 문제 설명
    if question_obj.get('description'):
        parts.append(question_obj['description'])
    
    # 입력 형식
    if question_obj.get('input_format'):
        parts.append(f"\n\n**입력**\n{question_obj['input_format']}")
    
    # 출력 형식
    if question_obj.get('output_format'):
        parts.append(f"\n\n**출력**\n{question_obj['output_format']}")
    
    # 제약 조건
    if question_obj.get('constraints'):
        parts.append(f"\n\n**제약 조건**\n{question_obj['constraints']}")
    
    return ''.join(parts) if parts else ''


def convert_examples_to_input_output(examples: List[Dict]) -> Dict:
    """
    examples 배열을 TACO의 input_output 형식으로 변환합니다.
    
    기존 형식:
    [{"input": "10 1 3 1\\n7\\n...", "output": "4"}, ...]
    
    TACO 형식:
    {"inputs": ["10 1 3 1\\n7\\n..."], "outputs": ["4"]}
    """
    if not examples:
        return {"inputs": [], "outputs": []}
    
    inputs = []
    outputs = []
    
    for example in examples:
        if example.get('input') is not None:
            inputs.append(example['input'])
        if example.get('output') is not None:
            outputs.append(example['output'])
    
    return {"inputs": inputs, "outputs": outputs}


def map_difficulty(difficulty: Optional[str]) -> str:
    """난이도를 TACO 형식으로 매핑합니다."""
    if difficulty is None:
        return 'UNKNOWN_DIFFICULTY'
    
    # 이미 대문자인 경우 그대로 반환
    if difficulty.upper() in ['EASY', 'MEDIUM', 'HARD', 'VERY_HARD', 'MEDIUM_HARD']:
        return difficulty.upper()
    
    return DIFFICULTY_MAP.get(difficulty.lower(), 'UNKNOWN_DIFFICULTY')


def build_tags_and_skills(item: Dict) -> tuple:
    """
    algorithm_category와 tags를 결합하여 TACO의 tags와 skill_types를 생성합니다.
    """
    tags = []
    skill_types = []
    
    # algorithm_category를 skill_types에 추가
    if item.get('algorithm_category'):
        skill_types.append(item['algorithm_category'])
    
    # 기존 tags 추가
    if item.get('tags'):
        tags.extend(item['tags'])
    
    # source를 tags에 추가
    if item.get('source'):
        tags.append(item['source'])
    
    # company가 있으면 tags에 추가
    if item.get('company'):
        tags.append(item['company'])
    
    return tags, skill_types


def convert_item_to_taco(item: Dict) -> Dict:
    """
    단일 알고리즘 문제를 TACO 형식으로 변환합니다.
    
    포함 필드: id, question, solutions, starter_code, input_output, 
              difficulty, raw_tags, source, _language
    """
    question_obj = item.get('question', {})
    answer_obj = item.get('answer', {})
    
    # 간소화된 TACO 형식 데이터 구성
    taco_item = {
        'id': item.get('id', ''),
        'question': build_question_text(question_obj),
        'solutions': [answer_obj.get('code', '')] if answer_obj.get('code') else [],
        'starter_code': '',
        'input_output': convert_examples_to_input_output(question_obj.get('examples', [])),
        'difficulty': map_difficulty(item.get('difficulty')),
        'raw_tags': item.get('tags', []),
        'source': item.get('source', ''),
        '_language': item.get('language')
    }
    
    return taco_item


def process_json_file(file_path: Path) -> List[Dict]:
    """
    JSON 파일을 읽어서 TACO 형식으로 변환합니다.
    """
    print(f"  - 처리 중: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    converted = []
    for item in data:
        taco_item = convert_item_to_taco(item)
        converted.append(taco_item)
    
    print(f"    ✓ {len(converted)}개 문제 변환 완료")
    return converted


def save_json(data: List[Dict], output_path: Path):
    """JSON 파일로 저장합니다."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    file_size = output_path.stat().st_size / 1024  # KB
    print(f"    ✓ 저장됨: {output_path.name} ({file_size:.1f} KB)")


def generate_stats(all_data: List[Dict], source_counts: Dict) -> Dict:
    """변환된 데이터의 통계를 생성합니다."""
    difficulty_dist = {}
    language_dist = {}
    tag_dist = {}
    
    for item in all_data:
        # 난이도 분포
        diff = item.get('difficulty', 'UNKNOWN_DIFFICULTY')
        difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        # 언어 분포
        lang = item.get('_language', 'unknown')
        language_dist[lang] = language_dist.get(lang, 0) + 1
        
        # 태그 분포
        for tag in item.get('raw_tags', []):
            tag_dist[tag] = tag_dist.get(tag, 0) + 1
    
    return {
        'total_problems': len(all_data),
        'source_distribution': source_counts,
        'difficulty_distribution': difficulty_dist,
        'language_distribution': language_dist,
        'tag_distribution': dict(sorted(tag_dist.items(), key=lambda x: -x[1])[:20]),  # 상위 20개
        'format': 'TACO-simplified',
        'fields': ['id', 'question', 'solutions', 'starter_code', 'input_output', 'difficulty', 'raw_tags', 'source', '_language'],
        'converted_from': '1_algorithm'
    }


def main():
    """메인 변환 함수"""
    print("=" * 60)
    print("Algorithm to TACO Format Converter")
    print("=" * 60)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n출력 디렉토리: {OUTPUT_DIR}")
    
    # 입력 파일 목록
    json_files = list(INPUT_DIR.glob('*.json'))
    print(f"\n[1/3] 입력 파일 검색: {len(json_files)}개 발견")
    
    if not json_files:
        print("  ❌ JSON 파일을 찾을 수 없습니다.")
        return
    
    # 각 파일 처리
    print("\n[2/3] 파일 변환 중...")
    all_converted = []
    source_counts = {}
    
    for json_file in json_files:
        converted = process_json_file(json_file)
        all_converted.extend(converted)
        
        # 소스별 카운트
        source_name = json_file.stem  # 파일명에서 확장자 제거
        source_counts[source_name] = len(converted)
        
        # 개별 파일 저장
        output_file = OUTPUT_DIR / f"{json_file.stem}_taco.json"
        save_json(converted, output_file)
    
    # 전체 데이터 병합 저장
    print("\n[3/3] 결과 저장 중...")
    
    # 전체 데이터
    all_output = OUTPUT_DIR / 'all_algorithms_taco.json'
    save_json(all_converted, all_output)
    
    # 난이도별 분류
    difficulty_dir = OUTPUT_DIR / 'by_difficulty'
    difficulty_dir.mkdir(exist_ok=True)
    
    by_difficulty = {}
    for item in all_converted:
        diff = item.get('difficulty', 'UNKNOWN_DIFFICULTY')
        if diff not in by_difficulty:
            by_difficulty[diff] = []
        by_difficulty[diff].append(item)
    
    for diff, items in by_difficulty.items():
        diff_file = difficulty_dir / f"{diff.lower()}.json"
        save_json(items, diff_file)
    
    # 통계 저장
    stats = generate_stats(all_converted, source_counts)
    stats_path = OUTPUT_DIR / 'stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"    ✓ 저장됨: stats.json")
    
    # 완료 메시지
    print("\n" + "=" * 60)
    print("변환 완료!")
    print("=" * 60)
    print(f"\n총 {stats['total_problems']}개 문제 변환됨")
    print("\n소스별 분포:")
    for source, count in source_counts.items():
        print(f"  - {source}: {count}개")
    print("\n난이도별 분포:")
    for diff, count in sorted(stats['difficulty_distribution'].items()):
        print(f"  - {diff}: {count}개")
    print(f"\n결과 저장 위치: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

