from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    llm_provider: Literal["anthropic", "openai", "gemini"] = "gemini"
    model_name: str | None = None
    model_temperature: float = 0.3
    analysis_timeout_seconds: int = 180
    ticker_validation_timeout_seconds: int = 15
    analysis_rate_limit_count: int = 5
    analysis_rate_limit_window_seconds: int = 600
    cors_origins: str = ""

    app_name: str = "StockPilot AI"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    backend_port: int = 8000
    frontend_port: int = 3000


@lru_cache
def get_settings() -> Settings:
    return Settings()
