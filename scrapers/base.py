"""
Base Scraper Framework (FR-1.1).

Every scraper module (LinkedIn, Google Maps, Website, Facebook, Instagram)
must subclass BaseScraper and implement `validate_input()` and `scrape()`.
A default `format_output()` is provided and rarely needs overriding, but
exists as its own method (not inlined into `run()`) so a scraper can
customize its output envelope if ever needed. This is what lets the queue
worker call any scraper identically (FR-G2),
and what satisfies the modularity principle from the source doc (Sec 1.2):
adding/removing a scraper should never require changes to this base class
or to the worker that calls it (NFR-1.1).

Design note on "minimal wiring later": this class deliberately has no
direct database or HTTP-framework imports. It only returns a plain dict
(see shared.schema.build_result). Whoever wires this to the backend later
just needs to take that dict and pass it to whatever Results/Job API
Intern 2 builds -- no scraper-side changes required.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from shared.exceptions import ScraperError
from shared.schema import build_result

logger = logging.getLogger("sdip.scrapers")


class BaseScraper(ABC):
    """Common interface for all SDIP scraper modules."""

    #: Must be overridden by subclasses, e.g. "linkedin", "google_maps"
    scraper_type: str = "base"

    def __init__(self, job_id: str | None = None):
        self.job_id = job_id

    @abstractmethod
    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize raw input params.

        Must raise shared.exceptions.InvalidInputError if params are
        missing/malformed. Should return the cleaned params dict to use
        for the rest of the run.
        """
        raise NotImplementedError

    @abstractmethod
    async def scrape(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Do the actual scraping. Must return a list of result rows, each
        built from shared.schema.empty_row(self.scraper_type) with fields
        filled in as found (never omit a key -- use None instead).

        Should raise one of shared.exceptions.ScraperError subclasses on
        failure (NetworkError, BlockedOrCaptchaError, ParsingError, etc.)
        rather than letting raw library exceptions propagate.
        """
        raise NotImplementedError

    def format_output(
        self,
        status: str,
        source_query: dict[str, Any],
        results: list[dict[str, Any]] | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build the final standardized envelope for this job (FR-1.1,
        FR-1.6). This is a dedicated hook -- distinct from `scrape()` --
        so subclasses can override it if a given scraper ever needs to
        post-process its envelope (e.g. redact a field) without touching
        `run()`'s control flow. The default implementation just delegates
        to the shared schema builder so every scraper produces an
        identical envelope shape.

        `source_query` must already be a clean, public-safe view of the
        input params -- callers are responsible for stripping anything
        that shouldn't be echoed back (e.g. auth/session data). See
        `_public_source_query()` below, which `run()` uses for this.
        """
        return build_result(
            scraper_type=self.scraper_type,
            status=status,
            source_query=source_query,
            results=results or [],
            errors=errors or [],
            job_id=self.job_id,
        )

    def _public_source_query(self, params: dict[str, Any]) -> dict[str, Any]:
        """Strip fields that should never be echoed back in the output
        envelope (credentials, session data, test-only fixture payloads).
        Subclasses may override to redact additional scraper-specific
        fields, but should always call super() first.
        """
        redacted_keys = {"auth", "fixture_html"}
        return {k: v for k, v in params.items() if k not in redacted_keys}

    async def run(self, raw_params: dict[str, Any]) -> dict[str, Any]:
        """Entry point called by the queue worker (FR-G2). Handles the
        validate -> scrape -> build standardized output flow, and makes
        sure a failure still produces a well-formed envelope rather than
        an unhandled exception reaching the worker.

        This is the ONE method the worker needs to know about, regardless
        of which scraper it's running -- this is the plug-in contract.
        """
        try:
            params = self.validate_input(raw_params)
        except ScraperError as exc:
            logger.error("[%s] Input validation failed: %s", self.scraper_type, exc)
            return self.format_output(
                status="failed",
                source_query=self._public_source_query(raw_params),
                errors=[exc.to_dict()],
            )

        clean_source_query = self._public_source_query(params)

        try:
            results = await self.scrape(params)
            return self.format_output(
                status="completed",
                source_query=clean_source_query,
                results=results,
            )
        except ScraperError as exc:
            logger.error("[%s] Scrape failed: %s", self.scraper_type, exc)
            return self.format_output(
                status="failed",
                source_query=clean_source_query,
                errors=[exc.to_dict()],
            )
        except Exception as exc:  # noqa: BLE001 - last-resort safety net
            # Anything not already mapped to a ScraperError subclass is a bug
            # in the scraper implementation. We still don't want it to crash
            # the worker process -- log it loudly and return a failed job.
            logger.exception(
                "[%s] Unexpected error (not a ScraperError subclass) -- "
                "this should be fixed to raise a proper ScraperError.",
                self.scraper_type,
            )
            return self.format_output(
                status="failed",
                source_query=clean_source_query,
                errors=[
                    {
                        "error_type": "unhandled_exception",
                        "message": str(exc),
                        "details": {},
                    }
                ],
            )
