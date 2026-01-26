"""
Azure Translator Service
- Azure Cognitive Services Translator API를 사용한 번역 서비스
- 지원 언어: 100+ (한국어, 영어, 일본어, 중국어 등)
"""

import httpx
import uuid
from typing import Optional
from ..config import get_settings

settings = get_settings()

# Azure Translator API 설정
TRANSLATOR_ENDPOINT = settings.azure_translator_endpoint
TRANSLATOR_KEY = settings.azure_translator_key
TRANSLATOR_REGION = settings.azure_translator_region

# 지원 언어 목록 (주요 언어)
SUPPORTED_LANGUAGES = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh-Hans": "简体中文",
    "zh-Hant": "繁體中文",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "vi": "Tiếng Việt",
    "th": "ไทย",
    "id": "Bahasa Indonesia",
}


async def translate_text(
    text: str,
    to_language: str,
    from_language: Optional[str] = None,
) -> dict:
    """
    텍스트 번역

    Args:
        text: 번역할 텍스트
        to_language: 대상 언어 코드 (예: 'ko', 'en', 'ja')
        from_language: 원본 언어 코드 (None이면 자동 감지)

    Returns:
        {
            "success": True,
            "translated_text": "번역된 텍스트",
            "detected_language": "en",  # 자동 감지된 경우
            "to_language": "ko"
        }
    """
    if not TRANSLATOR_KEY:
        return {
            "success": False,
            "error": "번역 서비스가 설정되지 않았습니다. 관리자에게 문의하세요.",
        }

    path = "/translate"
    params = {
        "api-version": "3.0",
        "to": to_language,
    }

    if from_language:
        params["from"] = from_language

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TRANSLATOR_ENDPOINT}{path}",
                params=params,
                headers=headers,
                json=body,
                timeout=30.0,
            )

            if response.status_code != 200:
                # 401: 인증 실패 (API 키 만료/유효하지 않음)
                if response.status_code == 401:
                    return {
                        "success": False,
                        "error": "번역 서비스 인증에 실패했습니다. API 키를 확인해주세요.",
                    }
                return {
                    "success": False,
                    "error": f"번역 서비스 오류가 발생했습니다. (코드: {response.status_code})",
                }

            result = response.json()

            if not result or len(result) == 0:
                return {
                    "success": False,
                    "error": "Empty response from translation API",
                }

            translation = result[0]
            translated_text = translation["translations"][0]["text"]
            detected_language = translation.get("detectedLanguage", {}).get("language")

            return {
                "success": True,
                "translated_text": translated_text,
                "detected_language": detected_language,
                "to_language": to_language,
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Translation request timed out",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Translation error: {str(e)}",
        }


async def detect_language(text: str) -> dict:
    """
    텍스트 언어 감지

    Args:
        text: 언어를 감지할 텍스트

    Returns:
        {
            "success": True,
            "language": "en",
            "score": 1.0,
            "language_name": "English"
        }
    """
    if not TRANSLATOR_KEY:
        return {
            "success": False,
            "error": "번역 서비스가 설정되지 않았습니다. 관리자에게 문의하세요.",
        }

    path = "/detect"
    params = {"api-version": "3.0"}

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TRANSLATOR_ENDPOINT}{path}",
                params=params,
                headers=headers,
                json=body,
                timeout=10.0,
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Detection API error: {response.status_code}",
                }

            result = response.json()

            if not result or len(result) == 0:
                return {
                    "success": False,
                    "error": "Empty response from detection API",
                }

            detection = result[0]
            language_code = detection["language"]
            score = detection["score"]
            language_name = SUPPORTED_LANGUAGES.get(language_code, language_code)

            return {
                "success": True,
                "language": language_code,
                "score": score,
                "language_name": language_name,
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Detection error: {str(e)}",
        }


def get_supported_languages() -> dict:
    """지원 언어 목록 반환"""
    return SUPPORTED_LANGUAGES
