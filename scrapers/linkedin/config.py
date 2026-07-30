"""
LinkedIn scraper configuration and input contract.

Auth model :
- No LinkedIn partner API, no third-party impersonation library.
- This scraper NEVER uses a developer/personal account for testing 
- This scraper does not store credentials
"""

from __future__ import annotations

import os

REQUIRED_INPUT_FIELDS = ["keywords", "location", "industry", "company_size"]

DEFAULT_DAILY_LIMIT = int(os.environ.get("LINKEDIN_DAILY_LIMIT", "50"))

LINKEDIN_SEARCH_URL = "https://www.linkedin.com/search/results/people/"

# Selectors are centralized here so a future LinkedIn layout change means
# editing one file, not hunting through scrape logic.
SELECTORS = {
    "result_card": "li.reusable-search__result-container",
    "name": ".entity-result__title-text a span[aria-hidden='true']",
    "position": ".entity-result__primary-subtitle",
    "company": ".entity-result__secondary-subtitle",
    "profile_link": ".entity-result__title-text a",
    "captcha_indicator": "#captcha-internal, .challenge-page",
}