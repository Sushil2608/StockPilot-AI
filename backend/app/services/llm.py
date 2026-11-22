import logging
from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o",
    "gemini": "gemini-3.5-flash-lite",
}


@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()
    model_name = settings.model_name or DEFAULT_MODELS[settings.llm_provider]
    logger.info(
        "Initializing LLM provider=%s model=%s",
        settings.llm_provider,
        model_name,
    )

    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Set ANTHROPIC_API_KEY when LLM_PROVIDER=anthropic")

        kwargs = {
            "model": model_name,
            "anthropic_api_key": settings.anthropic_api_key,
            "temperature": settings.model_temperature,
            "max_tokens": 4096,
            "max_retries": 3,
        }
        return ChatAnthropic(**kwargs)

    if settings.llm_provider == "gemini":
        if not settings.google_api_key:
            raise ValueError("Set GOOGLE_API_KEY when LLM_PROVIDER=gemini")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.model_temperature,
            max_output_tokens=4096,
            max_retries=3,
        )

    if not settings.openai_api_key:
        raise ValueError("Set OPENAI_API_KEY when LLM_PROVIDER=openai")

    kwargs = {
        "model": model_name,
        "api_key": settings.openai_api_key,
        "max_tokens": 4096,
        "max_retries": 3,
        "temperature": settings.model_temperature,
    }
    return ChatOpenAI(**kwargs)
