"""
Shared output schema for every SDIP scraper (FR-1.6 / FR-G3).

Every scraper's `run()` method must return a dict built by `build_result()`
below. Only the contents of `results` change per scraper type -- the
envelope (job_id, scraper_type, status, scraped_at, source_query,
result_count, errors) is identical across LinkedIn, Google Maps, Website,
Facebook, and Instagram so the backend never needs scraper-specific
handling (NFR-G6).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_result(
    scraper_type: str,
    status: str,
    source_query: dict[str, Any],
    results: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Build a standardized scraper output envelope.

    Args:
        scraper_type: e.g. "linkedin", "google_maps", "website", "facebook", "instagram"
        status: "completed" | "failed" | "partial"
        source_query: the validated input params the job was run with
        results: list of result rows (schema differs per scraper, see each
            scraper's RESULT_FIELDS for the expected keys)
        errors: list of error dicts (see shared.exceptions.ScraperError.to_dict())
        job_id: pass the queue's job id if available; otherwise one is generated
    """
    results = results or []
    errors = errors or []

    return {
        "job_id": job_id or str(uuid.uuid4()),
        "scraper_type": scraper_type,
        "status": status,
        "scraped_at": now_iso(),
        "source_query": source_query,
        "results": results,
        "result_count": len(results),
        "errors": errors,
    }


# Canonical field set per scraper. Every result row for a given scraper_type
# MUST contain exactly these keys, using `None` for anything not found --
# never omit a key. This is what lets the backend store results without
# special-casing per scraper (FR-G3).
RESULT_FIELDS = {
    "linkedin": ["name", "company", "position", "profile_url", "email", "website"],
    "google_maps": [
        "business_name",
        "phone",
        "email",
        "website",
        "address",
        "rating",
        "reviews",
    ],
    "website": ["emails", "phone_numbers", "social_links", "technologies_used"],
    "facebook": ["contact_info", "website", "phone"],
    "instagram": ["followers", "bio", "website", "email"],
}


def empty_row(scraper_type: str) -> dict[str, Any]:
    """Return a result row for the given scraper type with all fields set to None.
    Scrapers should start from this and fill in whatever they actually find,
    so no field is ever silently omitted.
    """
    if scraper_type not in RESULT_FIELDS:
        raise ValueError(f"Unknown scraper_type: {scraper_type}")
    return {field: None for field in RESULT_FIELDS[scraper_type]}
