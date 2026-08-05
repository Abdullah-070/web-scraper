"""
Facebook scraper configuration.

Input:  business_page (a Facebook Page URL or handle)
Output: contact_info, website, phone

"""

from __future__ import annotations

REQUIRED_INPUT_FIELDS = ["business_page"]

FACEBOOK_BASE_URL = "https://www.facebook.com/"

# Facebook's "About" tab exposes contact info -- selectors kept generic
# and centralized here so a markup change means editing one file.
SELECTORS = {
    "about_contact_block": '[data-testid="page_about_contact_and_basic_info"]',
    "phone": 'a[href^="tel:"]',
    "website_link": 'a[href^="http"]:not([href*="facebook.com"])',
    "contact_text_blocks": "span",
    # Facebook-specific challenge/checkpoint indicators, passed as extra
    # site_selectors to the shared shared.captcha_detection utility.
    "captcha_indicators": ["#checkpointSubmitButton", ".captcha_body"],
}
