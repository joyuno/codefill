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

    # LLM (추후 활성화)
    openrouter_api_key: str = ""
    openai_api_key: str = ""

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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
