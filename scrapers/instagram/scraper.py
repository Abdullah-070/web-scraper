"""
Instagram Scraper

Input:  username
Output: followers, bio, website, email

"""

from __future__ import annotations

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.instagram.config import (
    INSTAGRAM_BASE_URL,
    REQUIRED_INPUT_FIELDS,
    SELECTORS,
)
from shared.captcha_detection import check_for_block_or_captcha
from shared.exceptions import InvalidInputError, NetworkError, ParsingError
from shared.human_behavior import human_delay
from shared.proxy_pool import ProxyPool, default_proxy_pool
from shared.retry import async_retry
from shared.schema import empty_row
from shared.text_patterns import EMAIL_REGEX

logger = logging.getLogger("sdip.scrapers.instagram")


class InstagramScraper(BaseScraper):
    scraper_type = "instagram"

    def __init__(self, job_id: str | None = None, proxy_pool: ProxyPool | None = None):
        super().__init__(job_id=job_id)
        self.proxy_pool = proxy_pool or default_proxy_pool

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        username = (params.get("username") or "").strip().lstrip("@")
        if not username:
            raise InvalidInputError(
                "Missing required field: username",
                details={"missing_fields": ["username"]},
            )

        return {"username": username, "fixture_html": params.get("fixture_html")}

    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        if params.get("fixture_html"):
            html = params["fixture_html"]
        else:
            html = await self._fetch_live_html(params)

        return [self._parse_page(html)]

    @async_retry(max_attempts=3, retry_on=(NetworkError,))
    async def _fetch_live_html(self, params: dict[str, Any]) -> str:
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise NetworkError(
                "Playwright is not installed. Run `playwright install` "
                "after `pip install -r requirements.txt`."
            ) from exc

        url = f"{INSTAGRAM_BASE_URL}{params['username']}/"

        proxy = self.proxy_pool.get_proxy()
        launch_kwargs = {"headless": True}
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(**launch_kwargs)
                page = await browser.new_page()

                await human_delay(1.5, 3.0)
                await page.goto(url, timeout=30000)
                await human_delay(2.0, 4.0)

                content = await page.content()
                await browser.close()
                if proxy:
                    self.proxy_pool.report_success(proxy)
                return content

        except PlaywrightTimeoutError as exc:
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise NetworkError(f"Timed out loading Instagram profile: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise NetworkError(f"Failed to load Instagram profile: {exc}") from exc

    def _parse_page(self, html: str) -> dict[str, Any]:
        row = empty_row(self.scraper_type)
        soup = BeautifulSoup(html, "html.parser")

        check_for_block_or_captcha(
            soup, site_selectors=SELECTORS["captcha_indicators"]
        )

        try:
            followers_meta = soup.select_one(SELECTORS["followers_meta"])
            bio_meta = soup.select_one(SELECTORS["bio"])
            website_el = soup.select_one(SELECTORS["website_link"])

            bio_text = bio_meta.get("content", "") if bio_meta else ""
            row["bio"] = bio_text or None
            row["website"] = website_el.get("href") if website_el else None

            if followers_meta:
                content = followers_meta.get("content", "")
                row["followers"] = self._parse_followers(content)

            if bio_text:
                email_match = EMAIL_REGEX.search(bio_text)
                row["email"] = email_match.group(0) if email_match else None
        except Exception as exc:  # noqa: BLE001
            raise ParsingError(f"Failed to parse Instagram profile: {exc}") from exc

        return row

    @staticmethod
    def _parse_followers(meta_content: str) -> int | None:
        """Parse a string like '1,234 Followers, 56 Following, 78 Posts...'
        into 1234.
        """
        match = re.search(r"([\d,]+)\s*Followers", meta_content)
        if not match:
            return None
        return int(match.group(1).replace(",", ""))
