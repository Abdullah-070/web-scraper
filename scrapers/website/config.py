"""
Website scraper configuration (FR-2.2).

Input:  website_url
Output: emails, phone_numbers, social_links, technologies_used

Unlike LinkedIn/Google Maps, this scraper doesn't search anything -- it
fetches one given URL directly and extracts contact info + tech signals
from the page. Plain `requests` is sufficient for most sites (no JS
rendering needed for basic contact scraping); Playwright is not used here
to keep this scraper lightweight, per NFR-2.1's expectation that
malformed/unreachable URLs are handled gracefully rather than needing a
full browser stack.
"""

from __future__ import annotations

import re

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Deliberately conservative: matches common phone formats without being so
# loose it picks up unrelated numbers (e.g. dates, prices) from the page.
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
)

SOCIAL_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "tiktok.com",
]

# Lightweight technology fingerprints based on markup/response signals.
# Not exhaustive -- a real "Technologies Used" detector (e.g. Wappalyzer)
# is a much bigger undertaking; this is a reasonable Week 2 starting point
# that can be swapped out later without changing the scraper's interface.
TECH_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes"],
    "Shopify": ["cdn.shopify.com", "shopify"],
    "Wix": ["wix.com", "wixstatic.com"],
    "Squarespace": ["squarespace.com"],
    "React": ["__next_data__", "react"],
    "Google Analytics": ["google-analytics.com", "gtag("],
    "Google Tag Manager": ["googletagmanager.com"],
}

REQUEST_TIMEOUT_SECONDS = 15
