import logging
from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_llm() -> ChatAnthropic:
    settings = get_settings()
    logger.info("Initializing ChatAnthropic with model=%s", settings.model_name)
    return ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=settings.model_temperature,
        max_tokens=4096,
    )
