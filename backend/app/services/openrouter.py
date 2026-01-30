"""
OpenRouter Service
LLM API calls via OpenRouter with caching, rate limit handling, and key rotation

Gemini 모델은 GeminiService로 라우팅됨 (직접 Gemini API 사용)
OpenAI GPT 모델은 타임아웃 시 OpenAI 직접 API로 폴백
"""

import httpx
import json
import logging
import asyncio
import hashlib
import time
from typing import Optional, Dict, Any, AsyncGenerator, List
from functools import lru_cache
from ..config import get_settings

logger = logging.getLogger(__name__)

# Gemini 모델 키 목록 (이 모델들은 GeminiService로 라우팅)
GEMINI_MODEL_KEYS = {"gemini-flash", "gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-3-pro"}


class OpenRouterService:
    """Service for calling LLMs via OpenRouter API with rate limit handling."""

    BASE_URL = "https://openrouter.ai/api/v1"
    OPENAI_BASE_URL = "https://api.openai.com/v1"

    # Model IDs (OpenRouter format)
    MODELS = {
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "claude-sonnet": "anthropic/claude-sonnet-4",  # Claude Sonnet 4
        "gemini-flash": "google/gemini-3-flash-preview",
        "gemini-2.5-lite": "google/gemini-2.5-flash-lite-preview-09-2025",
        "gemini-3-pro": "google/gemini-3-pro-preview",
        "deepseek-v3": "deepseek/deepseek-v3.2",
    }

    # OpenRouter model ID -> OpenAI model ID (for fallback)
    OPENAI_FALLBACK_MODELS = {
        "openai/gpt-4o": "gpt-4o",
        "openai/gpt-4o-mini": "gpt-4o-mini",
    }

    # Rate limit handling settings
    MAX_RETRIES = 2  # 최대 재시도 횟수
    REQUEST_DELAY = 0.5  # 요청 간 딜레이 (초)
    CACHE_TTL = 300  # 캐시 유효 시간 (초)
    CACHE_MAX_SIZE = 1000  # 최대 캐시 항목 수

    # Timeout settings
    OPENROUTER_TIMEOUT = 60.0  # OpenRouter 타임아웃 (초)
    OPENAI_FALLBACK_TIMEOUT = 90.0  # OpenAI fallback 타임아웃 (초)

    def __init__(self, purpose: str = "default"):
        """
        Initialize OpenRouter service.

        Args:
            purpose: 용도 구분 (로깅용, 모든 용도에서 동일한 키 사용)
        """
        self.settings = get_settings()
        self.purpose = purpose

        # 단일 API 키 사용
        self.api_keys: List[str] = []
        if self.settings.openrouter_api_key:
            self.api_keys.append(self.settings.openrouter_api_key)

        self.current_key_index = 0
        self._last_request_time = 0.0

        # 간단한 인메모리 캐시 (TTL 지원)
        self._cache: Dict[str, tuple[Any, float]] = {}

        logger.debug(f"OpenRouterService initialized for purpose: {purpose}")

    def _get_current_api_key(self) -> str:
        """현재 활성 API 키 반환."""
        if not self.api_keys:
            raise ValueError("No OpenRouter API keys configured")
        return self.api_keys[self.current_key_index]

    def _rotate_api_key(self) -> bool:
        """
        다음 API 키로 로테이션.

        Returns:
            True if rotation successful, False if all keys exhausted
        """
        if len(self.api_keys) <= 1:
            return False

        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"Rotated to API key index {self.current_key_index}")
        return True

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with current API key."""
        return {
            "Authorization": f"Bearer {self._get_current_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://codefill.app",
            "X-Title": "CodeFill",
        }

    def _get_openai_headers(self) -> Dict[str, str]:
        """Get request headers for OpenAI direct API."""
        return {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

    def _can_fallback_to_openai(self, model_id: str) -> bool:
        """Check if model can fallback to OpenAI direct API."""
        return (
            model_id in self.OPENAI_FALLBACK_MODELS
            and bool(self.settings.openai_api_key)
        )

    async def _call_openai_direct(
        self,
        model_id: str,
        payload: Dict[str, Any],
        cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Call OpenAI API directly as fallback.

        Args:
            model_id: OpenRouter model ID (e.g., "openai/gpt-4o-mini")
            payload: Request payload (will be modified for OpenAI format)
            cache_key: Optional cache key for storing result

        Returns:
            API response dict
        """
        openai_model = self.OPENAI_FALLBACK_MODELS.get(model_id)
        if not openai_model:
            raise ValueError(f"No OpenAI fallback available for model: {model_id}")

        # OpenAI용 payload 수정
        openai_payload = payload.copy()
        openai_payload["model"] = openai_model

        logger.info(f"Falling back to OpenAI direct API for model: {openai_model}")

        async with httpx.AsyncClient(timeout=self.OPENAI_FALLBACK_TIMEOUT) as client:
            response = await client.post(
                f"{self.OPENAI_BASE_URL}/chat/completions",
                headers=self._get_openai_headers(),
                json=openai_payload,
            )

            if response.status_code != 200:
                logger.error(f"OpenAI fallback error: {response.text[:500]}")
            response.raise_for_status()

            result = response.json()

            # LangSmith 토큰 사용량 로깅 (OpenAI direct로 표시)
            usage = result.get("usage", {})
            if usage:
                from .langsmith_tracker import langsmith_tracker
                langsmith_tracker.log_llm_usage(
                    model=f"openai-direct/{openai_model}",
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                )

            # 캐시 저장
            if cache_key:
                self._set_cache(cache_key, result)

            logger.info(f"OpenAI fallback successful for model: {openai_model}")
            return result

    async def _call_openai_direct_stream(
        self,
        model_id: str,
        payload: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        """
        Stream from OpenAI API directly as fallback.

        Args:
            model_id: OpenRouter model ID
            payload: Request payload

        Yields:
            Content chunks as strings
        """
        openai_model = self.OPENAI_FALLBACK_MODELS.get(model_id)
        if not openai_model:
            raise ValueError(f"No OpenAI fallback available for model: {model_id}")

        openai_payload = payload.copy()
        openai_payload["model"] = openai_model

        logger.info(f"Falling back to OpenAI direct streaming for model: {openai_model}")

        async with httpx.AsyncClient(timeout=self.OPENAI_FALLBACK_TIMEOUT) as client:
            async with client.stream(
                "POST",
                f"{self.OPENAI_BASE_URL}/chat/completions",
                headers=self._get_openai_headers(),
                json=openai_payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

    def _generate_cache_key(self, model: str, messages: list, **kwargs) -> str:
        """Generate cache key from request parameters."""
        cache_data = {
            "model": model,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if v is not None}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid."""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                logger.debug(f"Cache hit for key {cache_key[:8]}...")
                return result
            else:
                # 만료된 캐시 삭제
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, result: Dict[str, Any]):
        """Store result in cache with TTL."""
        # 캐시 크기 제한
        if len(self._cache) >= self.CACHE_MAX_SIZE:
            # 가장 오래된 항목 삭제
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[cache_key] = (result, time.time())

    async def _apply_request_delay(self):
        """Apply delay between requests to avoid rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    async def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        json_schema: Optional[Dict] = None,
        stop: Optional[list] = None,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Call chat completion API with retry and key rotation.

        Args:
            model: Model key (gpt-4o-mini, claude-sonnet, gemini-flash)
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})
            json_schema: Optional JSON schema for structured output (OpenAI only)
            stop: Optional list of stop sequences
            frequency_penalty: Reduce repetition of same tokens (0.0-2.0)
            presence_penalty: Encourage new topics (0.0-2.0)
            use_cache: Whether to use caching (default: True)

        Returns:
            API response dict
        """
        # Gemini 모델은 GeminiService로 라우팅
        if model in GEMINI_MODEL_KEYS:
            from .gemini import gemini_service
            return await gemini_service.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                **{k: v for k, v in [
                    ("stop", stop),
                    ("frequency_penalty", frequency_penalty),
                    ("presence_penalty", presence_penalty),
                ] if v}
            )

        if not self.api_keys:
            raise ValueError("OpenRouter API key not configured")

        model_id = self.MODELS.get(model, model)

        # 캐시 확인 (temperature가 0일 때만 캐싱 효과적)
        cache_key = None
        if use_cache and temperature == 0:
            cache_key = self._generate_cache_key(
                model, messages,
                max_tokens=max_tokens,
                response_format=response_format,
                json_schema=json_schema,
            )
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Structured Output with JSON Schema (OpenAI models)
        if json_schema and model_id.startswith("openai/"):
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": json_schema
            }
        # Basic JSON mode (OpenAI, Google models)
        elif response_format and (model_id.startswith("openai/") or model_id.startswith("google/")):
            payload["response_format"] = response_format

        # Stop sequences
        if stop:
            payload["stop"] = stop

        # Repetition control
        if frequency_penalty > 0:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty > 0:
            payload["presence_penalty"] = presence_penalty

        last_error = None
        keys_tried = 0
        should_try_openai_fallback = False

        # 모든 키를 시도할 때까지 반복
        while keys_tried < len(self.api_keys):
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    # 요청 간 딜레이 적용
                    await self._apply_request_delay()

                    async with httpx.AsyncClient(timeout=self.OPENROUTER_TIMEOUT) as client:
                        response = await client.post(
                            f"{self.BASE_URL}/chat/completions",
                            headers=self._get_headers(),
                            json=payload,
                        )

                        # Rate limit 에러 체크
                        if response.status_code == 429:
                            logger.warning(f"Rate limit hit on key index {self.current_key_index}, attempt {attempt + 1}")

                            # 재시도 횟수 소진 시 키 로테이션
                            if attempt >= self.MAX_RETRIES:
                                if self._rotate_api_key():
                                    keys_tried += 1
                                    break  # 새 키로 재시도
                                else:
                                    raise httpx.HTTPStatusError(
                                        "All API keys exhausted due to rate limits",
                                        request=response.request,
                                        response=response
                                    )

                            # 재시도 전 대기 (지수 백오프)
                            wait_time = min(2 ** attempt, 10)
                            logger.info(f"Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            continue

                        if response.status_code != 200:
                            logger.error(f"Error response: {response.text[:500]}")
                        response.raise_for_status()

                        result = response.json()

                        # LangSmith 토큰 사용량 로깅
                        usage = result.get("usage", {})
                        if usage:
                            from .langsmith_tracker import langsmith_tracker
                            langsmith_tracker.log_llm_usage(
                                model=model_id,
                                prompt_tokens=usage.get("prompt_tokens", 0),
                                completion_tokens=usage.get("completion_tokens", 0),
                                total_tokens=usage.get("total_tokens", 0),
                            )

                        # 캐시 저장
                        if cache_key:
                            self._set_cache(cache_key, result)

                        return result

                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code == 429:
                        continue  # 이미 위에서 처리됨
                    raise
                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    # 타임아웃 또는 연결 에러 - OpenAI fallback 시도 대상
                    last_error = e
                    logger.warning(f"OpenRouter timeout/connection error: {e}")
                    should_try_openai_fallback = True
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(1)
                        continue
                    # 재시도 모두 실패 - 루프 탈출하여 fallback 시도
                    break
                except Exception as e:
                    last_error = e
                    logger.error(f"Request failed: {e}")
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(1)
                        continue
                    raise

            # 타임아웃으로 인한 fallback 시도 필요
            if should_try_openai_fallback:
                break

            # 현재 키로 모든 재시도 실패 - 다음 키로 시도
            if keys_tried < len(self.api_keys) - 1:
                if self._rotate_api_key():
                    keys_tried += 1
                else:
                    break
            else:
                break

        # OpenAI fallback 시도 (타임아웃/연결 에러 발생 시)
        if should_try_openai_fallback and self._can_fallback_to_openai(model_id):
            try:
                logger.info(f"Attempting OpenAI direct fallback for {model_id}")
                return await self._call_openai_direct(model_id, payload, cache_key)
            except Exception as fallback_error:
                logger.error(f"OpenAI fallback also failed: {fallback_error}")
                # 원래 에러를 raise
                if last_error:
                    raise last_error
                raise fallback_error

        # 모든 시도 실패
        if last_error:
            raise last_error
        raise RuntimeError("Unexpected error in chat_completion")

    async def chat_completion_stream(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion with retry and key rotation.

        Yields:
            Content chunks as strings
        """
        if not self.api_keys:
            raise ValueError("OpenRouter API key not configured")

        model_id = self.MODELS.get(model, model)

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        last_error = None
        keys_tried = 0
        should_try_openai_fallback = False

        while keys_tried < len(self.api_keys):
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    await self._apply_request_delay()

                    async with httpx.AsyncClient(timeout=self.OPENROUTER_TIMEOUT) as client:
                        async with client.stream(
                            "POST",
                            f"{self.BASE_URL}/chat/completions",
                            headers=self._get_headers(),
                            json=payload,
                        ) as response:
                            if response.status_code == 429:
                                logger.warning(f"Rate limit hit on streaming, key index {self.current_key_index}")
                                if attempt >= self.MAX_RETRIES:
                                    if self._rotate_api_key():
                                        keys_tried += 1
                                        break
                                    raise httpx.HTTPStatusError(
                                        "All API keys exhausted",
                                        request=response.request,
                                        response=response
                                    )
                                await asyncio.sleep(min(2 ** attempt, 10))
                                continue

                            response.raise_for_status()
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data = line[6:]
                                    if data == "[DONE]":
                                        return
                                    try:
                                        chunk = json.loads(data)
                                        content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        if content:
                                            yield content
                                    except json.JSONDecodeError:
                                        continue
                            return

                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code == 429:
                        continue
                    raise
                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    # 타임아웃 또는 연결 에러 - OpenAI fallback 시도 대상
                    last_error = e
                    logger.warning(f"OpenRouter streaming timeout/connection error: {e}")
                    should_try_openai_fallback = True
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(1)
                        continue
                    break
                except Exception as e:
                    last_error = e
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(1)
                        continue
                    raise

            # 타임아웃으로 인한 fallback 시도 필요
            if should_try_openai_fallback:
                break

            if keys_tried < len(self.api_keys) - 1:
                if self._rotate_api_key():
                    keys_tried += 1
                else:
                    break
            else:
                break

        # OpenAI fallback 시도 (타임아웃/연결 에러 발생 시)
        if should_try_openai_fallback and self._can_fallback_to_openai(model_id):
            try:
                logger.info(f"Attempting OpenAI direct streaming fallback for {model_id}")
                async for chunk in self._call_openai_direct_stream(model_id, payload):
                    yield chunk
                return
            except Exception as fallback_error:
                logger.error(f"OpenAI streaming fallback also failed: {fallback_error}")
                if last_error:
                    raise last_error
                raise fallback_error

        if last_error:
            raise last_error

    def get_content(self, response: Dict[str, Any]) -> str:
        """Extract content from API response."""
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON from response content.
        Handles markdown code blocks, truncated JSON, and various edge cases.
        """
        import re

        original_content = content
        content = content.strip()

        def try_parse(s: str):
            """Try to parse JSON, return None on failure."""
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        def fix_truncated_json(s: str) -> str:
            """Try to fix truncated JSON by closing open brackets/braces."""
            s = s.rstrip()

            # Count open brackets
            open_braces = s.count('{') - s.count('}')
            open_brackets = s.count('[') - s.count(']')
            open_quotes = s.count('"') % 2  # Odd number means unclosed string

            # If we're inside a string, close it
            if open_quotes:
                s += '"'

            # Close arrays first, then objects
            s += ']' * open_brackets
            s += '}' * open_braces

            return s

        def extract_json_object(s: str):
            """Extract the first complete JSON object from string."""
            start = s.find('{')
            if start == -1:
                return None

            depth = 0
            in_string = False
            escape = False

            for i, char in enumerate(s[start:], start):
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return s[start:i+1]

            # If we reach here, JSON is incomplete - return what we have
            return s[start:]

        # 1. Try direct JSON parse first
        result = try_parse(content)
        if result:
            return result

        # 2. Remove markdown code blocks (various formats)
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(code_block_pattern, content)
        if matches:
            content = matches[0].strip()
            result = try_parse(content)
            if result:
                return result

        # 3. Extract JSON object from content
        extracted = extract_json_object(content)
        if extracted:
            result = try_parse(extracted)
            if result:
                return result

            # 4. Try fixing truncated JSON
            fixed = fix_truncated_json(extracted)
            result = try_parse(fixed)
            if result:
                logger.debug("Fixed truncated JSON successfully")
                return result

        # 5. Manual cleanup and retry
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()

        result = try_parse(content)
        if result:
            return result

        # 6. Last resort: try to fix and parse
        fixed = fix_truncated_json(content)
        result = try_parse(fixed)
        if result:
            logger.debug("Fixed truncated JSON on final attempt")
            return result

        # Log the problematic content for debugging
        logger.error(f"All JSON parse attempts failed. Content preview: {original_content[:300]}...")
        raise ValueError(f"Failed to parse JSON from LLM response")


# 싱글톤 인스턴스 (모든 용도에서 동일한 키 사용)
openrouter_service = OpenRouterService(purpose="default")
# 하위 호환성을 위한 별칭
openrouter_problem = openrouter_service
openrouter_hint = openrouter_service
openrouter_codegen = openrouter_service
