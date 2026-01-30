"""
Google Gemini API Service
직접 Gemini API 호출 (OpenRouter 우회)

3개의 API 키 로테이션으로 Rate Limit 방지
"""

import httpx
import json
import logging
import asyncio
import time
from typing import Optional, Dict, Any, List
from ..config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini API 직접 호출 서비스 (키 로테이션 지원)"""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    # 모델 매핑 - gemini-3-flash-preview 사용
    MODELS = {
        "gemini-flash": "gemini-3-flash-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-3-pro": "gemini-3-pro-preview",
    }

    MAX_RETRIES = 2
    REQUEST_DELAY = 0.3  # 요청 간 딜레이 (초)

    def __init__(self):
        self.settings = get_settings()

        # 쉼표로 구분된 API 키들 파싱
        keys_str = self.settings.gemini_api_keys or ""
        self.api_keys: List[str] = [k.strip() for k in keys_str.split(",") if k.strip()]

        if not self.api_keys:
            logger.warning("No Gemini API keys configured")
        else:
            logger.info(f"GeminiService initialized with {len(self.api_keys)} API keys")

        self.current_key_index = 0
        self._last_request_time = 0.0
        self._key_error_counts: Dict[int, int] = {}  # 키별 에러 카운트

    def _get_current_api_key(self) -> str:
        """현재 활성 API 키 반환"""
        if not self.api_keys:
            raise ValueError("No Gemini API keys configured")
        return self.api_keys[self.current_key_index]

    def _rotate_api_key(self, mark_error: bool = False) -> bool:
        """
        다음 API 키로 로테이션

        Args:
            mark_error: 현재 키에 에러 표시

        Returns:
            True if rotation successful, False if all keys exhausted
        """
        if mark_error:
            self._key_error_counts[self.current_key_index] = \
                self._key_error_counts.get(self.current_key_index, 0) + 1

        if len(self.api_keys) <= 1:
            return False

        # 에러가 적은 키로 로테이션
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

        logger.info(f"Gemini API key rotated: {old_index} -> {self.current_key_index}")
        return True

    async def _apply_request_delay(self):
        """요청 간 딜레이 적용"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def _convert_messages_to_gemini_format(self, messages: list) -> Dict[str, Any]:
        """OpenAI 형식 메시지를 Gemini 형식으로 변환"""
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
            else:  # user
                contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })

        result = {"contents": contents}
        if system_instruction:
            result["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        return result

    async def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Gemini API 호출 (OpenAI 호환 인터페이스)

        Args:
            model: 모델 키 (gemini-flash, gemini-3-pro 등)
            messages: OpenAI 형식 메시지 리스트
            temperature: 샘플링 온도
            max_tokens: 최대 토큰
            response_format: JSON 모드 설정

        Returns:
            OpenAI 호환 응답 형식
        """
        if not self.api_keys:
            raise ValueError("No Gemini API keys configured")

        model_id = self.MODELS.get(model, "gemini-2.0-flash")
        logger.info(f"[GeminiService] Using model: {model} -> {model_id}, max_tokens: {max_tokens}")

        # 메시지 변환
        gemini_payload = self._convert_messages_to_gemini_format(messages)

        # 생성 설정
        generation_config = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }

        # JSON 모드
        if response_format and response_format.get("type") == "json_object":
            generation_config["responseMimeType"] = "application/json"

        gemini_payload["generationConfig"] = generation_config

        last_error = None
        keys_tried = 0

        while keys_tried < len(self.api_keys):
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    await self._apply_request_delay()

                    api_key = self._get_current_api_key()
                    url = f"{self.BASE_URL}/models/{model_id}:generateContent?key={api_key}"

                    async with httpx.AsyncClient(timeout=120.0) as client:
                        response = await client.post(
                            url,
                            json=gemini_payload,
                            headers={"Content-Type": "application/json"},
                        )

                        # Rate limit 또는 에러 체크
                        if response.status_code == 429:
                            logger.warning(f"Gemini rate limit hit on key {self.current_key_index}, attempt {attempt + 1}")
                            if attempt >= self.MAX_RETRIES:
                                if self._rotate_api_key(mark_error=True):
                                    keys_tried += 1
                                    break
                                else:
                                    raise Exception("All Gemini API keys exhausted due to rate limits")
                            await asyncio.sleep(min(2 ** attempt, 10))
                            continue

                        if response.status_code == 400:
                            # API 키 문제일 수 있음
                            error_text = response.text
                            logger.error(f"Gemini 400 error: {error_text[:300]}")
                            if "API_KEY" in error_text.upper() or "INVALID" in error_text.upper():
                                if self._rotate_api_key(mark_error=True):
                                    keys_tried += 1
                                    break
                            raise Exception(f"Gemini API error: {error_text[:200]}")

                        if response.status_code != 200:
                            logger.error(f"Gemini error {response.status_code}: {response.text[:300]}")
                            response.raise_for_status()

                        result = response.json()

                        # 디버그 로깅: Gemini 응답 확인
                        candidates = result.get('candidates', [])
                        logger.debug(f"[GeminiService] Raw response candidates: {len(candidates)}")
                        logger.info(f"[GeminiService] Request maxOutputTokens: {max_tokens}")
                        if not candidates:
                            logger.warning(f"[GeminiService] Empty candidates in response: {result}")
                        else:
                            # 응답 잘림 확인
                            finish_reason = candidates[0].get("finishReason", "")
                            usage = result.get("usageMetadata", {})
                            logger.info(f"[GeminiService] finishReason: {finish_reason}, usage: {usage}")
                            if finish_reason == "MAX_TOKENS":
                                logger.warning(f"[GeminiService] Response truncated due to MAX_TOKENS! Requested: {max_tokens}")

                        # OpenAI 호환 형식으로 변환
                        return self._convert_to_openai_format(result, model_id)

                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code in [429, 500, 503]:
                        if self._rotate_api_key(mark_error=True):
                            keys_tried += 1
                            break
                    raise

                except Exception as e:
                    last_error = e
                    logger.error(f"Gemini request failed: {e}")
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(1)
                        continue
                    # 키 로테이션 시도
                    if self._rotate_api_key(mark_error=True):
                        keys_tried += 1
                        break
                    raise

            # 다음 키로 시도
            if keys_tried < len(self.api_keys) - 1:
                if not self._rotate_api_key():
                    break
            else:
                break

        if last_error:
            raise last_error
        raise RuntimeError("Unexpected error in Gemini chat_completion")

    def _convert_to_openai_format(self, gemini_response: Dict, model: str) -> Dict[str, Any]:
        """Gemini 응답을 OpenAI 형식으로 변환"""
        candidates = gemini_response.get("candidates", [])
        if not candidates:
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": ""},
                    "finish_reason": "stop"
                }],
                "usage": {}
            }

        content = ""
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            if "text" in part:
                content += part["text"]

        # 토큰 사용량
        usage_metadata = gemini_response.get("usageMetadata", {})

        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": candidates[0].get("finishReason", "stop").lower()
            }],
            "usage": {
                "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                "total_tokens": usage_metadata.get("totalTokenCount", 0),
            },
            "model": model,
        }

    def get_content(self, response: Dict[str, Any]) -> str:
        """응답에서 콘텐츠 추출"""
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")


# 싱글톤 인스턴스
gemini_service = GeminiService()
