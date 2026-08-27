"""
Website scraper configuration (FR-2.2).

Input:  website_url
Output: emails, phone_numbers, social_links, technologies_used

"""

from __future__ import annotations

import os

from shared.text_patterns import EMAIL_REGEX, PHONE_REGEX  # noqa: F401

SOCIAL_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "tiktok.com",
]


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

CONTACT_PAGE_KEYWORDS = ["contact", "about", "support"]

FALLBACK_CONTACT_PATHS = ["/contact", "/contact-us"]

MAX_CONTACT_PAGES_TO_FETCH = int(os.environ.get("WEBSITE_MAX_CONTACT_PAGES", "3"))


ENABLE_JS_RENDER_FALLBACK = (
    os.environ.get("WEBSITE_ENABLE_JS_RENDER_FALLBACK", "true").lower() == "true"
)
JS_FRAMEWORK_SIGNATURES = ["react", "__next_data__", "vue", "ng-version", "__nuxt"]
