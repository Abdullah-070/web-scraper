"""
Website Scraper 

Input:  website_url
Output: emails, phone_numbers, social_links, technologies_used

"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.website.config import (
    CONTACT_PAGE_KEYWORDS,
    EMAIL_REGEX,
    FALLBACK_CONTACT_PATHS,
    MAX_CONTACT_PAGES_TO_FETCH,
    PHONE_REGEX,
    REQUEST_TIMEOUT_SECONDS,
    SOCIAL_DOMAINS,
    TECH_SIGNATURES,
)
from shared.exceptions import InvalidInputError, NetworkError
from shared.human_behavior import human_delay
from shared.retry import async_retry
from shared.schema import empty_row
from shared.validation import require_str

logger = logging.getLogger("sdip.scrapers.website")


class WebsiteScraper(BaseScraper):
    scraper_type = "website"

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        url = require_str(params, "website_url")

        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain_pattern = re.compile(
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
        )
        if not parsed.netloc or not domain_pattern.match(parsed.netloc.split(":")[0]):
            raise InvalidInputError(
                f"'{url}' is not a valid URL.", details={"website_url": url}
            )

        return {"website_url": parsed.geturl()}

    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        base_url = params["website_url"]
        html, headers = await self._fetch_page(base_url)
        row = self._parse_page(html, headers)

        for contact_url in self._find_contact_urls(html, base_url):
            try:
                c_html, c_headers = await self._fetch_page(contact_url)
                c_row = self._parse_page(c_html, c_headers)
                row = self._merge_rows(row, c_row)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Contact page fetch failed for %s: %s", contact_url, exc)
                continue

        return [row]

    def _find_contact_urls(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        found = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            link_text = a.get_text(" ", strip=True).lower()
            if any(kw in href.lower() or kw in link_text for kw in CONTACT_PAGE_KEYWORDS):
                absolute = urljoin(base_url, href)
                if absolute not in found and not absolute.startswith(("mailto:", "tel:")):
                    found.append(absolute)

        if not found:
            found = [urljoin(base_url, path) for path in FALLBACK_CONTACT_PATHS]

        return found[:MAX_CONTACT_PAGES_TO_FETCH]

    @staticmethod
    def _merge_rows(main: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
        merged = dict(main)
        for field in ("emails", "phone_numbers", "social_links", "technologies_used"):
            combined = set(main.get(field) or []) | set(extra.get(field) or [])
            merged[field] = sorted(combined) or None
        return merged

    @async_retry(max_attempts=3, retry_on=(NetworkError,))
    async def _fetch_page(self, url: str) -> tuple[str, dict[str, str]]:
        await human_delay(0.5, 1.5)

        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers={"User-Agent": "Mozilla/5.0 (SDIP Website Scraper)"},
            )
        except requests.exceptions.Timeout as exc:
            raise NetworkError(f"Timed out fetching {url}: {exc}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(f"Could not connect to {url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Failed to fetch {url}: {exc}") from exc

        if response.status_code >= 400:
            raise NetworkError(
                f"{url} returned HTTP {response.status_code}",
                details={"status_code": response.status_code},
            )

        return response.text, dict(response.headers)

    def _parse_page(self, html: str, headers: dict[str, str]) -> dict[str, Any]:
        row = empty_row(self.scraper_type)
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text(" ", strip=True)
        page_source_lower = html.lower()

        mailto_emails = {
            a["href"].replace("mailto:", "").split("?")[0]
            for a in soup.find_all("a", href=True)
            if a["href"].lower().startswith("mailto:")
        }
        tel_phones = {
            a["href"].replace("tel:", "")
            for a in soup.find_all("a", href=True)
            if a["href"].lower().startswith("tel:")
        }

        text_emails = set(EMAIL_REGEX.findall(text_content))
        row["emails"] = sorted(mailto_emails | text_emails) or None

        text_phones = set(PHONE_REGEX.findall(text_content))
        phones = tel_phones | {p for p in text_phones if len(re_digits(p)) >= 7}
        row["phone_numbers"] = sorted(phones) or None

        social_links = [
            a["href"]
            for a in soup.find_all("a", href=True)
            if any(domain in a["href"] for domain in SOCIAL_DOMAINS)
        ]
        row["social_links"] = sorted(set(social_links)) or None

        server_header = headers.get("Server", "") + headers.get("X-Powered-By", "")
        combined_signal = page_source_lower + server_header.lower()
        technologies = [
            name for name, sigs in TECH_SIGNATURES.items()
            if any(sig in combined_signal for sig in sigs)
        ]
        row["technologies_used"] = technologies or None

        return row


def re_digits(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())