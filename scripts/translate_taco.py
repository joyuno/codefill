import json
import time
import os
from groq import Groq
from dotenv import load_dotenv

# .env.local에서 환경변수 로드
load_dotenv('.env.local')

# Groq API 설정
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def translate_to_korean(text, max_retries=3):
    """영어 텍스트를 한국어로 번역"""
    if not text or len(text.strip()) == 0:
        return text

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Groq 무료 모델
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following programming problem description from English to Korean. Keep code snippets, variable names, and mathematical formulas unchanged. Only translate the natural language parts. Output only the translation without any explanation."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate_limit" in str(e).lower():
                wait_time = 60 * (attempt + 1)
                print(f"Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error: {e}")
                time.sleep(5)

    return text  # 실패 시 원본 반환

def translate_taco_dataset(input_path, output_path, start_idx=0):
    """TACO 데이터셋 번역"""
    print(f"Loading {input_path}...")
    with open(input_path, "r") as f:
        data = json.load(f)

    total = len(data)
    print(f"Total items: {total}")

    # 체크포인트 로드
    checkpoint_path = output_path + ".checkpoint"
    if os.path.exists(checkpoint_path) and start_idx == 0:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)
            start_idx = checkpoint.get("last_idx", 0) + 1
            data = checkpoint.get("data", data)
            print(f"Resuming from index {start_idx}")

    for i in range(start_idx, total):
        item = data[i]
        question = item.get("question", "")

        if question and len(question) > 0:
            print(f"[{i+1}/{total}] Translating...")
            translated = translate_to_korean(question)
            item["question_ko"] = translated
            item["question_en"] = question  # 원본 보존

            # 주기적 저장 (10개마다)
            if (i + 1) % 10 == 0:
                with open(checkpoint_path, "w") as f:
                    json.dump({"last_idx": i, "data": data}, f)
                print(f"Checkpoint saved at {i+1}")

            # Rate limit 방지 (분당 30 요청 제한)
            time.sleep(2.5)

        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")

    # 최종 저장
    print(f"Saving to {output_path}...")
    with open(output_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 체크포인트 삭제
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    print("Done!")

if __name__ == "__main__":
    import sys

    # 기본: train.json 번역
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/taco/train.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/taco/train_ko.json"

    translate_taco_dataset(input_file, output_file)
