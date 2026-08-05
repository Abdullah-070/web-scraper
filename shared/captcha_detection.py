"""
Shared CAPTCHA / block-page detection  .

One reusable check that every scraper calls against its fetched page,
instead of each scraper re-implementing its own CAPTCHA-sniffing logic
(NFR-3.1). Detection is intentionally basic for Week 3 scope: recognize
common CAPTCHA/challenge page signals and fail the job cleanly with
BlockedOrCaptchaError -- actually *solving* a CAPTCHA is out of scope.

Combines two signal types:
1. CSS selectors specific to a given site (passed in per-scraper, since
   e.g. LinkedIn's challenge page markup differs from Instagram's).
2. Generic keyword signals that show up across most anti-bot/CAPTCHA
   pages regardless of site (e.g. "unusual traffic", "verify you're human").
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from shared.exceptions import BlockedOrCaptchaError

GENERIC_BLOCK_KEYWORDS = [
    "unusual traffic",
    "verify you're human",
    "verify you are human",
    "are you a robot",
    "captcha",
    "automated queries",
    "temporarily blocked",
    "access denied",
    "checking your browser",
]


def check_for_block_or_captcha(
    soup: BeautifulSoup,
    site_selectors: list[str] | None = None,
    extra_keywords: list[str] | None = None,
) -> None:
    """Raise BlockedOrCaptchaError if the page looks like a CAPTCHA/block
    page.
    """
    for selector in site_selectors or []:
        if soup.select_one(selector):
            raise BlockedOrCaptchaError(
                f"Detected a CAPTCHA/challenge page (matched selector '{selector}')."
            )

    page_text = soup.get_text(" ", strip=True).lower()
    all_keywords = GENERIC_BLOCK_KEYWORDS + (extra_keywords or [])
    for keyword in all_keywords:
        if keyword in page_text:
            raise BlockedOrCaptchaError(
                f"Detected a CAPTCHA/challenge page (matched phrase '{keyword}')."
            )
