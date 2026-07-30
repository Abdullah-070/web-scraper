"""
Instagram scraper configuration .

Input:  username
Output: followers, bio, website, email

"""

from __future__ import annotations

INSTAGRAM_BASE_URL = "https://www.instagram.com/"

REQUIRED_INPUT_FIELDS = ["username"]

SELECTORS = {
    "bio": 'meta[name="description"]',
    "followers_meta": 'meta[property="og:description"]',
    "website_link": 'a[rel="me"]',
    "captcha_indicators": ["#slfErrorAlert", ".challenge-page"],
}
