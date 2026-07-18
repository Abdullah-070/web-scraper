"""
LinkedIn scraper configuration and input contract.

Auth model (per mentor decision, Week 1):
- No LinkedIn partner API, no third-party impersonation library.
- The END USER connects their own LinkedIn account through the platform
  (Settings > API Keys pattern, Sec 2.7). This scraper NEVER uses a
  developer/personal account for testing -- only a designated test
  account/fixtures provided separately.
- Credentials arrive as a session cookie string (`li_at` value) passed in
  at runtime via `raw_params["auth"]["session_cookie"]`. This scraper does
  not store credentials -- storage/encryption is the backend's job
  (Intern 2); this module only consumes what it's given for the duration
  of a single job run.
"""

from __future__ import annotations

REQUIRED_INPUT_FIELDS = ["keywords", "location", "industry", "company_size"]

# Daily cap per connected account, per FR-1.9. Kept low and configurable --
# tune based on real-world ban-risk observations once live.
DEFAULT_DAILY_LIMIT = 50

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
