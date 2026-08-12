"""
Facebook scraper configuration (FR-3.1).

Input:  business_page (a Facebook Page URL or handle)
Output: contact_info, website, phone

"""

from __future__ import annotations

REQUIRED_INPUT_FIELDS = ["business_page"]

FACEBOOK_BASE_URL = "https://www.facebook.com/"

SELECTORS = {
    
    "meta_description": 'meta[property="og:description"]',
    "all_links": "a[href]",
    
    "captcha_indicators": ["#checkpointSubmitButton", ".captcha_body"],
}

FACEBOOK_OWN_DOMAINS = ["facebook.com", "fbcdn.net", "fb.com", "fb.me"]
