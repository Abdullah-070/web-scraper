"""
Google Maps scraper configuration.

Inputs:  business_type, city, country
Outputs: business_name, phone, email, website, address, rating, reviews

"""

from __future__ import annotations

import os

REQUIRED_INPUT_FIELDS = ["business_type", "city", "country"]

GOOGLE_MAPS_SEARCH_URL = "https://www.google.com/maps/search/"

# Google Maps loads results via infinite scroll inside a side panel, not
# normal pagination links (NFR-2.2). Selectors centralized here so a
# layout change means editing one file, not hunting through scrape logic.
SELECTORS = {
    "results_panel": 'div[role="feed"]',
    "result_card": 'div[role="feed"] > div > div[jsaction]',
    "name": ".fontHeadlineSmall",
    "rating": 'span[role="img"]',
    "address_or_category": ".fontBodyMedium",
    "website_link": 'a[data-value="Website"]',
    "phone_button": 'button[data-item-id^="phone:"]',
}

# How many times to scroll the results feed to load more listings before
# stopping (bounds runtime -- Google Maps will keep loading more forever
# otherwise). Externalized via env var so it can be tuned in deployment
# without a code change.
MAX_SCROLL_ITERATIONS = int(os.environ.get("GOOGLE_MAPS_MAX_SCROLL_ITERATIONS", "6"))