"""
Google Maps Scraper (FR-2.1).

Inputs:  business_type, city, country
Outputs: business_name, phone, email, website, address, rating, reviews

Week 2 scope:
- Full BaseScraper compliance (validate_input/scrape/format_output all
  inherited/implemented per the framework from Week 1).
- No auth needed (public search results) -- unlike LinkedIn, there's no
  per-account daily cap here.
- Handles Google Maps' scroll-to-load-more results panel (NFR-2.2) by
  scrolling a bounded number of times rather than assuming all results
  are present on first load.
- Randomized delays between scroll/navigation actions (NFR-2.3).
- Email is not directly exposed by Google Maps listings -- left as None
  (would require visiting the business's own website, which is exactly
  what the separate Website Scraper is for).

Testing note: supports a `fixture_html` param, same pattern as the
LinkedIn scraper, so this can be fully tested without hitting live
Google Maps.
"""

from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.google_maps.config import (
    GOOGLE_MAPS_SEARCH_URL,
    MAX_SCROLL_ITERATIONS,
    REQUIRED_INPUT_FIELDS,
    SELECTORS,
)
from shared.exceptions import InvalidInputError, NetworkError, ParsingError
from shared.human_behavior import human_delay
from shared.retry import async_retry
from shared.schema import empty_row

logger = logging.getLogger("sdip.scrapers.google_maps")


class GoogleMapsScraper(BaseScraper):
    scraper_type = "google_maps"

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        missing = [f for f in REQUIRED_INPUT_FIELDS if not params.get(f)]
        if missing:
            raise InvalidInputError(
                f"Missing required field(s): {', '.join(missing)}",
                details={"missing_fields": missing},
            )

        return {
            "business_type": params["business_type"].strip(),
            "city": params["city"].strip(),
            "country": params["country"].strip(),
            "fixture_html": params.get("fixture_html"),
        }

    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        if params.get("fixture_html"):
            html = params["fixture_html"]
        else:
            html = await self._fetch_live_html(params)

        return self._parse_results(html)

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

        query = f"{params['business_type']} in {params['city']}, {params['country']}"
        url = f"{GOOGLE_MAPS_SEARCH_URL}{query.replace(' ', '+')}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await human_delay(1.0, 2.0)
                await page.goto(url, timeout=30000)
                await human_delay(2.0, 4.0)  # let the results panel render

                # Google Maps loads more listings as the results feed is
                # scrolled (NFR-2.2) -- scroll a bounded number of times
                # rather than assuming everything loads up front.
                feed_selector = SELECTORS["results_panel"]
                for _ in range(MAX_SCROLL_ITERATIONS):
                    await page.evaluate(
                        f"""
                        const feed = document.querySelector('{feed_selector}');
                        if (feed) {{ feed.scrollTop = feed.scrollHeight; }}
                        """
                    )
                    await human_delay(1.0, 2.5)

                content = await page.content()
                await browser.close()
                return content

        except PlaywrightTimeoutError as exc:
            raise NetworkError(f"Timed out loading Google Maps search: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise NetworkError(f"Failed to load Google Maps search page: {exc}") from exc

    def _parse_results(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
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

                # email is not exposed directly by Google Maps listings --
                # left as None; the Website Scraper module fills this gap.
            except Exception as exc:  # noqa: BLE001
                raise ParsingError(
                    f"Failed to parse a Google Maps result card: {exc}"
                ) from exc

            rows.append(row)

        return rows

    @staticmethod
    def _parse_rating_label(aria_label: str) -> tuple[float | None, int | None]:
        """Parse an aria-label like '4.5 stars 123 Reviews' into (4.5, 123)."""
        import re

        rating_match = re.search(r"(\d+(\.\d+)?)\s*stars?", aria_label)
        reviews_match = re.search(r"([\d,]+)\s*[Rr]eviews?", aria_label)

        rating = float(rating_match.group(1)) if rating_match else None
        reviews = int(reviews_match.group(1).replace(",", "")) if reviews_match else None
        return rating, reviews
