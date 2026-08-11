"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "resume_analyzer"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24h

    # AI provider
    ai_provider: str = "gemini"  # "gemini" or "openai"
    ai_api_key: str = ""
    ai_model: str = "gemini-1.5-flash"

    # Misc
    frontend_url: str = "http://localhost:5173"
    max_upload_size_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
