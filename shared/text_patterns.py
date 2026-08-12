"""
Shared text-extraction regex patterns.

Factored out so scrapers that both need to pull an email/phone out of
raw page text 
"""

from __future__ import annotations

import re

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE
)

# Handles: +92 51 1234 5678, (555) 123-4567, +1-555-123-4567,
# 020 7946 0958, +44 20 7946 0958, extensions (ext./x 123)
PHONE_REGEX = re.compile(
    r"(?:\+\d{1,3}[-.\s]?)?"
    r"(?:\(\d{1,4}\)[-.\s]?)?"
    r"\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}(?:[-.\s]?\d{1,4})?"
    r"(?:\s?(?:ext\.?|x)\s?\d{1,5})?",
    re.IGNORECASE,
)
