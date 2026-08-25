"""
Google Maps Scraper (FR-2.1).

Inputs:  business_type, city, country, max_results (optional)
Outputs: business_name, phone, email, website, address, rating, reviews


"""

from __future__ import annotations

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.google_maps.config import (
    DEFAULT_MAX_RESULTS,
    DEFAULT_REQUIRE_CONTACT_INFO,
    GOOGLE_MAPS_SEARCH_URL,
    MAX_SCROLL_ITERATIONS,
    REVIEWS_TEXT_PATTERN,
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

    PHONE_TEXT_PATTERN = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
    RATING_REVIEWS_INLINE_PATTERN = re.compile(
        r"(\d+(?:\.\d+)?)\s*\((\d[\d,]*)\)", re.IGNORECASE
    )
    DETAIL_REVIEW_SUMMARY_PATTERN = re.compile(
        r"Review summary[\s\S]{0,250}?([\d,]+(?:\.\d+)?)([KMkm]?)\s+reviews?",
        re.IGNORECASE,
    )
    GENERIC_REVIEWS_PATTERN = re.compile(
        r"\b([\d,]+(?:\.\d+)?)([KMkm]?)\s+reviews?\b", re.IGNORECASE
    )

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

        url = f"{GOOGLE_MAPS_SEARCH_URL}{query.replace(' ', '+')}?hl=en"

        proxy = self.proxy_pool.get_proxy()
        launch_kwargs = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--lang=en-US,en",
            ],
        }
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(**launch_kwargs)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                    ),
                    locale="en-US",
                    viewport={"width": 1366, "height": 900},
                )
                page = await context.new_page()

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
                        address_el = await card.query_selector(SELECTORS["address_or_category"])
                        rating_el = await card.query_selector(SELECTORS["rating"])
                        website_el = await card.query_selector(SELECTORS["website_link"])

                        card_text = (await card.inner_text()) if card else ""

                        row["business_name"] = (
                            (await name_el.inner_text()).strip() if name_el else None
                        )

                        if not row["business_name"]:
                            logger.info(
                                "Skipping a matched card with no business name "
                                "(likely a non-listing element, not a real result)."
                            )
                            continue

                        row["address"] = (
                            (await address_el.inner_text()).strip() if address_el else None
                        )

                        if website_el:
                            row["website"] = await website_el.get_attribute("href")

                        if rating_el:
                            aria_label = await rating_el.get_attribute("aria-label") or ""
                            row["rating"], row["reviews"] = self._parse_rating_label(aria_label)

                        if row["rating"] is None or row["reviews"] is None:
                            fallback_rating, fallback_reviews = (
                                self._parse_rating_reviews_from_card_text(card_text)
                            )
                            if row["rating"] is None:
                                row["rating"] = fallback_rating
                            if row["reviews"] is None:
                                row["reviews"] = fallback_reviews

                        row["phone"] = self._extract_phone_from_text(card_text)

                        await card.click()
                        detail_text = await self._extract_detail_panel_text(
                            page, row["business_name"]
                        )
                        if detail_text:
                            if row["reviews"] is None:
                                row["reviews"] = self._parse_reviews_from_detail_text(
                                    detail_text
                                )
                        if row["reviews"] is None:
                            full_text = await page.inner_text("body")
                            row["reviews"] = self._parse_reviews_from_detail_text(full_text)

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
                row["business_name"] = name_el.get_text(strip=True) if name_el else None

                if not row["business_name"]:
                    logger.info(
                        "Skipping a matched card with no business name "
                        "(likely a non-listing element, not a real result)."
                    )
                    continue

                rating_el = card.select_one(SELECTORS["rating"])
                address_el = card.select_one(SELECTORS["address_or_category"])
                website_el = card.select_one(SELECTORS["website_link"])
                phone_el = card.select_one(SELECTORS["phone_button"])

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
    def _parse_review_count(match: "re.Match") -> int | None:
        
        number_str, suffix = match.group(1), match.group(2)
        if not number_str:
            return None
        number = float(number_str.replace(",", ""))
        if suffix:
            if suffix.upper() == "K":
                number *= 1_000
            elif suffix.upper() == "M":
                number *= 1_000_000
        return int(number)

    @classmethod
    def _extract_phone_from_text(cls, text: str | None) -> str | None:
        if not text:
            return None
        match = cls.PHONE_TEXT_PATTERN.search(text)
        return match.group(1).strip() if match else None

    @classmethod
    def _parse_rating_reviews_from_card_text(
        cls, text: str | None
    ) -> tuple[float | None, int | None]:
        if not text:
            return None, None
        match = cls.RATING_REVIEWS_INLINE_PATTERN.search(text)
        if not match:
            return None, None
        rating = float(match.group(1))
        reviews = int(match.group(2).replace(",", ""))
        return rating, reviews

    @staticmethod
    def _parse_compact_count(number_str: str, suffix: str) -> int:
        number = float(number_str.replace(",", ""))
        if suffix:
            suffix = suffix.upper()
            if suffix == "K":
                number *= 1_000
            elif suffix == "M":
                number *= 1_000_000
        return int(number)

    @classmethod
    def _parse_reviews_from_detail_text(cls, text: str | None) -> int | None:
        if not text:
            return None

        summary_match = cls.DETAIL_REVIEW_SUMMARY_PATTERN.search(text)
        if summary_match:
            return cls._parse_compact_count(
                summary_match.group(1), summary_match.group(2) or ""
            )

        generic_match = cls.GENERIC_REVIEWS_PATTERN.search(text)
        if generic_match:
            return cls._parse_compact_count(
                generic_match.group(1), generic_match.group(2) or ""
            )

        return None

    @staticmethod
    async def _extract_detail_panel_text(page, business_name: str | None) -> str:
        panel_text = ""
        for _ in range(6):
            panel = await page.query_selector(SELECTORS["detail_panel_container"])
            if panel is None:
                await page.wait_for_timeout(500)
                continue

            panel_text = await panel.inner_text()
            panel_aria_label = (await panel.get_attribute("aria-label") or "").strip()

            if business_name and panel_aria_label.lower() == business_name.lower():
                return panel_text

            await page.wait_for_timeout(500)

        return panel_text

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
