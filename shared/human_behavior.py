"""
Human-like interaction pacing (FR-1.10, NFR-1.2).

Week 1 scope is intentionally simple: randomized delays instead of fixed
intervals, so scraping doesn't look like a bot hammering the target site at
a constant rate. Full proxy rotation and CAPTCHA handling come in Week 3
(FR-3.3 / FR-3.4) -- don't over-build this yet.
"""

from __future__ import annotations

import asyncio
import random


async def human_delay(min_seconds: float = 1.5, max_seconds: float = 4.0) -> None:
    """Await a randomized delay to simulate human pacing between actions.

    Use this between page navigations, searches, and profile visits --
    anywhere a real user would naturally pause.
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def human_typing_delay(min_seconds: float = 0.05, max_seconds: float = 0.2) -> None:
    """Shorter randomized delay, meant for use between simulated keystrokes
    if/when a scraper needs to type into a search box rather than navigating
    directly via URL params.
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def jittered_backoff(attempt: int, base: float = 2.0, cap: float = 60.0) -> float:
    """Exponential backoff with jitter for retry logic (used alongside
    shared.retry). attempt is 1-indexed.
    """
    exp = min(cap, base * (2 ** (attempt - 1)))
    return random.uniform(exp * 0.5, exp)
