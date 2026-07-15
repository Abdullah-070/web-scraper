"""
this class deliberately has no direct database or HTTP-framework imports. 
It only returns a plain dict
(see shared.schema.build_result). 
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
        #Do the actual scraping. Must return a list of result rows
        raise NotImplementedError

    def format_output(
        self,
        status: str,
        source_query: dict[str, Any],
        results: list[dict[str, Any]] | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        
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
        """
        redacted_keys = {"auth", "fixture_html"}
        return {k: v for k, v in params.items() if k not in redacted_keys}

    async def run(self, raw_params: dict[str, Any]) -> dict[str, Any]:
        """Entry point called by the queue worker. Handles the
        validate -> scrape -> build standardized output flow
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
