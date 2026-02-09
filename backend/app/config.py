"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Habit Tracker API"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://habit_user:password@localhost:5432/habit_tracker"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 43200  # 30 days

    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    apple_client_id: str = ""

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "anthropic"
    llm_model: str = "claude-3-5-haiku-20241022"

    # Rate limits
    llm_daily_limit: int = 20
    task_xp_daily_limit: int = 500

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "https://habit.apps.ilanewep.cloud"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
