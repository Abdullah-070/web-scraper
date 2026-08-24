"""
Google Maps Scraper (FR-2.1).

Inputs:  business_type, city, country, max_results (optional)
Outputs: business_name, phone, email, website, address, rating, reviews


"""

from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.google_maps.config import (
    DEFAULT_MAX_RESULTS,
    DEFAULT_REQUIRE_CONTACT_INFO,
    DETAIL_PANEL_POLL_ATTEMPTS,
    DETAIL_PANEL_POLL_DELAY_MS,
    GOOGLE_MAPS_SEARCH_URL,
    MAX_SCROLL_ITERATIONS,
    SELECTORS,
)
from shared.captcha_detection import check_for_block_or_captcha
from shared.exceptions import InvalidInputError, NetworkError, ParsingError
from shared.human_behavior import human_delay
from shared.proxy_pool import ProxyPool, default_proxy_pool
from shared.retry import async_retry
from shared.schema import empty_row
from shared.validation import require_str

logger = logging.getLogger("sdip.scrapers.google_maps")


class GoogleMapsScraper(BaseScraper):
    scraper_type = "google_maps"

    def __init__(self, job_id: str | None = None, proxy_pool: ProxyPool | None = None):
        super().__init__(job_id=job_id)

        self.proxy_pool = proxy_pool or default_proxy_pool

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        max_results = params.get("max_results", DEFAULT_MAX_RESULTS)
        try:
            max_results = int(max_results)
        except (TypeError, ValueError):
            raise InvalidInputError(
                f"'max_results' must be an integer, got {max_results!r}",
                details={"max_results": max_results},
            )
        if max_results < 1:
            raise InvalidInputError(
                f"'max_results' must be at least 1, got {max_results}",
                details={"max_results": max_results},
            )

        return {
            "business_type": require_str(params, "business_type"),
            "city": require_str(params, "city"),
            "country": require_str(params, "country"),
            "max_results": max_results,
            "require_contact_info": bool(
                params.get("require_contact_info", DEFAULT_REQUIRE_CONTACT_INFO)
            ),
            "fixture_html": params.get("fixture_html"),
        }

    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        if params.get("fixture_html"):
            html = params["fixture_html"]
            rows = self._parse_results(html)
        else:
            rows = await self._scrape_live(params)

        if params["require_contact_info"]:
            rows = [r for r in rows if r.get("phone") or r.get("website")]

        return rows[: params["max_results"]]

    @async_retry(max_attempts=3, retry_on=(NetworkError,))
    async def _scrape_live(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise NetworkError(
                "Playwright is not installed. Run `playwright install` "
                "after `pip install -r requirements.txt`."
            ) from exc

        query = f"{params['business_type']} in {params['city']}, {params['country']}"
        url = f"{GOOGLE_MAPS_SEARCH_URL}{query.replace(' ', '+')}"

        proxy = self.proxy_pool.get_proxy()
        launch_kwargs = {"headless": True}
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(**launch_kwargs)
                page = await browser.new_page()

                await human_delay(1.0, 2.0)
                await page.goto(url, timeout=30000)
                await human_delay(2.0, 4.0)  # let the results panel render

                block_check_html = await page.content()
                check_for_block_or_captcha(
                    BeautifulSoup(block_check_html, "html.parser"),
                    site_selectors=SELECTORS["captcha_indicators"],
                )

                feed_selector = SELECTORS["results_panel"]
                for _ in range(MAX_SCROLL_ITERATIONS):
                    cards_now = await page.query_selector_all(SELECTORS["result_card"])
                    if len(cards_now) >= params["max_results"]:
                        break
                    await page.evaluate(
                        f"""
                        const feed = document.querySelector('{feed_selector}');
                        if (feed) {{ feed.scrollTop = feed.scrollHeight; }}
                        """
                    )
                    await human_delay(1.0, 2.5)

                cards = await page.query_selector_all(SELECTORS["result_card"])
                cards = cards[: params["max_results"]]

                rows = []
                for card in cards:
                    row = empty_row(self.scraper_type)
                    try:

                        try:
                            await card.wait_for_selector(SELECTORS["name"], timeout=5000)
                        except Exception:  # noqa: BLE001
                            pass

                        name_el = await card.query_selector(SELECTORS["name"])
                        rating_el = await card.query_selector(SELECTORS["rating"])
                        address_el = await card.query_selector(SELECTORS["address_or_category"])

                        row["business_name"] = (
                            (await name_el.inner_text()).strip() if name_el else None
                        )
                        row["address"] = (
                            (await address_el.inner_text()).strip() if address_el else None
                        )
                        if rating_el:
                            aria_label = await rating_el.get_attribute("aria-label") or ""
                            row["rating"], row["reviews"] = self._parse_rating_label(
                                aria_label
                            )


                        await card.click()

                        panel_matched = False
                        for _ in range(DETAIL_PANEL_POLL_ATTEMPTS):
                            title_el = await page.query_selector(
                                SELECTORS["detail_panel_title"]
                            )
                            title_text = (
                                (await title_el.inner_text()).strip() if title_el else ""
                            )
                            if row["business_name"] and title_text == row["business_name"]:
                                panel_matched = True
                                break
                            await page.wait_for_timeout(DETAIL_PANEL_POLL_DELAY_MS)

                        if not panel_matched:
                            logger.warning(
                                "Detail panel never confirmed matching '%s' -- "
                                "skipping phone/website for this row rather "
                                "than risk stale data.",
                                row["business_name"],
                            )
                        else:
                            phone_el = await page.query_selector(SELECTORS["phone_button"])
                            if phone_el:
                                data_item_id = (
                                    await phone_el.get_attribute("data-item-id") or ""
                                )
                                row["phone"] = (
                                    data_item_id.replace("phone:tel:", "") or None
                                )

                            website_el = await page.query_selector(SELECTORS["website_link"])
                            if website_el:
                                row["website"] = await website_el.get_attribute("href")


                    except Exception as exc:  # noqa: BLE001

                        logger.warning(
                            "Partial parse failure on a Google Maps card: %s", exc
                        )

                    rows.append(row)

                await browser.close()
                if proxy:
                    self.proxy_pool.report_success(proxy)
                return rows

        except PlaywrightTimeoutError as exc:
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise NetworkError(f"Timed out loading Google Maps search: {exc}") from exc
        except NetworkError:
            raise
        except Exception as exc:  # noqa: BLE001
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise NetworkError(f"Failed to load Google Maps search page: {exc}") from exc

    def _parse_results(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")


        check_for_block_or_captcha(
            soup, site_selectors=SELECTORS["captcha_indicators"]
        )

        cards = soup.select(SELECTORS["result_card"])

        if not cards:
            logger.info("No result cards found for query -- returning empty results.")
            return []

        rows = []
        for card in cards:
            row = empty_row(self.scraper_type)
            try:
                name_el = card.select_one(SELECTORS["name"])
                rating_el = card.select_one(SELECTORS["rating"])
                address_el = card.select_one(SELECTORS["address_or_category"])
                website_el = card.select_one(SELECTORS["website_link"])
                phone_el = card.select_one(SELECTORS["phone_button"])

                row["business_name"] = name_el.get_text(strip=True) if name_el else None
                row["address"] = address_el.get_text(strip=True) if address_el else None
                row["website"] = website_el.get("href") if website_el else None

                if phone_el:
                    data_item_id = phone_el.get("data-item-id", "")
                    row["phone"] = data_item_id.replace("phone:tel:", "") or None

                if rating_el:
                    aria_label = rating_el.get("aria-label", "")
                    row["rating"], row["reviews"] = self._parse_rating_label(aria_label)

            except Exception as exc:  # noqa: BLE001
                raise ParsingError(
                    f"Failed to parse a Google Maps result card: {exc}"
                ) from exc

            rows.append(row)

        return rows

    @staticmethod
    def _parse_rating_label(aria_label: str) -> tuple[float | None, int | None]:
 
        import re

        rating_match = re.search(r"(\d+(\.\d+)?)\s*(?:stars?|out of 5)", aria_label)
        reviews_match = re.search(
            r"([\d,]+)\s*(?:reviews?)|\(([\d,]+)\)", aria_label, re.IGNORECASE
        )

        rating = float(rating_match.group(1)) if rating_match else None
        reviews = None
        if reviews_match:
            digits = reviews_match.group(1) or reviews_match.group(2)
            reviews = int(digits.replace(",", "")) if digits else None
        return rating, reviews
