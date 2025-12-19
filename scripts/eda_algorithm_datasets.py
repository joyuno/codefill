#!/usr/bin/env python3
"""
알고리즘 데이터셋 EDA (Exploratory Data Analysis)

두 데이터셋을 비교 분석합니다:
1. TACO 데이터셋 (data/taco/test.json)
2. 백준 데이터셋 (data/1_algorithm/baekjoon_with_answer.json)

실행 방법:
    python scripts/eda_algorithm_datasets.py
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# 한글 폰트 설정 (macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


# =============================================================================
# 1. 데이터 로드
# =============================================================================

def load_data():
    """데이터 파일을 로드합니다."""
    BASE_DIR = Path(__file__).parent.parent / 'data'
    
    # TACO 데이터 로드
    taco_path = BASE_DIR / 'taco' / 'test.json'
    with open(taco_path, 'r', encoding='utf-8') as f:
        taco_data = json.load(f)
    
    # 백준 데이터 로드
    baekjoon_path = BASE_DIR / '1_algorithm' / 'baekjoon_with_answer.json'
    with open(baekjoon_path, 'r', encoding='utf-8') as f:
        baekjoon_data = json.load(f)
    
    print(f"✓ TACO 데이터: {len(taco_data)}개 샘플 로드")
    print(f"✓ 백준 데이터: {len(baekjoon_data)}개 샘플 로드")
    
    return taco_data, baekjoon_data


# =============================================================================
# 2. 데이터프레임 생성
# =============================================================================

def create_dataframes(taco_data, baekjoon_data):
    """JSON 데이터를 데이터프레임으로 변환합니다."""
    
    # TACO 데이터프레임
    df_taco = pd.DataFrame(taco_data)
    
    # 백준 데이터프레임 (중첩 구조 평탄화)
    baekjoon_flat = []
    for item in baekjoon_data:
        flat_item = {
            'id': item.get('id'),
            'type': item.get('type'),
            'source': item.get('source'),
            'difficulty': item.get('difficulty'),
            'algorithm_category': item.get('algorithm_category'),
            'company': item.get('company'),
            'language': item.get('language'),
            'question_title': item.get('question', {}).get('title'),
            'question_description': item.get('question', {}).get('description'),
            'question_input_format': item.get('question', {}).get('input_format'),
            'question_output_format': item.get('question', {}).get('output_format'),
            'question_examples': item.get('question', {}).get('examples'),
            'question_external_link': item.get('question', {}).get('external_link'),
            'answer_code': item.get('answer', {}).get('code'),
            'answer_explanation': item.get('answer', {}).get('explanation'),
            'is_ai_generated': item.get('answer', {}).get('is_ai_generated'),
            'tags': item.get('tags'),
            'original_id': item.get('original_id'),
        }
        baekjoon_flat.append(flat_item)
    
    df_baekjoon = pd.DataFrame(baekjoon_flat)
    
    return df_taco, df_baekjoon


# =============================================================================
# 3. TACO 데이터 EDA
# =============================================================================

def eda_taco(df_taco):
    """TACO 데이터셋 EDA를 수행합니다."""
    print("\n" + "=" * 60)
    print("📊 TACO 데이터셋 EDA")
    print("=" * 60)
    
    # 기본 정보
    print(f"\n[기본 정보]")
    print(f"  - Shape: {df_taco.shape}")
    print(f"  - Columns: {df_taco.columns.tolist()}")
    
    # 샘플 데이터
    print(f"\n[첫 번째 샘플 (일부)]")
    sample = df_taco.iloc[0]
    for col in ['name', 'difficulty', 'source']:
        if col in df_taco.columns:
            print(f"  - {col}: {sample[col]}")
    
    # 난이도 분포
    print(f"\n[난이도 분포]")
    diff_counts = df_taco['difficulty'].value_counts()
    for diff, count in diff_counts.items():
        pct = count / len(df_taco) * 100
        print(f"  - {diff}: {count}개 ({pct:.1f}%)")
    
    # 출처 분포
    print(f"\n[출처(source) 분포]")
    source_counts = df_taco['source'].value_counts()
    for source, count in source_counts.items():
        pct = count / len(df_taco) * 100
        print(f"  - {source}: {count}개 ({pct:.1f}%)")
    
    # 문제 길이 분석
    df_taco['question_length'] = df_taco['question'].apply(lambda x: len(str(x)) if x else 0)
    print(f"\n[문제 길이 통계]")
    print(f"  - 평균: {df_taco['question_length'].mean():.0f}자")
    print(f"  - 중앙값: {df_taco['question_length'].median():.0f}자")
    print(f"  - 최소: {df_taco['question_length'].min()}자")
    print(f"  - 최대: {df_taco['question_length'].max()}자")
    
    # 솔루션 수 분석
    df_taco['solution_count'] = df_taco['solutions'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    print(f"\n[솔루션 수 통계]")
    print(f"  - 평균: {df_taco['solution_count'].mean():.1f}개")
    print(f"  - 최소: {df_taco['solution_count'].min()}개")
    print(f"  - 최대: {df_taco['solution_count'].max()}개")
    
    # 태그 분석
    all_tags = []
    for tags in df_taco['tags']:
        if isinstance(tags, list):
            all_tags.extend(tags)
    
    tag_counts = pd.Series(all_tags).value_counts()
    print(f"\n[상위 10개 태그]")
    for tag, count in tag_counts.head(10).items():
        print(f"  - {tag}: {count}개")
    
    return df_taco


# =============================================================================
# 4. 백준 데이터 EDA
# =============================================================================

def eda_baekjoon(df_baekjoon):
    """백준 데이터셋 EDA를 수행합니다."""
    print("\n" + "=" * 60)
    print("📊 백준 데이터셋 EDA")
    print("=" * 60)
    
    # 기본 정보
    print(f"\n[기본 정보]")
    print(f"  - Shape: {df_baekjoon.shape}")
    print(f"  - Columns: {df_baekjoon.columns.tolist()}")
    
    # 샘플 데이터
    print(f"\n[첫 번째 샘플 (일부)]")
    sample = df_baekjoon.iloc[0]
    for col in ['question_title', 'difficulty', 'language', 'algorithm_category']:
        if col in df_baekjoon.columns:
            print(f"  - {col}: {sample[col]}")
    
    # 난이도 분포
    print(f"\n[난이도 분포]")
    diff_counts = df_baekjoon['difficulty'].value_counts()
    for diff, count in diff_counts.items():
        pct = count / len(df_baekjoon) * 100
        print(f"  - {diff}: {count}개 ({pct:.1f}%)")
    
    # 알고리즘 카테고리 분포
    print(f"\n[알고리즘 카테고리 분포]")
    cat_counts = df_baekjoon['algorithm_category'].value_counts()
    for cat, count in cat_counts.head(15).items():
        pct = count / len(df_baekjoon) * 100
        print(f"  - {cat}: {count}개 ({pct:.1f}%)")
    
    # 언어 분포
    print(f"\n[프로그래밍 언어 분포]")
    lang_counts = df_baekjoon['language'].value_counts()
    for lang, count in lang_counts.items():
        pct = count / len(df_baekjoon) * 100
        print(f"  - {lang}: {count}개 ({pct:.1f}%)")
    
    # 문제 설명 길이 분석
    df_baekjoon['description_length'] = df_baekjoon['question_description'].apply(
        lambda x: len(str(x)) if x else 0
    )
    print(f"\n[문제 설명 길이 통계]")
    print(f"  - 평균: {df_baekjoon['description_length'].mean():.0f}자")
    print(f"  - 중앙값: {df_baekjoon['description_length'].median():.0f}자")
    print(f"  - 최소: {df_baekjoon['description_length'].min()}자")
    print(f"  - 최대: {df_baekjoon['description_length'].max()}자")
    
    # 코드 길이 분석
    df_baekjoon['code_length'] = df_baekjoon['answer_code'].apply(
        lambda x: len(str(x)) if x else 0
    )
    print(f"\n[정답 코드 길이 통계]")
    print(f"  - 평균: {df_baekjoon['code_length'].mean():.0f}자")
    print(f"  - 중앙값: {df_baekjoon['code_length'].median():.0f}자")
    print(f"  - 최소: {df_baekjoon['code_length'].min()}자")
    print(f"  - 최대: {df_baekjoon['code_length'].max()}자")
    
    # 언어별 코드 길이
    print(f"\n[언어별 평균 코드 길이]")
    lang_code_len = df_baekjoon.groupby('language')['code_length'].mean().sort_values(ascending=False)
    for lang, avg_len in lang_code_len.items():
        print(f"  - {lang}: {avg_len:.0f}자")
    
    # 태그 분석
    all_tags = []
    for tags in df_baekjoon['tags']:
        if isinstance(tags, list):
            all_tags.extend(tags)
    
    tag_counts = pd.Series(all_tags).value_counts()
    print(f"\n[상위 15개 태그]")
    for tag, count in tag_counts.head(15).items():
        print(f"  - {tag}: {count}개")
    
    return df_baekjoon


# =============================================================================
# 5. 두 데이터셋 비교
# =============================================================================

def compare_datasets(df_taco, df_baekjoon):
    """두 데이터셋을 비교합니다."""
    print("\n" + "=" * 60)
    print("📊 두 데이터셋 비교")
    print("=" * 60)
    
    # 기본 정보 비교
    print(f"\n[기본 정보 비교]")
    print(f"{'항목':<20} {'TACO':<15} {'백준':<15}")
    print("-" * 50)
    print(f"{'샘플 수':<20} {len(df_taco):<15} {len(df_baekjoon):<15}")
    print(f"{'컬럼 수':<20} {len(df_taco.columns):<15} {len(df_baekjoon.columns):<15}")
    print(f"{'난이도 종류':<20} {df_taco['difficulty'].nunique():<15} {df_baekjoon['difficulty'].nunique():<15}")
    
    avg_q_len_taco = df_taco['question_length'].mean() if 'question_length' in df_taco.columns else 0
    avg_q_len_baek = df_baekjoon['description_length'].mean() if 'description_length' in df_baekjoon.columns else 0
    print(f"{'평균 문제 길이':<20} {avg_q_len_taco:.0f}자{'':<10} {avg_q_len_baek:.0f}자")
    
    # 필드 구조 비교
    print(f"\n[TACO 필드 목록]")
    for col in df_taco.columns[:10]:  # 처음 10개만
        print(f"  - {col}")
    if len(df_taco.columns) > 10:
        print(f"  ... 외 {len(df_taco.columns) - 10}개")
    
    print(f"\n[백준 필드 목록]")
    for col in df_baekjoon.columns:
        print(f"  - {col}")
    
    # 결측치 비교
    print(f"\n[결측치 비교]")
    print(f"\nTACO 결측치:")
    taco_nulls = df_taco.isnull().sum()
    for col, null_count in taco_nulls[taco_nulls > 0].items():
        print(f"  - {col}: {null_count}개")
    
    print(f"\n백준 결측치:")
    baek_nulls = df_baekjoon.isnull().sum()
    for col, null_count in baek_nulls[baek_nulls > 0].items():
        print(f"  - {col}: {null_count}개")


# =============================================================================
# 6. 시각화 (선택적)
# =============================================================================

def create_visualizations(df_taco, df_baekjoon, save_plots=True):
    """시각화를 생성합니다."""
    print("\n" + "=" * 60)
    print("📊 시각화 생성 중...")
    print("=" * 60)
    
    # 출력 디렉토리
    output_dir = Path(__file__).parent.parent / 'outputs' / 'eda_plots'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 난이도 분포 비교
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    df_taco['difficulty'].value_counts().plot(kind='bar', ax=axes[0], color='steelblue')
    axes[0].set_title('TACO 난이도 분포')
    axes[0].set_xlabel('난이도')
    axes[0].set_ylabel('문제 수')
    axes[0].tick_params(axis='x', rotation=45)
    
    df_baekjoon['difficulty'].value_counts().plot(kind='bar', ax=axes[1], color='coral')
    axes[1].set_title('백준 난이도 분포')
    axes[1].set_xlabel('난이도')
    axes[1].set_ylabel('문제 수')
    axes[1].tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    if save_plots:
        plt.savefig(output_dir / 'difficulty_comparison.png', dpi=150)
        print(f"  ✓ 저장: difficulty_comparison.png")
    plt.close()
    
    # 2. TACO 출처 분포
    fig, ax = plt.subplots(figsize=(12, 5))
    df_taco['source'].value_counts().plot(kind='bar', ax=ax, color='teal')
    ax.set_title('TACO 출처 분포')
    ax.set_xlabel('출처')
    ax.set_ylabel('문제 수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_plots:
        plt.savefig(output_dir / 'taco_source_distribution.png', dpi=150)
        print(f"  ✓ 저장: taco_source_distribution.png")
    plt.close()
    
    # 3. 백준 알고리즘 카테고리 분포
    fig, ax = plt.subplots(figsize=(12, 6))
    df_baekjoon['algorithm_category'].value_counts().plot(kind='barh', ax=ax, color='purple')
    ax.set_title('백준 알고리즘 카테고리 분포')
    ax.set_xlabel('문제 수')
    plt.tight_layout()
    if save_plots:
        plt.savefig(output_dir / 'baekjoon_algorithm_category.png', dpi=150)
        print(f"  ✓ 저장: baekjoon_algorithm_category.png")
    plt.close()
    
    # 4. 백준 언어 분포 (파이 차트)
    fig, ax = plt.subplots(figsize=(8, 8))
    df_baekjoon['language'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_title('백준 프로그래밍 언어 분포')
    ax.set_ylabel('')
    plt.tight_layout()
    if save_plots:
        plt.savefig(output_dir / 'baekjoon_language_distribution.png', dpi=150)
        print(f"  ✓ 저장: baekjoon_language_distribution.png")
    plt.close()
    
    # 5. 문제 길이 분포
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    if 'question_length' in df_taco.columns:
        df_taco['question_length'].hist(bins=50, ax=axes[0], color='green', alpha=0.7)
        axes[0].set_title('TACO 문제 길이 분포')
        axes[0].set_xlabel('문자 수')
        axes[0].set_ylabel('빈도')
    
    if 'description_length' in df_baekjoon.columns:
        df_baekjoon['description_length'].hist(bins=50, ax=axes[1], color='orange', alpha=0.7)
        axes[1].set_title('백준 문제 설명 길이 분포')
        axes[1].set_xlabel('문자 수')
        axes[1].set_ylabel('빈도')
    
    plt.tight_layout()
    if save_plots:
        plt.savefig(output_dir / 'question_length_distribution.png', dpi=150)
        print(f"  ✓ 저장: question_length_distribution.png")
    plt.close()
    
    print(f"\n  📁 시각화 저장 위치: {output_dir}/")


# =============================================================================
# 7. 요약 출력
# =============================================================================

def print_summary(df_taco, df_baekjoon):
    """EDA 요약을 출력합니다."""
    print("\n" + "=" * 60)
    print("📊 EDA 요약")
    print("=" * 60)
    
    sol_count_mean = df_taco['solution_count'].mean() if 'solution_count' in df_taco.columns else 0
    q_len_taco = df_taco['question_length'].mean() if 'question_length' in df_taco.columns else 0
    desc_len = df_baekjoon['description_length'].mean() if 'description_length' in df_baekjoon.columns else 0
    code_len = df_baekjoon['code_length'].mean() if 'code_length' in df_baekjoon.columns else 0
    
    print(f"""
📊 TACO 데이터셋:
   - 총 {len(df_taco)}개 문제
   - {df_taco['difficulty'].nunique()}가지 난이도
   - {df_taco['source'].nunique()}개 출처
   - 평균 문제 길이: {q_len_taco:.0f}자
   - 평균 솔루션 수: {sol_count_mean:.1f}개

📊 백준 데이터셋:
   - 총 {len(df_baekjoon)}개 문제
   - {df_baekjoon['difficulty'].nunique()}가지 난이도
   - {df_baekjoon['algorithm_category'].nunique()}개 알고리즘 카테고리
   - {df_baekjoon['language'].nunique()}개 언어
   - 평균 문제 길이: {desc_len:.0f}자
   - 평균 코드 길이: {code_len:.0f}자
""")
    
    print("EDA 완료! 🎉")


# =============================================================================
# 메인 함수
# =============================================================================

def main():
    """메인 함수"""
    print("=" * 60)
    print("알고리즘 데이터셋 EDA")
    print("=" * 60)
    
    # 1. 데이터 로드
    print("\n[1/6] 데이터 로드 중...")
    taco_data, baekjoon_data = load_data()
    
    # 2. 데이터프레임 생성
    print("\n[2/6] 데이터프레임 생성 중...")
    df_taco, df_baekjoon = create_dataframes(taco_data, baekjoon_data)
    print(f"  ✓ TACO DataFrame: {df_taco.shape}")
    print(f"  ✓ 백준 DataFrame: {df_baekjoon.shape}")
    
    # 3. TACO EDA
    print("\n[3/6] TACO EDA 수행 중...")
    df_taco = eda_taco(df_taco)
    
    # 4. 백준 EDA
    print("\n[4/6] 백준 EDA 수행 중...")
    df_baekjoon = eda_baekjoon(df_baekjoon)
    
    # 5. 비교 분석
    print("\n[5/6] 비교 분석 중...")
    compare_datasets(df_taco, df_baekjoon)
    
    # 6. 시각화 생성
    print("\n[6/6] 시각화 생성 중...")
    try:
        create_visualizations(df_taco, df_baekjoon, save_plots=True)
    except Exception as e:
        print(f"  ⚠️ 시각화 생성 중 오류: {e}")
        print("  (matplotlib 한글 폰트 설정이 필요할 수 있습니다)")
    
    # 요약 출력
    print_summary(df_taco, df_baekjoon)


if __name__ == "__main__":
    main()

