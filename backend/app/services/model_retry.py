import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_MODEL_ATTEMPTS = 3
RETRYABLE_MODEL_MESSAGES = (
    "high demand",
    "overloaded",
    "overload",
    "resource_exhausted",
    "resource exhausted",
    "temporarily unavailable",
    "service unavailable",
    "try again later",
    "please retry",
    "rate limit",
    "too many requests",
    "429",
    "503",
    "529",
)
RETRYABLE_RESPONSE_MESSAGES = (
    "this model is experiencing high demand",
    "model is experiencing high demand",
    "currently experiencing high demand",
    "the model is currently overloaded",
    "this model is currently overloaded",
    "model is overloaded",
    "the model is temporarily unavailable",
    "this model is temporarily unavailable",
    "service is temporarily unavailable",
    "please try again later",
    "please retry your request",
)
NON_RETRYABLE_MODEL_MESSAGES = (
    "insufficient_quota",
    "quota exceeded",
    "no credits remaining",
    "exceeded your current quota",
    "billing",
)


class ModelUnavailableError(RuntimeError):
    """A temporary provider availability failure after retrying."""

    def __init__(self) -> None:
        super().__init__("The AI service is temporarily busy. Please try again shortly.")


def _contains_message(value: object, messages: tuple[str, ...]) -> bool:
    if isinstance(value, str):
        normalized = value.lower()
        return any(message in normalized for message in messages)
    if isinstance(value, dict):
        return any(_contains_message(item, messages) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_message(item, messages) for item in value)
    if hasattr(value, "model_dump"):
        try:
            return _contains_message(value.model_dump(), messages)
        except Exception:
            return False
    return False


def _is_retryable_exception(error: Exception) -> bool:
    pending = [error]
    visited: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in visited:
            continue
        visited.add(id(current))
        details = (str(current), current.args)
        if any(
            _contains_message(detail, RETRYABLE_MODEL_MESSAGES)
            and _contains_message(detail, NON_RETRYABLE_MODEL_MESSAGES)
            for detail in details
        ):
            return False
        if any(
            _contains_message(detail, RETRYABLE_MODEL_MESSAGES)
            for detail in details
        ):
            return True
        if current.__cause__ is not None:
            pending.append(current.__cause__)
        if current.__context__ is not None:
            pending.append(current.__context__)
    return False


async def invoke_with_model_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    operation_name: str,
) -> T:
    """Retry model availability failures, then expose only a generic error."""
    for attempt in range(MAX_MODEL_ATTEMPTS):
        try:
            result = await operation()
            if _contains_message(result, RETRYABLE_RESPONSE_MESSAGES):
                raise RuntimeError("The model is temporarily unavailable.")
            return result
        except Exception as error:
            if not _is_retryable_exception(error):
                raise

            if attempt == MAX_MODEL_ATTEMPTS - 1:
                logger.warning(
                    "Model operation %s remained unavailable after %d attempts",
                    operation_name,
                    MAX_MODEL_ATTEMPTS,
                    exc_info=error,
                )
                raise ModelUnavailableError() from error

            delay_seconds = 2 ** (attempt + 1)
            logger.info(
                "Model operation %s temporarily unavailable; retrying in %d seconds (%d/%d)",
                operation_name,
                delay_seconds,
                attempt + 2,
                MAX_MODEL_ATTEMPTS,
            )
            await asyncio.sleep(delay_seconds)

    raise AssertionError("Model retry loop exited unexpectedly")
