"""
Embedding Service
OpenAI embeddings + pgvector integration
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from ..config import get_settings


class EmbeddingService:
    """Service for generating embeddings and vector search."""

    OPENAI_EMBEDDING_URL = "https://api.openai.com/v1/embeddings"
    EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
    EMBEDDING_DIMENSIONS = 1536

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for OpenAI API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.OPENAI_EMBEDDING_URL,
                headers=self._get_headers(),
                json={
                    "model": self.EMBEDDING_MODEL,
                    "input": text,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (max 2048 for OpenAI)

        Returns:
            List of embedding vectors
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.OPENAI_EMBEDDING_URL,
                    headers=self._get_headers(),
                    json={
                        "model": self.EMBEDDING_MODEL,
                        "input": batch,
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Sort by index to maintain order
                sorted_data = sorted(data["data"], key=lambda x: x["index"])
                batch_embeddings = [item["embedding"] for item in sorted_data]
                all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def create_problem_text_for_embedding(self, problem: Dict[str, Any]) -> str:
        """
        Create text representation of a problem for embedding.
        Combines title, description, tags, and code for semantic search.

        🚀 개선사항:
        - 모든 언어 코드 임베딩 (Python, Java, C++)
        - 코드 구조 정보 추출 (함수/클래스 시그니처)
        - 긴 코드는 청킹하여 핵심 부분만 포함

        Args:
            problem: Problem dictionary

        Returns:
            Combined text for embedding
        """
        parts = []

        # Title/Name
        if problem.get("name"):
            parts.append(problem["name"])
        elif problem.get("title"):
            parts.append(problem["title"])

        # Question/Description
        if problem.get("question"):
            # Full question text (limit to 3000 chars for very long ones)
            question = problem["question"][:3000]
            parts.append(question)

        # Tags
        if problem.get("tags"):
            tags_str = ", ".join(problem["tags"])
            parts.append(f"Tags: {tags_str}")

        # Difficulty
        if problem.get("difficulty"):
            parts.append(f"Difficulty: {problem['difficulty']}")

        # 🚀 Solutions - 모든 언어 코드 임베딩
        solutions = problem.get("solutions", [])
        if solutions and isinstance(solutions, list):
            # 언어 우선순위: python > java > cpp
            lang_priority = {"python": 1, "java": 2, "cpp": 3, "c++": 3}
            sorted_solutions = sorted(
                solutions,
                key=lambda s: lang_priority.get(s.get("language", "python").lower(), 99)
            )

            for sol in sorted_solutions[:2]:  # 최대 2개 언어
                lang = sol.get("language", "python").lower()
                code = sol.get("code", "")

                if code:
                    # 코드 구조 추출 (함수/클래스 시그니처)
                    structure = self._extract_code_structure(code, lang)
                    if structure:
                        parts.append(f"{lang.upper()} Structure: {structure}")

                    # 긴 코드는 청킹하여 핵심 부분만
                    if len(code) > 1500:
                        chunks = self.chunk_code(code, chunk_size=800, overlap=100)
                        # 첫 번째와 마지막 청크 (시작과 끝이 중요)
                        code_summary = chunks[0]
                        if len(chunks) > 1:
                            code_summary += "\n...\n" + chunks[-1]
                        parts.append(f"{lang.upper()} Code:\n{code_summary}")
                    else:
                        parts.append(f"{lang.upper()} Code:\n{code}")

        return "\n\n".join(parts)

    def _extract_code_structure(self, code: str, language: str) -> str:
        """
        코드에서 구조 정보 추출 (함수/클래스 시그니처)

        Args:
            code: 소스 코드
            language: 프로그래밍 언어

        Returns:
            구조 정보 문자열 (예: "def solution(arr), class Solution")
        """
        import re
        structures = []

        if language in ["python"]:
            # Python: def, class
            func_matches = re.findall(r'def\s+(\w+)\s*\([^)]*\)', code)
            class_matches = re.findall(r'class\s+(\w+)', code)
            structures.extend([f"def {f}()" for f in func_matches[:5]])
            structures.extend([f"class {c}" for c in class_matches[:3]])

        elif language in ["java"]:
            # Java: public/private method, class
            method_matches = re.findall(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)', code)
            class_matches = re.findall(r'class\s+(\w+)', code)
            structures.extend([f"{m}()" for m in method_matches[:5]])
            structures.extend([f"class {c}" for c in class_matches[:3]])

        elif language in ["cpp", "c++"]:
            # C++: function, class
            func_matches = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*(?:const)?\s*\{', code)
            class_matches = re.findall(r'class\s+(\w+)', code)
            structures.extend([f"{f}()" for f in func_matches[:5]])
            structures.extend([f"class {c}" for c in class_matches[:3]])

        return ", ".join(structures) if structures else ""

    def chunk_code(self, code: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split code into overlapping chunks for better retrieval.

        Args:
            code: Source code to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of code chunks
        """
        if len(code) <= chunk_size:
            return [code]

        chunks = []
        lines = code.split("\n")
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line) + 1  # +1 for newline

            if current_length + line_length > chunk_size and current_chunk:
                # Save current chunk
                chunks.append("\n".join(current_chunk))

                # Start new chunk with overlap
                overlap_lines = []
                overlap_length = 0
                for prev_line in reversed(current_chunk):
                    if overlap_length + len(prev_line) + 1 > overlap:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_length += len(prev_line) + 1

                current_chunk = overlap_lines
                current_length = overlap_length

            current_chunk.append(line)
            current_length += line_length

        # Don't forget last chunk
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks


# Singleton instance
embedding_service = EmbeddingService()
