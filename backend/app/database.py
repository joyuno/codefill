from supabase import create_client, Client
from functools import lru_cache
from .config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


@lru_cache()
def get_supabase_anon_client() -> Client:
    """Get Supabase client with anon key for client-side operations."""
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )


def get_db() -> Client:
    """Dependency for database access."""
    return get_supabase_client()
