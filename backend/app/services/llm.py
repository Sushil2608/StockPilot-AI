import logging
from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()
    logger.info(
        "Initializing LLM provider=%s model=%s",
        settings.llm_provider,
        settings.model_name,
    )

    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Set ANTHROPIC_API_KEY when LLM_PROVIDER=anthropic")

        kwargs = {
            "model": settings.model_name,
            "anthropic_api_key": settings.anthropic_api_key,
            "temperature": settings.model_temperature,
            "max_tokens": 4096,
            "max_retries": 3,
        }
        return ChatAnthropic(**kwargs)

    if not settings.openai_api_key:
        raise ValueError("Set OPENAI_API_KEY when LLM_PROVIDER=openai")

    kwargs = {
        "model": settings.model_name,
        "api_key": settings.openai_api_key,
        "max_tokens": 4096,
        "max_retries": 3,
        "temperature": settings.model_temperature,
    }
    return ChatOpenAI(**kwargs)
