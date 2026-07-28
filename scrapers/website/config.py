"""
Website scraper configuration.

Input:  website_url
Output: emails, phone_numbers, social_links, technologies_used

"""

from __future__ import annotations

import os
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

REQUEST_TIMEOUT_SECONDS = int(os.environ.get("WEBSITE_SCRAPER_TIMEOUT_SECONDS", "15"))