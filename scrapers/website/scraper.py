"""
Website Scraper (FR-2.2).

Input:  website_url
Output: emails, phone_numbers, social_links, technologies_used

Week 2 scope:
- Full BaseScraper compliance.
- Uses plain `requests` (not Playwright) -- this scraper doesn't need JS
  rendering for the vast majority of contact-info extraction, and staying
  lightweight means it can run many more jobs per minute than the
  browser-based scrapers.
- Handles malformed/unreachable URLs gracefully (NFR-2.1): invalid URL
  format -> InvalidInputError (caught before any request is attempted);
  connection/timeout/DNS failures -> NetworkError (retryable);
  non-2xx responses -> NetworkError as well, since a 404/500 is still a
  "couldn't get the page" outcome, not a parsing problem.
- Respects a short per-request delay (NFR-2.3) -- less relevant for a
  single-URL fetch than for LinkedIn/Google Maps search scraping, but
  kept for consistency and to avoid hammering a URL on retry.

This scraper does NOT accept a `fixture_html` bypass the way LinkedIn and
Google Maps do, since there's no live-network auth/ban risk here to avoid
during testing -- instead, tests monkeypatch `requests.get` directly.
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from scrapers.website.config import (
    EMAIL_REGEX,
    PHONE_REGEX,
    REQUEST_TIMEOUT_SECONDS,
    SOCIAL_DOMAINS,
    TECH_SIGNATURES,
)
from shared.exceptions import InvalidInputError, NetworkError
from shared.human_behavior import human_delay
from shared.retry import async_retry
from shared.schema import empty_row

logger = logging.getLogger("sdip.scrapers.website")


class WebsiteScraper(BaseScraper):
    scraper_type = "website"

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        url = (params.get("website_url") or "").strip()
        if not url:
            raise InvalidInputError(
                "Missing required field: website_url",
                details={"missing_fields": ["website_url"]},
            )

        parsed = urlparse(url if "://" in url else f"https://{url}")
        # urlparse is lenient (e.g. "not a url at all" parses with a
        # space-containing netloc) -- apply a stricter domain-shape check
        # so obviously-invalid input is rejected before any network call
        # is attempted, rather than surfacing as a confusing DNS failure.
        domain_pattern = re.compile(
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
        )
        if not parsed.netloc or not domain_pattern.match(parsed.netloc.split(":")[0]):
            raise InvalidInputError(
                f"'{url}' is not a valid URL.",
                details={"website_url": url},
            )

        return {"website_url": parsed.geturl()}

    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        html, headers = await self._fetch_page(params["website_url"])
        return [self._parse_page(html, headers)]

    @async_retry(max_attempts=3, retry_on=(NetworkError,))
    async def _fetch_page(self, url: str) -> tuple[str, dict[str, str]]:
        await human_delay(0.5, 1.5)  # NFR-2.3 -- brief courtesy delay

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

        emails = sorted(set(EMAIL_REGEX.findall(text_content)))
        row["emails"] = emails or None

        phones = sorted(set(PHONE_REGEX.findall(text_content)))
        # phone regex is broad -- filter out obviously-too-short matches
        phones = [p for p in phones if len(re_digits(p)) >= 7]
        row["phone_numbers"] = phones or None

        social_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(domain in href for domain in SOCIAL_DOMAINS):
                social_links.append(href)
        row["social_links"] = sorted(set(social_links)) or None

        technologies = []
        server_header = headers.get("Server", "") + headers.get("X-Powered-By", "")
        combined_signal = page_source_lower + server_header.lower()
        for tech_name, signatures in TECH_SIGNATURES.items():
            if any(sig in combined_signal for sig in signatures):
                technologies.append(tech_name)
        row["technologies_used"] = technologies or None

        return row


def re_digits(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())
