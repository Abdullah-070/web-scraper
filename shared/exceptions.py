"""
Shared exception taxonomy for all SDIP scrapers.

"""


class ScraperError(Exception):
    """Base class for all scraper errors. Do not raise this directly."""

    error_type = "unknown_error"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "details": self.details,
        }


class InvalidInputError(ScraperError):
    """Raised when input params fail validation before a job is even queued."""

    error_type = "invalid_input"


class AuthenticationError(ScraperError):
    """Raised when user-supplied credentials/session are missing, expired, or rejected."""

    error_type = "authentication_error"


class RateLimitExceededError(ScraperError):
    """Raised when the daily/hourly scrape cap for this account has been reached."""

    error_type = "rate_limit_exceeded"


class BlockedOrCaptchaError(ScraperError):
    """Raised when the target site blocks the request or presents a CAPTCHA wall.

    Week 1 scope: detect and fail cleanly.
    Week 3 scope: this is where proxy rotation / CAPTCHA solving hooks in.
    """

    error_type = "blocked_or_captcha"


class NetworkError(ScraperError):
    """Raised for timeouts, connection resets, DNS failures, etc. Retryable."""

    error_type = "network_error"


class ParsingError(ScraperError):
    """Raised when the page loads but expected data/selectors aren't found
    (e.g. the target site changed its layout)."""

    error_type = "parsing_error"
