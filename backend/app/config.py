from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

# .env 파일 경로 결정
# 1. 환경변수 ENV_FILE_PATH가 있으면 사용
# 2. .env.local이 있으면 사용 (로컬 개발용)
# 3. 없으면 .env 사용
_env_file = os.getenv("ENV_FILE_PATH")
if not _env_file:
    _base_dir = Path(__file__).resolve().parent.parent
    _env_local = _base_dir / ".env.local"
    _env_default = _base_dir / ".env"
    _env_file = str(_env_local if _env_local.exists() else _env_default)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",  # Prisma용 DATABASE_URL, DIRECT_URL 등 허용
    )

    # App
    app_name: str = "CodeFill API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # Supabase PostgreSQL Direct Connection (for LangGraph Checkpointer)
    # Format: postgresql://user:password@host:port/database
    supabase_db_url: str = ""

    # Environment
    environment: str = "development"  # development, staging, production

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    frontend_url: str = "http://localhost:3000"

    # LLM API Keys
    openrouter_api_key: str = ""              # OpenRouter API 키 (gpt-4o-mini용)
    gemini_api_keys: str = ""                 # Gemini API 키들 (쉼표 구분, 로테이션)
    openai_api_key: str = ""
    groq_api_key: str = ""

    # LLM Models per Agent
    # Available aliases: gpt-4o, gpt-4o-mini, claude-sonnet, gemini-flash, gemini-3-pro, deepseek-v3
    llm_model_chat: str = "gpt-4o-mini"          # Chat agent, intent handler
    llm_model_lite: str = "gemini-flash"         # Lightweight tasks (intent, collection, general) - gemini-3-flash
    llm_model_intent: str = "gemini-flash"       # Intent classifier - gemini-3-flash
    llm_model_blank_gen: str = "gemini-flash"     # Blank problem generation
    llm_model_puzzle_gen: str = "gemini-flash"    # Puzzle problem generation
    llm_model_guided_gen: str = "gemini-flash"    # Guided problem generation
    llm_model_code_gen: str = "gemini-3-pro"      # Code generation (RAG fallback)
    llm_model_hint: str = "gemini-flash"          # Hint generation
    llm_model_analysis: str = "gemini-flash"      # Learning analysis report

    # Judge0 (Code Execution)
    judge0_url: str = "https://judge0-ce.p.rapidapi.com"
    judge0_api_key: str = ""
    judge0_api_host: str = "judge0-ce.p.rapidapi.com"

    # Frontend (Next.js에서 사용하지만 여기서도 허용)
    next_public_api_url: str = "http://localhost:8000"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Kakao OAuth
    kakao_client_id: str = ""
    kakao_client_secret: str = ""
    kakao_redirect_uri: str = "http://localhost:8000/auth/kakao/callback"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"

    # Azure Translator
    azure_translator_key: str = ""
    azure_translator_region: str = "koreacentral"
    azure_translator_endpoint: str = "https://api.cognitive.microsofttranslator.com"

    # Analytics (Next.js frontend uses these, but allow in backend env)
    next_public_clarity_id: str = ""
    next_public_ga_id: str = ""

    # PostgreSQL Cache TTL (seconds)
    cache_ttl_recommendations: int = 300  # 5 minutes
    cache_ttl_user_preferences: int = 600  # 10 minutes

    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# ============================================================
# Centralized Logging Configuration
# ============================================================

import logging
import sys

def setup_logging() -> None:
    """
    Configure application-wide logging.
    Call this once at application startup.
    """
    settings = get_settings()

    # Determine log level from settings/environment
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    if settings.debug:
        log_level = logging.DEBUG

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)
    logging.getLogger("h2").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given module name.

    Usage:
        from app.config import get_logger
        logger = get_logger(__name__)
        logger.info("Message")
        logger.error("Error", exc_info=True)  # Include stack trace
    """
    return logging.getLogger(name)
