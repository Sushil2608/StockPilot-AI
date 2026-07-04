from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    anthropic_api_key: str
    model_name: str = "claude-sonnet-4-6"
    model_temperature: float = 0.3

    app_name: str = "StockPilot AI"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    backend_port: int = 8000
    frontend_port: int = 3000


@lru_cache
def get_settings() -> Settings:
    return Settings()
