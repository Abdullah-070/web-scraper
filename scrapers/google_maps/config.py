"""
Google Maps scraper configuration 

Inputs:  business_type, city, country
Outputs: business_name, phone, email, website, address, rating, reviews


"""

from __future__ import annotations

import os

REQUIRED_INPUT_FIELDS = ["business_type", "city", "country"]

GOOGLE_MAPS_SEARCH_URL = "https://www.google.com/maps/search/"


SELECTORS = {
    "results_panel": 'div[role="feed"]',
    "result_card": 'div[role="feed"] > div > div[jsaction]',
    "name": ".fontHeadlineSmall",
    "rating": 'span[role="img"]',
    "address_or_category": ".fontBodyMedium",
    "website_link": 'a[data-value="Website"]',

    "phone_button": 'button[data-item-id^="phone:"]',

    "detail_panel_title": 'h1.DUwDvf, h1[class*="fontHeadlineLarge"]',
    "captcha_indicators": ["#recaptcha", ".g-recaptcha"],
}


DETAIL_PANEL_POLL_ATTEMPTS = 6
DETAIL_PANEL_POLL_DELAY_MS = 500


MAX_SCROLL_ITERATIONS = int(os.environ.get("GOOGLE_MAPS_MAX_SCROLL_ITERATIONS", "6"))


DEFAULT_MAX_RESULTS = int(os.environ.get("GOOGLE_MAPS_DEFAULT_MAX_RESULTS", "20"))

DEFAULT_REQUIRE_CONTACT_INFO = False