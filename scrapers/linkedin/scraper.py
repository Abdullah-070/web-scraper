from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.linkedin.config import (
    DEFAULT_DAILY_LIMIT,
    LINKEDIN_SEARCH_URL,
    REQUIRED_INPUT_FIELDS,
    SELECTORS,
)
from shared.exceptions import (
    AuthenticationError,
    BlockedOrCaptchaError,
    InvalidInputError,
    NetworkError,
    ParsingError,
)
from shared.human_behavior import human_delay
from shared.rate_limit import FileRateLimiter, RateLimiter
from shared.retry import async_retry
from shared.schema import empty_row

logger = logging.getLogger("sdip.scrapers.linkedin")


class LinkedInScraper(BaseScraper):
    scraper_type = "linkedin"

    def __init__(
        self,
        job_id: str | None = None,
        rate_limiter: RateLimiter | None = None,
        daily_limit: int = DEFAULT_DAILY_LIMIT,
    ):
        super().__init__(job_id=job_id)
        # Dependency-injected so the backend team can swap in a DB-backed
        # limiter later without touching this scraper (minimal wiring goal).
        self.rate_limiter = rate_limiter or FileRateLimiter(daily_limit=daily_limit)

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        missing = [f for f in REQUIRED_INPUT_FIELDS if not params.get(f)]
        if missing:
            raise InvalidInputError(
                f"Missing required field(s): {', '.join(missing)}",
                details={"missing_fields": missing},
            )

        auth = params.get("auth") or {}
        if not auth.get("session_cookie") and not params.get("fixture_html"):
            # fixture_html bypasses auth entirely for offline/dev testing
            raise AuthenticationError(
                "No LinkedIn session provided. The end user must connect "
                "their LinkedIn account (session cookie) before this "
                "scraper can run.",
            )

        # account_id is required whenever we're not in fixture/test mode --
        # silently defaulting it would let unrelated jobs share one rate
        # bucket, defeating the per-account daily cap (FR-1.9).
        if not auth.get("account_id") and not params.get("fixture_html"):
            raise InvalidInputError(
                "Missing auth.account_id. This is required to enforce the "
                "per-account daily scrape limit and cannot be defaulted.",
            )

        return {
            "keywords": params["keywords"].strip(),
            "location": params["location"].strip(),
            "industry": params["industry"].strip(),
            "company_size": params["company_size"].strip(),
            "auth": auth,
            "account_id": auth.get("account_id") or "fixture_test_account",
            "fixture_html": params.get("fixture_html"),
        }

    # ------------------------------------------------------------------ #
    # Scrape
    # ------------------------------------------------------------------ #
    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        # Enforce daily cap per connected account (FR-1.9) before doing
        # any actual work.
        self.rate_limiter.check_and_increment(
            account_id=params["account_id"], scraper_type=self.scraper_type
        )

        if params.get("fixture_html"):
            # Test/dev mode: parse a saved HTML fixture, no browser needed.
            html = params["fixture_html"]
        else:
            html = await self._fetch_live_html(params)

        return self._parse_results(html)

    @async_retry(max_attempts=3, retry_on=(NetworkError,))
    async def _fetch_live_html(self, params: dict[str, Any]) -> str:
        """Launch Playwright, authenticate with the user's session cookie,
        run the search, and return the rendered page HTML.

        Kept separate from `scrape()` so it can be retried independently
        and so `scrape()`'s control flow (rate limit -> fetch -> parse)
        stays easy to read.
        """
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise NetworkError(
                "Playwright is not installed. Run `playwright install` "
                "after `pip install -r requirements.txt`."
            ) from exc

        query = (
            f"{LINKEDIN_SEARCH_URL}?keywords={params['keywords']}"
            f"&location={params['location']}"
        )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                await context.add_cookies(
                    [
                        {
                            "name": "li_at",
                            "value": params["auth"]["session_cookie"],
                            "domain": ".linkedin.com",
                            "path": "/",
                        }
                    ]
                )
                page = await context.new_page()

                await human_delay(1.0, 2.5)
                await page.goto(query, timeout=30000)
                await human_delay(2.0, 4.0)  # let the page settle like a human would

                content = await page.content()
                await browser.close()
                return content

        except PlaywrightTimeoutError as exc:
            raise NetworkError(f"Timed out loading LinkedIn search: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise NetworkError(f"Failed to load LinkedIn search page: {exc}") from exc

    def _parse_results(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")

        if soup.select_one(SELECTORS["captcha_indicator"]):
            raise BlockedOrCaptchaError(
                "LinkedIn presented a CAPTCHA/challenge page. Full CAPTCHA "
                "handling is Week 3 scope -- failing this job cleanly for now."
            )

        cards = soup.select(SELECTORS["result_card"])
        if not cards:
            # Not necessarily an error -- could just be zero results. We only
            # treat total absence of the expected page structure as a
            # ParsingError if there's also no obvious "no results" signal.
            # For Week 1, keep this simple and just return an empty list.
            logger.info("No result cards found for query -- returning empty results.")
            return []

        rows = []
        for card in cards:
            row = empty_row(self.scraper_type)
            try:
                name_el = card.select_one(SELECTORS["name"])
                position_el = card.select_one(SELECTORS["position"])
                company_el = card.select_one(SELECTORS["company"])
                link_el = card.select_one(SELECTORS["profile_link"])

                row["name"] = name_el.get_text(strip=True) if name_el else None
                row["position"] = position_el.get_text(strip=True) if position_el else None
                row["company"] = company_el.get_text(strip=True) if company_el else None
                row["profile_url"] = link_el.get("href") if link_el else None
                # email/website are not available from search results directly;
                # left as None here. A future enhancement could visit each
                # profile individually, at the cost of far more requests/risk.
            except Exception as exc:  # noqa: BLE001
                raise ParsingError(
                    f"Failed to parse a LinkedIn result card: {exc}"
                ) from exc

            rows.append(row)

        return rows
