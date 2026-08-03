"""
Facebook Scraper.

Input:  business_page
Output: contact_info, website, phone

"""

from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.facebook.config import (
    FACEBOOK_BASE_URL,
    SELECTORS,
)
from shared.captcha_detection import check_for_block_or_captcha
from shared.exceptions import NetworkError, ParsingError
from shared.human_behavior import human_delay
from shared.proxy_pool import ProxyPool, default_proxy_pool
from shared.retry import async_retry
from shared.schema import empty_row
from shared.validation import require_str

logger = logging.getLogger("sdip.scrapers.facebook")


class FacebookScraper(BaseScraper):
    scraper_type = "facebook"

    def __init__(self, job_id: str | None = None, proxy_pool: ProxyPool | None = None):
        super().__init__(job_id=job_id)
        self.proxy_pool = proxy_pool or default_proxy_pool

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "business_page": require_str(params, "business_page"),
            "fixture_html": params.get("fixture_html"),
        }

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

        page_handle = params["business_page"]
        url = page_handle if page_handle.startswith("http") else f"{FACEBOOK_BASE_URL}{page_handle}/about"

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
            raise NetworkError(f"Timed out loading Facebook page: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise NetworkError(f"Failed to load Facebook page: {exc}") from exc

    def _parse_page(self, html: str) -> dict[str, Any]:
        row = empty_row(self.scraper_type)
        soup = BeautifulSoup(html, "html.parser")

        check_for_block_or_captcha(
            soup, site_selectors=SELECTORS["captcha_indicators"]
        )

        try:
            phone_el = soup.select_one(SELECTORS["phone"])
            website_el = soup.select_one(SELECTORS["website_link"])
            about_block = soup.select_one(SELECTORS["about_contact_block"])

            row["phone"] = (
                phone_el.get("href", "").replace("tel:", "") if phone_el else None
            )
            row["website"] = website_el.get("href") if website_el else None
            row["contact_info"] = (
                about_block.get_text(" ", strip=True) if about_block else None
            )
        except Exception as exc:  # noqa: BLE001
            raise ParsingError(f"Failed to parse Facebook page: {exc}") from exc

        return row
