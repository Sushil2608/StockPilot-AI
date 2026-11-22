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
        api_key = settings.ai_proxy_api_key or settings.anthropic_api_key
        if not api_key:
            raise ValueError(
                "Set ANTHROPIC_API_KEY or AI_PROXY_API_KEY when "
                "LLM_PROVIDER=anthropic"
            )

        kwargs = {
            "model": settings.model_name,
            "anthropic_api_key": api_key,
            "temperature": settings.model_temperature,
            "max_tokens": 4096,
            "max_retries": 3,
        }
        if settings.ai_proxy_base_url:
            kwargs["base_url"] = settings.ai_proxy_base_url
        return ChatAnthropic(**kwargs)

    if not settings.ai_proxy_api_key:
        raise ValueError(
            "Set AI_PROXY_API_KEY when LLM_PROVIDER=openai_compatible"
        )

    kwargs = {
        "model": settings.model_name,
        "api_key": settings.ai_proxy_api_key,
        "max_tokens": 4096,
        "max_retries": 3,
        "use_responses_api": settings.openai_use_responses_api,
    }
    if settings.ai_proxy_base_url:
        kwargs["base_url"] = settings.ai_proxy_base_url
    if not settings.openai_use_responses_api:
        kwargs["temperature"] = settings.model_temperature
    return ChatOpenAI(**kwargs)
