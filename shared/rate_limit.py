"""
Configurable daily usage cap per connected account .

"""

from __future__ import annotations

import json
import os
import threading
from datetime import date
from pathlib import Path

from shared.exceptions import RateLimitExceededError


class RateLimiter:
    """Interface every rate limiter implementation should follow."""

    def check_and_increment(self, account_id: str, scraper_type: str) -> None:
        """Raise RateLimitExceededError if the account is over its daily cap
        for this scraper type. Otherwise, increment the counter and return.
        """
        raise NotImplementedError


class FileRateLimiter(RateLimiter):
    
    def __init__(self, storage_path: str | None = None, daily_limit: int = 100):
        self.storage_path = Path(storage_path or "rate_limit_state.json")
        self.daily_limit = daily_limit
        self._lock = threading.Lock()
        if not self.storage_path.exists():
            self.storage_path.write_text("{}")

    def _load(self) -> dict:
        try:
            return json.loads(self.storage_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save(self, data: dict) -> None:
        self.storage_path.write_text(json.dumps(data, indent=2))

    def check_and_increment(self, account_id: str, scraper_type: str) -> None:
        today = date.today().isoformat()
        key = f"{account_id}:{scraper_type}:{today}"

        with self._lock:
            data = self._load()
            count = data.get(key, 0)

            if count >= self.daily_limit:
                raise RateLimitExceededError(
                    f"Daily scrape limit ({self.daily_limit}) reached for account "
                    f"'{account_id}' on scraper '{scraper_type}'.",
                    details={
                        "account_id": account_id,
                        "scraper_type": scraper_type,
                        "date": today,
                        "limit": self.daily_limit,
                    },
                )

            data[key] = count + 1
            self._save(data)
