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
    ai_model: str = "gemini-2.5-flash"

    # Misc
    # Comma-separated list — the frontend's dev server port varies (TanStack Start
    # picks the first free port starting at 8080; Vite SPAs default to 5173), and
    # a deployed app will add its production URL here too.
    frontend_url: str = "http://localhost:5173,http://localhost:8080,http://localhost:8081"
    max_upload_size_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
