"""
OpenRouter Service
LLM API calls via OpenRouter
"""

import httpx
import json
from typing import Optional, Dict, Any, AsyncGenerator
from ..config import get_settings


class OpenRouterService:
    """Service for calling LLMs via OpenRouter API."""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Model IDs (OpenRouter format)
    MODELS = {
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "claude-sonnet": "anthropic/claude-sonnet-4",  # Claude Sonnet 4
        "gemini-flash": "google/gemini-2.0-flash-001",
        "gemini-3-pro": "google/gemini-3-pro-preview",
        "deepseek-v3": "deepseek/deepseek-v3.2",
    }

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openrouter_api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://codefill.app",
            "X-Title": "CodeFill",
        }

    async def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Call chat completion API.

        Args:
            model: Model key (gpt-4o-mini, claude-sonnet, gemini-flash)
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            API response dict
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        model_id = self.MODELS.get(model, model)

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # response_format은 OpenAI 모델에서만 지원
        if response_format and model_id.startswith("openai/"):
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"[OpenRouter] Calling model: {model_id}")
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            print(f"[OpenRouter] Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[OpenRouter] Error response: {response.text[:500]}")
            response.raise_for_status()

            result = response.json()

            # 응답 내용 미리보기 (디버깅용)
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                print(f"[OpenRouter] Content preview: {content[:200]}...")

            return result

    async def chat_completion_stream(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion.

        Yields:
            Content chunks as strings
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        model_id = self.MODELS.get(model, model)

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.BASE_URL}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

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
                print(f"[JSON Parse] Fixed truncated JSON successfully")
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
            print(f"[JSON Parse] Fixed truncated JSON on final attempt")
            return result

        # Log the problematic content for debugging
        print(f"[JSON Parse] ❌ All parse attempts failed")
        print(f"[JSON Parse] Original content preview: {original_content[:300]}...")
        raise ValueError(f"Failed to parse JSON from LLM response")


# Singleton instance
openrouter_service = OpenRouterService()
