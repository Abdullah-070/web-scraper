"""
Shared retry decorator .

Retries only NetworkError by default -- BlockedOrCaptchaError,
InvalidInputError, AuthenticationError, and RateLimitExceededError should
NOT be retried blindly (retrying a CAPTCHA wall just burns more requests
against a site that's already suspicious of you).
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Callable, TypeVar

from shared.exceptions import NetworkError
from shared.human_behavior import jittered_backoff

logger = logging.getLogger("sdip.scrapers")

T = TypeVar("T")


def async_retry(
    max_attempts: int = 3,
    retry_on: tuple = (NetworkError,),
):
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.error(
                            "Retry exhausted after %s attempts for %s: %s",
                            attempt,
                            func.__name__,
                            exc,
                        )
                        raise
                    delay = jittered_backoff(attempt)
                    logger.warning(
                        "Attempt %s/%s failed for %s (%s). Retrying in %.1fs.",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
            raise last_exc  # pragma: no cover - unreachable safeguard

        return wrapper

    return decorator
