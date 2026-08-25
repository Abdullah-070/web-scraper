"""
Facebook Scraper (FR-3.1).

Input:  business_page
Output: contact_info, website, phone


"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.facebook.config import (
    FACEBOOK_BASE_URL,
    FACEBOOK_OWN_DOMAINS,
    OTHER_SOCIAL_DOMAINS,
    SELECTORS,
)
from shared.captcha_detection import check_for_block_or_captcha
from shared.exceptions import NetworkError, ParsingError
from shared.human_behavior import human_delay
from shared.proxy_pool import ProxyPool, default_proxy_pool
from shared.retry import async_retry
from shared.schema import empty_row
from shared.text_patterns import PHONE_REGEX
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

            meta_el = soup.select_one(SELECTORS["meta_description"])
            meta_content = meta_el.get("content", "") if meta_el else ""
            row["contact_info"] = meta_content or None

            page_text = soup.get_text(" ", strip=True)
            tel_link = soup.select_one('a[href^="tel:"]')
            if tel_link:
                row["phone"] = tel_link.get("href", "").replace("tel:", "") or None
            else:

                phone_match = PHONE_REGEX.search(meta_content) or PHONE_REGEX.search(
                    page_text
                )
                row["phone"] = phone_match.group(0) if phone_match else None

            excluded_domains = FACEBOOK_OWN_DOMAINS + OTHER_SOCIAL_DOMAINS
            for link in soup.select(SELECTORS["all_links"]):
                href = link.get("href", "")
                if not href.startswith("http"):
                    continue

                if "l.facebook.com/l.php" in href or "lm.facebook.com/l.php" in href:
                    qs = parse_qs(urlparse(href).query)
                    real_url = qs.get("u", [None])[0]
                    if real_url and not any(d in real_url for d in excluded_domains):
                        row["website"] = unquote(real_url)
                        break
                    continue

                if not any(domain in href for domain in excluded_domains):
                    row["website"] = href
                    break
        except Exception as exc:  # noqa: BLE001
            raise ParsingError(f"Failed to parse Facebook page: {exc}") from exc

        return row
