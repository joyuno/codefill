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
        Combines title, description, tags, and Python code for semantic search.

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

        # Solutions - Python code only, full content
        solutions = problem.get("solutions", [])
        if solutions and isinstance(solutions, list):
            for sol in solutions:
                # Support both formats: {"language": "python", "code": "..."} and {"code": "..."}
                lang = sol.get("language", "python").lower()
                code = sol.get("code", "")

                if lang == "python" and code:
                    # Include full Python code (no character limit)
                    parts.append(f"Python Code:\n{code}")
                    break  # Only include first Python solution

        return "\n\n".join(parts)

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
