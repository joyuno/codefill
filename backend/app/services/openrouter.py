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
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "claude-sonnet": "anthropic/claude-sonnet-4",  # Claude Sonnet 4
        "gemini-flash": "google/gemini-2.0-flash-001",
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

        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=60.0) as client:
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
            return response.json()

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
        Handles markdown code blocks and various edge cases.
        """
        import re

        content = content.strip()

        # 1. Try direct JSON parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 2. Remove markdown code blocks (various formats)
        # Handle ```json ... ``` or ``` ... ```
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(code_block_pattern, content)
        if matches:
            # Use the first code block found
            content = matches[0].strip()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass

        # 3. Try to find JSON object in the content
        # Look for { ... } pattern
        json_pattern = r'\{[\s\S]*\}'
        json_match = re.search(json_pattern, content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 4. Manual cleanup for edge cases
        # Remove leading/trailing backticks and "json" label
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Log the problematic content for debugging
            print(f"JSON parse error: {e}")
            print(f"Content preview: {content[:200]}...")
            raise ValueError(f"Failed to parse JSON: {str(e)[:100]}")


# Singleton instance
openrouter_service = OpenRouterService()
