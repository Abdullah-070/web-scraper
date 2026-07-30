"""
Shared Proxy Rotation 

A single reusable utility so proxy logic lives in exactly one place,
not copy-pasted into each scraper.
"""

from __future__ import annotations

import itertools
import logging
import os
import random
import threading

logger = logging.getLogger("sdip.scrapers")


class ProxyPool:
    """Round-robin proxy pool with simple failure-based deprioritization.

    """

    def __init__(self, proxies: list[str] | None = None):
        env_proxies = os.environ.get("PROXY_LIST", "")
        self._proxies: list[str] = proxies or [
            p.strip() for p in env_proxies.split(",") if p.strip()
        ]
        self._failure_counts: dict[str, int] = {p: 0 for p in self._proxies}
        self._lock = threading.Lock()
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None

    @property
    def enabled(self) -> bool:
        return bool(self._proxies)

    def get_proxy(self) -> str | None:
        """Return the next proxy in rotation
        """
        if not self._proxies:
            return None

        with self._lock:
            # Try up to len(proxies) times to find one that isn't
            # currently flagged as too-failed; falls back to a random
            # choice if all are equally bad (better than raising).
            for _ in range(len(self._proxies)):
                candidate = next(self._cycle)
                if self._failure_counts.get(candidate, 0) < 3:
                    return candidate
            return random.choice(self._proxies)

    def report_failure(self, proxy: str) -> None:
        """Call when a request through this proxy was blocked/failed
        """
        with self._lock:
            self._failure_counts[proxy] = self._failure_counts.get(proxy, 0) + 1
            logger.warning(
                "Proxy %s reported a failure (count=%s)",
                proxy,
                self._failure_counts[proxy],
            )

    def report_success(self, proxy: str) -> None:
        """Call after a successful request to reset a proxy's failure count."""
        with self._lock:
            self._failure_counts[proxy] = 0

default_proxy_pool = ProxyPool()
