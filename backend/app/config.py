from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "CodeFill API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    frontend_url: str = "http://localhost:3000"

    # LLM
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""

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

    # Azure Translator
    azure_translator_key: str = ""
    azure_translator_region: str = "koreacentral"
    azure_translator_endpoint: str = "https://api.cognitive.microsofttranslator.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
